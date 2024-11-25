import os

from fontbakery.prelude import check, Message, INFO, FAIL


@check(
    id="googlefonts/description/has_article",
    rationale="""
        Fonts may have a longer article about them, or a description, but
        not both - except for Noto fonts which should have both!
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3841",
        "https://github.com/fonttools/fontbakery/issues/4318",
        "https://github.com/fonttools/fontbakery/issues/4702",
    ],
)
def check_description_has_article(font):
    """Check for presence of an ARTICLE.en_us.html file"""
    directory = os.path.dirname(font.file)
    article_path = os.path.join(directory, "article", "ARTICLE.en_us.html")
    description_path = os.path.join(directory, "DESCRIPTION.en_us.html")
    has_article = os.path.exists(article_path)
    has_description = os.path.exists(description_path)
    article_is_empty = has_article and os.path.getsize(article_path) == 0
    description_is_empty = has_description and os.path.getsize(description_path) == 0

    if not font.is_noto:
        if not has_article:
            yield INFO, Message(
                "missing-article",
                "This font doesn't have an ARTICLE.en_us.html file.",
            )
        else:
            if article_is_empty:
                yield FAIL, Message(
                    "empty-article",
                    "The ARTICLE.en_us.html file is empty.",
                )
            if has_description:
                yield FAIL, Message(
                    "description-and-article",
                    "This font has both a DESCRIPTION.en_us.html file"
                    " and an ARTICLE.en_us.html file. In this case the"
                    " description must be deleted.",
                )
    elif font.is_noto:
        if not has_article:
            yield FAIL, Message(
                "missing-article",
                "This is a Noto font but it lacks an ARTICLE.en_us.html file.",
            )
        if article_is_empty:
            yield FAIL, Message(
                "empty-article",
                "The ARTICLE.en_us.html file is empty.",
            )
        if not has_description or description_is_empty:
            yield FAIL, Message(
                "missing-description",
                "This is a Noto font but it lacks a DESCRIPTION.en_us.html file.",
            )
