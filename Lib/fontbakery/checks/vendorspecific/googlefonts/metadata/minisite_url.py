from fontbakery.prelude import check, Message, INFO, FAIL, WARN


@check(
    id="googlefonts/metadata/minisite_url",
    conditions=["family_metadata"],
    rationale="""
        Validate family.minisite_url field.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4504",
)
def check_metadata_minisite_url(family_metadata, family_metadata_text_content):
    """METADATA.pb: Validate family.minisite_url field."""
    num_URLs = len(family_metadata_text_content.split("minisite_url")) - 1
    if num_URLs > 1:
        yield WARN, Message(
            "duplicated-url",
            "There seems to be more than a single entry for minisite_url",
        )

    minisite_url = family_metadata.minisite_url
    if not minisite_url:
        yield INFO, Message(
            "lacks-minisite-url", "Please consider adding a family.minisite_url entry."
        )
        return

    def clean_url(url):
        if url.endswith("/"):
            url = url[:-1]
        if url.endswith("/index.htm"):
            url = url[:-10]
        if url.endswith("/index.html"):
            url = url[:-11]
        return url

    expected = clean_url(minisite_url)
    if minisite_url != expected:
        yield FAIL, Message(
            "trailing-clutter",
            f"Please change minisite_url\n\n"
            f"From '{minisite_url}'\n\n"
            f"To: '{expected}'\n\n",
        )
