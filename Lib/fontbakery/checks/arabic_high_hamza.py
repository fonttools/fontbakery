from fontbakery.prelude import FAIL, SKIP, WARN, Message, check
from fontbakery.utils import get_glyph_name


@check(
    id="arabic_high_hamza",
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4290",
    ],
    rationale="""
        Many fonts incorrectly treat ARABIC LETTER HIGH HAMZA (U+0674) as a variant of
        ARABIC HAMZA ABOVE (U+0654) and make it a combining mark of the same size.

        But U+0674 is a base letter and should be a variant of ARABIC LETTER HAMZA
        (U+0621) but raised slightly above baseline.

        Not doing so effectively makes the font useless for Jawi and
        possibly Kazakh as well.
    """,
    severity=4,
)
def check_arabic_high_hamza(ttFont):
    """Check that glyph for U+0674 ARABIC LETTER HIGH HAMZA is not a mark."""
    from fontTools.pens.areaPen import AreaPen
    from copy import deepcopy

    ARABIC_LETTER_HAMZA = 0x0621
    ARABIC_LETTER_HIGH_HAMZA = 0x0674

    cmap = ttFont.getBestCmap()
    if ARABIC_LETTER_HIGH_HAMZA not in cmap:
        yield SKIP, Message(
            "glyphs-missing",
            "This check will only run on fonts that have U+0674 glyph",
        )
        return

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
        name = get_glyph_name(ttFont, ARABIC_LETTER_HIGH_HAMZA)
        if name in class_def and class_def[name] == 3:
            yield FAIL, Message(
                "mark-in-gdef",
                f'"{name}" is defined in GDEF as a mark (class 3).',
            )

    if ARABIC_LETTER_HAMZA not in cmap:
        yield SKIP, Message(
            "glyphs-missing",
            "This check will only run on fonts that have both glyphs U+0621 and U+0674",
        )
        return

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    ttFont_copy = deepcopy(ttFont)

    # Also validate the bounding box of the glyph and compare
    # it to U+0621 expecting them to have roughly the same size
    # (within a certain tolerance margin)
    glyph_set = ttFont_copy.getGlyphSet()
    area_pen = AreaPen(glyph_set)

    glyph_set[get_glyph_name(ttFont_copy, ARABIC_LETTER_HAMZA)].draw(area_pen)
    hamza_area = area_pen.value

    area_pen.value = 0
    glyph_set[get_glyph_name(ttFont_copy, ARABIC_LETTER_HIGH_HAMZA)].draw(area_pen)
    high_hamza_area = area_pen.value

    if abs((high_hamza_area - hamza_area) / hamza_area) > 0.1:
        yield WARN, Message(
            "glyph-area",
            "The arabic letter high hamza (U+0674) should have roughly"
            " the same size the arabic letter hamza (U+0621) while raised"
            " above baseline, but a different glyph outline area was detected.",
        )
