from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/canonical_weight_value",
    conditions=["font_metadata"],
    rationale="""
        This check ensures that the font weight declared in the METADATA.pb file
        has a canonical value. The canonical values are multiples of 100 between
        100 and 900.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_canonical_weight_value(font_metadata):
    """METADATA.pb: Check that font weight has a canonical value."""
    first_digit = font_metadata.weight / 100
    if (font_metadata.weight % 100) != 0 or (first_digit < 1 or first_digit > 9):
        yield FAIL, Message(
            "bad-weight",
            f"METADATA.pb: The weight is declared as {font_metadata.weight}"
            f" which is not a multiple of 100 between 100 and 900.",
        )
