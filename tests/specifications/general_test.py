# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import io

import defcon
import ufo2ft
from fontTools.ttLib import TTFont

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


def NOT_IMPLEMENTED_test_check_035():
  """ Checking with ftxvalidator. """
  # from fontbakery.specifications.general import com_google_fonts_check_035 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "ftxvalidator passed this file."
  # - FAIL, "ftxvalidator outputs to stderr."
  # - WARN, "ftxvalidator returned an error code."
  # - ERROR, "ftxvalidator is not available!"


def NOT_IMPLEMENTED_test_check_036():
  """ Checking with ots-sanitize. """
  # from fontbakery.specifications.general import com_google_fonts_check_036 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # PASS, "ots-sanitize passed this file."
  # FAIL, "ots-sanitize output..."
  # ERROR, "ots-sanitize is not available!"


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


def NOT_IMPLEMENTED_test_check_038():
  """ FontForge validation outputs error messages? """
  # from fontbakery.specifications.general import com_google_fonts_check_038 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # FAIL, "Fontforge printed messages to stderr."
  # PASS, "Fontforge validation did not output any error message."


def NOT_IMPLEMENTED_test_check_039():
  """ FontForge checks. """
  # from fontbakery.specifications.general import com_google_fonts_check_039 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS
  # - SKIP
  # - FAIL, "Contours are not closed!"
  # - FAIL, "There are countour intersections!"
  # - FAIL, "Contours have incorrect directions!"
  # - FAIL, "References in the glyph have been flipped!"
  # - FAIL, "Glyphs do not have points at extremas!"
  # - FAIL, "Glyph names referred to from glyphs not present in the font!"
  # - FAIL, "Points (or control points) are too far apart!"
  # - FAIL, "There are glyphs with more than 1,500 points! Exceeds a PostScript limit."
  # - FAIL, "Exceeds PostScript limit of 96 hints per glyph"
  # - FAIL, "Font has invalid glyph names!"
  # - FAIL, "Glyphs exceed allowed numbers of points defined in maxp"
  # - FAIL, "Glyphs exceed allowed numbers of paths defined in maxp!"
  # - FAIL, Composite glyphs exceed allowed numbers of points defined in maxp!"
  # - FAIL, "Composite glyphs exceed allowed numbers of paths defined in maxp!"
  # - FAIL, "Glyphs instructions have invalid lengths!"
  # - FAIL, "Points in glyphs are not integer aligned!"
  # - FAIL, "Glyphs do not have all required anchors!"
  # - FAIL, "Glyph names are not unique!"
  # - FAIL, "Unicode code points are not unique!"
  # - FAIL, "Hints should NOT overlap!"


def NOT_IMPLEMENTED_test_check_046():
  """ Font contains the first few mandatory glyphs (.null or NULL, CR and
  space)? """
  # from fontbakery.specifications.general import com_google_fonts_check_046 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "Font contains the first few mandatory glyphs" 
  # - WARN, "Font is missing glyphs for some mandatory codepoints"


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
        subtable.cmap = {
            codepoint: name for codepoint, name in subtable.cmap.items()
            if codepoint != cp
        }

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


def NOT_IMPLEMENTED_test_check_049():
  """ Whitespace glyphs have ink? """
  # from fontbakery.specifications.general import com_google_fonts_check_049 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "There is no whitespace glyph with ink."
  # - FAil, "Some glyphs have ink."


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


def NOT_IMPLEMENTED_test_check_058():
  """ Glyph names are all valid? """
  # from fontbakery.specifications.general import com_google_fonts_check_058 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "Glyph names do not comply with naming conventions"
  # - PASS, "Glyph names are all valid."


def NOT_IMPLEMENTED_test_check_059():
  """ Font contains unique glyph names? """
  # from fontbakery.specifications.general import com_google_fonts_check_059 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "Font contains unique glyph names."
  # - FAIL, "Glyph IDs occur twice"


def NOT_IMPLEMENTED_test_check_060():
  """ No glyph is incorrectly named? """
  # from fontbakery.specifications.general import com_google_fonts_check_060 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "Font does not have any incorrectly named glyph."
  # - FAIL, "Some glyph IDs are incorrectly named."


def test_check_078():
  """ Check that glyph names do not exceed max length. """
  from fontbakery.specifications.general import com_google_fonts_check_078 as check

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
