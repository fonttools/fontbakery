from fontbakery.prelude import check, Message, FAIL, PASS, WARN


def PANOSE_is_monospaced(panose):
    """
    This function considers the following PANOSE combinations monospace:

    2xx9x xxxxx (Family: Latin Text; Proportion: Monospaced)
    3xx3x xxxxx (Family: Latin Hand Written; Spacing: Monospaced)
    5xx3x xxxxx (Family: Latin Symbol; Spacing: Monospaced)
    """

    # https://github.com/fonttools/fontbakery/issues/2857#issue-608671015

    from fontbakery.constants import (
        PANOSE_Family_Type,
        PANOSE_Proportion,
        PANOSE_Spacing,
    )

    if panose.bFamilyType == PANOSE_Family_Type.LATIN_TEXT:
        return panose.bProportion == PANOSE_Proportion.MONOSPACED

    if panose.bFamilyType in [
        PANOSE_Family_Type.LATIN_HAND_WRITTEN,
        PANOSE_Family_Type.LATIN_SYMBOL,
    ]:
        # NOTE: fonttools has fixed nomenclature for the panose digits,
        #       regardless of context. So, semantically, here the 4th digit
        #       should be called bSpacing, but fonttools still gives it
        #       the 'bProportion' attribute name.
        return panose.bProportion == PANOSE_Spacing.MONOSPACED

    # otherwise
    return False


def PANOSE_expected(family_type):
    # https://github.com/fonttools/fontbakery/issues/2857#issue-608671015
    from fontbakery.constants import (
        PANOSE_Family_Type,
        PANOSE_Proportion,
        PANOSE_Spacing,
    )

    if family_type == PANOSE_Family_Type.LATIN_TEXT:
        return (
            f"Please set PANOSE Proportion to"
            f" {PANOSE_Proportion.MONOSPACED} (monospaced)"
        )

    if family_type in [
        PANOSE_Family_Type.LATIN_HAND_WRITTEN,
        PANOSE_Family_Type.LATIN_SYMBOL,
    ]:
        return f"Please set PANOSE Spacing to {PANOSE_Spacing.MONOSPACED} (monospaced)"

    # Otherwise:
    # I can't even suggest what to do
    # if it is that much broken!
    return ""
    # FIXME:
    # - https://github.com/fonttools/fontbakery/issues/2857
    # - https://github.com/fonttools/fontbakery/issues/2831
    # See also: https://github.com/fonttools/fontbakery/issues/4664


@check(
    id="opentype/monospace",
    conditions=["glyph_metrics_stats", "is_ttf"],
    rationale="""
        There are various metadata in the OpenType spec to specify if a font is
        monospaced or not. If the font is not truly monospaced, then no monospaced
        metadata should be set (as sometimes they mistakenly are...)

        Requirements for monospace fonts:

        * post.isFixedPitch - "Set to 0 if the font is proportionally spaced,
          non-zero if the font is not proportionally spaced (monospaced)"
          (https://www.microsoft.com/typography/otspec/post.htm)

        * hhea.advanceWidthMax must be correct, meaning no glyph's width value
          is greater. (https://www.microsoft.com/typography/otspec/hhea.htm)

        * OS/2.panose.bProportion must be set to 9 (monospace) on latin text fonts.

        * OS/2.panose.bSpacing must be set to 3 (monospace) on latin hand written
          or latin symbol fonts.

        * Spec says: "The PANOSE definition contains ten digits each of which currently
          describes up to sixteen variations. Windows uses bFamilyType, bSerifStyle
          and bProportion in the font mapper to determine family type. It also uses
          bProportion to determine if the font is monospaced."
          (https://www.microsoft.com/typography/otspec/os2.htm#pan
           https://monotypecom-test.monotype.de/services/pan2)

        * OS/2.xAvgCharWidth must be set accurately.
          "OS/2.xAvgCharWidth is used when rendering monospaced fonts,
          at least by Windows GDI"
          (http://typedrawers.com/discussion/comment/15397/#Comment_15397)

        Also we should report an error for glyphs not of average width.


        Please also note:

        Thomas Phinney told us that a few years ago (as of December 2019), if you gave
        a font a monospace flag in Panose, Microsoft Word would ignore the actual
        advance widths and treat it as monospaced.

        Source: https://typedrawers.com/discussion/comment/45140/#Comment_45140
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_monospace(ttFont, glyph_metrics_stats):
    """Checking correctness of monospaced metadata."""
    from fontbakery.constants import IsFixedWidth, PANOSE_Proportion

    # Check for missing tables before indexing them
    missing_tables = False
    required = ["glyf", "hhea", "hmtx", "OS/2", "post"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message("lacks-table", f"Font lacks '{key}' table.")

    if missing_tables:
        return

    passed = True
    # Note: These values are read from the dict here only to
    # reduce the max line length in the check implementation below:
    seems_monospaced = glyph_metrics_stats["seems_monospaced"]
    most_common_width = glyph_metrics_stats["most_common_width"]
    width_max = glyph_metrics_stats["width_max"]

    if ttFont["hhea"].advanceWidthMax != width_max:
        passed = False
        yield FAIL, Message(
            "bad-advanceWidthMax",
            f"Value of hhea.advanceWidthMax"
            f" should be set to {width_max}"
            f" but got {ttFont['hhea'].advanceWidthMax} instead.",
        )

    if seems_monospaced:
        number_of_h_metrics = ttFont["hhea"].numberOfHMetrics
        if number_of_h_metrics != 3:
            passed = False
            yield WARN, Message(
                "bad-numberOfHMetrics",
                f"The OpenType spec recommends at "
                f"https://learn.microsoft.com/en-us/typography/opentype/spec/recom#hhea-table"
                f" that hhea.numberOfHMetrics be set to 3"
                f" but this font has {number_of_h_metrics} instead.\n"
                f"Please read https://github.com/fonttools/fonttools/issues/3014"
                f" to decide whether this makes sense for your font.",
            )

        if not PANOSE_is_monospaced(ttFont["OS/2"].panose):
            passed = False
            family_type = ttFont["OS/2"].panose.bFamilyType
            yield FAIL, Message(
                "mono-bad-panose",
                f"The PANOSE numbers are incorrect for a monospaced font. "
                f"{PANOSE_expected(family_type)}",
            )

        num_glyphs = len(ttFont["glyf"].glyphs)
        unusually_spaced_glyphs = [
            g
            for g in ttFont["glyf"].glyphs
            if g not in [".notdef", ".null", "NULL"]
            and ttFont["hmtx"].metrics[g][0] != 0
            and ttFont["hmtx"].metrics[g][0] != most_common_width
        ]
        outliers_ratio = float(len(unusually_spaced_glyphs)) / num_glyphs
        if outliers_ratio > 0:
            passed = False
            yield WARN, Message(
                "mono-outliers",
                f"Font is monospaced"
                f" but {len(unusually_spaced_glyphs)} glyphs"
                f" ({100.0 * outliers_ratio:.2f}%)"
                f" have a different width."
                f" You should check the widths of:"
                f" {unusually_spaced_glyphs}",
            )
        elif ttFont["post"].isFixedPitch == IsFixedWidth.NOT_MONOSPACED:
            passed = False
            yield FAIL, Message(
                "mono-bad-post-isFixedPitch",
                f"On monospaced fonts, the value of post.isFixedPitch"
                f" must be set to a non-zero value"
                f" (meaning 'fixed width monospaced'),"
                f" but got {ttFont['post'].isFixedPitch} instead.",
            )

        if passed:
            yield PASS, Message(
                "mono-good", "Font is monospaced and all related metadata look good."
            )
    else:
        # it is a non-monospaced font, so lets make sure
        # that all monospace-related metadata is properly unset.

        if ttFont["post"].isFixedPitch != IsFixedWidth.NOT_MONOSPACED:
            passed = False
            yield FAIL, Message(
                "bad-post-isFixedPitch",
                f"On non-monospaced fonts,"
                f" the post.isFixedPitch value must be set to"
                f" {IsFixedWidth.NOT_MONOSPACED} (not monospaced),"
                f" but got {ttFont['post'].isFixedPitch} instead.",
            )

        if ttFont["OS/2"].panose.bProportion == PANOSE_Proportion.MONOSPACED:
            passed = False
            yield FAIL, Message(
                "bad-panose",
                "On non-monospaced fonts,"
                " the OS/2.panose.bProportion value can be set to"
                " any value except 9 (proportion: monospaced)"
                " which is the bad value we got in this font.",
            )
        if passed:
            yield PASS, Message(
                "good", "Font is not monospaced and all related metadata look good."
            )
