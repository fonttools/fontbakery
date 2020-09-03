import os

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL)
from fontbakery.codetesting import (TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_whitespace_widths():
    """ Whitespace glyphs have coherent widths? """
    from fontbakery.profiles.hmtx import com_google_fonts_check_whitespace_widths as check

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["space"] = (0, 1)
    assert_results_contain(check(ttFont),
                           FAIL, 'different-widths')

