from fontTools.ttLib import TTLibError

from fontbakery.prelude import check, Message, FAIL, PASS


@check(
    id="opentype/glyf_unused_data",
    rationale="""
        This check validates the structural integrity of the glyf table,
        by checking that all glyphs referenced in the loca table are
        actually present in the glyf table and that there is no unused
        data at the end of the glyf table. A failure here indicates a
        problem with the font compiler.
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_glyf_unused_data(ttFont):
    """Is there any unused data at the end of the glyf table?"""
    expected_glyphs = len(ttFont.getGlyphOrder())
    try:
        actual_glyphs = len(ttFont["glyf"].glyphs)
        diff = actual_glyphs - expected_glyphs

        if diff < 0:
            yield FAIL, Message(
                "unreachable-data",
                f"Glyf table has unreachable data at the end of the table."
                f" Expected glyf table length {expected_glyphs} (from loca"
                f" table), got length {actual_glyphs}"
                f" (difference: {diff})",
            )
        elif not diff:  # negative diff -> exception below
            yield PASS, "There is no unused data at the end of the glyf table."
        else:
            raise Exception("Bug: fontTools did not raise an expected exception.")
    except TTLibError as error:
        if "not enough 'glyf' table data" in format(error):
            yield FAIL, Message(
                "missing-data",
                f"Loca table references data beyond"
                f" the end of the glyf table."
                f" Expected glyf table length {expected_glyphs}"
                f" (from loca table).",
            )
        else:
            raise Exception("Bug: Unexpected fontTools exception.")
