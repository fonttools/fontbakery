"""Reporter class that renders report as a HTML document."""

import collections
import html
from typing import List, Dict
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions

from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.utils import unindent_and_unwrap_rationale, html5_collapsible

from fontbakery import __version__ as fb_version

LOGLEVELS = ["ERROR", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]
EMOTICON = {
    "ERROR": "💥",
    "FAIL": "🔥",
    "WARN": "⚠️",
    "INFO": "ℹ️",
    "SKIP": "⏩",
    "PASS": "✅",
    "DEBUG": "🔎",
}
HTML_STYLES = """
html {
    font-family: -apple-system, sans-serif;
}

body {
    margin: 0;
}

header {
    border-bottom: 1px solid #dadada;
    padding-top: 1rem;
    padding-bottom: 1rem;
    display: flex;
    align-items: center;
    padding-left: 2rem;
    padding-right: 2rem;
}

main {
    max-width: 720px;
    margin: auto;
    padding-bottom: 3rem;
}

header svg {
    height: 2rem
}

header .titleBar {
    margin-left: 2rem;
    font-size: 1rem;
}


h2 {
    margin-top: 2em;
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

h3 {
    margin-bottom: 1px;
    margin-top: 2rem;
    border-top: 1px solid #cecece;
    padding-top: 2rem;
}

.check__idlabel {
    color: #999;
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

.section__emoji {
    overflow-wrap: break-word;
}
"""


class TNReporter(SerializeReporter):
    """Renders a report as a HTML document."""

    def write(self):
        with open(self.output_file, "w", encoding="utf-8") as fh:
            fh.write(self.get_html())
        print(f'A TN report in HTML format has been saved to "{self.output_file}"')

    def get_html(self) -> str:
        """Return complete report as a HTML string."""
        data = self.getdoc()
        num_checks = 0
        body_elements = []

        # Order by section first...
        for section in data["sections"]:
            section_name = html.escape(
                section["key"][0].replace("<", "").replace(">", "")
            )
            section_stati_of_note = (
                e for e in section["result"].elements() if e != "PASS"
            )
            if all([self.omit_loglevel(s) for s in section["result"].elements()]):
                continue
            section_stati = "".join(
                EMOTICON[s] for s in sorted(section_stati_of_note, key=LOGLEVELS.index)
            )
            body_elements.append(f"<h2>{section_name}</h2>")
            body_elements.append(f"<span class='section__emoji'>{section_stati}</span>")

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
                if all([self.omit_loglevel(result["result"]) for result in results]):
                    continue
                check_name = html.escape(check)
                body_elements.append(f"<h3>{results[0]['description']}</h3>")
                body_elements.append(
                    f"<div class='check__idlabel'>Check ID: {check_name}</div>"
                )
                body_elements.append(self.render_rationale(results[0], check))
                for result in results:
                    if self.omit_loglevel(result["result"]):
                        continue
                    if "filename" in result:
                        shortFilename = result["filename"].split("/")[-1]
                        body_elements.append(
                            html5_collapsible(
                                f"{EMOTICON[result['result']]} {shortFilename}",
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

        # ---------------------------------- HEADER ---------------------------------- #
        header = getHeader(data, num_checks, self.omit_loglevel)

        body_elements[0:0] = header
        return html5_document(body_elements)

    def html_for_check(self, check) -> str:
        """Return HTML string for complete single check."""
        check["logs"].sort(key=lambda c: LOGLEVELS.index(c["status"]))
        logs = "<ul>" + "".join([self.log_html(log) for log in check["logs"]]) + "</ul>"
        return logs

    def render_rationale(self, check, checkid) -> str:
        if self.succinct or "rationale" not in check:
            return ""
        content = unindent_and_unwrap_rationale(check["rationale"], checkid)
        return cmarkgfm.markdown_to_html(
            content, options=cmarkgfmOptions.CMARK_OPT_UNSAFE
        )

    def log_html(self, log) -> str:
        """Return single check sub-result string as HTML or not if below log
        level."""
        if not self.omit_loglevel(log["status"]):
            emoticon = EMOTICON[log["status"]]
            status = log["status"]
            message = cmarkgfm.markdown_to_html(
                log["message"], options=cmarkgfmOptions.CMARK_OPT_UNSAFE
            )
            return (
                "<li class='details_item'>"
                f"<span class='details_indicator'>{emoticon} {status}</span>"
                f"<span class='details_text'>{message}</span>"
                "</li>"
            )
        return ""


def html5_document(body_elements) -> str:
    """Returns complete HTML5 document string."""

    style = HTML_STYLES
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
                        <header>
                            <svg viewBox="0 0 1608 835" xml:space="preserve" class="sc-cUEOzv itDyay pointer h2"><title>Type Network Logo</title><g class="logo-T"><rect x="-0.3" y="-0.3" fill-rule="evenodd" clip-rule="evenodd" fill="currentColor" width="791.3" height="149.9"></rect><rect x="312.8" y="130.9" fill-rule="evenodd" clip-rule="evenodd" fill="currentColor" width="165.1" height="704.2"></rect></g><polygon class="logo-N" fill-rule="evenodd" clip-rule="evenodd" fill="currentColor" points="878.6,-0.3 983.6,-0.3 1442.4,541.3 1442.4,-0.3 1605,-0.3 1608.2,-0.3 1608.2,835.1 1497.7,835.1 1042.7,300.3 1042.7,835.1 878.6,835.1 	"></polygon></svg>
                            <div class="titleBar">
                                Fontbakery Technical Report
                            </div>
                        </header>

                        <main>
                            {body}
                        </main>
                    </body>
                </html>"""


def getHeader(data, num_checks, omit_loglevel) -> str:
    BODY_TOP = [
        """
        <p>The Type Network fontQA process strives to ensure that your fonts work in and for the various applications, browsers, and platforms as expected by our customers. TN’s fontQA also ensures that the binary data meets current technical specifications (e.g. OpenType Specification) and follows best practices we have put in place to produce consistent, high quality pieces of software—your fonts!</p>
        <p>These checks have been carefully put together by TN staff, taken from the various existing Font Bakery profiles and adding new ones of our own. Some checks have been edited to meet TN’s requirements. This means we may have relaxed the requirement or vice versa. We have tried to include a rationale with each and how to address the issue when reported as a fail or warn. Of course, if you have any questions, please ask; we are here to help you.</p>
        """
    ]

    if num_checks:
        results_summary = [data["result"][k] for k in LOGLEVELS]
        BODY_TOP.append(summary_table(*results_summary, num_checks))

    omitted = [level for level in LOGLEVELS if omit_loglevel(level)]
    if omitted:
        BODY_TOP.append(
            "<p><strong>Note:</strong>"
            " The following loglevels were omitted in this report:"
            f" {', '.join(omitted)}</p>"
        )

    BODY_TOP.append(
        f"""
        <p>On fontbakery grammar, the different checks results means the following:</p>
        <ul>
            <li>🔥 FAIL: A fix must be made in order to meet OT or Unicode specifications;</li>
            <li>⚠️ WARN: A fix that is necessary for proper functioning/expectations of the font/design but is up to the foundry to fixed or not.
            <li>ℹ️ INFO: A recommendation, information, or inquiry</li>
            <li>⏩ SKIP: The check was skipped because it doesn’t apply to the current font. eg. Checks regarding variable font data on static font files.</li>
            <li>💥 ERROR: There was an error when doing the check; this is an error in the check’s code, not in the font. Please report it to us.</li>
            <li>✅ PASS: The check has passed :)</li>
        </ul>

        <p>
            fontbakery version: {fb_version}
        </p>
        """
    )

    return BODY_TOP


def summary_table(
    errors: int,
    fails: int,
    warns: int,
    skips: int,
    infos: int,
    passes: int,
    debugs: int,
    total: int,
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
