from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/description/urls",
    conditions=["description_and_article_html"],
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
def check_description_urls(description_and_article_html):
    """URLs on DESCRIPTION file must not display http(s) prefix."""
    for source, doc in description_and_article_html.items():
        for a_href in doc.iterfind(".//a[@href]"):
            link_text = a_href.text
            if not link_text:
                if a_href.attrib:
                    yield FAIL, Message(
                        "empty-link-text",
                        f"The following anchor in the {source} has empty text content:\n\n"
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
