"""Reporter class that renders report as a HTML document."""

import collections
import html
from typing import Any, List, Dict
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions

from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.utils import unindent_and_unwrap_rationale, html5_collapsible

from fontbakery import __version__ as fb_version

LOGLEVELS = ["ERROR", "FATAL", "FAIL", "WARN", "SKIP", "INFO", "PASS", "DEBUG"]
EMOTICON = {
    "ERROR": "💥",
    "FATAL": "☠",
    "FAIL": "🔥",
    "WARN": "⚠️",
    "INFO": "ℹ️",
    "SKIP": "⏩",
    "PASS": "✅",
    "DEBUG": "🔎",
}
ISSUE_URL = "https://github.com/fonttools/fontbakery/issues"
LOGO_SVG = ""  # this will be set later, after inferrence of vendor-specific profile
BODY_TOP = []  # This will be a piece of header content
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

header img {
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


class HTMLReporter(SerializeReporter):
    """Renders a report as a HTML document."""

    def write(self):
        with open(self.output_file, "w", encoding="utf-8") as fh:
            fh.write(self.get_html())
        print(f'A report in HTML format has been saved to "{self.output_file}"')

    def set_document_branding(self, data):
        """Figure out whether this report belongs to some vendor-specific profile
        based on the presence of specific section names.

        When a logo is provided, it is displayed in the header of the page.

        Similarly, a vendor-specific text can be provided.
        """
        global LOGO_SVG, BODY_TOP  # pylint: disable=global-statement
        for section in data["sections"]:
            section_name = html.escape(section["key"][0])
            if "Type Network" in section_name:
                LOGO_SVG = """<svg viewBox="0 0 1608 835" xml:space="preserve"
                class="sc-cUEOzv itDyay pointer h2"><title>Type Network Logo</title>
                <g class="logo-T"><rect x="-0.3" y="-0.3" fill-rule="evenodd"
                clip-rule="evenodd" fill="currentColor" width="791.3" height="149.9">
                </rect><rect x="312.8" y="130.9" fill-rule="evenodd" clip-rule="evenodd"
                fill="currentColor" width="165.1" height="704.2"></rect></g>
                <polygon class="logo-N" fill-rule="evenodd" clip-rule="evenodd"
                fill="currentColor" points="878.6,-0.3 983.6,-0.3 1442.4,541.3 1442.4,
                -0.3 1605,-0.3 1608.2,-0.3 1608.2,835.1 1497.7,835.1 1042.7,300.3
                1042.7,835.1 878.6,835.1"></polygon></svg>
                """

                BODY_TOP = [
                    """<p>The Type Network fontQA process strives to ensure that your
                    fonts work in and for the various applications, browsers, and
                    platforms as expected by our customers. TN’s fontQA also ensures
                    that the binary data meets current technical specifications
                    (e.g. OpenType Specification) and follows best practices we have
                    put in place to produce consistent, high quality pieces of
                    software—your fonts!</p>
                    <p>These checks have been carefully put together by TN staff,
                    taken from the various existing Font Bakery profiles and adding
                    new ones of our own. Some checks have been edited to meet TN’s
                    requirements. This means we may have relaxed the requirement
                    or vice versa. We have tried to include a rationale with each and
                    how to address the issue when reported as a FAIL or a WARN.
                    Of course, if you have any questions, please ask; we are here to
                    help you.</p>
                    """,
                ]
                return

            # TODO: add other vendor-specific logos here
            else:
                from pkg_resources import resource_filename

                base64_data = open(
                    resource_filename("fontbakery", "data/fontbakery-logo.base64"),
                    encoding="utf-8",
                ).read()
                LOGO_SVG = f"<img src='data:image/svg+xml;base64,{base64_data}'/>"

                BODY_TOP = [
                    "<p>If you think a check is flawed or have an idea for a check,"
                    f" please file an issue at <a href='{ISSUE_URL}'>{ISSUE_URL}</a>"
                    " and remember to include a pointer to the repo and branch"
                    " you're checking.</p>",
                ]
                return

    def get_html(self) -> str:
        """Returns complete report as a HTML string."""
        data = self.getdoc()
        num_checks = 0
        body_elements = []
        self.set_document_branding(data)

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

            checks_by_id: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(
                list
            )
            # ...and check second.
            for cluster in section["checks"]:
                if not isinstance(cluster, list):
                    cluster = [cluster]
                num_checks += len(cluster)
                for check in cluster:
                    check_id = check["key"][1].split(":")[1].split(">")[0]
                    checks_by_id[check_id].append(check)
            for check_id, results in checks_by_id.items():
                if all([self.omit_loglevel(result["result"]) for result in results]):
                    continue
                check_name = html.escape(check_id)
                exp = ""
                if results[0]["experimental"]:
                    exp = (
                        "<div style='color:#88c'>"
                        "EXPERIMENTAL CHECK"
                        f" - {results[0]['experimental']}"
                        "</div>"
                    )
                body_elements.append(f"<h3>{exp}{results[0]['description']}</h3>")
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
                                f"{EMOTICON[result['result']]}"
                                " <strong>Family check</strong>",
                                self.html_for_check(result),
                            )
                        )

        # ------------------------ HEADER --------------------- #
        header = getHeader(data, num_checks, self.omit_loglevel)

        body_elements[0:0] = header
        return html5_document(body_elements)

    def html_for_check(self, check) -> str:
        """Returns HTML string for complete single check."""
        check["logs"].sort(key=lambda c: LOGLEVELS.index(c["status"]))
        logs = "<ul>" + "".join([self.log_html(log) for log in check["logs"]]) + "</ul>"
        return logs

    def render_rationale(self, check, checkid) -> str:
        if self.succinct or not check.get("rationale"):
            return ""
        content = unindent_and_unwrap_rationale(check["rationale"], checkid)
        return cmarkgfm.github_flavored_markdown_to_html(
            content, options=cmarkgfmOptions.CMARK_OPT_UNSAFE
        )

    def log_html(self, log) -> str:
        """Returns single check sub-result string as HTML or not if below log
        level."""
        if not self.omit_loglevel(log["status"]):
            emoticon = EMOTICON[log["status"]]
            status = log["status"]
            message = cmarkgfm.github_flavored_markdown_to_html(
                log["message"]["message"], options=cmarkgfmOptions.CMARK_OPT_UNSAFE
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
                        <title>FontBakery Check Report</title>
                        <style>
                            {style}
                        </style>
                    </head>
                    <body>
                        <header>
                            {LOGO_SVG}
                            <div class="titleBar">
                                Fontbakery Technical Report
                            </div>
                        </header>

                        <main>
                            {body}
                        </main>
                    </body>
                </html>"""


def getHeader(data, num_checks, omit_loglevel) -> List[str]:
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

    MEANING_OF_RESULTS = f"""
    <p>Meaning of check results:</p>

    <ul>
    <li>💥 An <em>ERROR</em> is something wrong with FontBakery itself, possibly a bug.
    <li>☠ A <em>FATAL</em> is an extremely severe issue that must be addressed
    immediately.
    <li>🔥 A <em>FAIL</em> is a problem with the font that must be fixed.
    <li>⚠️ A <em>WARN</em> is something that you should consider addressing.
    <li>ℹ️ An <em>INFO</em> result simply prints something useful. Typically stats.
    <li>✅ A <em>PASS</em> means the font looks good for the given checking routine.
    <li>⏩ And a <em>SKIP</em> happens when the check does not apply to the given font.
    </ul>

    <p>If you get ERRORs, please help us improve the tool by reporting them at our
        <a href="{ISSUE_URL}">issue tracker.</a></p>

    <p>(but other kinds of bug reports and/or feature requests
       are also always welcome, of course!)</p>

    <p>FontBakery version: {fb_version}</p>
    """
    BODY_TOP.append(MEANING_OF_RESULTS)

    return BODY_TOP


def summary_table(
    errors: int,
    fatals: int,
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
                <th>{EMOTICON['FATAL']} FATAL</th>
                <th>{EMOTICON['FAIL']} FAIL</th>
                <th>{EMOTICON['WARN']} WARN</th>
                <th>{EMOTICON['SKIP']} SKIP</th>
                <th>{EMOTICON['INFO']} INFO</th>
                <th>{EMOTICON['PASS']} PASS</th>
            </tr>
            <tr>
                <td>{errors}</td>
                <td>{fatals}</td>
                <td>{fails}</td>
                <td>{warns}</td>
                <td>{skips}</td>
                <td>{infos}</td>
                <td>{passes}</td>
            </tr>
            <tr>
                <td>{round(errors / total * 100)}%</td>
                <td>{round(fatals / total * 100)}%</td>
                <td>{round(fails / total * 100)}%</td>
                <td>{round(warns / total * 100)}%</td>
                <td>{round(skips / total * 100)}%</td>
                <td>{round(infos / total * 100)}%</td>
                <td>{round(passes / total * 100)}%</td>
            </tr>
            </table>
            """
