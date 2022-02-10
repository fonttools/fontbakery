from fontTools.ttLib import TTFont
from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.constants import (PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID)
from fontbakery.profiles import fontwerk as fontwerk_profile


def test_check_name_no_mac_entries():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/no_mac_entries')

    font = TEST_FILE('abeezee/ABeeZee-Italic.ttf')
    assert_results_contain(check(font),
                           FAIL, 'mac-names',
                           'with a font containing Mac names')

    font = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    assert_PASS(check(font),
                'with a font without Mac names')


def test_check_vendor_id():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/vendor_id')

    font = TEST_FILE('abeezee/ABeeZee-Italic.ttf')
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-vendor-id',
                           ", but should be 'WERK'.")

    ttFont['OS/2'].achVendID = 'WERK'
    assert_PASS(check(ttFont),
                "'WERK' is correct.")


def test_check_weight_class_fvar():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/weight_class_fvar')

    font = TEST_FILE('varfont/Oswald-VF.ttf')
    ttFont = TTFont(font)
    assert_PASS(check(ttFont),
                "matches fvar default value.")

    ttFont['OS/2'].usWeightClass = 333
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-weight-class',
                           "but should match fvar default value.")


def test_check_names_match_default_fvar():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/names_match_default_fvar')

    PID = PlatformID.WINDOWS
    EID = WindowsEncodingID.UNICODE_BMP
    LID = WindowsLanguageID.ENGLISH_USA

    font = TEST_FILE('varfont/Oswald-VF.ttf')
    ttFont = TTFont(font)
    assert_PASS(check(ttFont),
                "Name matches fvar default name")

    ttFont["name"].setName("Not a proper family name", 1, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 2, PID, EID, LID)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-name',
                           "does not match fvar default name")

    ttFont["name"].setName("Not a proper family name", 16, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 17, PID, EID, LID)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-name',
                           "does not match fvar default name")

    ttFont["name"].setName("Not a proper family name", 21, PID, EID, LID)
    ttFont["name"].setName("Not a proper subfamily name", 22, PID, EID, LID)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-name',
                           "does not match fvar default name")
