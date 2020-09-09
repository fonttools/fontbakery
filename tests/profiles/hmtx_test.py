from fontTools.ttLib import TTFont

from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain,
                                    CheckTester)
from fontbakery.profiles import opentype as opentype_profile


def test_check_whitespace_widths():
    """ Whitespace glyphs have coherent widths? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/whitespace_widths")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["space"] = (0, 1)
    assert_results_contain(check(ttFont),
                           FAIL, 'different-widths')

