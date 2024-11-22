from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/unique_full_name_values",
    conditions=["family_metadata"],
    rationale="""
        Each font field in the METADATA.pb file should have a unique
        "full_name" value. If this is not the case, it may indicate that
        the font files have been incorrectly named, or that the METADATA.pb
        file has been incorrectly edited.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_unique_full_name_values(family_metadata):
    """METADATA.pb: check if fonts field only has
    unique "full_name" values.
    """
    fonts = {}
    for f in family_metadata.fonts:
        fonts[f.full_name] = f

    if len(set(fonts.keys())) != len(family_metadata.fonts):
        yield FAIL, Message(
            "duplicated",
            'Found duplicated "full_name" values in METADATA.pb fonts field.',
        )
