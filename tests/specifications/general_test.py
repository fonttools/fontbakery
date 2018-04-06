# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

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

def test_check_002():
  """ Fonts are all in the same directory. """
  from fontbakery.specifications.general import com_google_fonts_check_002 as check
  same_dir = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  multiple_dirs = [
    "data/test/mada/Mada-Regular.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  print('Test PASS with same dir: {}'.format(same_dir))
  status, message = list(check(same_dir))[-1]
  assert status == PASS

  print('Test FAIL with multiple dirs: {}'.format(multiple_dirs))
  status, message = list(check(multiple_dirs))[-1]
  assert status == FAIL

# TODO: test_check_035
# TODO: test_check_036

def test_check_037():
  """ MS Font Validator checks """
  from fontbakery.specifications.general import com_google_fonts_check_037 as check

  font = "data/test/mada/Mada-Regular.ttf"
  RASTER_EXCEPTION_MESSAGE = ("MS-FonVal: An exception occurred"
                              " during rasterization testing")
  # we want to run all FValidator checks only once,
  # so here we cache all results:
  fval_results = list(check(font))

  # Then we make sure that the freetype backend we're using
  # supports the hinting instructions validation checks,
  # which are refered to as "rasterization testing":
  # (See also: https://github.com/googlefonts/fontbakery/issues/1524)
  for status, message in fval_results:
    assert RASTER_EXCEPTION_MESSAGE not in message

  # and finaly, we make sure that there wasn't an ERROR
  # which would mean FontValidator is not properly installed:
  assert status != ERROR

# TODO: test_check_038
# TODO: test_check_039
# TODO: test_check_046

def test_check_047():
  """ Font contains glyphs for whitespace characters ? """
  from fontbakery.specifications.general import com_google_fonts_check_047 as check
  from fontbakery.specifications.shared_conditions import missing_whitespace_chars

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  missing = missing_whitespace_chars(ttFont)

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont, missing))[-1]
  assert status == PASS

  # Then we remove the nbsp char (0x00A0) so that we get a FAIL:
  print ("Test FAIL with a font lacking a nbsp (0x00A0)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(check(ttFont, missing))[-1]
  assert status == FAIL

  # restore original Mada Regular font:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # And finally remove the space character (0x0020) to get another FAIL:
  print ("Test FAIL with a font lacking a space (0x0020)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(check(ttFont, missing))[-1]
  assert status == FAIL


def test_check_048():
  """ Font has **proper** whitespace glyph names ? """
  from fontbakery.specifications.general import com_google_fonts_check_048 as check

  def deleteGlyphEncodings(font, cp):
    """ This routine is used on to introduce errors
        in a given font by removing specific entries
        in the cmap tables.
    """
    for subtable in font['cmap'].tables:
      if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
          if codepoint == cp:
            del subtable.cmap[codepoint]

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print ("Test SKIP with post.formatType == 3.0 ...")
  value = ttFont["post"].formatType
  ttFont["post"].formatType = 3.0
  status, message = list(check(ttFont))[-1]
  assert status == SKIP
  # and restore good value:
  ttFont["post"].formatType = value

  print ("Test FAIL with bad glyph name for char 0x0020 ...")
  deleteGlyphEncodings(ttFont, 0x0020)
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "bad20"

  # restore the original font object in preparation for the next test-case:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print ("Test FAIL with bad glyph name for char 0x00A0 ...")
  deleteGlyphEncodings(ttFont, 0x00A0)
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "badA0"

# TODO: test_check_049

def test_check_052():
  """ Font contains all required tables ? """
  from fontbakery.specifications.general import com_google_fonts_check_052 as check

  required_tables = ["cmap", "head", "hhea", "hmtx",
                     "maxp", "name", "OS/2", "post"]
  optional_tables = ["cvt ", "fpgm", "loca", "prep",
                     "VORG", "EBDT", "EBLC", "EBSC",
                     "BASE", "GPOS", "GSUB", "JSTF",
                     "DSIG", "gasp", "hdmx", "kern",
                     "LTSH", "PCLT", "VDMX", "vhea",
                     "vmtx"]
  # Our reference Mada Regular font is good here
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Now we test the special cases for variable fonts:

  print ("Test FAIL with fvar but no STAT...")
  # Note: A TTF with an fvar table but no STAT table
  #       is probably a GX font. For now we're OK with
  #       rejecting those by emitting a FAIL in this case.
  #
  # TODO: Maybe we could someday emit a more explicit
  #       message to the users regarding that...
  ttFont.reader.tables["fvar"] = "foo"
  status, message = list(check(ttFont))[-1]
  assert status == FAIL

  print ("Test PASS with STAT on a non-variable font...")
  del ttFont.reader.tables["fvar"]
  ttFont.reader.tables["STAT"] = "foo"
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # and finally remove what we've just added:
  del ttFont.reader.tables["STAT"]
  # Now we remove required tables one-by-one to validate the FAIL code-path:
  for required in required_tables:
    print ("Test FAIL with missing mandatory table {} ...".format(required))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    if required in ttFont.reader.tables:
      del ttFont.reader.tables[required]
    status, message = list(check(ttFont))[-1]
    assert status == FAIL

  # Then, in preparation for the next step, we make sure
  # there's no optional table (by removing them all):
  for optional in optional_tables:
    if optional in ttFont.reader.tables:
      del ttFont.reader.tables[optional]

  # Then re-insert them one by one to validate the INFO code-path:
  for optional in optional_tables:
    print ("Test INFO with optional table {} ...".format(required))
    ttFont.reader.tables[optional] = "foo"
    # and ensure that the second to last logged message is an
    # INFO status informing the user about it:
    status, message = list(check(ttFont))[-2]
    assert status == INFO
    # remove the one we've just inserted before trying the next one:
    del ttFont.reader.tables[optional]


def test_check_053():
  """ Are there unwanted tables ? """
  from fontbakery.specifications.general import com_google_fonts_check_053 as check

  unwanted_tables = ["FFTM", "TTFA", "prop"]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS
 
  # We now add unwanted tables one-by-one to validate the FAIL code-path:
  for unwanted in unwanted_tables:
    print ("Test FAIL with unwanted table {} ...".format(unwanted))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    ttFont.reader.tables[unwanted] = "foo"
    status, message = list(check(ttFont))[-1]
    assert status == FAIL

# TODO: test_check_058
# TODO: test_check_059
# TODO: test_check_060
