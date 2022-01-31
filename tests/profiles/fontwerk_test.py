from fontbakery.message import Message
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
    assert_results_contain(check(font),
                           FAIL, 'bad-vendor-id',
                           ", but should be 'WERK'.")

    font['OS/2'].achVendID = 'WERK'
    assert_PASS(check(font),
                "'WERK' is correct.")
