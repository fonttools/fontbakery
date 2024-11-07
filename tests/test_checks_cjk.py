from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import WARN, SKIP


@check_id("cjk_not_enough_glyphs")
def test_check_cjk_not_enough_glyphs(check):
    "Any CJK font should contain at least a minimal set of 150 CJK characters."

    ttFont = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_claiming_to_be_cjk_font" in msg

    # Let's modify Montserrat's cmap so there's a cjk glyph
    cmap = ttFont["cmap"].getcmap(3, 1)
    # Add first character of the CJK unified Ideographs
    cmap.cmap[0x4E00] = "A"
    # And let's declare that we are a CJK font
    ttFont["OS/2"].ulCodePageRange1 |= 1 << 17

    msg = assert_results_contain(check(ttFont), WARN, "cjk-not-enough-glyphs")
    assert msg.startswith("There is only one CJK glyph")

    # Add second character of the CJK unified Ideographs
    cmap.cmap[0x4E01] = "B"
    msg = assert_results_contain(check(ttFont), WARN, "cjk-not-enough-glyphs")
    assert msg.startswith("There are only 2 CJK glyphs")
