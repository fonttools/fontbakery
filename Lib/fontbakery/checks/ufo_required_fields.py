from fontbakery.prelude import check, FAIL, PASS, Message


@check(
    id="ufo_required_fields",
    conditions=["ufo_font"],
    rationale="""
        ufo2ft requires these info fields to compile a font binary:
        unitsPerEm, ascender, descender, xHeight, capHeight and familyName.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
)
def check_ufo_required_fields(ufo_font):
    """Check that required fields are present in the UFO fontinfo."""
    required_fields = []

    for field in [
        "unitsPerEm",
        "ascender",
        "descender",
        "xHeight",
        "capHeight",
        "familyName",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            required_fields.append(field)

    if required_fields:
        yield FAIL, Message(
            "missing-required-fields", f"Required field(s) missing: {required_fields}"
        )
    else:
        yield PASS, "Required fields present."
