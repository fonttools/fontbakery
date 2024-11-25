from fontbakery.prelude import check, Message, FATAL
from fontbakery.utils import exit_with_install_instructions


@check(
    id="googlefonts/description/has_unsupported_elements",
    conditions=["description_and_article"],
    rationale="""
        The Google Fonts backend doesn't support the following html elements:
        https://googlefonts.github.io/gf-guide/description.html#requirements
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2811#issuecomment-1907566857",
    ],
)
def check_description_has_unsupported_elements(
    description_and_article, description_and_article_html
):
    """Check the description doesn't contain unsupported html elements"""
    try:
        from lxml import html
    except ImportError:
        exit_with_install_instructions("googlefonts")

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

    for file, doc in description_and_article.items():
        found = set()
        for tag in unsupported_elements:
            if f"<{tag}>" in doc or f"<{tag} " in doc:
                found.add(tag)

        if found:
            found = map(r"\<{}\>".format, found)
            found = ", ".join(found)
            yield FATAL, Message(
                "unsupported-elements",
                f"{file} contains unsupported html element(s). Please remove: {found}",
            )

        parsed = html.fromstring(doc)
        # Video tags must have a src attribute
        bad_video = False
        for video in parsed.iterfind(".//video"):
            bad_video = bad_video or not video.get("src")
        if bad_video:
            yield FATAL, Message(
                "video-tag-needs-src",
                "{file} contains a video tag with no src attribute.",
            )
