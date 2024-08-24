from fontbakery.codetesting import (
    TEST_FILE,
    CheckTester,
    assert_PASS,
    assert_results_contain,
)
from fontbakery.status import FAIL


def test_check_family_control_chars():
    """Are any unacceptable control characters present in font files?"""
    check = CheckTester("family/control_chars")

    good_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCGood-Regular.ttf"
    )
    onebad_cc_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCOneBad-Regular.ttf"
    )
    multibad_cc_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCMultiBad-Regular.ttf"
    )

    # No unacceptable control characters should pass with one file
    fonts = [good_font]
    assert_PASS(check(fonts), "with one good font...")

    # No unacceptable control characters should pass with multiple good files
    fonts = [good_font, good_font]
    assert_PASS(check(fonts), "with multiple good fonts...")

    # Unacceptable control chars should fail with one file x one bad char in font
    fonts = [onebad_cc_font]
    assert_results_contain(
        check(fonts), FAIL, "unacceptable", "with one bad font that has one bad char..."
    )

    # Unacceptable control chars should fail with one file x multiple bad char in font
    fonts = [multibad_cc_font]
    assert_results_contain(
        check(fonts),
        FAIL,
        "unacceptable",
        "with one bad font that has multiple bad char...",
    )

    # Unacceptable control chars should fail with multiple files x multiple bad chars
    # in fonts
    fonts = [onebad_cc_font, multibad_cc_font]
    assert_results_contain(
        check(fonts),
        FAIL,
        "unacceptable",
        "with multiple bad fonts that have multiple bad chars...",
    )
