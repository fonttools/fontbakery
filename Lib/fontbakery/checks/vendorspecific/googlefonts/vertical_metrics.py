import os

from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="googlefonts/vertical_metrics",
    conditions=["not listed_on_gfonts_api", "not is_cjk_font"],
    rationale="""
        This check generally enforces Google Fonts’ vertical metrics specifications.
        In particular:
        * lineGap must be 0
        * Sum of hhea ascender + abs(descender) + linegap must be
          between 120% and 200% of UPM
        * Warning if sum is over 150% of UPM

        The threshold levels 150% (WARN) and 200% (FAIL) are somewhat arbitrarily chosen
        and may hint at a glaring mistake in the metrics calculations or UPM settings.

        Our documentation includes further information:
        https://github.com/googlefonts/gf-docs/tree/main/VerticalMetrics
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/3762",
        "https://github.com/fonttools/fontbakery/pull/3921",
    ],
)
def check_vertical_metrics(ttFont):
    """Check font follows the Google Fonts vertical metric schema"""

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
        "OS/2.sTypoLineGap": 0,
        "hhea.lineGap": 0,
    }

    # Check typo metrics and hhea lineGap match our expected values
    for k in expected_metrics:
        if font_metrics[k] != expected_metrics[k]:
            yield FAIL, Message(
                f"bad-{k}",
                f'{k} is "{font_metrics[k]}" it should' f" be {expected_metrics[k]}",
            )

    hhea_sum = (
        font_metrics["hhea.ascent"]
        + abs(font_metrics["hhea.descent"])
        + font_metrics["hhea.lineGap"]
    ) / font_upm

    # Check the sum of the hhea metrics is not below 1.2
    # (120% of upm or 1200 units for 1000 upm font)
    if hhea_sum < 1.2:
        yield FAIL, Message(
            "bad-hhea-range",
            f"The sum of hhea.ascender + abs(hhea.descender) + hhea.lineGap"
            f" is {int(hhea_sum * font_upm)} when it should be"
            f" at least {int(font_upm * 1.2)}",
        )

    # Check the sum of the hhea metrics is below 2.0
    elif hhea_sum > 2.0:
        yield FAIL, Message(
            "bad-hhea-range",
            f"The sum of hhea.ascender + abs(hhea.descender) + hhea.lineGap"
            f" is {int(hhea_sum * font_upm)} when it should be"
            f" at most {int(font_upm * 2.0)}",
        )

    # Check the sum of the hhea metrics is between 1.1-1.5x of the font's upm
    elif hhea_sum > 1.5:
        yield WARN, Message(
            "bad-hhea-range",
            f"We recommend the absolute sum of the hhea metrics should be"
            f" between 1.2-1.5x of the font's upm. This font"
            f" has {hhea_sum}x ({int(hhea_sum * font_upm)})",
        )

    # OS/2.sTypoAscender must be strictly positive
    if font_metrics["OS/2.sTypoAscender"] < 0:
        yield FAIL, Message(
            "typo-ascender",
            "The OS/2 sTypoAscender must be strictly positive,"
            " but the font has {font_metrics['OS/2.sTypoAscender']}",
        )

    # hhea.ascent must be strictly positive
    if font_metrics["hhea.ascent"] <= 0:
        yield FAIL, Message(
            "hhea-ascent",
            "The hhea ascender must be strictly positive,"
            " but the font has {font_metrics['hhea.ascent']}",
        )

    # OS/2.usWinAscent must be strictly positive
    if font_metrics["OS/2.usWinAscent"] <= 0:
        yield FAIL, Message(
            "win-ascent",
            f"The OS/2.usWinAscent must be strictly positive,"
            f" but the font has {font_metrics['OS/2.usWinAscent']}",
        )

    # OS/2.sTypoDescender must be negative or zero
    if font_metrics["OS/2.sTypoDescender"] > 0:
        yield FAIL, Message(
            "typo-descender",
            "The OS/2 sTypoDescender must be negative or zero."
            " This font has a strictly positive value.",
        )

    # hhea.descent must be negative or zero
    if font_metrics["hhea.descent"] > 0:
        yield FAIL, Message(
            "hhea-descent",
            "The hhea descender must be negative or zero."
            " This font has a strictly positive value.",
        )

    # OS/2.usWinDescent must be positive or zero
    if font_metrics["OS/2.usWinDescent"] < 0:
        yield FAIL, Message(
            "win-descent",
            "The OS/2.usWinDescent must be positive or zero."
            " This font has a negative value.",
        )
