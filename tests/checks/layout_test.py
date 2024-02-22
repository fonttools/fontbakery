from fontTools.ttLib import TTFont
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_layout_valid_feature_tags():
    """Does the font have any invalid feature tags?"""
    check = CheckTester("com.google.fonts/check/layout_valid_feature_tags")

    # test font with valid, registered feature tags.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    # test font with valid, private use feature tags.
    # change font's feature tag to have non-registered, all uppercase private tags
    font_obj = TTFont(font)
    font_obj["GSUB"].table.FeatureList.FeatureRecord[0].FeatureTag = "TEST"
    assert_PASS(check(font_obj))

    # test font with invalid feature tags: not registered, and not all uppercase.
    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_results_contain(check(font), FAIL, "bad-feature-tags")


def test_check_layout_valid_script_tags():
    """Does the font have any invalid script tags?"""
    check = CheckTester("com.google.fonts/check/layout_valid_script_tags")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_results_contain(check(font), FAIL, "bad-script-tags")


def test_check_layout_valid_language_tags():
    """Does the font have any invalid language tags?"""
    check = CheckTester("com.google.fonts/check/layout_valid_language_tags")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_results_contain(check(font), FAIL, "bad-language-tags")
