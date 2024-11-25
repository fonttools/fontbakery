from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import typo_metrics_enabled
from fontbakery.constants import (
    NameID,
    PlatformID,
    UnicodeEncodingID,
    WindowsLanguageID,
)


@check(
    id="googlefonts/vertical_metrics_regressions",
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
def check_vertical_metrics_regressions(regular_ttFont, font):
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
