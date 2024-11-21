from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/varfont/family_axis_ranges",
    rationale="""
        Between members of a family (such as Roman & Italic),
        the ranges of variable axes must be identical.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4445",
    conditions=["VFs"],
)
def check_varfont_family_axis_ranges(ttFonts):
    """Check that family axis ranges are indentical"""

    def axis_info(ttFont):
        if "fvar" in ttFont:
            fvar = ttFont["fvar"]
            axis_info = [
                (a.axisTag, a.minValue, a.maxValue, a.defaultValue) for a in fvar.axes
            ]
            return tuple(sorted(axis_info))

    axes_info_from_font_files = {axis_info(ttFont) for ttFont in ttFonts}
    if len(axes_info_from_font_files) != 1:
        yield FAIL, Message(
            "axis-range-mismatch",
            "Variable axes ranges not matching between font files",
        )
