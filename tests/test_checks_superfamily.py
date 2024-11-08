import os

from fontTools.ttLib import TTFont
import pytest

from conftest import check_id
from fontbakery.status import INFO, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    MockFont,
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


cabin_fonts = [
    TEST_FILE("cabin/Cabin-BoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-Bold.ttf"),
    TEST_FILE("cabin/Cabin-Italic.ttf"),
    TEST_FILE("cabin/Cabin-MediumItalic.ttf"),
    TEST_FILE("cabin/Cabin-Medium.ttf"),
    TEST_FILE("cabin/Cabin-Regular.ttf"),
    TEST_FILE("cabin/Cabin-SemiBoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-SemiBold.ttf"),
]


@pytest.fixture
def cabin_ttFonts():
    return [TTFont(path) for path in cabin_fonts]


@pytest.fixture
def cabin_condensed_ttFonts():
    paths = [
        TEST_FILE("cabincondensed/CabinCondensed-Regular.ttf"),
        TEST_FILE("cabincondensed/CabinCondensed-Medium.ttf"),
        TEST_FILE("cabincondensed/CabinCondensed-Bold.ttf"),
        TEST_FILE("cabincondensed/CabinCondensed-SemiBold.ttf"),
    ]
    return [TTFont(path) for path in paths]


@check_id("superfamily/list")
def test_check_superfamily_list(check):
    msg = assert_results_contain(
        check(MockFont(superfamily=[cabin_fonts])), INFO, "family-path"
    )
    assert msg == os.path.normpath("data/test/cabin")


@check_id("superfamily/vertical_metrics")
def test_check_superfamily_vertical_metrics(
    check, montserrat_ttFonts, cabin_ttFonts, cabin_condensed_ttFonts
):
    msg = assert_SKIP(check(MockFont(superfamily_ttFonts=[cabin_ttFonts[0]])))
    assert msg == "Sibling families were not detected."

    assert_PASS(
        check(MockFont(superfamily_ttFonts=[cabin_ttFonts, cabin_condensed_ttFonts])),
        "with multiple good families...",
    )

    assert_results_contain(
        check(MockFont(superfamily_ttFonts=[cabin_ttFonts, montserrat_ttFonts])),
        WARN,
        "superfamily-vertical-metrics",
        "with families that diverge on vertical metric values...",
    )
