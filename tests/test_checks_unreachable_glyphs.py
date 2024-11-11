from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("unreachable_glyphs")
def test_check_unreachable_glyphs(check):
    """Check font contains no unreachable glyphs."""

    font = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_PASS(check(font))

    # Also ensure it works correctly with a color font in COLR v0 format:
    font = TEST_FILE("color_fonts/AmiriQuranColored.ttf")
    assert_PASS(check(font))

    # And also with a color font in COLR v1 format:
    font = TEST_FILE("color_fonts/noto-glyf_colr_1.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    message = assert_results_contain(check(font), WARN, "unreachable-glyphs")
    for glyph in [
        "Gtilde",
        "eight.dnom",
        "four.dnom",
        "three.dnom",
        "two.dnom",
        "i.dot",
        "five.numr",
        "seven.numr",
        "bullet.cap",
        "periodcentered.cap",
        "ampersand.sc",
        "I.uc",
    ]:
        assert glyph in message

    for glyph in [
        "caronvertical",
        "acute.cap",
        "breve.cap",
        "caron.cap",
        "circumflex.cap",
        "dotaccent.cap",
        "dieresis.cap",
        "grave.cap",
        "hungarumlaut.cap",
        "macron.cap",
        "ring.cap",
        "tilde.cap",
        "breve.r",
        "breve.rcap",
    ]:
        assert glyph not in message

    ttFont = TTFont(TEST_FILE("notosansmath/NotoSansMath-Regular.ttf"))
    ttFont.ensureDecompiled()  # (required for mock glyph removal below)
    glyph_order = ttFont.getGlyphOrder()

    # upWhiteMediumTriangle is used as a component in circledTriangle,
    # since CFF does not have composites it became unused.
    # So that is a build tooling issue.
    message = assert_results_contain(check(ttFont), WARN, "unreachable-glyphs")
    assert "upWhiteMediumTriangle" in message
    assert "upWhiteMediumTriangle" in glyph_order

    # Other than that problem, no other glyphs are unreachable;
    # Remove the glyph and then try again.
    glyph_order.remove("upWhiteMediumTriangle")
    ttFont.setGlyphOrder(glyph_order)
    assert "upWhiteMediumTriangle" not in ttFont.glyphOrder
    assert_PASS(check(ttFont))
