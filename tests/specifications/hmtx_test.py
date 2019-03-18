import os

from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL)
from fontTools.ttLib import TTFont

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_050():
  """ Whitespace glyphs have coherent widths? """
  from fontbakery.specifications.hmtx import com_google_fonts_check_050 as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  test_font["hmtx"].metrics["space"] = (0, 1)
  status, _ = list(check(test_font))[-1]
  assert status == FAIL
