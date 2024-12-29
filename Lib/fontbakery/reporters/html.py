"""Reporter class that renders report as a HTML document."""

from collections import defaultdict
import os
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions
from jinja2 import ChoiceLoader, Environment, PackageLoader, Template, select_autoescape
from markupsafe import Markup

from fontbakery.reporters.serialize import SerializeReporter
from fontbakery import __version__ as fb_version
from fontbakery.utils import unindent_and_unwrap_rationale

LOGLEVELS = ["ERROR", "FATAL", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]


def emoticon(status):
    return {
        "ERROR": "💥",
        "FATAL": "☠",
        "FAIL": "🔥",
        "WARN": "⚠️",
        "INFO": "ℹ️",
        "SKIP": "⏩",
        "PASS": "✅",
        "DEBUG": "🔎",
    }.get(status, "❓")


ISSUE_URL = "https://github.com/fonttools/fontbakery/issues"


def percent_of(value, total=100):
    return f"{round(value / total * 100)}%"


def markdown(message):
    return Markup(
        cmarkgfm.github_flavored_markdown_to_html(
            message or "", options=cmarkgfmOptions.CMARK_OPT_UNSAFE
        )
    )


class HTMLReporter(SerializeReporter):
    """Renders a report as a HTML document."""

    format_name = "HTML"
    format = "html"

    def template_engine(self) -> Template:
        loaders = [PackageLoader("fontbakery.reporters", f"templates/{self.format}")]
        try:
            profile = self.runner.profile.name
            loaders.insert(
                0,
                PackageLoader(
                    "fontbakery.reporters", f"templates/{profile}/{self.format}"
                ),
            )
        except ValueError:
            pass  # No special templates for this profile
        environment = Environment(
            loader=ChoiceLoader(loaders), autoescape=select_autoescape()
        )

        def omitted(result):
            # This is horribly polymorphic, sorry
            if isinstance(result, list):  # I am cluster of checks
                # Only omit if every check in the cluster should be omitted,
                # otherwise there is useful information here.
                return all(omitted(check) for check in result)
            if "status" in result:  # I am a single subresult
                return self.omit_loglevel(result["status"])
            if "checks" in result:  # I am section
                return all(
                    [
                        self.omit_loglevel(result["result"])
                        for result in result["checks"]
                    ]
                )
            if "result" in result:  # I am check
                return self.omit_loglevel(result["result"])
            # I'm just a string
            return self.omit_loglevel(result)

        environment.tests["omitted"] = omitted
        environment.filters["percent_of"] = percent_of
        environment.filters["markdown"] = markdown
        environment.filters["emoticon"] = emoticon
        environment.filters["basename"] = os.path.basename
        environment.filters["unwrap"] = unindent_and_unwrap_rationale

        return environment.get_template("main." + self.format.lower())

    def template(self, data) -> str:
        """Returns complete report as a HTML string."""
        total = 0

        # Rearrange the data so that checks in each section
        # are clustered by id
        for section in data["sections"]:
            checks = section["checks"]
            total += len(checks)
            checks_by_id = defaultdict(list)
            for check in checks:
                checks_by_id[check["key"][1]].append(check)
            section["clustered_checks"] = list(checks_by_id.values())
            section["status_summary"] = sorted(
                (e for e in section["result"].elements() if e != "PASS"),
                key=LOGLEVELS.index,
            )
        if self.legacy_checkid_references:
            deprecation_warning = (
                "By late-December 2024, FontBakery version 0.13.0"
                " introduced a new naming scheme for the check-IDs.<br>"
                "<br>"
                "Fontbakery detected usage of old IDs and performed an"
                " automatic backwards-compatibility translation for you.<br>"
                "This automatic translation will be deprecated in the next"
                " major release.<br>"
                "<br>"
                "Please start using the new check-IDs as documented at"
                " <a href='https://github.com/fonttools/fontbakery/blob/"
                "31970cdc5807c3b75c2f9b6e223aca57ffda535f/Lib/"
                "fontbakery/legacy_checkids.py'>"
                "/Lib/fontbakery/legacy_checkids.py</a><br>"
                "<br>"
                "The following legacy check-IDs were detected:<br>"
                f" - {'<br> - '.join(self.legacy_checkid_references)}<br>"
                "<br>"
            )
        else:
            deprecation_warning = None

        return self.template_engine().render(
            sections=data["sections"],
            ISSUE_URL=ISSUE_URL,
            fb_version=fb_version,
            total=total,
            summary={k: data["result"][k] for k in LOGLEVELS},
            succinct=self.succinct,
            deprecation_warning=deprecation_warning,
        )
