from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL, WARN


@check_id("color_cpal_brightness")
def test_check_color_cpal_brightness(check):
    """Color layers should have a minimum brightness"""

    font = TEST_FILE("color_fonts/AmiriQuranColored_too_dark.ttf")
    assert_results_contain(
        check(font),
        WARN,
        "glyphs-too-dark-or-too-bright",
        "with a colrv0 font with doo dark layers",
    )

    font = TEST_FILE("color_fonts/AmiriQuranColored.ttf")
    assert_PASS(check(font), "with a colrv0 font with good layer colors")


@check_id("empty_glyph_on_gid1_for_colrv0")
def test_check_empty_glyph_on_gid1_for_colrv0(check):
    """Put an empty glyph on GID 1 right after the .notdef glyph for COLRv0 fonts."""

    def gid1area(ttFont):
        from fontTools.pens.areaPen import AreaPen

        glyphOrder = ttFont.getGlyphOrder()
        glyphSet = ttFont.getGlyphSet()
        pen = AreaPen(glyphSet)
        gid1 = glyphSet[glyphOrder[1]]
        gid1.draw(pen)
        return pen.value

    ttFont = TTFont(TEST_FILE("color_fonts/AmiriQuranColored_gid1_notempty.ttf"))
    assert (
        "COLR" in ttFont.keys()
        and ttFont["COLR"].version == 0
        and gid1area(ttFont) != 0
    )
    assert_results_contain(
        check(ttFont),
        FAIL,
        "gid1-has-contours",
        "with a font with COLR table but no empty glyph on GID 1.",
    )

    ttFont = TTFont(TEST_FILE("color_fonts/AmiriQuranColored.ttf"))
    assert (
        "COLR" in ttFont.keys()
        and ttFont["COLR"].version == 0
        and gid1area(ttFont) == 0
    )
    assert_PASS(
        check(ttFont), "with a good font with COLR table and an empty glyph on GID 1."
    )
