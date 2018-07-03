# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

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

import fontTools.ttLib
from fontTools.ttLib import TTFont
import fontTools.subset

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

cabin_fonts = [
  "data/test/cabin/Cabin-BoldItalic.ttf",
  "data/test/cabin/Cabin-Bold.ttf",
  "data/test/cabin/Cabin-Italic.ttf",
  "data/test/cabin/Cabin-MediumItalic.ttf",
  "data/test/cabin/Cabin-Medium.ttf",
  "data/test/cabin/Cabin-Regular.ttf",
  "data/test/cabin/Cabin-SemiBoldItalic.ttf",
  "data/test/cabin/Cabin-SemiBold.ttf"
]


def test_check_009(mada_ttFonts):
  """ Fonts have consistent PANOSE proportion ? """
  from fontbakery.specifications.os2 import com_google_fonts_check_009 as check

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


def test_check_010(mada_ttFonts):
  """ Fonts have consistent PANOSE family type ? """
  from fontbakery.specifications.os2 import com_google_fonts_check_010 as check

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


def test_check_034():
  """ Check if OS/2 xAvgCharWidth is correct. """
  from fontbakery.specifications.os2 import com_google_fonts_check_034 as check

  test_font_path = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  status, message = list(check(test_font))[-1]
  assert status == PASS

  test_font['OS/2'].xAvgCharWidth = 556
  status, message = list(check(test_font))[-1]
  assert status == WARN

  test_font['OS/2'].xAvgCharWidth = 500
  status, message = list(check(test_font))[-1]
  assert status == FAIL

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
  assert status == WARN

  test_font['OS/2'].xAvgCharWidth = 500
  status, message = list(check(test_font))[-1]
  assert status == FAIL

  test_font = TTFont(temp_file)
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs=['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'space'])
  subsetter.subset(test_font)
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert message.code == "missing-glyphs"
