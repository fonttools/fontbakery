from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/unique_weight_style_pairs",
    conditions=["family_metadata"],
    rationale="""
        Each font field in the METADATA.pb file should have a unique
        style and weight. If there are duplications, it may indicate that
        that the METADATA.pb file has been incorrectly edited.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_unique_weight_style_pairs(family_metadata):
    """METADATA.pb: check if fonts field only contains unique style:weight pairs."""
    pairs = {}
    for f in family_metadata.fonts:
        styleweight = f"{f.style}:{f.weight}"
        pairs[styleweight] = 1
    if len(set(pairs.keys())) != len(family_metadata.fonts):
        yield FAIL, Message(
            "duplicated",
            "Found duplicated style:weight pair in METADATA.pb fonts field.",
        )
