import os

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import typo_metrics_enabled


@check(
    id="googlefonts/cjk_vertical_metrics",
    conditions=["is_cjk_font", "not listed_on_gfonts_api"],
    rationale="""
        CJK fonts have different vertical metrics when compared to Latin fonts.
        We follow the schema developed by dr Ken Lunde for Source Han Sans and
        the Noto CJK fonts.

        Our documentation includes further information:
        https://github.com/googlefonts/gf-docs/tree/main/Spec#cjk-vertical-metrics
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2797",
)
def check_cjk_vertical_metrics(ttFont):
    """Check font follows the Google Fonts CJK vertical metric schema"""

    filename = os.path.basename(ttFont.reader.file.name)

    # Check necessary tables are present.
    missing_tables = False
    required = ["OS/2", "hhea", "head"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message(f"lacks-{key}", f"{filename} lacks a '{key}' table.")

    if missing_tables:
        return

    font_upm = ttFont["head"].unitsPerEm
    font_metrics = {
        "OS/2.sTypoAscender": ttFont["OS/2"].sTypoAscender,
        "OS/2.sTypoDescender": ttFont["OS/2"].sTypoDescender,
        "OS/2.sTypoLineGap": ttFont["OS/2"].sTypoLineGap,
        "hhea.ascent": ttFont["hhea"].ascent,
        "hhea.descent": ttFont["hhea"].descent,
        "hhea.lineGap": ttFont["hhea"].lineGap,
        "OS/2.usWinAscent": ttFont["OS/2"].usWinAscent,
        "OS/2.usWinDescent": ttFont["OS/2"].usWinDescent,
    }
    expected_metrics = {
        "OS/2.sTypoAscender": round(font_upm * 0.88),
        "OS/2.sTypoDescender": round(font_upm * -0.12),
        "OS/2.sTypoLineGap": 0,
        "hhea.lineGap": 0,
    }

    # Check fsSelection bit 7 is not enabled
    if typo_metrics_enabled(ttFont):
        yield FAIL, Message(
            "bad-fselection-bit7", "OS/2 fsSelection bit 7 must be disabled"
        )

    # Check typo metrics and hhea lineGap match our expected values
    for k in expected_metrics:
        if font_metrics[k] != expected_metrics[k]:
            yield FAIL, Message(
                f"bad-{k}",
                f'{k} is "{font_metrics[k]}" it should be {expected_metrics[k]}',
            )

    # Check hhea and win values match
    if font_metrics["hhea.ascent"] != font_metrics["OS/2.usWinAscent"]:
        yield FAIL, Message(
            "ascent-mismatch", "hhea.ascent must match OS/2.usWinAscent"
        )

    if abs(font_metrics["hhea.descent"]) != font_metrics["OS/2.usWinDescent"]:
        yield FAIL, Message(
            "descent-mismatch",
            "hhea.descent must match absolute value of OS/2.usWinDescent",
        )

    # Check the sum of the hhea metrics is between 1.1-1.5x of the font's upm
    hhea_sum = (
        font_metrics["hhea.ascent"]
        + abs(font_metrics["hhea.descent"])
        + font_metrics["hhea.lineGap"]
    ) / font_upm
    if not 1.1 < hhea_sum <= 1.5:
        yield WARN, Message(
            "bad-hhea-range",
            f"We recommend the absolute sum of the hhea metrics should be"
            f" between 1.1-1.4x of the font's upm. This font has {hhea_sum}x",
        )
