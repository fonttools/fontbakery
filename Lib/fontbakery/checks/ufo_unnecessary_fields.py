from fontbakery.prelude import check, PASS, WARN, Message


@check(
    id="ufo_unnecessary_fields",
    conditions=["ufo_font"],
    rationale="""
        ufo2ft will generate these.

        openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted
        because it is useful to toggle a range when not _all_ the glyphs in that
        region are present.

        year is deprecated since UFO v2.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
)
def check_ufo_unnecessary_fields(ufo_font):
    """Check that no unnecessary fields are present in the UFO fontinfo."""
    unnecessary_fields = []

    for field in [
        "openTypeNameUniqueID",
        "openTypeNameVersion",
        "postscriptUniqueID",
        "year",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is not None:
            unnecessary_fields.append(field)

    if unnecessary_fields:
        yield WARN, Message(
            "unnecessary-fields", f"Unnecessary field(s) present: {unnecessary_fields}"
        )
    else:
        yield PASS, "Unnecessary fields omitted."
