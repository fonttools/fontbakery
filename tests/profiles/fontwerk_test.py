import os

from fontTools.ttLib import TTFont
from fontbakery.checkrunner import (PASS, WARN, FAIL)
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
    assert_results_contain(check(font),
                           WARN, 'Please remove mac name table ID')

    # try fonts without Mac names
    font = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    assert_PASS(check(font))


