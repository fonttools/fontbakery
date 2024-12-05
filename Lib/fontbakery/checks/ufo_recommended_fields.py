from fontbakery.prelude import check, PASS, WARN, Message


@check(
    id="ufo_recommended_fields",
    conditions=["ufo_font"],
    rationale="""
        This includes fields that should be in any production font.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
)
def check_ufo_recommended_fields(ufo_font):
    """Check that recommended fields are present in the UFO fontinfo."""
    recommended_fields = []

    for field in [
        "postscriptUnderlineThickness",
        "postscriptUnderlinePosition",
        "versionMajor",
        "versionMinor",
        "styleName",
        "copyright",
        "openTypeOS2Panose",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            recommended_fields.append(field)

    if recommended_fields:
        yield WARN, Message(
            "missing-recommended-fields",
            f"Recommended field(s) missing: {recommended_fields}",
        )
    else:
        yield PASS, "Recommended fields present."
