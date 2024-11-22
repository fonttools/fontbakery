from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/regular_is_400",
    conditions=["family_metadata", "has_regular_style"],
    rationale="""
        The weight of the regular style should be set to 400.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_regular_is_400(family_metadata):
    """METADATA.pb: Regular should be 400."""
    badfonts = []
    for f in family_metadata.fonts:
        if f.full_name.endswith("Regular") and f.weight != 400:
            badfonts.append(f"{f.filename} (weight: {f.weight})")
    if len(badfonts) > 0:
        badfonts = ", ".join(badfonts)
        yield FAIL, Message(
            "not-400",
            f"METADATA.pb: Regular font weight must be 400."
            f" Please fix these: {badfonts}",
        )
