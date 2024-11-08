import pytest
from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL


@pytest.mark.parametrize(
    "font_path",
    [
        "montserrat/Montserrat-Regular.ttf",
        "ubuntusans/UbuntuSans[wdth,wght].ttf",
    ],
)
@check_id("tnum_glyphs_equal_widths")
def test_tnum_glyphs_equal_widths(check, font_path):
    # Pass condition
    font = TTFont(TEST_FILE(font_path))
    assert_PASS(check(font))

    # TODO: This should also have a FAIL test-case!


@check_id("tabular_kerning")
def test_check_tabular_kerning(check):
    """Check tabular widths don't have kerning."""

    # Has no numerals at all
    font = TEST_FILE("BadGrades/BadGrades-VF.ttf")
    assert_SKIP(check(font))

    # Has no tabular numerals
    font = TEST_FILE("akshar/Akshar[wght].ttf")
    assert_SKIP(check(font))

    font = TEST_FILE("montserrat/Montserrat-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("sharetech/ShareTech-Regular.ttf")
    assert_results_contain(check(font), FAIL, "has-tabular-kerning")

    # Ubuntu Sans has digraphs (like DZ) that get decomposed in ccmp
    # and then have kerning between the individual D and Z, which
    # used to throw off the check
    font = TEST_FILE("ubuntusans/UbuntuSans[wdth,wght].ttf")
    assert_PASS(check(font))
