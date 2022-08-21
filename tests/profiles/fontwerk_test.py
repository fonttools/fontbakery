from fontTools.ttLib import TTFont
from fontbakery.checkrunner import FAIL, SKIP
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

    ttFont = TTFont(TEST_FILE('abeezee/ABeeZee-Italic.ttf'))
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-vendor-id',
                           ", but should be 'WERK'.")

    ttFont['OS/2'].achVendID = 'WERK'
    assert_PASS(check(ttFont),
                "'WERK' is correct.")


def test_check_weight_class_fvar():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/weight_class_fvar')

    ttFont = TTFont(TEST_FILE('varfont/Oswald-VF.ttf'))
    assert_PASS(check(ttFont),
                "matches fvar default value.")

    ttFont['OS/2'].usWeightClass = 333
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-weight-class',
                           "but should match fvar default value.")

    # Test with a variable font that doesn't have a 'wght' (Weight) axis.
    # The check should yield SKIP.
    ttFont = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: has_wght_axis"


def test_check_inconsistencies_between_fvar_stat():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/inconsistencies_between_fvar_stat')

    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    msg = assert_PASS(check(ttFont), "with a good varfont...")
    assert msg == "STAT and fvar axis records are consistent."

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


def test_check_style_linking():
    check = CheckTester(fontwerk_profile,
                        'com.fontwerk/check/style_linking')

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-BoldItalic.ttf")
    assert_results_contain(check(font),
                           FAIL, 'style-linking-issue')

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-Bold.ttf")
    assert_results_contain(check(font),
                           FAIL, 'style-linking-issue')

    font = TEST_FILE("bad_fonts/style_linking_issues/NotoSans-MediumItalic.ttf")
    assert_PASS(check(font),
                "Style linking looks good.")
