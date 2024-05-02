"""
FontBakery reporters/terminal can report the events of the FontBakery
CheckRunner Protocol to the terminal (or by pipe to files).
"""
from dataclasses import dataclass
import os
import re
import sys
import atexit
from typing import Optional

from rich.segment import Segment, Segments
from rich.live import Live
from rich.markdown import Markdown
from rich.markup import escape
import rich

from fontbakery.constants import LIGHT_THEME, CUPCAKE, MEANING_MESSAGE
from fontbakery.message import Message
from fontbakery.result import CheckResult
from fontbakery.reporters import FontbakeryReporter

from fontbakery.status import (
    DEBUG,
    ERROR,
    FATAL,
    FAIL,
    INFO,
    PASS,
    SKIP,
    WARN,
)
from fontbakery.utils import IndentedParagraph


statuses = (
    INFO,
    WARN,
    ERROR,
    SKIP,
    PASS,
    FATAL,
    FAIL,
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

    def __post_init__(self):
        super().__post_init__()

        stdout = sys.stdout
        self.theme = self.theme or LIGHT_THEME
        self._console = rich.console.Console(theme=self.theme, highlight=False)
        if self.succinct or self.quiet:
            self.print_progress = False
        self.progressbar = None
        self._log_context = None
        if self.print_progress:
            self.progressbar = ProgressBar(0, self.theme)
            self._log_context = Live(self.progressbar, console=self._console)
            self._log_context.__enter__()
            atexit.register(self._log_context.__exit__, None, None, None)

        self.print_progress = stdout.isatty() and self.print_progress

        self.stdout = stdout

        self._event_buffers = {}

        # logs can occur at any point in the logging protocol
        # especially DEBUG, INFO, WARNING and ERROR
        # FAIL, PASS and SKIP are only expected within checks though
        # Log statuses have weights >= 0
        log_threshold = min(self.loglevels) if self.loglevels else WARN
        self._log_threshold = min(ERROR.weight + 1, max(0, log_threshold.weight))

    def _set_progress_event(self, event):
        index = self._get_index(event.identity)
        self.progressbar[index] = event.summary_status
        total = max(len(self._order), len(self._results))
        self.progressbar.percent = (
            int(round(len(self._results) / total * 100)) if total else 0
        )
        self.progressbar._tick = self._tick
        self._log_context.update(self.progressbar, refresh=True)

    def _get_index(self, identity):
        index = super()._get_index(identity)
        if self.print_progress and len(self._indexes) < len(self.progressbar.slots):
            self.progressbar.slots.append(".")
        return index

    def add_to_event_buffer(self, event, *renderables):
        if event.identity.key not in self._event_buffers:
            self._event_buffers[event.identity.key] = []
        self._event_buffers[event.identity.key].extend(renderables)

    def start(self, order):
        super().start(order)
        if self.quiet:
            return
        self._console.print(
            f"Start ... running {len(order)} individual check executions."
        )
        if self.print_progress:
            self.progressbar.reset(len(order))
            for event in self._results:
                self._set_progress_event(event)

    def end(self):
        super().end()
        if self.quiet:
            return
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
            self._console.print(self._render_results_counter())
            return

        self._console.print("Total:")
        self._console.print(self._render_results_counter())
        self._console.print("")
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

    def receive_result(self, checkresult: CheckResult):
        super().receive_result(checkresult)
        if self.quiet:
            return
        if self.print_progress:
            self._set_progress_event(checkresult)

        msg = checkresult.summary_status
        if msg.weight < self._log_threshold:
            return
        check = checkresult.identity.check

        formatted_iterargs = tuple(
            ("{}[{}]".format(*item), self.runner.get_iterarg(*item))
            for item in checkresult.identity.iterargs
        )

        if self.succinct:
            with_string = "All fonts"
            if formatted_iterargs:
                with_string = os.path.basename(f"{formatted_iterargs[0][1]}")

            self._console.print(
                "{}: [check-id]{}[/]: ".format(
                    escape(with_string),
                    check.id,
                ),
                end="",
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

            self._console.print(
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
                self._console.print(
                    "    [rationale_title]Rationale:" + " " * 64 + "[/]"
                )
                lines = content.wrap(self._console, self._console.width - 6)
                for line in lines._lines:
                    line.pad_left(4)
                    line.set_length(self._console.width)
                self._console.print(lines)

            if check.suggested_profile:
                self._console.print(
                    "    [rationale-title]Suggested Profile:[/] "
                    + f" {check.suggested_profile}",
                )

            if check.proponent:
                self._console.print(
                    "    [rationale-title]Proponent:[/]" + f" {check.proponent}\n",
                )

            if check.proposal:
                moreinfo = check.proposal
                if not isinstance(moreinfo, list):
                    moreinfo = [moreinfo]

                # Here I remove the "legacy" entries because they lack an actual
                # url which the users could access to read more about the check
                moreinfo = [mi for mi in moreinfo if "legacy" not in mi]
                if moreinfo:
                    moreinfo_str = (
                        "    [rationale-title]More info:[/] " + moreinfo[0] + "\n"
                    )
                    if len(moreinfo) > 1:
                        moreinfo_str += (
                            "\n".join(["               " + i for i in moreinfo[1:]])
                            + "\n"
                        )
                    self._console.print(moreinfo_str)

        for result in checkresult.results:
            self._render_subresult(result)

        if not self.succinct:
            self._console.print(
                f"\n    Result: [message-{msg.name}]{msg.name}[/message-{msg.name}]\n"
            )
        else:
            codes = ", ".join(
                set(
                    f"[message-{m.status.name}]{m.message.code}[/]"
                    for m in checkresult.results
                )
            )
            self._console.print(
                f"[message-{msg.name}]{msg.name}[/message-{msg.name}] \\[{codes}]"
            )

    def _render_subresult(self, event):
        if self.succinct:
            return
        msg = event.message
        status = event.status
        if status.weight < self._log_threshold:
            return

        # Log statuses have weights >= 0
        # log_statuses = (INFO, WARN, PASS, SKIP, FATAL, FAIL, ERROR, DEBUG)

        if not isinstance(msg, Message):
            raise (TypeError(f"Expected Message, got {type(msg)}: {msg}"))

        message = str(msg)

        if hasattr(msg, "traceback"):
            message = re.sub(r"(<[^<>]*>)", r"**`\1`**", message, flags=re.MULTILINE)
            traceback = "  \n`" + "`  \n`".join(msg.traceback.strip().split("\n")) + "`"
            traceback = re.sub(r'\n`\s*(File ".*)`', r"\n  ↳ \1", traceback)
            traceback = re.sub(r"\n`\s*(.*)", r"\n`\1", traceback)
            message += traceback

        # This is slightly gross, but rich automatically separates a string from a renderable
        # object with __rich_console__ using a newline, and we want a space.
        output = []
        output.extend(
            self._console.render(
                f"    [message-{status.name.lower()}]{status.name}[/] "
            )
        )
        output.pop()
        output.extend(
            self._console.render(
                IndentedParagraph(Markdown(message), right=2, left=9, first=0)
            )
        )
        self._console.print(Segments(output, new_lines=False))

        if status not in statuses:
            self._console.print("-" * 8, status, "-" * 8)

    def _render_results_counter(self, counter=None):
        if counter is None:
            counter = self._counter
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

        # # there may be custom statuses
        # for name in self._counter:
        #     if name not in seen:
        #         seen.add(name)
        #         result.append(formatting(name.lower(), name, self._counter[name]))
        return separator.join(result)
