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


def test_check_008(mada_ttFonts):
  """ Fonts have consistent underline thickness ? """
  from fontbakery.specifications.post import com_google_fonts_check_008 as check

  # We start with our reference Mada font family,
  # which we know has the same value of post.underlineThickness
  # accross all of its font files, based on our inspection
  # of the file contents using TTX.
  #
  # So the check should PASS in this case:
  print('Test PASS with a good family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == PASS

  # Then we introduce the issue by setting a
  # different underlineThickness value in just
  # one of the font files:
  value = mada_ttFonts[0]['post'].underlineThickness
  incorrect_value = value + 1
  mada_ttFonts[0]['post'].underlineThickness = incorrect_value

  # And now re-running the check on the modified
  # family should result in a FAIL:
  print('Test FAIL with an inconsistent family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == FAIL


def test_check_015():
  """ Font has post table version 2 ? """
  from fontbakery.specifications.post import com_google_fonts_check_015 as check

  print('Test PASS with good font.')
  # our reference Mada family is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check(ttFont, 'glyf' in ttFont))[-1]
  assert status == PASS

  # modify the post table version
  ttFont['post'].formatType = 3

  print('Test FAIL with fonts that diverge on the fontRevision field value.')
  status, message = list(check(ttFont, 'glyf' in ttFont))[-1]
  assert status == FAIL
