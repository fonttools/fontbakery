import io
import os

from fontTools.ttLib import TTFont

from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_069():
  """ Is there any unused data at the end of the glyf table? """
  from fontbakery.specifications.glyf import com_google_fonts_check_069 as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  # Always start with a fresh copy, as fT works lazily. Accessing certain data
  # can prevent the test from working because we rely on uninitialized
  # behavior.
  test_font = TTFont(test_font_path)
  test_font["loca"].locations.pop()
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert message.code == "unreachable-data"

  test_font = TTFont(test_font_path)
  test_font["loca"].locations.append(50000)
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert message.code == "missing-data"


def test_check_075():
  """ Check for points out of bounds. """
  from fontbakery.specifications.glyf import com_google_fonts_check_075 as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == WARN

  test_font2 = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
  status, _ = list(check(test_font2))[-1]
  assert status == PASS
