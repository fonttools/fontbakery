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


def test_check_inconsistencies_between_fvar_stat():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/inconsistencies_between_fvar_stat')

    ttFont = TTFont(TEST_FILE("bad_fonts/fvar_stat_differences/AxisLocationVAR.ttf"))
    ttFont['name'].removeNames(nameID=277)
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-name-id',
                           'fvar instance is missing in the name table')

    # add name with wrong order of name parts
    ttFont['name'].setName('Medium Text', 277, 3, 1, 0x409)
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-fvar-instance-axis-value',
                           'missing in STAT table')
