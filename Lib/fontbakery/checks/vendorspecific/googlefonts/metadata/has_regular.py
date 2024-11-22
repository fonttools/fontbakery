from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/has_regular",
    conditions=["family_metadata"],
    rationale="""
        According to Google Fonts standards, families should have a Regular
        style.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_has_regular(font):
    """Ensure there is a regular style defined in METADATA.pb."""
    if not font.has_regular_style:
        yield FAIL, Message(
            "lacks-regular",
            "This family lacks a Regular"
            " (style: normal and weight: 400)"
            " as required by Google Fonts standards."
            " If family consists of a single-weight non-Regular style only,"
            " consider the Google Fonts specs for this case:"
            " https://github.com/googlefonts/gf-docs/"
            "tree/main/Spec#single-weight-families",
        )
