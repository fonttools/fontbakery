"""Reporter class that renders report as a HTML document."""

import collections
import html
from typing import List, Dict

import fontbakery.checkrunner
import fontbakery.reporters.serialize

LOGLEVELS = ["ERROR", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]
EMOTICON = {
    "ERROR": "💥",
    "FAIL": "🔥",
    "WARN": "⚠️",
    "INFO": "ℹ️",
    "SKIP": "⏩",
    "PASS": "✔️",
    "DEBUG": "🔎"
}
ISSUE_URL = "https://github.com/googlefonts/fontbakery/issues"


class HTMLReporter(fontbakery.reporters.serialize.SerializeReporter):
    """Renders a report as a HTML document."""

    def __init__(self, loglevels, **kwd):
        super(HTMLReporter, self).__init__(**kwd)
        self.loglevels = loglevels

    def get_html(self) -> str:
        """Return complete report as a HTML string."""
        data = self.getdoc()
        num_checks = 0
        body_elements = []

        # Order by section first...
        for section in data["sections"]:
            section_name = html.escape(section["key"][0])
            section_stati_of_note = (
                e for e in section["result"].elements() if e != "PASS"
            )
            section_stati = "".join(
                EMOTICON[s] for s in sorted(section_stati_of_note, key=LOGLEVELS.index)
            )
            body_elements.append(f"<h2>{section_name} {section_stati}</h2>")

            checks_by_id: Dict[str, List[Dict[str, str]]] = collections.defaultdict(
                list
            )
            # ...and check second.
            for cluster in section["checks"]:
                if not isinstance(cluster, list):
                    cluster = [cluster]
                num_checks += len(cluster)
                for check in cluster:
                    checks_by_id[check["key"][1]].append(check)
            for check, results in checks_by_id.items():
                check_name = html.escape(check)
                body_elements.append(f"<h3>{results[0]['description']}</h3>")
                body_elements.append(f"<div>Check ID: {check_name}</div>")
                for result in results:
                    if "filename" in result:
                        body_elements.append(
                            html5_collapsible(
                                f"{EMOTICON[result['result']]} <strong>{result['filename']}</strong>",
                                self.html_for_check(result),
                            )
                        )
                    else:
                        body_elements.append(
                            html5_collapsible(
                                f"{EMOTICON[result['result']]} <strong>Family check</strong>",
                                self.html_for_check(result),
                            )
                        )

        body_top = [
            "<h1>Fontbakery Technical Report</h1>",
            "<div>If you think a check is flawed or have an idea for a check, please "
            f" file an issue at <a href='{ISSUE_URL}'>{ISSUE_URL}</a> and remember "
            "to include a pointer to the repo and branch you're checking.</div>",
        ]

        if num_checks:
            results_summary = [data["result"][k] for k in LOGLEVELS]
            body_top.append(summary_table(*results_summary, num_checks))

        omitted = [l for l in LOGLEVELS if self.omit_loglevel(l)]
        if omitted:
            body_top.append(
                "<p><strong>Note:</strong>"
                " The following loglevels were omitted in this report:"
                f" {', '.join(omitted)}</p>"
            )

        body_elements[0:0] = body_top
        return html5_document(body_elements)

    def omit_loglevel(self, msg) -> bool:
        """Determine if message is below log level."""
        return self.loglevels and (
            self.loglevels[0] > fontbakery.checkrunner.Status(msg)
        )

    def html_for_check(self, check) -> str:
        """Return HTML string for complete single check."""
        check["logs"].sort(key=lambda c: LOGLEVELS.index(c["status"]))
        logs = "<ul>" + "".join([self.log_html(log) for log in check["logs"]]) + "</ul>"
        return logs

    def log_html(self, log) -> str:
        """Return single check sub-result string as HTML or not if below log
        level."""
        if not self.omit_loglevel(log["status"]):
            emoticon = EMOTICON[log["status"]]
            status = log["status"]
            message = html.escape(log["message"]).replace("\n", "<br/>")
            return (
                "<li class='details_item'>"
                f"<span class='details_indicator'>{emoticon} {status}</span>"
                f"<span class='details_text'>{message}</span>"
                "</li>"
            )
        return ""


def html5_document(body_elements) -> str:
    """Return complete HTML5 document string."""

    style = """
            html {
                font-family: sans-serif;
            }

            h2 {
                margin-top: 2em;
            }

            h3 {
                margin-bottom: 1px;
            }

            table {
                border-collapse: collapse;
            }

            th,
            td {
                border: 1px solid #ddd;
                padding: 0.5em
            }

            tr:nth-child(even) {
                background-color: #f2f2f2;
            }

            tr {
                text-align: left;
            }

            ul {
                margin-top: 0;
            }

            .details_item {
                list-style: none;
                display: flex;
                align-items: baseline;
            }

            .details_indicator {
                flex: 0 0 5em;
                font-weight: bold;
                padding-right: 0.5em;
                text-align: right;
            }

            .details_text {
                flex: 1 0;
            }
            """
    body = "\n".join(body_elements)
    return f"""<!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <title>Fontbakery Check Report</title>
                        <style>
                            {style}
                        </style>
                    </head>
                    <body>
                    {body}
                    </body>
                </html>"""


def html5_collapsible(summary, details) -> str:
    """Return nestable, collapsible <detail> tag for check grouping and sub-
    results."""

    return f"<details><summary>{summary}</summary><div>{details}</div></details>"


def summary_table(
    errors: int, fails: int, warns: int, skips: int, infos: int, passes: int, debugs: int, total: int
) -> str:
    """Return summary table with statistics."""

    # DEBUG messages are omitted for now...
    return f"""<h2>Summary</h2>
            <table>
            <tr>
                <th>{EMOTICON['ERROR']} ERROR</th>
                <th>{EMOTICON['FAIL']} FAIL</th>
                <th>{EMOTICON['WARN']} WARN</th>
                <th>{EMOTICON['SKIP']} SKIP</th>
                <th>{EMOTICON['INFO']} INFO</th>
                <th>{EMOTICON['PASS']} PASS</th>
            </tr>
            <tr>
                <td>{errors}</td>
                <td>{fails}</td>
                <td>{warns}</td>
                <td>{skips}</td>
                <td>{infos}</td>
                <td>{passes}</td>
            </tr>
            <tr>
                <td>{round(errors / total * 100)}%</td>
                <td>{round(fails / total * 100)}%</td>
                <td>{round(warns / total * 100)}%</td>
                <td>{round(skips / total * 100)}%</td>
                <td>{round(infos / total * 100)}%</td>
                <td>{round(passes / total * 100)}%</td>
            </tr>
            </table>
            """
