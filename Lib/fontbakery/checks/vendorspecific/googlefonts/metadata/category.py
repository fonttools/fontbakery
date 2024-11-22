from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/category",
    conditions=["family_metadata"],
    rationale="""
        There are only five acceptable values for the category field in a METADATA.pb
        file:

        - MONOSPACE

        - SANS_SERIF

        - SERIF

        - DISPLAY

        - HANDWRITING

        This check is meant to avoid typos in this field.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2972",
)
def check_metadata_category(family_metadata):
    """Ensure METADATA.pb category field is valid."""
    for category in family_metadata.category:
        if category not in [
            "MONOSPACE",
            "SANS_SERIF",
            "SERIF",
            "DISPLAY",
            "HANDWRITING",
        ]:
            yield FAIL, Message(
                "bad-value",
                f'The field category has "{category}" which is not valid.',
            )
