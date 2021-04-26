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
