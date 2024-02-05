import os

from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.utils import html5_collapsible
from fontbakery import __version__ as version

LOGLEVELS = ["ERROR", "FATAL", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]


class GHMarkdownReporter(SerializeReporter):
    def write(self):
        with open(self.output_file, "w", encoding="utf8") as fh:
            fh.write(self.get_markdown())
        if not self.quiet:
            print(
                f"A report in GitHub Markdown format which can be useful\n"
                f" for posting issues on a GitHub issue tracker has been\n"
                f' saved to "{self.output_file}"'
            )

    @staticmethod
    def emoticon(name):
        return {
            "ERROR": "\U0001F494",  # 💔  :broken_heart:
            "FATAL": "\U00002620",  # ☠️  :skull_and_crossbones:
            "FAIL": "\U0001F525",  # 🔥  :fire:
            "WARN": "\U000026A0",  # ⚠️  :warning:
            "INFO": "\U00002139",  # ℹ️  :information_source:
            "SKIP": "\U0001F4A4",  # 💤  :zzz:
            "PASS": "\U0001F35E",  # 🍞  :bread
            "DEBUG": "\U0001F50E",  # 🔎 :mag_right:
        }[name]

    def log_md(self, log):
        if not self.omit_loglevel(log["status"]):
            msg = log["message"]
            message = msg["message"]
            if "code" in msg and msg["code"]:
                message += f" [code: {msg['code']}]"
            return "* {} **{}** {}\n".format(
                self.emoticon(log["status"]), log["status"], message
            )
        else:
            return ""

    def render_rationale(self, check, checkid):
        if self.succinct or not check.get("rationale"):
            return ""

        from fontbakery.utils import unindent_and_unwrap_rationale

        content = unindent_and_unwrap_rationale(check["rationale"], checkid)
        return "\n".join([">" + line for line in content.split("\n")])

    def check_md(self, check):
        checkid = check["key"][1].split(":")[1].split(">")[0]
        profile = check["profile"]

        check["logs"].sort(key=lambda c: c["status"])
        logs = "".join(map(self.log_md, check["logs"]))
        github_search_url = (
            '<a href="https://font-bakery.readthedocs.io/en/stable'
            f'/fontbakery/profiles/{profile}.html#{checkid}">'
            f"{checkid}</a>"
        )

        rationale = self.render_rationale(check, checkid)

        return html5_collapsible(
            "{} <b>{}:</b> {} ({})".format(
                self.emoticon(check["result"]),
                check["result"],
                check["description"],
                github_search_url,
            ),
            f"\n\n{rationale}\n{logs}",
        )

    @staticmethod
    def deduce_profile_from_section_name(section):
        # This is very hacky!
        # We should have a much better way of doing it...
        if "Google Fonts" in section:
            return "googlefonts"
        if "Adobe" in section:
            return "adobefonts"
        if "Font Bureau" in section:
            return "fontbureau"
        if "Universal" in section:
            return "universal"
        if "Basic UFO checks" in section:
            return "ufo_sources"
        if "Checks inherited from Microsoft Font Validator" in section:
            return "fontval"
        if "fontbakery.profiles." in section:
            return section.split("fontbakery.profiles.")[1].split(">")[0]
        return section

    @staticmethod
    def result_is_all_same(cluster):
        first_check = cluster[0]
        return all(check["logs"] == first_check["logs"] for check in cluster[1:])

    def get_markdown(self):
        fatal_checks = {}
        experimental_checks = {}
        other_checks = {}

        data = self.getdoc()
        num_checks = 0
        for section in data["sections"]:
            for cluster in section["checks"]:
                if not isinstance(cluster, list):
                    cluster = [cluster]

                num_checks += len(cluster)
                if len(cluster) > 1 and self.result_is_all_same(cluster):
                    # Pretend it's a family check
                    cluster = [cluster[0]]
                    del cluster[0]["filename"]

                for check in cluster:
                    if self.omit_loglevel(check["result"]):
                        continue
                    check["profile"] = self.deduce_profile_from_section_name(
                        section["key"][0]
                    )

                    if "filename" in check.keys():
                        key = os.path.basename(check["filename"])
                    else:
                        key = "Family checks"

                    if check["result"] == "FATAL":
                        # These will be reported at the very top.
                        if key not in fatal_checks:
                            fatal_checks[key] = []
                        fatal_checks[key].append(check)
                    elif check["experimental"]:
                        # These will also be reported separately.
                        if key not in experimental_checks:
                            experimental_checks[key] = []
                        experimental_checks[key].append(check)
                    else:
                        # All other checks are reported last.
                        if key not in other_checks:
                            other_checks[key] = []
                        other_checks[key].append(check)

        md = f"## FontBakery report\n\nfontbakery version: {version}\n\n"

        if fatal_checks:
            md += (
                "<h2>Checks with FATAL results</h2>"
                "<p>These must be addressed first.</p>"
            )
            for filename in fatal_checks.keys():
                md += html5_collapsible(
                    "<b>[{}] {}</b>".format(len(fatal_checks[filename]), filename),
                    "".join(map(self.check_md, fatal_checks[filename])) + "<br>",
                )

        if experimental_checks:
            md += (
                "<h2>Experimental checks</h2>"
                "<p>These won't break the CI job for now, but will become effective"
                " after some time if nobody raises any concern.</p>"
            )
            for filename in experimental_checks.keys():
                experimental_checks[filename].sort(
                    key=lambda c: LOGLEVELS.index(c["result"])
                )
                md += html5_collapsible(
                    "<b>[{}] {}</b>".format(
                        len(experimental_checks[filename]), filename
                    ),
                    "".join(map(self.check_md, experimental_checks[filename])) + "<br>",
                )

        if other_checks:
            if experimental_checks or fatal_checks:
                md += "<h2>All other checks</h2>"
            else:
                md += "<h2>Check results</h2>"

            for filename in other_checks.keys():
                other_checks[filename].sort(key=lambda c: LOGLEVELS.index(c["result"]))
                md += html5_collapsible(
                    "<b>[{}] {}</b>".format(len(other_checks[filename]), filename),
                    "".join(map(self.check_md, other_checks[filename])) + "<br>",
                )

        if num_checks != 0:
            summary_table = (
                "\n### Summary\n\n"
                + ("| {} " + " | {} ".join(LOGLEVELS) + " |\n").format(
                    *[self.emoticon(k) for k in LOGLEVELS]
                )
                + (
                    "|" + "|".join([":-----:"] * len(LOGLEVELS)) + "|\n"
                    "|" + "|".join([" {} "] * len(LOGLEVELS)) + "|\n"
                ).format(*[data["result"][k] for k in LOGLEVELS])
                + ("|" + "|".join([" {:.0f}% "] * len(LOGLEVELS)) + "|\n").format(
                    *[100 * data["result"][k] / num_checks for k in LOGLEVELS]
                )
            )
            md += "\n" + summary_table

        omitted = [loglvl for loglvl in LOGLEVELS if self.omit_loglevel(loglvl)]
        if omitted:
            md += (
                "\n"
                + "**Note:** The following loglevels were omitted in this report:\n"
                + "".join(map("* **{}**\n".format, omitted))
            )

        return md
