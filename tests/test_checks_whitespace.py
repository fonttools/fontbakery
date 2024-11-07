from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("whitespace_widths")
def test_check_whitespace_widths(check):
    """Whitespace glyphs have coherent widths?"""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["space"] = (0, 1)
    assert_results_contain(check(ttFont), FAIL, "different-widths")


@check_id("whitespace_ink")
def test_check_whitespace_ink(check):
    """Whitespace glyphs have ink?"""

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font["cmap"].tables[0].cmap[0x1680] = "a"
    assert_PASS(check(test_font), "because Ogham space mark does have ink.")

    test_font["cmap"].tables[0].cmap[0x0020] = "uni1E17"
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",
        "for whitespace character having composites (with ink).",
    )

    test_font["cmap"].tables[0].cmap[0x0020] = "scedilla"
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",
        "for whitespace character having outlines (with ink).",
    )

    import fontTools.pens.ttGlyphPen

    pen = fontTools.pens.ttGlyphPen.TTGlyphPen(test_font.getGlyphSet())
    pen.addComponent("space", (1, 0, 0, 1, 0, 0))
    test_font["glyf"].glyphs["uni200B"] = pen.glyph()
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",  # should we give is a separate keyword? This looks wrong.
        "for whitespace character having composites (without ink).",
    )
