from fontbakery.prelude import check, PASS, FAIL


@check(
    id="microsoft/vertical_metrics",
    rationale="""
        If OS/2.fsSelection.useTypoMetrics is not set, then
            hhea.ascender == OS/2.winAscent
            hhea.descender == OS/2.winDescent
            hhea.lineGap == 0
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_vertical_metrics(ttFont):
    """Checking hhea OS/2 vertical_metrics."""
    os2_table = ttFont["OS/2"]
    hhea_table = ttFont["hhea"]
    failed = False
    if os2_table.fsSelection & 1 << 7:
        # useTypoMetrics is set
        if hhea_table.ascender != os2_table.sTypoAscender:
            failed = True
            yield FAIL, (
                "hhea.ascent != OS/2.sTypoAscender: "
                f"{hhea_table.ascender} != {os2_table.sTypoAscender}"
            )
        if hhea_table.descender != os2_table.sTypoDescender:
            failed = True
            yield FAIL, (
                "hhea.descent != OS/2.sTypoDescender: "
                f"{abs(hhea_table.descender)} != {os2_table.sTypoDescender}"
            )
        if hhea_table.lineGap != os2_table.sTypoLineGap:
            failed = True
            yield FAIL, (
                "hhea.lineGap != OS/2.sTypoLineGap: "
                f"{abs(hhea_table.lineGap)} != {os2_table.sTypoLineGap}"
            )
    else:
        # useTypoMetrics is clear
        if hhea_table.ascender != os2_table.usWinAscent:
            failed = True
            yield FAIL, (
                "hhea.ascent != OS/2.usWinAscent: "
                f"{hhea_table.ascender} != {os2_table.usWinAscent}"
            )
        if abs(hhea_table.descender) != os2_table.usWinDescent:
            failed = True
            yield FAIL, (
                "hhea.descent != OS/2.usWinDescent: "
                f"{abs(hhea_table.descender)} != {os2_table.usWinDescent}"
            )
    if not failed:
        yield PASS, "Vertical metrics OK"
