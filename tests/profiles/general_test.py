import io
import os

import defcon
import pytest
import ufo2ft
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


def test_check_family_single_directory():
  """ Fonts are all in the same directory. """
  from fontbakery.profiles.general import com_google_fonts_check_family_single_directory as check
  same_dir = [
    TEST_FILE("cabin/Cabin-Thin.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]
  multiple_dirs = [
    TEST_FILE("mada/Mada-Regular.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]
  print(f'Test PASS with same dir: {same_dir}')
  status, message = list(check(same_dir))[-1]
  assert status == PASS

  print(f'Test FAIL with multiple dirs: {multiple_dirs}')
  status, message = list(check(multiple_dirs))[-1]
  assert status == FAIL


def test_check_ftxvalidator_is_available():
  """ Is the command `ftxvalidator` (Apple Font Tool Suite) available? """
  from fontbakery.profiles.general import com_google_fonts_check_ftxvalidator_is_available as check

  # code-paths:
  # - PASS, "ftxvalidator is available."
  # - WARN, "ftxvalidator is not available."
  status, output = check(True)
  assert status == PASS
  assert "is available" in output

  status, output = check(False)
  assert status == WARN
  assert "is not available" in output


def NOT_IMPLEMENTED_test_check_ftxvalidator():
  """ Checking with ftxvalidator. """
  # from fontbakery.profiles.general import com_google_fonts_check_ftxvalidator as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "ftxvalidator passed this file."
  # - FAIL, "ftxvalidator outputs to stderr."
  # - ERROR, "ftxvalidator returned an error code."
  # - ERROR, "ftxvalidator is not available!"


def test_check_ots():
  """ Checking with ots-sanitize. """
  from fontbakery.profiles.general import com_google_fonts_check_ots as check

  sanitary_font = TEST_FILE("cabin/Cabin-Regular.ttf")
  status, _ = list(check(sanitary_font))[-1]
  assert status == PASS

  bogus_font = TEST_FILE("README.txt")
  status, output = list(check(bogus_font))[-1]
  assert status == FAIL
  assert "invalid version tag" in output
  assert "Failed to sanitize file!" in output


def NOT_IMPLEMENTED_test_check_fontforge_stderr():
  """ FontForge validation outputs error messages? """
  # from fontbakery.profiles.general import com_google_fonts_check_fontforge_error_messages as check
  # TODO: Implement-me!
  #
  # code-paths:
  # WARN, "Fontforge printed messages to stderr."
  # PASS, "Fontforge validation did not output any error message."


def NOT_IMPLEMENTED_test_check_fontforge():
  """ FontForge checks. """
  # from fontbakery.profiles.general import com_google_fonts_check_fontforge as check
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


def test_check_mandatory_glyphs():
  """ Font contains the first few mandatory glyphs (.null or NULL, CR and
  space)? """
  from fontbakery.profiles.general import com_google_fonts_check_mandatory_glyphs as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  import fontTools.subset
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs="n")  # Arbitrarily remove everything except n.
  subsetter.subset(test_font)
  status, _ = list(check(test_font))[-1]
  assert status == WARN


def test_check_whitespace_glyphs():
  """ Font contains glyphs for whitespace characters ? """
  from fontbakery.profiles.general import com_google_fonts_check_whitespace_glyphs as check
  from fontbakery.profiles.shared_conditions import missing_whitespace_chars

  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
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
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # And finally remove the space character (0x0020) to get another FAIL:
  print ("Test FAIL with a font lacking a space (0x0020)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(check(ttFont, missing))[-1]
  assert status == FAIL


def test_check_whitespace_glyphnames():
  """ Font has **proper** whitespace glyph names ? """
  from fontbakery.profiles.general import com_google_fonts_check_whitespace_glyphnames as check

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
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

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
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  print ("Test FAIL with bad glyph name for char 0x00A0 ...")
  deleteGlyphEncodings(ttFont, 0x00A0)
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "badA0"


def test_check_whitespace_ink():
  """ Whitespace glyphs have ink? """
  from fontbakery.profiles.general import com_google_fonts_check_whitespace_ink as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  print ("Test for whitespace character having composites (with ink).")
  test_font["cmap"].tables[0].cmap[0x0020] = "uni1E17"
  status, _ = list(check(test_font))[-1]
  assert status == FAIL

  print ("Test for whitespace character having outlines (with ink).")
  test_font["cmap"].tables[0].cmap[0x0020] = "scedilla"
  status, _ = list(check(test_font))[-1]
  assert status == FAIL

  print ("Test for whitespace character having composites (without ink).")
  import fontTools.pens.ttGlyphPen
  pen = fontTools.pens.ttGlyphPen.TTGlyphPen(test_font.getGlyphSet())
  pen.addComponent("space", (1, 0, 0, 1, 0, 0))
  test_font["glyf"].glyphs["uni200B"] = pen.glyph()
  status, _ = list(check(test_font))[-1]
  assert status == FAIL


def test_check_required_tables():
  """ Font contains all required tables ? """
  from fontbakery.profiles.general import com_google_fonts_check_required_tables as check

  required_tables = ["cmap", "head", "hhea", "hmtx",
                     "maxp", "name", "OS/2", "post"]
  optional_tables = ["cvt ", "fpgm", "loca", "prep",
                     "VORG", "EBDT", "EBLC", "EBSC",
                     "BASE", "GPOS", "GSUB", "JSTF",
                     "DSIG", "gasp", "hdmx", "kern",
                     "LTSH", "PCLT", "VDMX", "vhea",
                     "vmtx"]
  # Our reference Mada Regular font is good here
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

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
    print (f"Test FAIL with missing mandatory table {required} ...")
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
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
    print (f"Test INFO with optional table {required} ...")
    ttFont.reader.tables[optional] = "foo"
    # and ensure that the second to last logged message is an
    # INFO status informing the user about it:
    status, message = list(check(ttFont))[-2]
    assert status == INFO
    # remove the one we've just inserted before trying the next one:
    del ttFont.reader.tables[optional]


def test_check_unwanted_tables():
  """ Are there unwanted tables ? """
  from fontbakery.profiles.general import com_google_fonts_check_unwanted_tables as check

  unwanted_tables = [
    "FFTM", # FontForge
    "TTFA", # TTFAutohint
    "TSI0", # TSI* = VTT
    "TSI1",
    "TSI2",
    "TSI3",
    "TSI5",
    "prop" # FIXME: Why is this one unwanted?
  ]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # We now add unwanted tables one-by-one to validate the FAIL code-path:
  for unwanted in unwanted_tables:
    print (f"Test FAIL with unwanted table {unwanted} ...")
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    ttFont.reader.tables[unwanted] = "foo"
    status, message = list(check(ttFont))[-1]
    assert status == FAIL


def test_check_valid_glyphnames():
  """ Glyph names are all valid? """
  from fontbakery.profiles.general import com_google_fonts_check_valid_glyphnames as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")
  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  bad_name1 = "a" * 32
  bad_name2 = "3cents"
  bad_name3 = ".threecents"
  good_name1 = "b" * 31
  test_font.glyphOrder[2] = bad_name1
  test_font.glyphOrder[3] = bad_name2
  test_font.glyphOrder[4] = bad_name3
  test_font.glyphOrder[5] = good_name1
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert bad_name1 in message
  assert bad_name2 in message
  assert bad_name3 in message
  assert good_name1 not in message

  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_font = TTFont(test_font_path)
  test_font["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  status, message = list(check(test_font))[-1]
  assert status == SKIP


def test_check_unique_glyphnames():
  """ Font contains unique glyph names? """
  from fontbakery.profiles.general import com_google_fonts_check_unique_glyphnames as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")
  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  # Fonttools renames duplicate glyphs with #1, #2, ... on load.
  # Code snippet from https://github.com/fonttools/fonttools/issues/149.
  glyph_names = test_font.getGlyphOrder()
  glyph_names[2] = glyph_names[3]
  # Load again, we changed the font directly.
  test_font = TTFont(test_font_path)
  test_font.setGlyphOrder(glyph_names)
  test_font['post']  # Just access the data to make fonttools generate it.
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  status, message = list(check(test_font))[-1]
  assert status == FAIL
  assert "space" in message

  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_font = TTFont(test_font_path)
  test_font.setGlyphOrder(glyph_names)
  test_font["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  status, message = list(check(test_font))[-1]
  assert status == SKIP


def DISABLED_test_check_glyphnames_max_length():
  """ Check that glyph names do not exceed max length. """
  from fontbakery.profiles.general import com_google_fonts_check_glyphnames_max_length as check

  # TTF
  test_font = defcon.Font(TEST_FILE("test.ufo"))
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
  test_font = defcon.Font(TEST_FILE("test.ufo"))
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


def test_check_ttx_roundtrip():
  """ Checking with fontTools.ttx """
  from fontbakery.profiles.general import com_google_fonts_check_ttx_roundtrip as check

  good_font_path = TEST_FILE("mada/Mada-Regular.ttf")
  status, _ = list(check(good_font_path))[-1]
  assert status == PASS

  # TODO: Can anyone show us a font file that fails ttx roundtripping?!
  #bad_font_path = TEST_FILE("...")
  #status, _ = list(check(bad_font_path))[-1]
  #assert status == FAIL


def test_is_up_to_date():
  from fontbakery.profiles.general import is_up_to_date
  # is_up_to_date(installed, latest)
  assert(is_up_to_date(installed="0.5.0",
                          latest="0.5.0") == True)
  assert(is_up_to_date(installed="0.5.1",
                          latest="0.5.0") == True)
  assert(is_up_to_date(installed="0.4.1",
                          latest="0.5.0") == False)
  assert(is_up_to_date(installed="0.3.4",
                          latest="0.3.5") == False)
  assert(is_up_to_date(installed="1.0.0",
                          latest="1.0.1") == False)
  assert(is_up_to_date(installed="2.0.0",
                          latest="1.5.3") == True)
  assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                          latest="0.5.1") == True)
  assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                          latest="0.5.2") == False)
  assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                          latest="0.5.3") == False)


def test_glyph_has_ink():
  from fontbakery.utils import glyph_has_ink
  from fontTools.ttLib import TTFont

  print()  # so next line doesn't start with '.....'

  cff_test_font = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
  print('Test if CFF glyph with ink has ink')
  assert(glyph_has_ink(cff_test_font, '.notdef') is True)
  print('Test if CFF glyph without ink has ink')
  assert(glyph_has_ink(cff_test_font, 'space') is False)

  ttf_test_font = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Regular.ttf"))
  print('Test if TTF glyph with ink has ink')
  assert(glyph_has_ink(ttf_test_font, '.notdef') is True)
  print('Test if TTF glyph without ink has ink')
  assert(glyph_has_ink(ttf_test_font, 'space') is False)

  cff2_test_font = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
  print('Test if CFF2 glyph with ink has ink')
  assert(glyph_has_ink(cff2_test_font, '.notdef') is True)
  print('Test if CFF2 glyph without ink has ink')
  assert(glyph_has_ink(cff2_test_font, 'space') is False)
