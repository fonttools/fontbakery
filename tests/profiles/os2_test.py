import io
import os

import pytest

from fontbakery.utils import TEST_FILE, portable_path
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

import fontTools.ttLib
from fontTools.ttLib import TTFont
import fontTools.subset

mada_fonts = [
  TEST_FILE("mada/Mada-Black.ttf"),
  TEST_FILE("mada/Mada-ExtraLight.ttf"),
  TEST_FILE("mada/Mada-Medium.ttf"),
  TEST_FILE("mada/Mada-SemiBold.ttf"),
  TEST_FILE("mada/Mada-Bold.ttf"),
  TEST_FILE("mada/Mada-Light.ttf"),
  TEST_FILE("mada/Mada-Regular.ttf")
]

@pytest.fixture
def mada_ttFonts():
  return [TTFont(path) for path in mada_fonts]

cabin_fonts = [
  TEST_FILE("cabin/Cabin-BoldItalic.ttf"),
  TEST_FILE("cabin/Cabin-Bold.ttf"),
  TEST_FILE("cabin/Cabin-Italic.ttf"),
  TEST_FILE("cabin/Cabin-MediumItalic.ttf"),
  TEST_FILE("cabin/Cabin-Medium.ttf"),
  TEST_FILE("cabin/Cabin-Regular.ttf"),
  TEST_FILE("cabin/Cabin-SemiBoldItalic.ttf"),
  TEST_FILE("cabin/Cabin-SemiBold.ttf")
]


def test_check_panose_proportion(mada_ttFonts):
  """ Fonts have consistent PANOSE proportion ? """
  from fontbakery.profiles.os2 import com_google_fonts_check_panose_proportion as check

  print('Test PASS with good family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bProportion
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bProportion = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == FAIL


def test_check_panose_familytype(mada_ttFonts):
  """ Fonts have consistent PANOSE family type ? """
  from fontbakery.profiles.os2 import com_google_fonts_check_panose_familytype as check

  print('Test PASS with good family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bFamilyType
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bFamilyType = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check(mada_ttFonts))[-1]
  assert status == FAIL


def test_check_xavgcharwidth():
  """ Check if OS/2 xAvgCharWidth is correct. """
  from fontbakery.profiles.os2 import com_google_fonts_check_xavgcharwidth as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  status, message = list(check(test_font))[-1]
  assert status == PASS

  test_font['OS/2'].xAvgCharWidth = 556
  status, message = list(check(test_font))[-1]
  assert status == INFO

  test_font['OS/2'].xAvgCharWidth = 500
  status, message = list(check(test_font))[-1]
  assert status == WARN

  test_font = TTFont()
  test_font['OS/2'] = fontTools.ttLib.newTable('OS/2')
  test_font['OS/2'].version = 4
  test_font['OS/2'].xAvgCharWidth = 1000
  test_font['glyf'] = fontTools.ttLib.newTable('glyf')
  test_font['glyf'].glyphs = {}
  test_font['hmtx'] = fontTools.ttLib.newTable('hmtx')
  test_font['hmtx'].metrics = {}
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert message.code == "missing-glyphs"

  test_font = TTFont(test_font_path)
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'space'])
  subsetter.subset(test_font)
  test_font['OS/2'].xAvgCharWidth = 447
  test_font['OS/2'].version = 2
  temp_file = io.BytesIO()
  test_font.save(temp_file)
  test_font = TTFont(temp_file)
  status, message = list(check(test_font))[-1]
  assert status == PASS

  test_font['OS/2'].xAvgCharWidth = 450
  status, message = list(check(test_font))[-1]
  assert status == INFO

  test_font['OS/2'].xAvgCharWidth = 500
  status, message = list(check(test_font))[-1]
  assert status == WARN

  test_font = TTFont(temp_file)
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs=['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'space'])
  subsetter.subset(test_font)
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert message.code == "missing-glyphs"


def test_check_fsselection_matches_macstyle():
  """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""
  from fontbakery.profiles.os2 import \
    com_adobe_fonts_check_fsselection_matches_macstyle as check
  from fontbakery.constants import FsSelection

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

  # try a regular (not bold, not italic) font
  test_font = TTFont(test_font_path)
  status, message = list(check(test_font))[-1]
  assert status == PASS

  # now turn on bold in OS/2.fsSelection, but not in head.macStyle
  test_font['OS/2'].fsSelection |= FsSelection.BOLD
  status, message = list(check(test_font))[-1]
  assert 'bold' in message
  assert status == FAIL

  # now turn off bold in OS/2.fsSelection so we can focus on italic
  test_font['OS/2'].fsSelection &= ~FsSelection.BOLD

  # now turn on italic in OS/2.fsSelection, but not in head.macStyle
  test_font['OS/2'].fsSelection |= FsSelection.ITALIC
  status, message = list(check(test_font))[-1]
  assert 'italic' in message
  assert status == FAIL


def test_check_bold_italic_unique_for_nameid1():
  """Check that OS/2.fsSelection bold/italic settings are unique within each
  Compatible Family group (i.e. group of up to 4 with same NameID1)"""
  from fontbakery.profiles.os2 import \
    com_adobe_fonts_check_bold_italic_unique_for_nameid1 as check
  from fontbakery.constants import FsSelection

  base_path = portable_path("data/test/source-sans-pro/OTF")

  # these fonts have the same NameID1
  font_names = ['SourceSansPro-Regular.otf',
                'SourceSansPro-Bold.otf',
                'SourceSansPro-It.otf',
                'SourceSansPro-BoldIt.otf']

  font_paths = [os.path.join(base_path, n) for n in font_names]

  test_fonts = [TTFont(x) for x in font_paths]

  # the family should be correctly constructed
  status, message = list(check(test_fonts))[-1]
  assert status == PASS

  # now hack the italic font to also have the bold bit set
  test_fonts[2]['OS/2'].fsSelection |= FsSelection.BOLD

  # we should get a failure due to two fonts with both bold & italic set
  status, message = list(check(test_fonts))[-1]
  expected_message = "Family 'Source Sans Pro' has 2 fonts (should be no " \
                     "more than 1) with the same OS/2.fsSelection " \
                     "bold & italic settings: Bold=True, Italic=True"
  assert message == expected_message
  assert status == FAIL
