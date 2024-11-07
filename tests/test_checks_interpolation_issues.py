from fontTools.ttLib import TTFont

from fontbakery.status import SKIP, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_interpolation_issues():
    """Detect any interpolation issues in the font."""
    check = CheckTester("interpolation_issues")
    # With a good font
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("notosansbamum/NotoSansBamum[wght].ttf"))
    msg = assert_results_contain(check(ttFont), WARN, "interpolation-issues")
    assert "becomes underweight" in msg
    assert "has a kink" in msg

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_variable_font" in msg

    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_ttf" in msg
