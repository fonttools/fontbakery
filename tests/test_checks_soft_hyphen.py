from fontTools.ttLib import TTFont
import pytest

from conftest import check_id
from fontbakery.status import WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.utils import remove_cmap_entry


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


@check_id("soft_hyphen")
def test_check_soft_hyphen(check, montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    for ttFont in montserrat_ttFonts:
        # Montserrat has a softhyphen...
        assert_results_contain(check(ttFont), WARN, "softhyphen")

        remove_cmap_entry(ttFont, 0x00AD)
        assert_PASS(check(ttFont))
