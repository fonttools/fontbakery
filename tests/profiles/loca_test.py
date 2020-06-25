import io
import os

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import PASS, FAIL
from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_results_contain)


def test_check_loca_maxp_num_glyphs():
  """Does the number of glyphs in the loca table match the maxp table?"""
  from fontbakery.profiles.loca import com_google_fonts_check_loca_maxp_num_glyphs as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  assert_PASS(check(test_font))

  test_font = TTFont(test_font_path)
  test_font["loca"].locations.pop()
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  assert_results_contain(check(test_font),
                         FAIL, 'corrupt')

