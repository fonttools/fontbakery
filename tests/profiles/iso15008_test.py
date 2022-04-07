from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles import iso15008 as iso15008_profile


def test_check_iso15008_proportions():
    """Check if 0.65 => (H width / H height) => 0.80"""
    check = CheckTester(iso15008_profile, "com.google.fonts/check/iso15008_proportions")

    # Cabin has a proportion of 0.7, so that's good.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    # Wonky Paths doesn't have an H
    font = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    assert_results_contain(
        check(font),
        FAIL,
        "glyph-not-present",
        "with a font that does not have an 'H' glyph...",
    )

    # Covered By Your Grace is really tall (proportion 0.39)
    font = TEST_FILE("coveredbyyourgrace/CoveredByYourGrace.ttf")
    assert_results_contain(
        check(font),
        FAIL,
        "invalid-proportion",
        "with a very tall font (proportion of 'H' width to 'H' height)...",
    )


def test_check_iso15008_stem_width():
    """Check if 0.10 <= (stem width / ascender) <= 0.82"""
    check = CheckTester(iso15008_profile, "com.google.fonts/check/iso15008_stem_width")

    font = TEST_FILE("cabin/Cabin-SemiBold.ttf")
    assert_PASS(check(font), "with a good font...")

    # Wonky Paths doesn't have an 'l'
    font = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    assert_results_contain(
        check(font), FAIL, "no-stem-width", "with a font lacking an 'l' glyph..."
    )

    # Cabin Regular is actually slightly too thin for displays
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font),
        FAIL,
        "invalid-proportion",
        "with a too thin font (proportion of stem width to ascender)...",
    )


def test_check_iso15008_intercharacter_spacing():
    """Check if spacing between characters is adequate for display use"""
    check = CheckTester(
        iso15008_profile, "com.google.fonts/check/iso15008_intercharacter_spacing"
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("cabin/Cabin-SemiBold.ttf")
    # l stem width is 111, LSB at x-height is 59, RSB at x-Height is 83
    # 142 / 111 = 128%, so this font is too tight.
    assert_results_contain(
        check(font),
        FAIL,
        "bad-vertical-vertical-spacing",
        "with a too tight font (space between vertical strokes)...",
    )

    # v LSB is 5, lv kern is -6 (!) so lv distance is 83+5-6 = 82
    # 82 / 111 = 0.73%, so that fails too.
    assert_results_contain(
        check(font),
        FAIL,
        "bad-vertical-diagonal-spacing",
        "with bad spacing between vertical and diagonal strokes...",
    )

    font = TEST_FILE("montserrat/Montserrat-Black.ttf")
    # vv touches
    assert_results_contain(
        check(font),
        FAIL,
        "bad-diagonal-diagonal-spacing",
        "with diagonal strokes (vv) that are touching...",
    )


def test_check_iso15008_interword_spacing():
    """Check if spacing between words is adequate for display use"""
    check = CheckTester(
        iso15008_profile, "com.google.fonts/check/iso15008_interword_spacing"
    )

    font = TEST_FILE("cabin/CabinCondensed-Bold.ttf")
    # lm space is 112; m+space+l space is 286; 286/112 = 255%
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    # lm space is 147; m+space+l space is 341; 341/147 = 232%
    assert_results_contain(
        check(font), FAIL, "bad-interword-spacing", "with bad interword space..."
    )


def test_check_iso15008_interline_spacing():
    """Check if spacing between lines is adequate for display use"""
    check = CheckTester(
        iso15008_profile, "com.google.fonts/check/iso15008_interline_spacing"
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("source-sans-pro/TTF/SourceSansPro-Bold.ttf")
    # 39 units at bottom of g + 49 units at top of h + no typolinegap = 88
    # stem width = 147
    assert_results_contain(
        check(font), FAIL, "bad-interline-spacing", "with bad interline space..."
    )
