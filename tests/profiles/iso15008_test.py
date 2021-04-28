from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.checkrunner import FAIL
from fontbakery.profiles import iso15008

from fontTools.ttLib import TTFont


def test_check_iso15008_proportions():
    """Check if 0.65 => (H width / H height) => 0.80"""
    check = CheckTester(iso15008, "com.google.fonts/check/iso15008_proportions")

    # Cabin has a proportion of 0.7, so that's good.
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # Wonky Paths doesn't have an H
    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "glyph-not-present",
        "There was no 'H' glyph in the font",
    )

    # Covered By Your Grace is really tall (proportion 0.39)
    ttFont = TTFont(TEST_FILE("coveredbyyourgrace/CoveredByYourGrace.ttf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "invalid-proportion",
        "The proportion of H width to H height",
    )


def test_check_iso15008_stem_width():
    """Check if 0.10 <= (stem width / ascender) <= 0.82"""
    check = CheckTester(iso15008, "com.google.fonts/check/iso15008_stem_width")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-SemiBold.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # Wonky Paths doesn't have a l
    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "no-stem-width",
        "Could not determine",
    )

    # Cabin Regular is actually slightly too thin for displays
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "invalid-proportion",
        "The proportion of stem width to ascender",
    )


def test_check_iso15008_intercharacter_spacing():
    """Check if spacing between characters is adequate for display use"""
    check = CheckTester(
        iso15008, "com.google.fonts/check/iso15008_intercharacter_spacing"
    )

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-SemiBold.ttf"))
    # l stem width is 111, LSB at x-height is 59, RSB at x-Height is 83
    # 142 / 111 = 128%, so this font is too tight.
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-vertical-vertical-spacing",
        "The space between vertical strokes",
    )
    # v LSB is 5, lv kern is -6 (!) so lv distance is 83+5-6 = 82
    # 82 / 111 = 0.73%, so that fails too.
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-vertical-diagonal-spacing",
        "The space between vertical and diagonal strokes",
    )

    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-Black.ttf"))
    # vv touches
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-diagonal-diagonal-spacing",
        "Diagonal strokes (vv) were touching",
    )
