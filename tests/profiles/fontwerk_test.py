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

    # try fonts with Mac names
    font = TEST_FILE('abeezee/ABeeZee-Italic.ttf')
    message = assert_results_contain(check(font),
                           FAIL, 'Mac Names')

    # try fonts without Mac names
    font = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    assert_PASS(check(font))


