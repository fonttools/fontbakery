import io
import os

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain)


def test_check_loca_maxp_num_glyphs():
    """Does the number of glyphs in the loca table match the maxp table?"""
    from fontbakery.profiles.loca import com_google_fonts_check_loca_maxp_num_glyphs as check

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont))

    ttFont["loca"].locations.pop()
    test_file = io.BytesIO()
    ttFont.save(test_file)
    ttFont = TTFont(test_file)
    assert_results_contain(check(ttFont),
                           FAIL, 'corrupt')

