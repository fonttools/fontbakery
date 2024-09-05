from fontTools.ttLib import newTable, TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.status import FAIL, WARN


def test_check_colorfont_tables():
    """Ensure font has the expected color font tables."""
    check = CheckTester("colorfont_tables")

    ttFont = TTFont(TEST_FILE("color_fonts/noto-glyf_colr_1.ttf"))
    assert "SVG " not in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    # Check colr v1 static font has an svg table (since v1 isn't yet broadly supported).
    # Will fail since font doesn't have one.
    assert_results_contain(
        check(ttFont), FAIL, "add-svg", "with a static colr v1 font lacking SVG table"
    )

    # Fake a variable font by adding an fvar table.
    ttFont["fvar"] = newTable("fvar")
    assert "fvar" in ttFont.keys()

    # SVG does not support OpenType Variations
    assert_PASS(check(ttFont), "with a variable color font without SVG table")

    # Fake an SVG table:
    ttFont["SVG "] = newTable("SVG ")
    assert "SVG " in ttFont.keys()

    assert_results_contain(
        check(ttFont), FAIL, "variable-svg", "with a variable color font with SVG table"
    )

    # Make it a static again:
    del ttFont["fvar"]
    assert "fvar" not in ttFont.keys()

    assert "SVG " in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    assert_PASS(check(ttFont), "with a static colr v1 font containing both tables.")

    # Now downgrade to colr table to v0:
    ttFont["COLR"].version = 0
    assert "SVG " in ttFont.keys()
    assert_results_contain(
        check(ttFont),
        FAIL,
        "drop-svg",
        "with a font which should not have an SVG table",
    )

    # Delete colr table and keep SVG:
    del ttFont["COLR"]
    assert "SVG " in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_results_contain(
        check(ttFont), FAIL, "add-colr", "with a font which should have a COLR table"
    )

    # Finally delete both color font tables
    del ttFont["SVG "]
    assert "SVG " not in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_PASS(check(ttFont), "with a good font without SVG or COLR tables.")


def test_check_color_cpal_brightness():
    """Color layers should have a minimum brightness"""
    check = CheckTester("color_cpal_brightness")

    font = TEST_FILE("color_fonts/AmiriQuranColored_too_dark.ttf")
    assert_results_contain(
        check(font),
        WARN,
        "glyphs-too-dark-or-too-bright",
        "with a colrv0 font with doo dark layers",
    )

    font = TEST_FILE("color_fonts/AmiriQuranColored.ttf")
    assert_PASS(check(font), "with a colrv0 font with good layer colors")


def test_check_empty_glyph_on_gid1_for_colrv0():
    """Put an empty glyph on GID 1 right after the .notdef glyph for COLRv0 fonts."""

    def gid1area(ttFont):
        from fontTools.pens.areaPen import AreaPen

        glyphOrder = ttFont.getGlyphOrder()
        glyphSet = ttFont.getGlyphSet()
        pen = AreaPen(glyphSet)
        gid1 = glyphSet[glyphOrder[1]]
        gid1.draw(pen)
        return pen.value

    check = CheckTester("empty_glyph_on_gid1_for_colrv0")

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
