import os

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.constants import (
    NameID,
    PlatformID,
    UnicodeEncodingID,
    WindowsLanguageID,
)


def typo_metrics_enabled(ttFont):
    return ttFont["OS/2"].fsSelection & 0b10000000 > 0


@check(
    id="com.google.fonts/check/vertical_metrics",
    conditions=["not remote_styles", "not is_cjk_font"],
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
def com_google_fonts_check_vertical_metrics(ttFont):
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


@check(
    id="com.google.fonts/check/vertical_metrics_regressions",
    conditions=["regular_remote_style", "not is_cjk_font"],
    rationale="""
        If the family already exists on Google Fonts, we need to ensure that the
        checked family's vertical metrics are similar. This check will test the
        following schema which was outlined in Font Bakery issue #1162 [1]:

        - The family should visually have the same vertical metrics as the Regular
          style hosted on Google Fonts.

        - If the family on Google Fonts has differing hhea and typo metrics, the family
          being checked should use the typo metrics for both the hhea and typo entries.

        - If the family on Google Fonts has use typo metrics not enabled and the family
          being checked has it enabled, the hhea and typo metrics should use the family
          on Google Fonts winAscent and winDescent values.

        - If the upms differ, the values must be scaled so the visual appearance is
          the same.

        [1] https://github.com/fonttools/fontbakery/issues/1162
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1162",
)
def com_google_fonts_check_vertical_metrics_regressions(regular_ttFont, font):
    """Check if the vertical metrics of a family are similar to the same
    family hosted on Google Fonts."""
    import math

    gf_ttFont = font.regular_remote_style
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

    gf_has_typo_metrics = typo_metrics_enabled(gf_ttFont)
    ttFont_has_typo_metrics = typo_metrics_enabled(ttFont)

    if gf_has_typo_metrics:
        if not ttFont_has_typo_metrics:
            yield FAIL, Message(
                "bad-fsselection-bit7",
                "fsSelection bit 7 needs to be enabled because "
                "the family on Google Fonts has it enabled.",
            )
            # faux enable it so we can see which metrics also need changing
            ttFont_has_typo_metrics = True
        expected_ascender = math.ceil(gf_ttFont["OS/2"].sTypoAscender * upm_scale)
        expected_descender = math.ceil(gf_ttFont["OS/2"].sTypoDescender * upm_scale)
    else:
        # if the win metrics have changed, the updated fonts must have bit 7
        # enabled
        if (
            math.ceil(gf_ttFont["OS/2"].usWinAscent * upm_scale),
            math.ceil(gf_ttFont["OS/2"].usWinDescent * upm_scale),
        ) != (
            math.ceil(ttFont["OS/2"].usWinAscent),
            math.ceil(ttFont["OS/2"].usWinDescent),
        ):
            if not ttFont_has_typo_metrics:
                yield FAIL, Message(
                    "bad-fsselection-bit7",
                    "fsSelection bit 7 needs to be enabled "
                    "because the win metrics differ from "
                    "the family on Google Fonts.",
                )
                ttFont_has_typo_metrics = True
        expected_ascender = math.ceil(gf_ttFont["OS/2"].usWinAscent * upm_scale)
        expected_descender = -math.ceil(gf_ttFont["OS/2"].usWinDescent * upm_scale)

    full_font_name = (
        ttFont["name"]
        .getName(
            NameID.FULL_FONT_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        .toUnicode()
    )
    typo_ascender = ttFont["OS/2"].sTypoAscender
    typo_descender = ttFont["OS/2"].sTypoDescender
    hhea_ascender = ttFont["hhea"].ascent
    hhea_descender = ttFont["hhea"].descent

    if typo_ascender != expected_ascender:
        yield FAIL, Message(
            "bad-typo-ascender",
            f"{full_font_name}:"
            f" OS/2 sTypoAscender is {typo_ascender}"
            f" when it should be {expected_ascender}",
        )

    if typo_descender != expected_descender:
        yield FAIL, Message(
            "bad-typo-descender",
            f"{full_font_name}:"
            f" OS/2 sTypoDescender is {typo_descender}"
            f" when it should be {expected_descender}",
        )

    if hhea_ascender != expected_ascender:
        yield FAIL, Message(
            "bad-hhea-ascender",
            f"{full_font_name}:"
            f" hhea Ascender is {hhea_ascender}"
            f" when it should be {expected_ascender}",
        )

    if hhea_descender != expected_descender:
        yield FAIL, Message(
            "bad-hhea-descender",
            f"{full_font_name}:"
            f" hhea Descender is {hhea_descender}"
            f" when it should be {expected_descender}",
        )


@check(
    id="com.google.fonts/check/cjk_vertical_metrics",
    conditions=["is_cjk_font", "not remote_styles"],
    rationale="""
        CJK fonts have different vertical metrics when compared to Latin fonts.
        We follow the schema developed by dr Ken Lunde for Source Han Sans and
        the Noto CJK fonts.

        Our documentation includes further information:
        https://github.com/googlefonts/gf-docs/tree/main/Spec#cjk-vertical-metrics
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2797",
)
def com_google_fonts_check_cjk_vertical_metrics(ttFont):
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


@check(
    id="com.google.fonts/check/cjk_vertical_metrics_regressions",
    conditions=["is_cjk_font", "regular_remote_style", "regular_ttFont"],
    rationale="""
        Check CJK family has the same vertical metrics as the same family
        hosted on Google Fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3244",
)
def com_google_fonts_check_cjk_vertical_metrics_regressions(
    regular_ttFont, regular_remote_style
):
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
