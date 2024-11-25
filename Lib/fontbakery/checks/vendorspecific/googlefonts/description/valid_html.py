from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import exit_with_install_instructions


@check(
    id="googlefonts/description/valid_html",
    conditions=["description_and_article"],
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
        "https://github.com/fonttools/fontbakery/issues/2664",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_description_valid_html(descfile, description_and_article):
    """Is this a proper HTML snippet?"""
    try:
        from lxml import html
    except ImportError:
        exit_with_install_instructions("googlefonts")

    for source, content in description_and_article.items():
        if "<html>" in content or "</html>" in content:
            yield FAIL, Message(
                "html-tag",
                f"{source} should not have an \\<html\\> tag,"
                f" since it should only be a snippet that will"
                f" later be included in the Google Fonts"
                f" font family specimen webpage.",
            )

        try:
            html.fromstring("<html>" + content + "</html>")
        except Exception as e:
            yield FAIL, Message(
                "malformed-snippet",
                f"{source} does not look like a proper HTML snippet."
                f" Please look for syntax errors."
                f" Maybe the following parser error message can help"
                f" you find what's wrong:\n"
                f"----------------\n"
                f"{e}\n"
                f"----------------\n",
            )

        if "<p>" not in content or "</p>" not in content:
            yield FAIL, Message(
                "lacks-paragraph", f"{descfile} does not include an HTML \\<p\\> tag."
            )
