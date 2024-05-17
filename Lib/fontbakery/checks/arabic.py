from fontbakery.prelude import PASS, FAIL, SKIP, Message, check
from fontbakery.utils import get_glyph_name


@check(
    id="arabic_spacing_symbols",
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4295",
    ],
    rationale="""
        Unicode has a few spacing symbols representing Arabic dots and other marks,
        but they are purposefully not classified as marks.

        Many fonts mistakenly classify them as marks, making them unsuitable
        for their original purpose as stand-alone symbols to used in pedagogical
        contexts discussing Arabic consonantal marks.
    """,
    severity=4,
)
def check_arabic_spacing_symbols(ttFont):
    """Check that Arabic spacing symbols U+FBB2–FBC1 aren't classified as marks."""

    # code-points
    ARABIC_SPACING_SYMBOLS = {
        0xFBB2,  # Dot Above
        0xFBB3,  # Dot Below
        0xFBB4,  # Two Dots Above
        0xFBB5,  # Two Dots Below
        0xFBB6,  # Three Dots Above
        0xFBB7,  # Three Dots Below
        0xFBB8,  # Three Dots Pointing Downwards Above
        0xFBB9,  # Three Dots Pointing Downwards Below
        0xFBBA,  # Four Dots Above
        0xFBBB,  # Four Dots Below
        0xFBBC,  # Double Vertical Bar Below
        0xFBBD,  # Two Dots Vertically Above
        0xFBBE,  # Two Dots Vertically Below
        0xFBBF,  # Ring
        0xFBC0,  # Small Tah Above
        0xFBC1,  # Small Tah Below
        0xFBC2,  # Wasla Above
    }

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
        reverseCmap = ttFont["cmap"].buildReversed()
        for name in reverseCmap:
            if reverseCmap[name].intersection(ARABIC_SPACING_SYMBOLS):
                if name in class_def and class_def[name] == 3:
                    yield FAIL, Message(
                        "mark-in-gdef",
                        f'"{name}" is defined in GDEF as a mark (class 3).',
                    )


@check(
    id="arabic_high_hamza",
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4290",
    ],
    rationale="""
        Many fonts incorrectly treat ARABIC LETTER HIGH HAMZA (U+0675) as a variant of
        ARABIC HAMZA ABOVE (U+0654) and make it a combining mark of the same size.

        But U+0675 is a base letter and should be a variant of ARABIC LETTER HAMZA
        (U+0621) but raised slightly above baseline.

        Not doing so effectively makes the font useless for Jawi and
        possibly Kazakh as well.
    """,
    severity=4,
)
def check_arabic_high_hamza(ttFont):
    """Check that glyph for U+0675 ARABIC LETTER HIGH HAMZA is not a mark."""
    from fontTools.pens.areaPen import AreaPen
    from copy import deepcopy

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    ttFont_copy = deepcopy(ttFont)

    ARABIC_LETTER_HAMZA = 0x0621
    ARABIC_LETTER_HIGH_HAMZA = 0x0675

    cmap = ttFont_copy.getBestCmap()
    if ARABIC_LETTER_HAMZA not in cmap or ARABIC_LETTER_HIGH_HAMZA not in cmap:
        yield SKIP, Message(
            "glyphs-missing",
            "This check will only run on fonts that have both glyphs U+0621 and U+0675",
        )
        return

    if "GDEF" in ttFont_copy and ttFont_copy["GDEF"].table.GlyphClassDef:
        class_def = ttFont_copy["GDEF"].table.GlyphClassDef.classDefs
        reverseCmap = ttFont_copy["cmap"].buildReversed()
        glyphOrder = ttFont_copy.getGlyphOrder()
        for name in glyphOrder:
            if ARABIC_LETTER_HIGH_HAMZA in reverseCmap.get(name, set()):
                if name in class_def and class_def[name] == 3:
                    yield FAIL, Message(
                        "mark-in-gdef",
                        f'"{name}" is defined in GDEF as a mark (class 3).',
                    )

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
        yield FAIL, Message(
            "glyph-area",
            "The arabic letter high hamza (U+0675) should have roughly"
            " the same size the arabic letter hamza (U+0621),"
            " but a different glyph outline area was detected.",
        )


@check(
    id="allah_ligature",
    rationale="""
        Ensure that the allah ligature, if present in a font, is correctly
        formed in the presence of manually placed tashkeel marks.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4727",
)
def com_google_fonts_check_allah_ligature(ttFont):
    """Ensure correct formation of allah ligature in the presence of tashkeel marks."""

    cmap = ttFont["cmap"].getBestCmap()
    allah_unicode = 0xFDF2

    if allah_unicode not in cmap.keys():
        yield SKIP, "Font does not contain the allah ligature."
        return

    allah_glyphname = cmap[allah_unicode]

    from vharfbuzz import Vharfbuzz

    vharfbuzz = Vharfbuzz(ttFont.reader.file.name)

    def shape(text):
        buf = vharfbuzz.shape(text)
        return vharfbuzz.serialize_buf(buf, glyphsonly=True)

    # Even though the font contains the allah ligature, it's generally not used
    if shape("الله") != allah_glyphname:
        yield PASS, (
            "The allah ligature is present but not substituted for "
            "plain 'allah' input string."
        )
        return

    # The allah ligature is used, so we need to check if it's correctly formed
    plain_allah = shape("الله")
    allah_with_tashkeel = shape("اللَّهُ")

    if plain_allah in allah_with_tashkeel.split("|"):
        yield FAIL, Message(
            "wrong-allah-with-tashkeel",
            "The basic allah ligature (U+FDF2) is used in the presence of tashkeel marks. ",
        )

    # TODO:
    # add check that checks whether the damma is placed on the heh, not the lam
    # see IBM Plex Sans Arabic v1.004
