from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("fontwerk/vendor_id")
def test_check_vendor_id(check):
    """Checking OS/2 achVendID."""

    ttFont = TTFont(TEST_FILE("abeezee/ABeeZee-Italic.ttf"))
    assert_results_contain(
        check(ttFont), FAIL, "bad-vendor-id", ", but should be 'WERK'."
    )

    ttFont["OS/2"].achVendID = "WERK"
    assert_PASS(check(ttFont), "'WERK' is correct.")


@check_id("fontwerk/style_linking")
def test_check_style_linking(check):
    """Checking style linking entries"""

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-BoldItalic.ttf")
    assert_results_contain(check(font), FAIL, "style-linking-issue")

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-Bold.ttf")
    assert_results_contain(check(font), FAIL, "style-linking-issue")

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-MediumItalic.ttf")
    assert_PASS(check(font), "Style linking looks good.")


@check_id("fontwerk/names_match_default_fvar")
def test_check_names_match_default_fvar(check):
    """Checking if names match default fvar."""

    from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID

    PID = PlatformID.WINDOWS
    EID = WindowsEncodingID.UNICODE_BMP
    LID = WindowsLanguageID.ENGLISH_USA

    font = TEST_FILE("varfont/Oswald-VF.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont), "Name matches fvar default name")

    ttFont["name"].setName("Not a proper family name", 1, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 2, PID, EID, LID)
    assert_results_contain(
        check(ttFont), FAIL, "bad-name", "does not match fvar default name"
    )

    ttFont["name"].setName("Not a proper family name", 16, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 17, PID, EID, LID)
    assert_results_contain(
        check(ttFont), FAIL, "bad-name", "does not match fvar default name"
    )

    ttFont["name"].setName("Not a proper family name", 21, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 22, PID, EID, LID)
    assert_results_contain(
        check(ttFont), FAIL, "bad-name", "does not match fvar default name"
    )
