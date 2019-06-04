import os

import fontTools.ttLib
from fontTools.ttLib import TTFont

from fontbakery.utils import TEST_FILE, portable_path
from fontbakery.constants import NameID, PlatformID, WindowsEncodingID, WIN_ENGLISH_LANG_ID
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

def test_check_name_empty_records():
    from fontbakery.profiles.name import com_adobe_fonts_check_name_empty_records as check

    font_path = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    test_font = TTFont(font_path)

    # try a font with fully populated name records
    status, message = list(check(test_font))[-1]
    assert status == PASS

    # now try a completely empty string
    test_font['name'].names[3].string = b''
    status, message = list(check(test_font))[-1]
    assert status == FAIL

    # now try a string that only has whitespace
    test_font['name'].names[3].string = b' '
    status, message = list(check(test_font))[-1]
    assert status == FAIL


def test_check_name_no_copyright_on_description():
  """ Description strings in the name table
      must not contain copyright info.
  """
  from fontbakery.profiles.name import com_google_fonts_check_name_no_copyright_on_description as check

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # here we add a "Copyright" string to a NameID.DESCRIPTION
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NameID.DESCRIPTION:
      ttFont['name'].names[i].string = "Copyright".encode(name.getEncoding())

  print('Test FAIL with a bad font...')
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


# If we ever reuse this helper function,
# then move it into fontbakery.utils:
def results_contain(results, expected_status, expected_code):
  for status, message in results:
    if status == expected_status and message.code == expected_code:
      return True
  # else
  return False


def test_check_monospace():
  """ Checking correctness of monospaced metadata. """
  from fontbakery.profiles.name import com_google_fonts_check_monospace as check
  from fontbakery.profiles.shared_conditions import glyph_metrics_stats
  from fontbakery.constants import (PANOSE_Proportion,
                                    IsFixedWidth)

  # This check has a large number of code-paths
  # We'll make sure to test them all here.
  #
  # --------------------------------------------
  # Starting with non-monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good non-monospace font...')
  # Our reference Mada Regular is a non-monospace font
  # know to have good metadata for this check.
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
  stats = glyph_metrics_stats(ttFont)
  status, message = list(check(ttFont, stats))[-1]
  assert status == PASS and message.code == "good"

  # We'll mark it as monospaced on the post table and make sure it fails:
  print('Test FAIL with a non-monospaced font with bad post.isFixedPitch value ...')
  ttFont["post"].isFixedPitch = 42 # *any* non-zero value means monospaced
  status, message = list(check(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-post-isFixedPitch"

  # restore good value:
  ttFont["post"].isFixedPitch = IsFixedWidth.NOT_MONOSPACED

  # Now we mark it as monospaced on the OS/2 and it should also fail:
  print('Test FAIL with a non-monospaced font with bad OS/2.panose.bProportion value (MONOSPACED) ...')
  ttFont["OS/2"].panose.bProportion = PANOSE_Proportion.MONOSPACED
  status, message = list(check(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-panose-proportion"

  # --------------------------------------------
  # And now we test the monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good monospaced font...')
  # Our reference OverpassMono Regular is know to be
  # a monospaced font with good metadata here.
  ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))

  stats = glyph_metrics_stats(ttFont)
  assert stats['most_common_width'] == 616
  status, message = list(check(ttFont, stats))[-1]
  # WARN is emitted when there's at least one outlier.
  # I don't see a good reason to be picky and also test that one separately here...
  assert (status == WARN and message.code == "mono-outliers") or \
         (status == PASS and message.code == "mono-good")

  # Let's incorrectly mark it as a non-monospaced on the post table and it should fail:
  print('Test FAIL with a monospaced font with bad post.isFixedPitch value ...')
  ttFont["post"].isFixedPitch = IsFixedWidth.NOT_MONOSPACED
  # here we search for the expected FAIL among all results
  # instead of simply looking at the last one
  # because we may also get an outliers WARN in some cases:
  results = list(check(ttFont, stats))
  assert results_contain(results, FAIL, "mono-bad-post-isFixedPitch")

  # There are several bad panose proportion values for a monospaced font.
  # Only PANOSE_Proportion.MONOSPACED would be valid.
  # So we'll try all the bad ones here to make sure all of them emit a FAIL:
  bad_monospaced_panose_values = [
    PANOSE_Proportion.ANY,
    PANOSE_Proportion.NO_FIT,
    PANOSE_Proportion.OLD_STYLE,
    PANOSE_Proportion.MODERN,
    PANOSE_Proportion.EVEN_WIDTH,
    PANOSE_Proportion.EXTENDED,
    PANOSE_Proportion.CONDENSED,
    PANOSE_Proportion.VERY_EXTENDED,
    PANOSE_Proportion.VERY_CONDENSED,
  ]
  good_value = ttFont["OS/2"].panose.bProportion
  for bad_value in bad_monospaced_panose_values:
    print(f'Test FAIL with a monospaced font with bad OS/2.panose.bProportion value ({bad_value}) ...')
    ttFont["OS/2"].panose.bProportion = bad_value
    # again, we search the expected FAIL because we may algo get an outliers WARN here:
    results = list(check(ttFont, stats))
    assert results_contain(results, FAIL, "mono-bad-panose-proportion")


def test_check_name_line_breaks():
  """ Name table entries should not contain line-breaks. """
  from fontbakery.profiles.name import com_google_fonts_check_name_line_breaks as check

  # Our reference Mada Regular font is good here:
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print ("Test FAIL with name entries containing a linebreak...")
  for i in range(len(ttFont["name"].names)):
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    encoding = ttFont["name"].names[i].getEncoding()
    ttFont["name"].names[i].string = "bad\nstring".encode(encoding)
    status, message = list(check(ttFont))[-1]
    assert status == FAIL


def test_check_name_match_familyname_fullfont():
  """ Does full font name begin with the font family name? """
  from fontbakery.profiles.name import com_google_fonts_check_name_match_familyname_fullfont as check
  # Our reference Mada Regular is known to be good
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # alter the full-font-name prepending a bad prefix:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NameID.FULL_FONT_NAME:
      ttFont["name"].names[i].string = "bad-prefix".encode(name.getEncoding())

  # and make sure the check FAILs:
  print ("Test FAIL with a font in which the family name begins with a digit...")
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "does-not"

  print ("Test FAIL with no FULL_FONT_NAME entries...")
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NameID.FULL_FONT_NAME:
      del ttFont["name"].names[i]
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "no-full-font-name"

  print ("Test FAIL with no FONT_FAMILY_NAME entries...")
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NameID.FONT_FAMILY_NAME:
      del ttFont["name"].names[i]
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "no-font-family-name"

def assert_name_table_check_result(ttFont, index, name, check, value, expected_result):
  backup = name.string
  # set value
  ttFont["name"].names[index].string = value.encode(name.getEncoding())
  # run check
  status, message = list(check(ttFont))[-1]
  # restore value
  ttFont["name"].names[index].string = backup
  assert status == expected_result


def test_check_family_naming_recommendations():
  """ Font follows the family naming recommendations ? """
  from fontbakery.profiles.name import com_google_fonts_check_family_naming_recommendations as check
  # Our reference Mada Medium is known to be good
  ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # We'll test rule violations in all entries one-by-one
  for index, name in enumerate(ttFont["name"].names):
    # and we'll test all INFO/PASS code-paths for each of the rules:
    def name_test(value, expected):
      assert_name_table_check_result(ttFont, index, name, check, value, expected) #pylint: disable=cell-var-from-loop

    if name.nameID == NameID.POSTSCRIPT_NAME:
      print ("== NameID.POST_SCRIPT_NAME ==")

      print ("Test INFO: May contain only a-zA-Z0-9 characters and an hyphen...")
      # The '@' and '!' chars here are the expected rule violations:
      name_test("B@zinga!", INFO)

      print ("Test PASS: A name with a single hyphen is OK...")
      # A single hypen in the name is OK:
      name_test("Big-Bang", PASS)

      print ("Test INFO: May not contain more than a single hyphen...")
      # The second hyphen char here is the expected rule violation:
      name_test("Big-Bang-Theory", INFO)

      print ("Test INFO: Exceeds max length (29)...")
      name_test("A"*30, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*29, PASS)

    elif name.nameID == NameID.FULL_FONT_NAME:
      print ("== NameID.FULL_FONT_NAME ==")

      print ("Test INFO: Exceeds max length (63)...")
      name_test("A"*64, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*63, PASS)

    elif name.nameID == NameID.FONT_FAMILY_NAME:
      print ("== NameID.FONT_FAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NameID.FONT_SUBFAMILY_NAME:
      print ("== NameID.FONT_SUBFAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
      print ("== NameID.TYPOGRAPHIC_FAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NameID.TYPOGRAPHIC_SUBFAMILY_NAME:
      print ("== NameID.FONT_TYPOGRAPHIC_SUBFAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)


def test_check_name_rfn():
  """ Name table strings must not contain 'Reserved Font Name'. """
  from fontbakery.profiles.name import com_google_fonts_check_name_rfn as check

  test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))

  status, _ = list(check(test_font))[-1]
  assert status == PASS

  test_font["name"].setName("Bla Reserved Font Name", 5, 3, 1, 0x409)
  status, _ = list(check(test_font))[-1]
  assert status == WARN


def test_check_name_postscript_vs_cff():
  from fontbakery.profiles.name import com_adobe_fonts_check_name_postscript_vs_cff as check
  test_font = TTFont()
  test_font['CFF '] = fontTools.ttLib.newTable('CFF ')
  test_font['CFF '].cff.fontNames = ['SomeFontName']
  test_font['name'] = fontTools.ttLib.newTable('name')

  test_font['name'].setName(
    'SomeOtherFontName',
    NameID.POSTSCRIPT_NAME,
    PlatformID.WINDOWS,
    WindowsEncodingID.UNICODE_BMP,
    WIN_ENGLISH_LANG_ID
  )
  status, message = list(check(test_font))[-1]
  assert status == FAIL

  test_font['name'].setName(
    'SomeFontName',
    NameID.POSTSCRIPT_NAME,
    PlatformID.WINDOWS,
    WindowsEncodingID.UNICODE_BMP,
    WIN_ENGLISH_LANG_ID
  )
  status, message = list(check(test_font))[-1]
  assert status == PASS


def test_check_name_postscript_name_consistency():
  from fontbakery.profiles.name import \
    com_adobe_fonts_check_name_postscript_name_consistency as check

  base_path = portable_path("data/test/source-sans-pro/TTF")
  font_path = os.path.join(base_path, 'SourceSansPro-Regular.ttf')
  test_font = TTFont(font_path)

  # SourceSansPro-Regular only has one name ID 6 entry (for Windows),
  # let's add another one for Mac that matches the Windows entry:
  test_font['name'].setName(
    'SourceSansPro-Regular',
    NameID.POSTSCRIPT_NAME,
    PlatformID.MACINTOSH,
    WindowsEncodingID.UNICODE_BMP,
    WIN_ENGLISH_LANG_ID
  )
  status, message = list(check(test_font))[-1]
  assert status == PASS

  # ...now let's change the Mac name ID 6 entry to something else:
  test_font['name'].setName(
    'YetAnotherFontName',
    NameID.POSTSCRIPT_NAME,
    PlatformID.MACINTOSH,
    WindowsEncodingID.UNICODE_BMP,
    WIN_ENGLISH_LANG_ID
  )
  status, message = list(check(test_font))[-1]
  assert status == FAIL


def test_check_family_max_4_fonts_per_family_name():
  from fontbakery.profiles.name import \
    com_adobe_fonts_check_family_max_4_fonts_per_family_name as check

  base_path = portable_path("data/test/source-sans-pro/OTF")

  font_names = [
    'SourceSansPro-Black.otf',
    'SourceSansPro-BlackIt.otf',
    'SourceSansPro-Bold.otf',
    'SourceSansPro-BoldIt.otf',
    'SourceSansPro-ExtraLight.otf',
    'SourceSansPro-ExtraLightIt.otf',
    'SourceSansPro-It.otf',
    'SourceSansPro-Light.otf',
    'SourceSansPro-LightIt.otf',
    'SourceSansPro-Regular.otf',
    'SourceSansPro-Semibold.otf',
    'SourceSansPro-SemiboldIt.otf']

  font_paths = [os.path.join(base_path, n) for n in font_names]

  test_fonts = [TTFont(x) for x in font_paths]

  # try fonts with correct family name grouping
  status, message = list(check(test_fonts))[-1]
  assert status == PASS

  # now set 5 of the fonts to have the same family name
  for font in test_fonts[:5]:
    name_records = font['name'].names
    for name_record in name_records:
      if name_record.nameID == 1:
        # print(repr(name_record.string))
        name_record.string = 'foobar'.encode('utf-16be')

  status, message = list(check(test_fonts))[-1]
  assert status == FAIL
