from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/cjk_vertical_metrics_regressions",
    conditions=["is_cjk_font", "regular_remote_style", "regular_ttFont"],
    rationale="""
        Check CJK family has the same vertical metrics as the same family
        hosted on Google Fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3244",
)
def check_cjk_vertical_metrics_regressions(regular_ttFont, regular_remote_style):
    """Check if the vertical metrics of a CJK family are similar to the same
    family hosted on Google Fonts."""
    import math

    gf_ttFont = regular_remote_style
    ttFont = regular_ttFont

    if not ttFont:
        yield FAIL, Message(
            "couldnt-find-local-regular",
            "Could not identify a local Regular style font",
        )
        return
    if not gf_ttFont:
        yield FAIL, Message(
            "couldnt-find-remote-regular",
            "Could not identify a Regular style font hosted on Google Fonts",
        )
        return

    upm_scale = ttFont["head"].unitsPerEm / gf_ttFont["head"].unitsPerEm

    for tbl, attrib in [
        ("OS/2", "sTypoAscender"),
        ("OS/2", "sTypoDescender"),
        ("OS/2", "sTypoLineGap"),
        ("OS/2", "usWinAscent"),
        ("OS/2", "usWinDescent"),
        ("hhea", "ascent"),
        ("hhea", "descent"),
        ("hhea", "lineGap"),
    ]:
        gf_val = math.ceil(getattr(gf_ttFont[tbl], attrib) * upm_scale)
        f_val = math.ceil(getattr(ttFont[tbl], attrib))
        if gf_val != f_val:
            yield FAIL, Message(
                "cjk-metric-regression",
                f" {tbl} {attrib} is {f_val}" f" when it should be {gf_val}",
            )
