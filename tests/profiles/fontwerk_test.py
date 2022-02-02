from fontTools.ttLib import TTFont
from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
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
