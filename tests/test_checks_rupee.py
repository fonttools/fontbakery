from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import SKIP, FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("rupee")
def test_check_rupee(check):
    """Ensure indic fonts have the Indian Rupee Sign glyph."""

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_indic_font" in msg

    # This one is good:
    ttFont = TTFont(
        TEST_FILE("indic-font-with-rupee-sign/NotoSerifDevanagari-Regular.ttf")
    )
    assert_PASS(check(ttFont))

    # But this one lacks the glyph:
    ttFont = TTFont(
        TEST_FILE("indic-font-without-rupee-sign/NotoSansOlChiki-Regular.ttf")
    )
    msg = assert_results_contain(check(ttFont), FAIL, "missing-rupee")
    assert msg == "Please add a glyph for Indian Rupee Sign (₹) at codepoint U+20B9."
