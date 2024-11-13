from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/cff_deprecated_operators",
    conditions=["ttFont", "is_cff", "cff_analysis"],
    rationale="""
        The 'dotsection' operator and the use of 'endchar' to build accented characters
        from the Adobe Standard Encoding Character Set ("seac") are deprecated in CFF.
        Adobe recommends repairing any fonts that use these, especially endchar-as-seac,
        because a rendering issue was discovered in Microsoft Word with a font that
        makes use of this operation. The check treats that usage as a FAIL.
        There are no known ill effects of using dotsection, so that check is a WARN.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3033",
)
def check_cff_deprecated_operators(cff_analysis):
    """Does the font use deprecated CFF operators or operations?"""

    if cff_analysis.glyphs_dotsection or cff_analysis.glyphs_endchar_seac:
        for gn in cff_analysis.glyphs_dotsection:
            yield WARN, Message(
                "deprecated-operator-dotsection",
                f'Glyph "{gn}" uses deprecated "dotsection" operator.',
            )
        for gn in cff_analysis.glyphs_endchar_seac:
            yield FAIL, Message(
                "deprecated-operation-endchar-seac",
                f'Glyph "{gn}" has deprecated use of "endchar"'
                f" operator to build accented characters (seac).",
            )
