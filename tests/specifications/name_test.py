import os

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

def test_check_031():
  """ Description strings in the name table
      must not contain copyright info.
  """
  from fontbakery.specifications.name import com_google_fonts_check_031 as check
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # here we add a "Copyright" string to a NAMEID_DESCRIPTION
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
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


def test_check_033():
  """ Checking correctness of monospaced metadata. """
  from fontbakery.specifications.name import com_google_fonts_check_033 as check
  from fontbakery.specifications.shared_conditions import monospace_stats
  from fontbakery.constants import (PANOSE_PROPORTION__ANY,
                                    PANOSE_PROPORTION__NO_FIT,
                                    PANOSE_PROPORTION__OLD_STYLE,
                                    PANOSE_PROPORTION__MODERN,
                                    PANOSE_PROPORTION__EVEN_WIDTH,
                                    PANOSE_PROPORTION__EXTENDED,
                                    PANOSE_PROPORTION__CONDENSED,
                                    PANOSE_PROPORTION__VERY_EXTENDED,
                                    PANOSE_PROPORTION__VERY_CONDENSED,
                                    PANOSE_PROPORTION__MONOSPACED,
                                    IS_FIXED_WIDTH__MONOSPACED,
                                    IS_FIXED_WIDTH__NOT_MONOSPACED)

  # This check has a large number of code-paths
  # We'll make sure to test them all here.
  #
  # --------------------------------------------
  # Starting with non-monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good non-monospace font...')
  # Our reference Mada Regular is a non-monospace font
  # know to have good metadata for this check.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  stats = monospace_stats(ttFont)
  status, message = list(check(ttFont, stats))[-1]
  assert status == PASS and message.code == "good"

  # We'll mark it as monospaced on the post table and make sure it fails:
  print('Test FAIL with a non-monospaced font with bad post.isFixedPitch value ...')
  ttFont["post"].isFixedPitch = IS_FIXED_WIDTH__MONOSPACED
  status, message = list(check(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-post-isFixedPitch"

  # restore good value:
  ttFont["post"].isFixedPitch = IS_FIXED_WIDTH__NOT_MONOSPACED

  # Now we mark it as monospaced on the OS/2 and it should also fail:
  print('Test FAIL with a non-monospaced font with bad OS/2.panose.bProportion value (MONOSPACED) ...')
  ttFont["OS/2"].panose.bProportion = PANOSE_PROPORTION__MONOSPACED
  status, message = list(check(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-panose-proportion"

  # --------------------------------------------
  # And now we test the monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good monospaced font...')
  # Our reference OverpassMono Regular is know to be
  # a monospaced font with good metadata here.
  ttFont = TTFont("data/test/overpassmono/OverpassMono-Regular.ttf")
  stats = monospace_stats(ttFont)
  status, message = list(check(ttFont, stats))[-1]
  # WARN is emitted when there's at least one outlier.
  # I don't see a good reason to be picky and also test that one separately here...
  assert (status == WARN and message.code == "mono-outliers") or \
         (status == PASS and message.code == "mono-good")

  # Let's incorrectly mark it as a non-monospaced on the post table and it should fail:
  print('Test FAIL with a monospaced font with bad post.isFixedPitch value ...')
  ttFont["post"].isFixedPitch = IS_FIXED_WIDTH__NOT_MONOSPACED
  # here we search for the expected FAIL among all results
  # instead of simply looking at the last one
  # because we may also get an outliers WARN in some cases:
  results = list(check(ttFont, stats))
  assert results_contain(results, FAIL, "mono-bad-post-isFixedPitch")

  # There are several bad panose proportion values for a monospaced font.
  # Only PANOSE_PROPORTION__MONOSPACED would be valid.
  # So we'll try all the bad ones here to make sure all of them emit a FAIL:
  bad_monospaced_panose_values = [
    PANOSE_PROPORTION__ANY,
    PANOSE_PROPORTION__NO_FIT,
    PANOSE_PROPORTION__OLD_STYLE,
    PANOSE_PROPORTION__MODERN,
    PANOSE_PROPORTION__EVEN_WIDTH,
    PANOSE_PROPORTION__EXTENDED,
    PANOSE_PROPORTION__CONDENSED,
    PANOSE_PROPORTION__VERY_EXTENDED,
    PANOSE_PROPORTION__VERY_CONDENSED,
  ]
  good_value = ttFont["OS/2"].panose.bProportion
  for bad_value in bad_monospaced_panose_values:
    print(f'Test FAIL with a monospaced font with bad OS/2.panose.bProportion value ({bad_value}) ...')
    ttFont["OS/2"].panose.bProportion = bad_value
    # again, we search the expected FAIL because we may algo get an outliers WARN here:
    results = list(check(ttFont, stats))
    assert results_contain(results, FAIL, "mono-bad-panose-proportion")


def test_check_057():
  """ Name table entries should not contain line-breaks. """
  from fontbakery.specifications.name import com_google_fonts_check_057 as check

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print ("Test FAIL with name entries containing a linebreak...")
  for i in range(len(ttFont["name"].names)):
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    encoding = ttFont["name"].names[i].getEncoding()
    ttFont["name"].names[i].string = "bad\nstring".encode(encoding)
    status, message = list(check(ttFont))[-1]
    assert status == FAIL


def test_check_068():
  """ Does full font name begin with the font family name ? """
  from fontbakery.specifications.name import com_google_fonts_check_068 as check
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME)
  # Our reference Mada Regular is known to be good
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # alter the full-font-name prepending a bad prefix:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      ttFont["name"].names[i].string = "bad-prefix".encode(name.getEncoding())

  # and make sure the check FAILs:
  print ("Test FAIL with a font in which the family name begins with a digit...")
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "does-not"

  print ("Test FAIL with no FULL_FONT_NAME entries...")
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      del ttFont["name"].names[i]
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "no-full-font-name"

  print ("Test FAIL with no FONT_FAMILY_NAME entries...")
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
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


def test_check_071():
  """ Font follows the family naming recommendations ? """
  from fontbakery.specifications.name import com_google_fonts_check_071 as check
  from fontbakery.constants import (NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  # Our reference Mada Medium is known to be good
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # We'll test rule violations in all entries one-by-one
  for index, name in enumerate(ttFont["name"].names):
    # and we'll test all INFO/PASS code-paths for each of the rules:
    def name_test(value, expected):
      assert_name_table_check_result(ttFont, index, name, check, value, expected) #pylint: disable=cell-var-from-loop

    if name.nameID == NAMEID_POSTSCRIPT_NAME:
      print ("== NAMEID_POST_SCRIPT_NAME ==")

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

    elif name.nameID == NAMEID_FULL_FONT_NAME:
      print ("== NAMEID_FULL_FONT_NAME ==")

      print ("Test INFO: Exceeds max length (63)...")
      name_test("A"*64, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*63, PASS)

    elif name.nameID == NAMEID_FONT_FAMILY_NAME:
      print ("== NAMEID_FONT_FAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NAMEID_FONT_SUBFAMILY_NAME:
      print ("== NAMEID_FONT_SUBFAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NAMEID_TYPOGRAPHIC_FAMILY_NAME:
      print ("== NAMEID_TYPOGRAPHIC_FAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)

    elif name.nameID == NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME:
      print ("== NAMEID_FONT_TYPOGRAPHIC_SUBFAMILY_NAME ==")

      print ("Test INFO: Exceeds max length (31)...")
      name_test("A"*32, INFO)

      print ("Test PASS: Does not exceeds max length...")
      name_test("A"*31, PASS)


def test_check_152():
  """ Name table strings must not contain 'Reserved Font Name'. """
  from fontbakery.specifications.name import com_google_fonts_check_152 as check

  test_font = TTFont(
      os.path.join("data", "test", "nunito", "Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  test_font["name"].setName("Bla Reserved Font Name", 5, 3, 1, 0x409)
  status, _ = list(check(test_font))[-1]
  assert status == WARN


def test_check_163():
  """ Check font name is the same as family name. """
  from fontbakery.specifications.name import com_google_fonts_check_163 as check
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME)
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Then we emit a WARNing with the long family/style names
  # that were used as an example on the glyphs tutorial
  # (at https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances):
  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      ttFont["name"].names[index].string = "ImpossibleFamilyNameFont".encode(name.getEncoding())
      break

  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_SUBFAMILY_NAME:
      ttFont["name"].names[index].string = "WithAVeryLongStyleName".encode(name.getEncoding())
      break

  print ("Test WARN with a bad font...")
  status, message = list(check(ttFont))[-1]
  assert status == WARN
