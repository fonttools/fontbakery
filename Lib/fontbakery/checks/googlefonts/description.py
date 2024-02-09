import os

from fontbakery.prelude import check, condition, Message, INFO, PASS, FAIL, WARN, FATAL
from fontbakery.utils import exit_with_install_instructions
from fontbakery.testable import Font


@condition(Font)
def description(font):
    """Read DESCRIPTION.en_us.html file from a font directory."""
    descfile = os.path.join(os.path.dirname(font.file), "DESCRIPTION.en_us.html")
    if os.path.exists(descfile):
        return open(descfile, "r", encoding="utf-8").read()
    else:
        return None


@condition(Font)
def description_html(font):
    try:
        from lxml import etree
    except ImportError:
        exit_with_install_instructions()

    if not font.description:
        return

    html = "<html>" + font.description + "</html>"
    try:
        return etree.fromstring(html)
    except etree.XMLSyntaxError:
        return None


def github_gfonts_description(font: Font, network):
    """Get the contents of the DESCRIPTION.en_us.html file
    from the google/fonts github repository corresponding
    to a given ttFont.
    """
    license_file = font.license_filename  # pytype: disable=attribute-error
    if not license_file or not network:
        return None

    from fontbakery.utils import download_file
    from urllib.request import HTTPError

    LICENSE_DIRECTORY = {"OFL.txt": "ofl", "UFL.txt": "ufl", "LICENSE.txt": "apache"}
    filename = os.path.basename(font.file)
    familyname = filename.split("-")[0].lower()
    url = (
        f"https://github.com/google/fonts/raw/main"
        f"/{LICENSE_DIRECTORY[license_file]}/{familyname}/DESCRIPTION.en_us.html"
    )
    try:
        descfile = download_file(url)
        if descfile:
            return descfile.read().decode("UTF-8")
    except HTTPError:
        return None


@check(
    id="com.google.fonts/check/description/noto_has_article",
    conditions=["is_noto"],
    rationale="""
        Noto fonts are displayed in a different way on the fonts.google.com
         web site, and so must also contain an article about them.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3841",
)
def com_google_fonts_check_description_noto_has_article(font):
    """Noto fonts must have an ARTICLE.en_us.html file"""
    directory = os.path.dirname(font.file)
    descfilepath = os.path.join(directory, "article", "ARTICLE.en_us.html")
    if os.path.exists(descfilepath):
        yield PASS, "ARTICLE.en_us.html exists"
    else:
        yield FAIL, Message(
            "missing-article",
            "This is a Noto font but it lacks an ARTICLE.en_us.html file",
        )


@check(
    id="com.google.fonts/check/description/has_unsupported_elements",
    conditions=["description"],
    rationale="""
        The Google Fonts backend doesn't support the following html elements:
        https://googlefonts.github.io/gf-guide/description.html#requirements
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2811#issuecomment-1907566857",
    ],
    experimental="Since 2024/Feb/07",
)
def com_google_fonts_check_description_has_unsupported_elements(description):
    """Check the description doesn't contain unsupported html elements"""
    unsupported_elements = frozenset(
        [
            "applet",
            "base",
            "embed",
            "form",
            "frame",
            "frameset",
            "head",
            "iframe",
            "link",
            "math",
            "meta",
            "object",
            "script",
            "style",
            "svg",
            "template",
        ]
    )
    found = set()
    for tag in unsupported_elements:
        if f"<{tag}>" in description or f"<{tag} " in description:
            found.add(tag)

    if found:
        found = map(r"\<{}\>".format, found)
        found = ", ".join(found)
        yield FATAL, Message(
            "unsupported-elements",
            f"Description.en_us.html contains unsupported"
            f" html element(s). Please remove: {found}",
        )
    else:
        yield PASS, "DESCRIPTION.en_us.html contains correct elements"


@check(
    id="com.google.fonts/check/description/broken_links",
    conditions=["network", "description_html"],
    rationale="""
        The snippet of HTML in the DESCRIPTION.en_us.html file is added to the font
        family webpage on the Google Fonts website. For that reason, all hyperlinks
        in it must be properly working.
    """,
    proposal=[
        "legacy:check/003",
        "https://github.com/fonttools/fontbakery/issues/4110",
    ],
)
def com_google_fonts_check_description_broken_links(description_html):
    """Does DESCRIPTION file contain broken links?"""
    import requests

    doc = description_html
    broken_links = []
    unique_links = []
    for a_href in doc.iterfind(".//a[@href]"):
        link = a_href.get("href")

        # avoid requesting the same URL more then once
        if link in unique_links:
            continue

        if link.startswith("mailto:") and "@" in link and "." in link.split("@")[1]:
            yield FAIL, Message("email", f"Found an email address: {link}")
            continue

        unique_links.append(link)
        try:
            response = requests.head(link, allow_redirects=True, timeout=10)
            code = response.status_code
            # Status 429: "Too Many Requests" is acceptable
            # because it means the website is probably ok and
            # we're just perhaps being too agressive in probing the server!
            if code not in [requests.codes.ok, requests.codes.too_many_requests]:
                broken_links.append(f"{link} (status code: {code})")
        except requests.exceptions.Timeout:
            yield WARN, Message(
                "timeout",
                f"Timedout while attempting to access: '{link}'."
                f" Please verify if that's a broken link.",
            )
        except requests.exceptions.RequestException:
            broken_links.append(link)

    if len(broken_links) > 0:
        broken_links_list = "\n\t".join(broken_links)
        yield FAIL, Message(
            "broken-links",
            f"The following links are broken"
            f" in the DESCRIPTION file:\n\t"
            f"{broken_links_list}",
        )
    else:
        yield PASS, "All links in the DESCRIPTION file look good!"


@check(
    id="com.google.fonts/check/description/urls",
    conditions=["description_html"],
    rationale="""
        The snippet of HTML in the DESCRIPTION.en_us.html file is added to the font
        family webpage on the Google Fonts website.

        Google Fonts has a content formatting policy for that snippet that expects the
        text content of anchors not to include the http:// or https:// prefixes.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3497",
        "https://github.com/fonttools/fontbakery/issues/4283",
    ],
)
def com_google_fonts_check_description_urls(description_html):
    """URLs on DESCRIPTION file must not display http(s) prefix."""
    passed = True
    for a_href in description_html.iterfind(".//a[@href]"):
        link_text = a_href.text
        if not link_text:
            if a_href.attrib:
                yield FAIL, Message(
                    "empty-link-text",
                    "The following anchor has empty text content:\n\n"
                    f"{a_href.attrib}\n",
                )
            continue

        if link_text.startswith("http://") or link_text.startswith("https://"):
            passed = False
            yield FAIL, Message(
                "prefix-found",
                'Please remove the "http(s)://" prefix from the text content'
                f" of the following anchor:\n\n{link_text}",
            )
            continue

    if passed:
        yield PASS, "All good!"


@check(
    id="com.google.fonts/check/description/git_url",
    conditions=["description_html", "not is_noto"],
    rationale="""
        The contents of the DESCRIPTION.en-us.html file are displayed on the
        Google Fonts website in the about section of each font family specimen page.

        Since all of the Google Fonts collection is composed of libre-licensed fonts,
        this check enforces a policy that there must be a hypertext link in that page
        directing users to the repository where the font project files are
        made available.

        Such hosting is typically done on sites like Github, Gitlab, GNU Savannah or
        any other git-based version control service.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2523",
)
def com_google_fonts_check_description_git_url(description_html):
    """Does DESCRIPTION file contain a upstream Git repo URL?"""
    git_urls = []
    for a_href in description_html.iterfind(".//a[@href]"):
        link = a_href.get("href")
        if "://git" in link:
            git_urls.append(link)
            yield INFO, Message("url-found", f"Found a git repo URL: {link}")

    if len(git_urls) > 0:
        yield PASS, "Looks great!"
    else:
        yield FAIL, Message(
            "lacks-git-url",
            "Please host your font project on a public Git repo"
            " (such as GitHub or GitLab) and place a link"
            " in the DESCRIPTION.en_us.html file.",
        )


@check(
    id="com.google.fonts/check/description/valid_html",
    conditions=["description"],
    rationale="""
        Sometimes people write malformed HTML markup. This check should ensure the
        file is good.

        Additionally, when packaging families for being pushed to the `google/fonts`
        git repo, if there is no DESCRIPTION.en_us.html file, some older versions of
        the `add_font.py` tool insert a placeholder description file which contains
        invalid html. This file needs to either be replaced with an existing
        description file or edited by hand.
    """,
    proposal=[
        "legacy:check/004",
        "https://github.com/fonttools/fontbakery/issues/2664",
    ],
)
def com_google_fonts_check_description_valid_html(descfile, description):
    """Is this a proper HTML snippet?"""
    try:
        from lxml import html
    except ImportError:
        exit_with_install_instructions()

    passed = True
    if "<html>" in description or "</html>" in description:
        yield FAIL, Message(
            "html-tag",
            f"{descfile} should not have an <html> tag,"
            f" since it should only be a snippet that will"
            f" later be included in the Google Fonts"
            f" font family specimen webpage.",
        )

    try:
        html.fromstring("<html>" + description + "</html>")
    except Exception as e:
        passed = False
        yield FAIL, Message(
            "malformed-snippet",
            f"{descfile} does not look like a propper HTML snippet."
            f" Please look for syntax errors."
            f" Maybe the following parser error message can help"
            f" you find what's wrong:\n"
            f"----------------\n"
            f"{e}\n"
            f"----------------\n",
        )

    if "<p>" not in description or "</p>" not in description:
        passed = False
        yield FAIL, Message(
            "lacks-paragraph", f"{descfile} does not include an HTML <p> tag."
        )

    if passed:
        yield PASS, f"{descfile} is a propper HTML file."


@check(
    id="com.google.fonts/check/description/min_length",
    conditions=["description"],
    proposal="legacy:check/005",
)
def com_google_fonts_check_description_min_length(description):
    """DESCRIPTION.en_us.html must have more than 200 bytes."""
    if len(description) <= 200:
        yield FAIL, Message(
            "too-short",
            "DESCRIPTION.en_us.html must have size larger than 200 bytes.",
        )
    else:
        yield PASS, "DESCRIPTION.en_us.html is larger than 200 bytes."


@check(
    id="com.google.fonts/check/description/eof_linebreak",
    conditions=["description"],
    rationale="""
        Some older text-handling tools sometimes misbehave if the last line of data
        in a text file is not terminated with a newline character (also known as '\\n').

        We know that this is a very small detail, but for the sake of keeping all
        DESCRIPTION.en_us.html files uniformly formatted throughout the GFonts
        collection, we chose to adopt the practice of placing this final linebreak
        character on them.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2879",
)
def com_google_fonts_check_description_eof_linebreak(description):
    """DESCRIPTION.en_us.html should end in a linebreak."""
    if description[-1] != "\n":
        yield WARN, Message(
            "missing-eof-linebreak",
            "The last characther on DESCRIPTION.en_us.html"
            " is not a line-break. Please add it.",
        )
    else:
        yield PASS, ":-)"


@check(
    id="com.google.fonts/check/description/family_update",
    rationale="""
        We want to ensure that any significant changes to the font family are
        properly mentioned in the DESCRIPTION file.

        In general, it means that the contents of the DESCRIPTION.en_us.html file
        will typically change if when font files are updated. Please treat this check
        as a reminder to do so whenever appropriate!
    """,
    conditions=["description", "network"],
    proposal="https://github.com/fonttools/fontbakery/issues/3182",
)
def com_google_fonts_check_description_family_update(font, network):
    """
    On a family update, the DESCRIPTION.en_us.html file should ideally also be updated.
    """
    remote_description = github_gfonts_description(font, network)
    if remote_description == font.description:
        yield WARN, Message(
            "description-not-updated",
            "The DESCRIPTION.en_us.html file in this family has not changed"
            " in comparison to the latest font release on the"
            " google/fonts github repo.\n"
            "Please consider mentioning note-worthy improvements made"
            " to the family recently.",
        )
    else:
        yield PASS, "OK"
