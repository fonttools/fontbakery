import os

from fontbakery.reporters.html import HTMLReporter
from fontbakery import __version__ as version

LOGLEVELS = ["ERROR", "FATAL", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]


class GHMarkdownReporter(HTMLReporter):
    format_name = "GitHub Markdown"
    format = "markdown"

    @staticmethod
    def result_is_all_same(cluster):
        first_check = cluster[0]
        return all(check["logs"] == first_check["logs"] for check in cluster[1:])

    def template(self, data):
        fatal_checks = {}
        experimental_checks = {}
        other_checks = {}

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
                    if "filename" in check.keys():
                        key = os.path.basename(check["filename"])
                    else:
                        key = "Family checks"

                    module_parts = check["module"].split(".")
                    if module_parts[0] == "vendorspecific":
                        module = module_parts[1]
                    elif module_parts[0] == "opentype":
                        module = "opentype"
                    else:
                        module = "universal"

                    check["id"] = check["key"][1].split(":")[1]
                    check["id"] = check["id"].split(">")[0]
                    check_id = check["id"].replace("_", "-")
                    check_id = check_id.replace("/", "-")
                    check_id = check_id.replace(".", "-")

                    check["doc_url"] = (
                        f"https://fontbakery.readthedocs.io/en/"
                        f"stable/fontbakery/checks/"
                        f"{module}.html#"
                        f"{check_id}"
                    )

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

                    if self.legacy_checkid_references:
                        references = "\n - ".join(self.legacy_checkid_references)
                        deprecation_warning = (
                            "By late-December 2024, FontBakery version 0.13.0"
                            " introduced a new naming scheme for the check-IDs.\n"
                            "\n"
                            "Fontbakery detected usage of old IDs and performed an"
                            " automatic backwards-compatibility translation for you.\n"
                            "This automatic translation will be deprecated in the next"
                            " major release.\n"
                            "\n"
                            "Please start using the new check-IDs as documented at\n"
                            "https://github.com/fonttools/fontbakery/blob/"
                            "31970cdc5807c3b75c2f9b6e223aca57ffda535f/Lib/"
                            "fontbakery/legacy_checkids.py\n"
                            "\n"
                            "The following legacy check-IDs were detected:\n"
                            f" - {references}\n"
                            "\n"
                        )
                    else:
                        deprecation_warning = None

        # Sort them by log-level results:
        ordering = ["ERROR", "FATAL", "FAIL", "WARN", "INFO", "PASS", "SKIP"]
        for check_group in [fatal_checks, experimental_checks, other_checks]:
            for k in check_group:
                check_group[k] = sorted(
                    check_group[k], key=lambda c: ordering.index(c["result"])
                )

        return self.template_engine().render(
            fb_version=version,
            summary={k: data["result"][k] for k in LOGLEVELS},
            omitted=[loglvl for loglvl in LOGLEVELS if self.omit_loglevel(loglvl)],
            fatal_checks=fatal_checks,
            experimental_checks=experimental_checks,
            other_checks=other_checks,
            succinct=self.succinct,
            total=num_checks,
            deprecation_warning=deprecation_warning,
        )
