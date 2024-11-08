from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN, FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/maxadvancewidth")
def test_check_maxadvancewidth(check):
    """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""

    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["A"] = (1234567, 1234567)
    assert_results_contain(check(ttFont), FAIL, "mismatch")

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont["hmtx"]
    assert_results_contain(check(ttFont), FAIL, "lacks-table")


@check_id("opentype/caret_slope")
def test_check_caretslope(check):
    """Check hhea.caretSlopeRise and hhea.caretSlopeRun"""

    # PASS
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    # WARN for right-leaning
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    ttFont["post"].italicAngle = -12
    message = assert_results_contain(check(ttFont), WARN, "caretslope-mismatch")
    assert message == (
        "hhea.caretSlopeRise and hhea.caretSlopeRun"
        " do not match with post.italicAngle.\n"
        "Got: caretSlopeRise 1000 and caretSlopeRun 194\n"
        "Expected: caretSlopeRise 1000 and caretSlopeRun 213"
    )

    # FIX
    ttFont["hhea"].caretSlopeRun = 213
    assert_PASS(check(ttFont))

    good_value = ttFont["hhea"].caretSlopeRise
    ttFont["hhea"].caretSlopeRise = 0
    assert_results_contain(check(ttFont), FAIL, "zero-rise")

    # Fix it again from backed up good value
    ttFont["hhea"].caretSlopeRise = good_value

    # WARN for left-leaning
    ttFont["post"].italicAngle = 12
    message = assert_results_contain(check(ttFont), WARN, "caretslope-mismatch")
    assert message == (
        "hhea.caretSlopeRise and hhea.caretSlopeRun"
        " do not match with post.italicAngle.\n"
        "Got: caretSlopeRise 1000 and caretSlopeRun 213\n"
        "Expected: caretSlopeRise 1000 and caretSlopeRun -213"
    )

    # FIX
    ttFont["hhea"].caretSlopeRun = -213
    assert_PASS(check(ttFont))
