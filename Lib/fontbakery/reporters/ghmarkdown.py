import os
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.utils import html5_collapsible
from fontbakery.checkrunner import Status
from fontbakery import __version__ as version

LOGLEVELS = ["ERROR", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]


class GHMarkdownReporter(SerializeReporter):
    def write(self):
        with open(self.output_file, "w", encoding="utf8") as fh:
            fh.write(self.get_markdown())
        print(
            f"A report in GitHub Markdown format which can be useful\n"
            f" for posting issues on a GitHub issue tracker has been\n"
            f' saved to "{self.output_file}"'
        )

    @staticmethod
    def emoticon(name):
        return {
            "ERROR": "\U0001F494",  # 💔  :broken_heart:
            "FAIL": "\U0001F525",  # 🔥  :fire:
            "WARN": "\U000026A0",  # ⚠️  :warning:
            "INFO": "\U00002139",  # ℹ️  :information_source:
            "SKIP": "\U0001F4A4",  # 💤  :zzz:
            "PASS": "\U0001F35E",  # 🍞  :bread
            "DEBUG": "\U0001F50E",  # 🔎 :mag_right:
        }[name]

    def log_md(self, log):
        if not self.omit_loglevel(log["status"]):
            return "* {} **{}** {}\n".format(
                self.emoticon(log["status"]), log["status"], log["message"]
            )
        else:
            return ""

    def render_rationale(self, check, checkid):
        if self.succinct or not "rationale" in check:
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
        checks = {}
        family_checks = []
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
                    if "filename" not in check.keys():
                        # That's a family check!
                        family_checks.append(check)
                    else:
                        key = os.path.basename(check["filename"])
                        if key not in checks:
                            checks[key] = []
                        checks[key].append(check)

        md = f"## Fontbakery report\n" f"\n" f"Fontbakery version: {version}\n" f"\n"

        if family_checks:
            family_checks.sort(key=lambda c: c["result"])
            md += html5_collapsible(
                "<b>[{}] Family checks</b>".format(len(family_checks)),
                "".join(map(self.check_md, family_checks)) + "<br>",
            )

        for filename in checks.keys():
            checks[filename].sort(key=lambda c: LOGLEVELS.index(c["result"]))
            md += html5_collapsible(
                "<b>[{}] {}</b>".format(len(checks[filename]), filename),
                "".join(map(self.check_md, checks[filename])) + "<br>",
            )

        if num_checks != 0:
            summary_table = (
                "\n### Summary\n\n"
                + ("| {} " + " | {} ".join(LOGLEVELS) + " |\n").format(
                    *[self.emoticon(k) for k in LOGLEVELS]
                )
                + (
                    "|:-----:|:----:|:----:|:----:|:----:|:----:|:----:|\n"
                    "| {} | {} | {} | {} | {} | {} | {} |\n"
                    ""
                ).format(*[data["result"][k] for k in LOGLEVELS])
                + (
                    "| {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% |\n"
                    ""
                ).format(*[100 * data["result"][k] / num_checks for k in LOGLEVELS])
            )
            md += "\n" + summary_table

        omitted = [l for l in LOGLEVELS if self.omit_loglevel(l)]
        if omitted:
            md += (
                "\n"
                + "**Note:** The following loglevels were omitted in this report:\n"
                + "".join(map("* **{}**\n".format, omitted))
            )

        return md
