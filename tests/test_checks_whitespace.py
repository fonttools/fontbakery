from fontTools.ttLib import TTFont

from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.utils import remove_cmap_entry


def test_check_whitespace_glyphs():
    """Font contains glyphs for whitespace characters?"""
    check = CheckTester("whitespace_glyphs")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # We remove the nbsp char (0x00A0)
    remove_cmap_entry(ttFont, 0x00A0)

    # And make sure the problem is detected:
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x00A0",
        "with a font lacking a nbsp (0x00A0)...",
    )

    # restore original Mada Regular font:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # And finally do the same with the space character (0x0020):
    remove_cmap_entry(ttFont, 0x0020)
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x0020",
        "with a font lacking a space (0x0020)...",
    )


def test_check_whitespace_ink():
    """Whitespace glyphs have ink?"""
    check = CheckTester("whitespace_ink")

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
