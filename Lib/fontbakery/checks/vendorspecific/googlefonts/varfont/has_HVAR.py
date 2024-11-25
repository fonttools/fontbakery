from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/varfont/has_HVAR",
    rationale="""
        Not having a HVAR table can lead to costly text-layout operations on some
        platforms, which we want to avoid.

        So, all variable fonts on the Google Fonts collection should have an HVAR
        with valid values.

        More info on the HVAR table can be found at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements
    """,
    # FIX-ME: We should clarify which are these platforms in which there can be issues
    #         with costly text-layout operations when an HVAR table is missing!
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2119",
)
def check_varfont_has_HVAR(ttFont):
    """Check that variable fonts have an HVAR table."""
    if "HVAR" not in ttFont.keys():
        yield FAIL, Message(
            "lacks-HVAR",
            "All variable fonts on the Google Fonts collection"
            " must have a properly set HVAR table in order"
            " to avoid costly text-layout operations on"
            " certain platforms.",
        )
