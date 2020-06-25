import os

from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_results_contain)

from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL)
from fontTools.ttLib import TTFont

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_whitespace_widths():
  """ Whitespace glyphs have coherent widths? """
  from fontbakery.profiles.hmtx import com_google_fonts_check_whitespace_widths as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  assert_PASS(check(test_font))

  test_font["hmtx"].metrics["space"] = (0, 1)
  assert_results_contain(check(test_font),
                         FAIL, 'different-widths')

