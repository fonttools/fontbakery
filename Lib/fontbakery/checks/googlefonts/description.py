import os

from fontbakery.prelude import check, condition, Message, INFO, FAIL, WARN, FATAL
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
        exit_with_install_instructions("googlefonts")

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
    id="com.google.fonts/check/description/has_article",
    rationale="""
        Fonts may have a longer article about them, or a description, but
        not both - except for Noto fonts which should have both!
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3841",
        "https://github.com/fonttools/fontbakery/issues/4318",
    ],
)
def com_google_fonts_check_description_has_article(font):
    """Check for presence of an ARTICLE.en_us.html file"""
    directory = os.path.dirname(font.file)
    article_path = os.path.join(directory, "article", "ARTICLE.en_us.html")
    has_article = os.path.exists(article_path)
    article_is_empty = has_article and os.path.getsize(article_path) == 0
    description_is_empty = not font.description

    if not font.is_noto and has_article:
        if not description_is_empty:
            yield FAIL, Message(
                "description-and-article",
                "This font has both a DESCRIPTION.en_us.html file"
                " and an ARTICLE.en_us.html file. In this case the"
                " description must be empty.",
            )
        if article_is_empty:
            yield FAIL, Message(
                "empty-article",
                "The ARTICLE.en_us.html file is empty.",
            )
    elif font.is_noto:
        if not has_article:
            yield FAIL, Message(
                "missing-article",
                "This is a Noto font but it lacks an ARTICLE.en_us.html file",
            )
        if has_article and article_is_empty:
            yield FAIL, Message(
                "empty-article",
                "The ARTICLE.en_us.html file is empty.",
            )
        if not font.description or description_is_empty:
            yield FAIL, Message(
                "empty-description",
                "This is a Noto font but it lacks a DESCRIPTION.en_us.html file",
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

    if broken_links:
        broken_links_list = "\n\t".join(broken_links)
        yield FAIL, Message(
            "broken-links",
            f"The following links are broken"
            f" in the DESCRIPTION file:\n\t"
            f"{broken_links_list}",
        )


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
            yield FAIL, Message(
                "prefix-found",
                'Please remove the "http(s)://" prefix from the text content'
                f" of the following anchor:\n\n{link_text}",
            )
            continue


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

    if not git_urls:
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
        exit_with_install_instructions("googlefonts")

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
        yield FAIL, Message(
            "lacks-paragraph", f"{descfile} does not include an HTML <p> tag."
        )


@check(
    id="com.google.fonts/check/description/min_length",
    conditions=["description"],
    proposal="legacy:check/005",
    rationale="""
        The DESCRIPTION.en_us.html file is intended to provide a brief overview of
        the font family. It should be long enough to be useful to users, but not so
        long that it becomes overwhelming.

        We chose 200 bytes as a minimum length because it suggests that someone has
        taken the time to write "something sensible" about the font.
    """,
)
def com_google_fonts_check_description_min_length(description):
    """DESCRIPTION.en_us.html must have more than 200 bytes."""
    if len(description) <= 200:
        yield FAIL, Message(
            "too-short",
            "DESCRIPTION.en_us.html must have size larger than 200 bytes.",
        )


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
