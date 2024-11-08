from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/layout_valid_feature_tags")
def test_check_layout_valid_feature_tags(check):
    """Does the font have any invalid feature tags?"""

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


@check_id("opentype/layout_valid_script_tags")
def test_check_layout_valid_script_tags(check):
    """Does the font have any invalid script tags?"""

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_results_contain(check(font), FAIL, "bad-script-tags")


@check_id("opentype/layout_valid_language_tags")
def test_check_layout_valid_language_tags(check):
    """Does the font have any invalid language tags?"""

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_results_contain(check(font), FAIL, "bad-language-tags")
