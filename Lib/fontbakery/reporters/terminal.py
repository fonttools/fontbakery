"""
FontBakery reporters/terminal can report the events of the FontBakery
CheckRunner Protocol to the terminal (or by pipe to files). It understands
both, the synchronous and asynchronous execution model.

Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
from dataclasses import dataclass
import os
import re
import sys
from typing import Optional

from rich.segment import Segment
from rich.live import Live
from rich.markdown import Markdown
from rich.markup import escape
import rich

from fontbakery.constants import LIGHT_THEME, CUPCAKE, MEANING_MESSAGE
from fontbakery.reporters import FontbakeryReporter

from fontbakery.status import (
    Status,
    DEBUG,
    END,
    ENDCHECK,
    ERROR,
    FATAL,
    FAIL,
    INFO,
    PASS,
    SECTIONSUMMARY,
    SKIP,
    START,
    STARTCHECK,
    WARN,
)

statuses = (
    INFO,
    WARN,
    ERROR,
    STARTCHECK,
    SKIP,
    PASS,
    FATAL,
    FAIL,
    ENDCHECK,
    SECTIONSUMMARY,
    START,
    END,
    DEBUG,
)
# these are displayed in the result counters
check_statuses = [ERROR, FATAL, FAIL, SKIP, PASS, WARN, INFO]
check_statuses.sort(key=lambda s: s.weight, reverse=True)


class ProgressBar:
    spinnerstates = " ░▒▓█▓▒░"

    def __init__(self, count, theme):
        self.percent = 0
        self.theme = theme
        self.reset(count)
        self._tick = 0

    def reset(self, count):
        self.slots = ["."] * count

    def __setitem__(self, index, value):
        self.slots[index] = value

    @staticmethod
    def _needs_break(count, columns, right_margin):
        return columns and count > columns and (count % (columns - right_margin))

    def __rich_console__(self, console, options):
        count = 0
        spinner = self.spinnerstates[self._tick % len(self.spinnerstates)]
        yield Segment(f"{spinner} [")
        for slot in self.slots:
            count += 1
            if isinstance(slot, str):
                yield Segment(slot)
            else:
                yield Segment(
                    slot.name[0],
                    style=self.theme.styles["message-" + slot.name.lower()],
                )
            if self._needs_break(count, options.max_width, 1):
                yield Segment("\n  ")
                count = 2
        yield Segment(f"] {self.percent}%")


@dataclass
class TerminalReporter(FontbakeryReporter):
    print_progress: bool = True
    theme: Optional[dict] = None
    skip_status_report: Optional[tuple] = None

    def __post_init__(self):
        super().__post_init__()

        stdout = sys.stdout
        self.theme = self.theme or LIGHT_THEME
        self._console = rich.console.Console(theme=self.theme)
        if self.succinct:
            self.print_progress = False
        self.progressbar = None
        self._log_context = None
        if self.print_progress:
            self.progressbar = ProgressBar(0, self.theme)
            self._log_context = Live(self.progressbar, console=self._console)
            self._log_context.__enter__()

        self.print_progress = stdout.isatty() and self.print_progress

        self.stdout = stdout
        if not self.skip_status_report:
            self.skip_status_report = tuple()
        self._structure_threshold = START.weight
        if self._structure_threshold % 2:
            # always include the according START status
            self._structure_threshold -= 1

        self._event_buffers = {}

        # logs can occur at any point in the logging protocol
        # especially DEBUG, INFO, WARNING and ERROR
        # FAIL, PASS and SKIP are only expected within checks though
        # Log statuses have weights >= 0
        log_threshold = min(self.loglevels) if self.loglevels else WARN
        check_threshold = log_threshold
        self._log_threshold = min(ERROR.weight + 1, max(0, log_threshold.weight))

        # Use this to silence the output checks in async mode, it also activates
        # async mode if turned off.
        # You can't silence whole checks in sync output, as the events are
        # rendered as soon as they happen, you can however silence some log
        # messages in sync mode, use log_threshold for this.
        # default: no DEBUG output
        check_threshold = (
            check_threshold
            if not isinstance(check_threshold, Status)
            else check_threshold.weight
        )
        self._check_threshold = min(ERROR.weight + 1, max(PASS.weight, check_threshold))

        # if this is used we must use async rendering, otherwise we can't
        # suppress the output of checks, because we only know the final
        # status after ENDCHECK.
        self._render_async = self.is_async or check_threshold is not None

    def _register(self, event):
        super()._register(event)
        status, message, identity = event
        if status == ENDCHECK and self.print_progress:
            self._set_progress_event(event)

    def _output(self, event):
        super()._output(event)
        self._render_event(event)

    def _set_order(self, order):
        super()._set_order(order)
        if self.print_progress:
            self.progressbar.reset(len(order))
            for event in self._results:
                self._set_progress_event(event)

    def _set_progress_event(self, event):
        status, message, identity = event
        index = self._get_index(identity)
        self.progressbar[index] = message
        total = max(len(self._order), len(self._results))
        self.progressbar.percent = (
            int(round(len(self._results) / total * 100)) if total else 0
        )
        self.progressbar._tick = self._tick
        self._log_context.update(self.progressbar)

    def _get_index(self, identity):
        index = super()._get_index(identity)
        if self.print_progress and len(self._indexes) < len(self.progressbar.slots):
            self.progressbar.slots.append(".")
        return index

    def add_to_event_buffer(self, event, *renderables):
        status, message, identity = event
        section, check, iterargs = identity
        key = self._get_key(identity)
        if key not in self._event_buffers:
            self._event_buffers[key] = []
        self._event_buffers[key].extend(renderables)

    def _render_START(self, event):
        _, order, _ = event
        self._console.print(
            f"Start ... running {len(order)} individual check executions."
        )

    def _render_END(self, event):
        status, message, identity = event
        self._console.print("")
        if self.collect_results_by:
            self._console.print("Collected results by", self.collect_results_by)
            for key in self._collected_results:
                if self.collect_results_by == "*check":
                    val = key
                elif key is not None and self.runner:
                    val = self.runner.get_iterarg(self.collect_results_by, key)
                elif key is not None:
                    val = key
                else:
                    val = f'(not using "{self.collect_results_by}")'
                self._console.print(f"{self.collect_results_by}: {val}")
                self._console.print(
                    self._render_results_counter(self._collected_results[key])
                )
                self._console.print("")

        if self.print_progress:
            self._log_context.__exit__(None, None, None)

        if self.succinct:
            self._console.print(self._render_results_counter(message))
            return

        self._console.print("Total:")
        self._console.print("")
        self._console.print(self._render_results_counter(message))
        self._console.print("")
        self._console.print(MEANING_MESSAGE)
        self._console.print("")
        if (
            len(self._order)
            and self._counter[ERROR.name]
            + self._counter[FAIL.name]
            + self._counter[FATAL.name]
            == 0
            and self._counter[PASS.name] > 20
        ):
            self._console.print(CUPCAKE)
        self._console.print("DONE!")

    def _render_STARTCHECK(self, event):
        status, message, identity = event
        section, check, iterargs = identity

        formatted_iterargs = tuple(
            ("{}[{}]".format(*item), self.runner.get_iterarg(*item))
            for item in iterargs
        )

        if self.succinct:
            with_string = "All fonts"
            if formatted_iterargs:
                with_string = os.path.basename(f"{formatted_iterargs[0][1]}")

            self.add_to_event_buffer(
                event,
                ("{}: [check-id]{}[/]: ").format(
                    escape(with_string),
                    check.id,
                ),
            )

        else:
            # Omit printing of iterargs when there's none of them:
            with_string = ""
            if formatted_iterargs:
                with_string = f"with {formatted_iterargs[0][1]}"

            experimental = ""
            if hasattr(check, "experimental") and check.experimental:
                exp = f"[EXPERIMENTAL CHECK - {check.experimental}]"
                experimental = f"    [experimental]{exp}[/]\n"

            self.add_to_event_buffer(
                event,
                (" >> [check-id]{}[/]\n{}    [description]{}[/]\n    {}\n").format(
                    check.id,
                    experimental,
                    check.description,
                    with_string,
                ),
            )

            if check.rationale:
                from fontbakery.utils import (
                    unindent_and_unwrap_rationale,
                )

                content = rich.text.Text(
                    unindent_and_unwrap_rationale(check.rationale), "rationale-text"
                )
                self.add_to_event_buffer(
                    event, "\n   [rationale_title]Rationale:" + " " * 64 + "[/]"
                )
                lines = content.wrap(self._console, self._console.width - 6)
                for line in lines._lines:
                    line.pad_left(4)
                self.add_to_event_buffer(event, lines)

            if check.suggested_profile:
                self.add_to_event_buffer(
                    event,
                    "    [rationale-title]Suggested Profile:[/] "
                    + f" {check.suggested_profile}",
                )

            if check.proponent:
                self.add_to_event_buffer(
                    event, "    [rationale-title]Proponent:[/]" + f" {check.proponent}"
                )

            if check.proposal:
                moreinfo = check.proposal
                if not isinstance(moreinfo, list):
                    moreinfo = [moreinfo]

                # Here I remove the "legacy" entries because they lack an actual
                # url which the users could access to read more about the check
                moreinfo = [mi for mi in moreinfo if "legacy" not in mi]
                if moreinfo:
                    moreinfo_str = "    [rationale-title]More info:[/] " + moreinfo[0]
                    if len(moreinfo) > 1:
                        moreinfo_str += "\n".join(
                            ["               " + i for i in moreinfo[1:]]
                        )
                    self.add_to_event_buffer(event, moreinfo_str)

    def _render_ENDCHECK(self, event):
        status, msg, identity = event
        key = self._get_key(identity)
        if msg not in self.loglevels:
            return
        # Deal with event buffer
        if self._event_buffers[key]:
            self._console.print(*self._event_buffers[key], end="")
        if not self.succinct:
            self._console.print("\n")
            self._console.print("    Result: ", end="")
        self._console.print(f"[message-{msg.name}]{msg.name}[/message-{msg.name}]")

    def _render_event(self, event):
        status, message, identity = event
        if (
            not status.weight >= self._structure_threshold
            or status in self.skip_status_report
        ):
            return

        if status == START:
            self._render_START(event)
        elif status == END:
            self._render_END(event)
        elif status == STARTCHECK:
            self._render_STARTCHECK(event)
        elif status == ENDCHECK:
            self._render_ENDCHECK(event)
        elif status == SECTIONSUMMARY:
            self._render_SECTIONSUMMARY(event)
        else:
            self._render_checkresult(event)

    def _render_SECTIONSUMMARY(self, event):
        msg = event.message
        order, counter = msg
        self._console.print("")
        self._console.print(
            "=" * 8, f"Section results: {event.identity.section}", "=" * 8
        )
        self._console.print(
            "{} {} in section".format(
                len(order), len(order) == 1 and "check" or "checks"
            )
        )
        self._console.print("")
        self._console.print(self._render_results_counter(counter))

    def _render_checkresult(self, event):
        if self.succinct:
            return
        status, msg, identity = event

        # Log statuses have weights >= 0
        # log_statuses = (INFO, WARN, PASS, SKIP, FATAL, FAIL, ERROR, DEBUG)
        if status in self.loglevels:
            self.add_to_event_buffer(event, "\n")

            status_name = getattr(status, "name", status)

            try:
                message = f"{msg.message}\n" f"[code: {msg.code}]"
            except AttributeError:
                message = str(msg)

            if hasattr(msg, "traceback"):
                message = re.sub(
                    r"(<[^<>]*>)", r"**`\1`**", message, flags=re.MULTILINE
                )
                traceback = (
                    "  \n`" + "`  \n`".join(msg.traceback.strip().split("\n")) + "`"
                )
                traceback = re.sub(r'\n`\s*(File ".*)`', r"\n  ↳ \1", traceback)
                traceback = re.sub(r"\n`\s*(.*)", r"\n`\1", traceback)
                message += traceback

            self.add_to_event_buffer(
                event, f"[message-{status.name.lower()}]{status.name}[/] "
            )
            self.add_to_event_buffer(event, Markdown(message))

        if status not in statuses:
            self._console.print("-" * 8, status, "-" * 8)

    def _render_results_counter(self, counter):
        if self.succinct:
            formatting = " [message-{}]{:1s}[/]: {}".format
            separator = ""
        else:
            formatting = "    [message-{}]{}[/]: {}".format
            separator = "\n"
        result = []

        seen = set()
        for s in check_statuses:
            name = s.name
            seen.add(name)
            result.append(formatting(name.lower(), name, counter[name]))

        # there may be custom statuses
        for name in counter:
            if name not in seen:
                seen.add(name)
                result.append(formatting(name.lower(), name, counter[name]))
        return separator.join(result)
