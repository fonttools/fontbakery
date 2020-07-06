import pytest
import os
from fontTools.ttLib import TTFont

from fontbakery.constants import NameID
from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_SKIP,
                              assert_results_contain,
                              portable_path)


from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


@pytest.fixture
def montserrat_ttFonts():
  paths = [
    TEST_FILE("montserrat/Montserrat-Black.ttf"),
    TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Bold.ttf"),
    TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Italic.ttf"),
    TEST_FILE("montserrat/Montserrat-Light.ttf"),
    TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Medium.ttf"),
    TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Regular.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Thin.ttf"),
    TEST_FILE("montserrat/Montserrat-ThinItalic.ttf")
  ]
  return [TTFont(path) for path in paths]


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

cabin_condensed_fonts = [
  TEST_FILE("cabin/CabinCondensed-Regular.ttf"),
  TEST_FILE("cabin/CabinCondensed-Medium.ttf"),
  TEST_FILE("cabin/CabinCondensed-Bold.ttf"),
  TEST_FILE("cabin/CabinCondensed-SemiBold.ttf")
]

@pytest.fixture
def cabin_ttFonts():
  return [TTFont(path) for path in cabin_fonts]

@pytest.fixture
def cabin_condensed_ttFonts():
  return [TTFont(path) for path in cabin_condensed_fonts]


def test_check_valid_glyphnames():
  """ Glyph names are all valid? """
  import io
  from fontbakery.profiles.universal import com_google_fonts_check_valid_glyphnames as check

  # We start with a good font file:
  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")
  test_font = TTFont(test_font_path)
  assert_PASS(check(test_font))

  # There used to be a 31 char max-length limit.
  # This was good:
  test_font.glyphOrder[2] = "a" * 31
  assert_PASS(check(test_font))

  # And this was bad:
  legacy_too_long = "a" * 32
  test_font.glyphOrder[2] = legacy_too_long
  message = assert_results_contain(check(test_font),
                                   WARN, 'legacy-long-names')
  assert legacy_too_long in message

  # Nowadays, it seems most implementations can deal with
  # up to 63 char glyph names:
  good_name = "b" * 63
  bad_name1 = "a" * 64
  bad_name2 = "3cents"
  bad_name3 = ".threecents"
  test_font.glyphOrder[2] = bad_name1
  test_font.glyphOrder[3] = bad_name2
  test_font.glyphOrder[4] = bad_name3
  test_font.glyphOrder[5] = good_name
  message = assert_results_contain(check(test_font),
                                   FAIL, 'found-invalid-names')
  assert good_name not in message
  assert bad_name1 in message
  assert bad_name2 in message
  assert bad_name3 in message

  # TrueType fonts with a format 3.0 post table contain
  # no glyph names, so the check must be SKIP'd in that case.
  #
  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_font = TTFont(test_font_path)
  test_font["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  assert_SKIP(check(test_font))


def test_check_unique_glyphnames():
  """ Font contains unique glyph names? """
  import io
  from fontbakery.profiles.universal import com_google_fonts_check_unique_glyphnames as check

  test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")
  test_font = TTFont(test_font_path)
  assert_PASS(check(test_font))

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
  message = assert_results_contain(check(test_font),
                                   FAIL, None) # FIXME: This needs a message keyword
  assert "space" in message

  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_font = TTFont(test_font_path)
  test_font.setGlyphOrder(glyph_names)
  test_font["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_font.save(test_file)
  test_font = TTFont(test_file)
  assert_SKIP(check(test_font))


def DISABLED_test_check_glyphnames_max_length():
  """ Check that glyph names do not exceed max length. """
  from fontbakery.profiles.universal import com_google_fonts_check_glyphnames_max_length as check
  import defcon
  import ufo2ft

  # TTF
  test_font = defcon.Font(TEST_FILE("test.ufo"))
  test_ttf = ufo2ft.compileTTF(test_font)
  assert_PASS(check(test_ttf))

  test_glyph = defcon.Glyph()
  test_glyph.unicode = 0x1234
  test_glyph.name = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                     "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                     "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
  test_font.insertGlyph(test_glyph)
  test_ttf = ufo2ft.compileTTF(test_font, useProductionNames=False)
  assert_results_contain(check(test_ttf),
                         FAIL, None) # FIXME: This needs a message keyword

  test_ttf = ufo2ft.compileTTF(test_font, useProductionNames=True)
  assert_PASS(check(test_ttf))

  # Upgrade to post format 3.0 and roundtrip data to update TTF object.
  test_ttf["post"].formatType = 3.0
  test_file = io.BytesIO()
  test_ttf.save(test_file)
  test_ttf = TTFont(test_file)
  message = assert_PASS(check(test_ttf))
  assert "format 3.0" in message

  del test_font, test_ttf, test_file  # Prevent copypasta errors.

  # CFF
  test_font = defcon.Font(TEST_FILE("test.ufo"))
  test_otf = ufo2ft.compileOTF(test_font)
  assert_PASS(check(test_otf))

  test_font.insertGlyph(test_glyph)
  test_otf = ufo2ft.compileOTF(test_font, useProductionNames=False)
  assert_results_contain(check(test_otf),
                         FAIL, None) # FIXME: This needs a message keyword

  test_otf = ufo2ft.compileOTF(test_font, useProductionNames=True)
  assert_PASS(check(test_otf))


def test_check_ttx_roundtrip():
  """ Checking with fontTools.ttx """
  from fontbakery.profiles.universal import com_google_fonts_check_ttx_roundtrip as check

  good_font_path = TEST_FILE("mada/Mada-Regular.ttf")
  assert_PASS(check(good_font_path))

  # TODO: Can anyone show us a font file that fails ttx roundtripping?!
  #
  # bad_font_path = TEST_FILE("...")
  # assert_results_contain(check(bad_font_path),
  #                        FAIL, None) # FIXME: This needs a message keyword


def test_is_up_to_date():
  from fontbakery.profiles.universal import is_up_to_date
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


def test_check_name_trailing_spaces():
  """ Name table entries must not have trailing spaces. """
  from fontbakery.profiles.universal import com_google_fonts_check_name_trailing_spaces as check
  # Our reference Cabin Regular is known to be good:
  fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
  ttFont = TTFont(fontfile)

  # So it must PASS the check:
  assert_PASS(check(ttFont),
              'with a good font...')

  for i, entry in enumerate(ttFont['name'].names):
    good_string = ttFont['name'].names[i].toUnicode()
    bad_string = good_string + " "
    ttFont['name'].names[i].string = bad_string.encode(entry.getEncoding())
    assert_results_contain(check(ttFont),
                           FAIL, None, # FIXME: This needs a message keyword
                           f'with a bad name table entry ({i}: "{bad_string}")...')

    #restore good entry before moving to the next one:
    ttFont['name'].names[i].string = good_string.encode(entry.getEncoding())


def test_check_family_single_directory():
  """ Fonts are all in the same directory. """
  from fontbakery.profiles.universal import com_google_fonts_check_family_single_directory as check
  same_dir = [
    TEST_FILE("cabin/Cabin-Thin.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]
  multiple_dirs = [
    TEST_FILE("mada/Mada-Regular.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]

  assert_PASS(check(same_dir),
              f'with same dir: {same_dir}')

  assert_results_contain(check(multiple_dirs),
                         FAIL, None, # FIXME: This needs a message keyword
                         f'with multiple dirs: {multiple_dirs}')


def test_check_ftxvalidator_is_available():
  """ Is the command `ftxvalidator` (Apple Font Tool Suite) available? """
  from fontbakery.profiles.universal import com_google_fonts_check_ftxvalidator_is_available as check

  found = '/usr/local/bin/ftxvalidator'
  message = assert_PASS(check(found))
  assert "is available" in message

  found = None
  message = assert_results_contain(check(found),
                                   WARN, None) # FIXME: This needs a message keyword
  assert "Could not find" in message


def NOT_IMPLEMENTED_test_check_ftxvalidator():
  """ Checking with ftxvalidator. """
  # from fontbakery.profiles.universal import com_google_fonts_check_ftxvalidator as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - PASS, "ftxvalidator passed this file."
  # - FAIL, "ftxvalidator outputs to stderr."
  # - ERROR, "ftxvalidator returned an error code."
  # - ERROR, "ftxvalidator is not available!"


def test_check_ots():
  """ Checking with ots-sanitize. """
  from fontbakery.profiles.universal import com_google_fonts_check_ots as check

  sanitary_font = TEST_FILE("cabin/Cabin-Regular.ttf")
  assert_PASS(check(sanitary_font))

  bogus_font = TEST_FILE("README.txt")
  message = assert_results_contain(check(bogus_font),
                                   FAIL, None) # FIXME: This needs a message keyword
  assert "invalid version tag" in message
  assert "Failed to sanitize file!" in message


def test_check_mandatory_glyphs():
  """ Font contains the first few mandatory glyphs (.null or NULL, CR and
  space)? """
  from fontbakery.profiles.universal import com_google_fonts_check_mandatory_glyphs as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  assert_PASS(check(test_font))

  import fontTools.subset
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs="n")  # Arbitrarily remove everything except n.
  subsetter.subset(test_font)
  assert_results_contain(check(test_font),
                         WARN, None) # FIXME: This needs a message keyword


def test_check_whitespace_glyphs():
  """ Font contains glyphs for whitespace characters ? """
  from fontbakery.profiles.universal import com_google_fonts_check_whitespace_glyphs as check
  from fontbakery.profiles.shared_conditions import missing_whitespace_chars

  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
  missing = missing_whitespace_chars(ttFont)

  # So it must PASS the check:
  assert_PASS(check(ttFont, missing),
              'with a good font...')

  # Then we remove the nbsp char (0x00A0) so that we get a FAIL:
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  assert_results_contain(check(ttFont, missing),
                         FAIL, 'missing-whitespace-glyph-0x00A0',
                         'with a font lacking a nbsp (0x00A0)...')

  # restore original Mada Regular font:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # And finally remove the space character (0x0020) to get another FAIL:
  for table in ttFont['cmap'].tables:
    if 0x0020 in table.cmap:
      del table.cmap[0x0020]

  missing = missing_whitespace_chars(ttFont)
  assert_results_contain(check(ttFont, missing),
                         FAIL, 'missing-whitespace-glyph-0x0020',
                         'with a font lacking a space (0x0020)...')


def test_check_whitespace_glyphnames():
  """ Font has **proper** whitespace glyph names ? """
  from fontbakery.profiles.universal import com_google_fonts_check_whitespace_glyphnames as check

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

  def editCmap(font, cp, name):
    """ Corrupt the cmap by changing the glyph name
        for a given code point.
    """
    for subtable in font['cmap'].tables:
      if subtable.isUnicode():
        # Copy the map
        subtable.cmap = subtable.cmap.copy()
        # edit it
        subtable.cmap[cp] = name

  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  assert_PASS(check(ttFont),
              'with a good font...')

  value = ttFont["post"].formatType
  ttFont["post"].formatType = 3.0
  assert_SKIP(check(ttFont),
              'with post.formatType == 3.0 ...')

  # and restore good value:
  ttFont["post"].formatType = value

  deleteGlyphEncodings(ttFont, 0x0020)
  assert_results_contain(check(ttFont),
                         FAIL, 'bad20',
                         'with bad glyph name for char 0x0020 ...')

  # restore the original font object in preparation for the next test-case:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  deleteGlyphEncodings(ttFont, 0x00A0)
  assert_results_contain(check(ttFont),
                         FAIL, 'badA0',
                         'with bad glyph name for char 0x00A0 ...')

  # restore the original font object in preparation for the next test-case:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # See https://github.com/googlefonts/fontbakery/issues/2624
  # nbsp is not Adobe Glyph List compliant.
  editCmap(ttFont, 0x00A0, "nbsp")
  assert_results_contain(check(ttFont), FAIL, 'badA0',
                         'with bad glyph name for char 0x00A0 ...')

  editCmap(ttFont, 0x00A0, "nbspace")
  assert_results_contain(check(ttFont), WARN, 'badA0',
                         "for naming 0x00A0 nbspace ...")

  editCmap(ttFont, 0x00A0, "uni00A0")
  assert_PASS(check(ttFont),
              "for naming 0x00A0 uni00A0 ...")


def test_check_whitespace_ink():
  """ Whitespace glyphs have ink? """
  from fontbakery.profiles.universal import com_google_fonts_check_whitespace_ink as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
  assert_PASS(check(test_font))

  test_font["cmap"].tables[0].cmap[0x0020] = "uni1E17"
  assert_results_contain(check(test_font),
                         FAIL, None, # FIXME: This needs a message keyword
                         'for whitespace character having composites (with ink).')

  test_font["cmap"].tables[0].cmap[0x0020] = "scedilla"
  assert_results_contain(check(test_font),
                         FAIL, None, # FIXME: This needs a message keyword
                         'for whitespace character having outlines (with ink).')

  import fontTools.pens.ttGlyphPen
  pen = fontTools.pens.ttGlyphPen.TTGlyphPen(test_font.getGlyphSet())
  pen.addComponent("space", (1, 0, 0, 1, 0, 0))
  test_font["glyf"].glyphs["uni200B"] = pen.glyph()
  assert_results_contain(check(test_font),
                         FAIL, None, # FIXME: This needs a message keyword
                         'for whitespace character having composites (without ink).')


def test_check_required_tables():
  """ Font contains all required tables ? """
  from fontbakery.profiles.universal import com_google_fonts_check_required_tables as check

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
  assert_PASS(check(ttFont),
              'with a good font...')

  # Now we test the special cases for variable fonts:
  #
  # Note: A TTF with an fvar table but no STAT table
  #       is probably a GX font. For now we're OK with
  #       rejecting those by emitting a FAIL in this case.
  #
  # TODO: Maybe we could someday emit a more explicit
  #       message to the users regarding that...
  ttFont.reader.tables["fvar"] = "foo"
  assert_results_contain(check(ttFont),
                         FAIL, None, # FIXME: This needs a message keyword
                         'with fvar but no STAT...')

  del ttFont.reader.tables["fvar"]
  ttFont.reader.tables["STAT"] = "foo"
  assert_PASS(check(ttFont),
              'with STAT on a non-variable font...')

  # and finally remove what we've just added:
  del ttFont.reader.tables["STAT"]
  # Now we remove required tables one-by-one to validate the FAIL code-path:
  for required in required_tables:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    if required in ttFont.reader.tables:
      del ttFont.reader.tables[required]
    assert_results_contain(check(ttFont),
                           FAIL, None, # FIXME: This needs a message keyword
                           f'with missing mandatory table {required} ...')
  # Then, in preparation for the next step, we make sure
  # there's no optional table (by removing them all):
  for optional in optional_tables:
    if optional in ttFont.reader.tables:
      del ttFont.reader.tables[optional]

  # Then re-insert them one by one to validate the INFO code-path:
  for optional in optional_tables:
    ttFont.reader.tables[optional] = "foo"
    # and ensure that the second to last logged message is an
    # INFO status informing the user about it:
    assert_results_contain(check(ttFont),
                           INFO, None, # FIXME: This needs a message keyword
                           f'with optional table {required} ...')
    # remove the one we've just inserted before trying the next one:
    del ttFont.reader.tables[optional]


def test_check_unwanted_tables():
  """ Are there unwanted tables ? """
  from fontbakery.profiles.universal import com_google_fonts_check_unwanted_tables as check

  unwanted_tables = [
    "FFTM", # FontForge
    "TTFA", # TTFAutohint
    "TSI0", # TSI* = VTT
    "TSI1",
    "TSI2",
    "TSI3",
    "TSI5",
    "prop", # FIXME: Why is this one unwanted?
    "MVAR", # Bugs in DirectWrite
  ]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  assert_PASS(check(ttFont),
              'with a good font...')

  # We now add unwanted tables one-by-one to validate the FAIL code-path:
  for unwanted in unwanted_tables:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    ttFont.reader.tables[unwanted] = "foo"
    assert_results_contain(check(ttFont),
                           FAIL, None, # FIXME: This needs a message keyword
                           f'with unwanted table {unwanted} ...')


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


mada_fonts = [
  TEST_FILE("mada/Mada-Black.ttf"),
  TEST_FILE("mada/Mada-ExtraLight.ttf"),
  TEST_FILE("mada/Mada-Medium.ttf"),
  TEST_FILE("mada/Mada-SemiBold.ttf"),
  TEST_FILE("mada/Mada-Bold.ttf"),
  TEST_FILE("mada/Mada-Light.ttf"),
  TEST_FILE("mada/Mada-Regular.ttf"),
]

@pytest.fixture
def mada_ttFonts():
  return [TTFont(path) for path in mada_fonts]


def test_check_family_win_ascent_and_descent(mada_ttFonts):
  """ Checking OS/2 usWinAscent & usWinDescent. """
  from fontbakery.profiles.universal import com_google_fonts_check_family_win_ascent_and_descent as check
  from fontbakery.profiles.shared_conditions import vmetrics

  # Our reference Mada Regular is know to be bad here.
  vm = vmetrics(mada_ttFonts)
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # But we fix it first to test the PASS code-path:
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  assert_PASS(check(ttFont, vm),
              'with a good font...')

  # Then we break it:
  ttFont['OS/2'].usWinAscent = vm['ymax'] - 1
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  assert_results_contain(check(ttFont, vm),
                         FAIL, 'ascent',
                         'with a bad OS/2.usWinAscent...')

  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin']) - 1
  assert_results_contain(check(ttFont, vm),
                         FAIL, 'descent',
                         'with a bad OS/2.usWinDescent...')


def test_check_os2_metrics_match_hhea(mada_ttFonts):
  """ Checking OS/2 Metrics match hhea Metrics. """
  from fontbakery.profiles.universal import com_google_fonts_check_os2_metrics_match_hhea as check

  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  assert_PASS(check(ttFont),
              'with a good font...')

  # Now we break it:
  correct = ttFont['hhea'].ascent
  ttFont['OS/2'].sTypoAscender = correct + 1
  assert_results_contain(check(ttFont),
                         FAIL, 'ascender',
                         'with a bad OS/2.sTypoAscender font...')

  # Restore good value:
  ttFont['OS/2'].sTypoAscender = correct

  # And break it again, now on sTypoDescender value:
  correct = ttFont['hhea'].descent
  ttFont['OS/2'].sTypoDescender = correct + 1
  assert_results_contain(check(ttFont),
                         FAIL, 'descender',
                         'with a bad OS/2.sTypoDescender font...')


def test_check_family_vertical_metrics(montserrat_ttFonts):
  from fontbakery.profiles.universal import com_google_fonts_check_family_vertical_metrics as check

  assert_PASS(check(montserrat_ttFonts),
              'with multiple good fonts...')

  montserrat_ttFonts[0]['OS/2'].usWinAscent = 4000
  assert_results_contain(check(montserrat_ttFonts),
                         FAIL, 'usWinAscent-mismatch',
                         'with one bad font that has one different vertical metric val...')

  # TODO: Also test these code-paths:
  # FAIL, 'mismatch-<other values>'
  # FAIL, 'lacks-OS/2'
  # FAIL, 'lacks-hhea'


def test_check_superfamily_vertical_metrics(montserrat_ttFonts, cabin_ttFonts, cabin_condensed_ttFonts):
  from fontbakery.profiles.universal import com_google_fonts_check_superfamily_vertical_metrics as check

  assert_PASS(check([cabin_ttFonts,
                     cabin_condensed_ttFonts]),
             'with multiple good families...')

  assert_results_contain(check([cabin_ttFonts,
                                montserrat_ttFonts]),
                         WARN, None, # FIXME: This needs a message keyword
                         'with families that diverge on vertical metric values...')


def test_check_STAT_strings():
  from fontbakery.profiles.universal import com_google_fonts_check_STAT_strings as check

  good = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
  assert_PASS(check(good))

  bad = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Italic.ttf"))
  assert_results_contain(check(bad),
                         FAIL, None) # FIXME: This needs a message keyword

