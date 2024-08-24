import pytest
from fontTools.ttLib import TTFont

from fontbakery.checks.googlefonts.glyphset import is_icon_font
from fontbakery.codetesting import TEST_FILE, MockContext, MockFont
from fontbakery.fonts_profile import setup_context
from fontbakery.testable import Font


@pytest.mark.parametrize(
    "font, expected_stylename",
    [
        (TEST_FILE("merriweather/Merriweather.ttf"), None),
        (TEST_FILE("merriweather/Merriweather-Regular.ttf"), "Regular"),
        (TEST_FILE("mada/Mada-Black.ttf"), "Black"),
        (TEST_FILE("mada/Mada-ExtraLight.ttf"), "ExtraLight"),
        (TEST_FILE("mada/Mada-Medium.ttf"), "Medium"),
        (TEST_FILE("mada/Mada-SemiBold.ttf"), "SemiBold"),
        (TEST_FILE("mada/Mada-Bold.ttf"), "Bold"),
        (TEST_FILE("mada/Mada-Light.ttf"), "Light"),
        (TEST_FILE("mada/Mada-Regular.ttf"), "Regular"),
        (TEST_FILE("montserrat/Montserrat-Thin.ttf"), "Thin"),
        (TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"), "ThinItalic"),
        (TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"), "ExtraLightItalic"),
        (TEST_FILE("montserrat/Montserrat-LightItalic.ttf"), "LightItalic"),
        (TEST_FILE("montserrat/Montserrat-Italic.ttf"), "Italic"),
        (TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"), "MediumItalic"),
        (TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"), "SemiBoldItalic"),
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"), "BoldItalic"),
        (TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"), "ExtraBoldItalic"),
        (TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"), "BlackItalic"),
        (TEST_FILE("cabinvfbeta/CabinVFBeta-Italic[wght].ttf"), None),
        (TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"), None),
        (TEST_FILE("cabinvfbeta/Cabin-Italic.ttf"), None),
        (TEST_FILE("cabinvfbeta/Cabin-Roman.ttf"), None),
        (TEST_FILE("cabinvfbeta/Cabin-Italic-VF.ttf"), "Italic-VF"),
        (TEST_FILE("cabinvfbeta/Cabin-Roman-VF.ttf"), "Roman-VF"),
        (TEST_FILE("cabinvfbeta/Cabin-VF.ttf"), "VF"),
        (TEST_FILE("cabinvfbeta/CabinVFBeta[wdth,wght].ttf"), None),
        (TEST_FILE("cabinvfbeta/CabinVFBeta[wght,wdth].ttf"), None),
        (TEST_FILE("cabin/Cabin-BoldItalic.ttf"), "BoldItalic"),
        (TEST_FILE("cabin/Cabin-Bold.ttf"), "Bold"),
        (TEST_FILE("cabin/Cabin-Italic.ttf"), "Italic"),
        (TEST_FILE("cabin/Cabin-MediumItalic.ttf"), "MediumItalic"),
        (TEST_FILE("cabin/Cabin-Medium.ttf"), "Medium"),
        (TEST_FILE("cabin/Cabin-Regular.ttf"), "Regular"),
        (TEST_FILE("cabin/Cabin-SemiBoldItalic.ttf"), "SemiBoldItalic"),
        (TEST_FILE("cabin/Cabin-SemiBold.ttf"), "SemiBold"),
        (TEST_FILE("cabincondensed/CabinCondensed-Regular.ttf"), "Regular"),
        (TEST_FILE("cabincondensed/CabinCondensed-Medium.ttf"), "Medium"),
        (TEST_FILE("cabincondensed/CabinCondensed-Bold.ttf"), "Bold"),
        (TEST_FILE("cabincondensed/CabinCondensed-SemiBold.ttf"), "SemiBold"),
        (TEST_FILE("varfont/Oswald-VF.ttf"), "VF"),
        (TEST_FILE("cjk/SourceHanSans-Regular.otf"), "Regular"),
    ],
)
def test_canonical_stylename_condition(font, expected_stylename):
    assert Font(font).canonical_stylename == expected_stylename


def test_stylenames_are_canonical_condition():
    context = setup_context(
        [
            TEST_FILE("mada/Mada-Light.ttf"),
            TEST_FILE("mada/Mada-Regular.ttf"),
        ]
    )
    assert context.stylenames_are_canonical is True

    context = MockContext(
        testables=[
            MockFont(file=TEST_FILE("merriweather/Merriweather-Regular.ttf")),
            MockFont(file=TEST_FILE("merriweather/Merriweather.ttf")),
        ]
    )
    assert context.stylenames_are_canonical is False


def test_is_icon_font_condition():
    font = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert is_icon_font(font, {}) is False
    assert is_icon_font(font, {"is_icon_font": True}) is True

    font = TTFont(TEST_FILE("notoemoji/NotoEmoji-Regular.ttf"))
    assert is_icon_font(font, {}) is True
