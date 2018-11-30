import io
import os

import pytest
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

from fontTools.ttLib import TTFont

mada_fonts = [
  "data/test/mada/Mada-Black.ttf",
  "data/test/mada/Mada-ExtraLight.ttf",
  "data/test/mada/Mada-Medium.ttf",
  "data/test/mada/Mada-SemiBold.ttf",
  "data/test/mada/Mada-Bold.ttf",
  "data/test/mada/Mada-Light.ttf",
  "data/test/mada/Mada-Regular.ttf",
]

@pytest.fixture
def mada_ttFonts():
  return [TTFont(path) for path in mada_fonts]


def test_check_014(mada_ttFonts):
  """ Make sure all font files have the same version value. """
  from fontbakery.specifications.head import com_google_fonts_check_014 as check

  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(check(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce a mismatching version value into the second font file:
  version = bad_ttFonts[0]['head'].fontRevision
  bad_ttFonts[1]['head'].fontRevision = version + 1

  print('Test WARN with fonts that diverge on the fontRevision field value.')
  status, message = list(check(bad_ttFonts))[-1]
  assert status == WARN


def test_check_043():
  """ Checking unitsPerEm value is reasonable. """
  from fontbakery.specifications.head import com_google_fonts_check_043 as check

  # In this test we'll forge several known-good and known-bad values.
  # We'll use Mada Regular to start with:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  for good_value in [16, 32, 64, 128, 256, 512, 1000,
                     1024, 2000, 2048, 4096, 8192, 16384]:
    print(f"Test PASS with a good value of unitsPerEm = {good_value} ...")
    ttFont['head'].unitsPerEm = good_value
    status, _ = list(check(ttFont))[-1]
    assert status == PASS

  for warn_value in [20, 50, 100, 500, 4000]:
    print(f"Test WARN with a value of unitsPerEm = {warn_value} ...")
    ttFont['head'].unitsPerEm = warn_value
    status, _ = list(check(ttFont))[-1]
    assert status == WARN

  # These are arbitrarily chosen bad values:
  for bad_value in [0, 1, 2, 4, 8, 10, 15, 16385, 32768]:
    print(f"Test FAIL with a bad value of unitsPerEm = {bad_value} ...")
    ttFont['head'].unitsPerEm = bad_value
    status, message = list(check(ttFont))[-1]
    assert status == FAIL


def test_parse_version_string():
  """ Checking font version fields. """
  from fontbakery.specifications.head import parse_version_string

  version_tests_good = {"Version 01.234": ("1", "234"),
    "1.234": ("1", "234"),
    "01.234; afjidfkdf 5.678": ("1", "234"),
    "1.3": ("1", "300"),
    "1.003": ("1", "003"),
    "1.0": ("1", "000"),
    "1.000": ("1", "000"),
    "3.000;NeWT;Nunito-Regular": ("3", "000"),
    "Something Regular Italic Version 1.234": ("1", "234")}

  version_tests_bad = ["Version 0x.234", "x", "212122;asdf 01.234"]

  for string, version in version_tests_good.items():
    assert parse_version_string(string) == version

  for string in version_tests_bad:
    with pytest.raises(ValueError):
      parse_version_string(string)


def test_check_044():
  """ Checking font version fields. """
  from fontbakery.specifications.head import com_google_fonts_check_044 as check

  test_font_path = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  # 1.00099 is only a mis-interpretation of a valid float value (1.001)
  # See more detailed discussion at:
  # https://github.com/googlefonts/fontbakery/issues/2006
  test_font = TTFont(test_font_path)
  test_font["head"].fontRevision = 1.00099
  test_font["name"].setName("Version 1.001", 5, 1, 0, 0x0)
  test_font["name"].setName("Version 1.001", 5, 3, 1, 0x409)
  status, message = list(check(test_font))[-1]
  assert status == PASS

  test_font = TTFont(test_font_path)
  test_font["head"].fontRevision = 3.1
  test_font["name"].setName("Version 3.000", 5, 1, 0, 0x0)
  test_font["name"].setName("Version 3.000", 5, 3, 1, 0x409)
  status, message = list(check(test_font))[-1]
  assert status == FAIL and message.code == "mismatch"

  test_font = TTFont(test_font_path)
  test_font["head"].fontRevision = 3.0
  test_font["name"].setName("Version 1.000", 5, 3, 1, 0x409)
  status, message = list(check(test_font))[-1]
  assert status == FAIL and message.code == "mismatch"

  test_font = TTFont(test_font_path)
  test_font["name"].setName("Version x.000", 5, 3, 1, 0x409)
  status, message = list(check(test_font))[-1]
  assert status == FAIL and message.code == "parse"

  test_font = TTFont(test_font_path)
  v1 = test_font["name"].getName(5, 3, 1)
  v2 = test_font["name"].getName(5, 1, 0)
  test_font["name"].names.remove(v1)
  test_font["name"].names.remove(v2)
  status, message = list(check(test_font))[-1]
  assert status == FAIL and message.code == "missing"
