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

        # Sort them by log-level results:
        for check_group in [fatal_checks, experimental_checks, other_checks]:
            for k in check_group:
                check_group[k] = sorted(
                    check_group[k], key=lambda c: c["result"], reverse=True
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
        )
