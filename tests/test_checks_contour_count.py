from fontTools.ttLib import TTFont
import pytest

from conftest import check_id
from fontbakery.status import FAIL, WARN, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@pytest.fixture
def montserrat_ttFonts():
    paths = [
        TEST_FILE("montserrat/Montserrat-Black.ttf"),
        TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Bold.ttf"),
        TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Italic.ttf"),
        TEST_FILE("montserrat/Montserrat-Light.ttf"),
        TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Medium.ttf"),
        TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Regular.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Thin.ttf"),
        TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
    ]
    return [TTFont(path) for path in paths]


@check_id("contour_count")
def test_check_contour_count(check, montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    from fontTools import subset

    ttFont = TTFont(TEST_FILE("rokkitt/Rokkitt-Regular.otf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_ttf" in msg

    ttFont = TTFont(TEST_FILE("mutatorsans-vf/MutatorSans-VF.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg

    ttFont = montserrat_ttFonts[0]

    # Lets swap the glyf 'a' (2 contours) with glyf 'c' (1 contour)
    ttFont["glyf"]["a"] = ttFont["glyf"]["c"]
    msg = assert_results_contain(check(ttFont), WARN, "contour-count")
    assert "Glyph name: a\tContours detected: 1\tExpected: 2" in msg

    # Lets swap the glyf 'a' (2 contours) with space (0 contour) to get a FAIL
    ttFont["glyf"]["a"] = ttFont["glyf"]["space"]
    msg = assert_results_contain(check(ttFont), FAIL, "no-contour")
    assert "Glyph name: a\tExpected: 2" in msg

    # Subset the font to just the 'c' glyph to get a PASS
    subsetter = subset.Subsetter()
    subsetter.populate(text="c")
    subsetter.subset(ttFont)
    assert_PASS(check(ttFont))

    # Now delete the 'cmap' table to trigger a FAIL
    del ttFont["cmap"]
    msg = assert_results_contain(check(ttFont), FAIL, "lacks-cmap")
    assert msg == "This font lacks cmap data."
