# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import io

import defcon
import ufo2ft
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

from fontTools.ttLib import TTFont

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

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


def test_check_013(mada_ttFonts):
  """ Fonts have equal unicode encodings ? """
  from fontbakery.specifications.cmap import com_google_fonts_check_013 as check
  from fontbakery.constants import (PLAT_ENC_ID__SYMBOL,
                                    PLAT_ENC_ID__UCS2)
  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(check(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce mismatching encodings into the first 2 font files:
  for i, encoding in enumerate([PLAT_ENC_ID__SYMBOL,
                                PLAT_ENC_ID__UCS2]):
    for table in bad_ttFonts[i]['cmap'].tables:
      if table.format == 4:
        table.platEncID = encoding

  print('Test FAIL with fonts that diverge on unicode encoding.')
  status, message = list(check(bad_ttFonts))[-1]
  assert status == FAIL


def NOT_IMPLEMENTED_test_check_076():
  """ Check glyphs have unique unicode codepoints. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_076 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "Some glyphs carry the same unicode value."
  # - PASS


def NOT_IMPLEMENTED_test_check_077():
  """ Check all glyphs have codepoints assigned. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_077 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "A glyph lacks a unicode codepoint assignment."
  # - PASS


def test_check_078():
  """ Check that glyph names do not exceed max length. """
  from fontbakery.specifications.cmap import com_google_fonts_check_078 as check

  # TTF
  test_font = defcon.Font("data/test/test.ufo")
  test_ttf = ufo2ft.compileTTF(test_font)
  status, _ = list(check(test_ttf))[-1]
  assert status == PASS

  test_glyph = defcon.Glyph()
  test_glyph.unicode = 0x1234
  test_glyph.name = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                     "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                     "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
  test_font.insertGlyph(test_glyph)

  test_ttf = ufo2ft.compileTTF(test_font, useProductionNames=False)
  status, _ = list(check(test_ttf))[-1]
  assert status == FAIL

  test_ttf = ufo2ft.compileTTF(test_font, useProductionNames=True)
  status, _ = list(check(test_ttf))[-1]
  assert status == PASS

  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_ttf["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_ttf.save(test_file)
  test_ttf = TTFont(test_file)
  status, message = list(check(test_ttf))[-1]
  assert status == PASS
  assert "format 3.0" in message

  del test_font, test_ttf, test_file  # Prevent copypasta errors.

  # CFF
  test_font = defcon.Font("data/test/test.ufo")
  test_otf = ufo2ft.compileOTF(test_font)
  status, _ = list(check(test_otf))[-1]
  assert status == PASS

  test_font.insertGlyph(test_glyph)

  test_otf = ufo2ft.compileOTF(test_font, useProductionNames=False)
  status, _ = list(check(test_otf))[-1]
  assert status == FAIL

  test_otf = ufo2ft.compileOTF(test_font, useProductionNames=True)
  status, _ = list(check(test_otf))[-1]
  assert status == PASS
