import pytest
import os

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

@pytest.fixture
def cabin_ttFonts():
  return [TTFont(path) for path in cabin_fonts]


@pytest.fixture
def montserrat_ttFonts():
  paths = [
    "data/test/montserrat/Montserrat-Black.ttf",
    "data/test/montserrat/Montserrat-BlackItalic.ttf",
    "data/test/montserrat/Montserrat-Bold.ttf",
    "data/test/montserrat/Montserrat-BoldItalic.ttf",
    "data/test/montserrat/Montserrat-ExtraBold.ttf",
    "data/test/montserrat/Montserrat-ExtraBoldItalic.ttf",
    "data/test/montserrat/Montserrat-ExtraLight.ttf",
    "data/test/montserrat/Montserrat-ExtraLightItalic.ttf",
    "data/test/montserrat/Montserrat-Italic.ttf",
    "data/test/montserrat/Montserrat-Light.ttf",
    "data/test/montserrat/Montserrat-LightItalic.ttf",
    "data/test/montserrat/Montserrat-Medium.ttf",
    "data/test/montserrat/Montserrat-MediumItalic.ttf",
    "data/test/montserrat/Montserrat-Regular.ttf",
    "data/test/montserrat/Montserrat-SemiBold.ttf",
    "data/test/montserrat/Montserrat-SemiBoldItalic.ttf",
    "data/test/montserrat/Montserrat-Thin.ttf",
    "data/test/montserrat/Montserrat-ThinItalic.ttf"
  ]
  return [TTFont(path) for path in paths]


def change_name_table_id(ttFont, nameID, newEntryString, platEncID=0):
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID and nameRecord.platEncID == platEncID:
      ttFont['name'].names[i].string = newEntryString

def delete_name_table_id(ttFont, nameID):
  delete = []
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID:
      delete.append(i)
  for i in sorted(delete, reverse=True):
    del(ttFont['name'].names[i])

@pytest.fixture
def cabin_regular_path():
  # FIXME: find absolute path via the path of this module
  return 'data/test/cabin/Cabin-Regular.ttf'


def test_example_checkrunner_based(cabin_regular_path):
  """ This is just an example test. We'll probably need something like
      this setup in a checkrunner_test.py testsuite.
      Leave it here for the moment until we implemented a real case.

      This test is run via the checkRunner and demonstrate how to get
      (mutable) objects from the conditions cache and change them.

      NOTE: the actual fontbakery checks of conditions should never
      change a condition object.
  """
  from fontbakery.checkrunner import CheckRunner
  from fontbakery.specifications.googlefonts import specification
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION
  values = dict(fonts=[cabin_regular_path])
  runner = CheckRunner(specification, values, explicit_checks=['com.google.fonts/check/029'])

  print('Test PASS ...')
  # run
  for status, message, _ in runner.run():
    if status in check_statuses:
      last_check_message = message
    if status == ENDCHECK:
      assert message == PASS
      break

  # we could also reuse the `iterargs` that was assigned in the previous
  # for loop, but this here is more explicit
  iterargs = (('font', 0),)
  ttFont = runner.get('ttFont', iterargs)

  print('Test failing entry ...')
  # prepare
  change_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION, 'failing entry')
  # run
  for status, message, _ in runner.run():
    if status in check_statuses:
      last_check_message = message
    if status == ENDCHECK:
      assert message == FAIL and last_check_message.code == 'wrong'
      break

  print('Test missing entry ...')
  # prepare
  delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
  # run
  for status, message, _ in runner.run():
    if status in check_statuses:
      last_check_message = message
    if status == ENDCHECK:
      assert message == FAIL and last_check_message.code == 'missing'
      break


def test_check_001():
  """ Files are named canonically. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_001 as check
  canonical_names = [
    "data/test/montserrat/Montserrat-Thin.ttf",
    "data/test/montserrat/Montserrat-ExtraLight.ttf",
    "data/test/montserrat/Montserrat-Light.ttf",
    "data/test/montserrat/Montserrat-Regular.ttf",
    "data/test/montserrat/Montserrat-Medium.ttf",
    "data/test/montserrat/Montserrat-SemiBold.ttf",
    "data/test/montserrat/Montserrat-Bold.ttf",
    "data/test/montserrat/Montserrat-ExtraBold.ttf",
    "data/test/montserrat/Montserrat-Black.ttf",
    "data/test/montserrat/Montserrat-ThinItalic.ttf",
    "data/test/montserrat/Montserrat-ExtraLightItalic.ttf",
    "data/test/montserrat/Montserrat-LightItalic.ttf",
    "data/test/montserrat/Montserrat-Italic.ttf",
    "data/test/montserrat/Montserrat-MediumItalic.ttf",
    "data/test/montserrat/Montserrat-SemiBoldItalic.ttf",
    "data/test/montserrat/Montserrat-BoldItalic.ttf",
    "data/test/montserrat/Montserrat-ExtraBoldItalic.ttf",
    "data/test/montserrat/Montserrat-BlackItalic.ttf",
    "data/test/cabinvfbeta/Cabin-Italic-VF.ttf",
    "data/test/cabinvfbeta/Cabin-Roman-VF.ttf",
    "data/test/cabinvfbeta/Cabin-VF.ttf"
  ]
  non_canonical_names = [
    "data/test/montserrat/Montserrat/Montserrat.ttf",
    "data/test/montserrat/Montserrat-semibold.ttf",
    "data/test/cabinvfbeta/CabinVFBeta-Italic.ttf",
    "data/test/cabinvfbeta/CabinVFBeta.ttf",
  ]

  for canonical in canonical_names:
    print(f'Test PASS with "{canonical}" ...')
    status, message = list(check(canonical))[-1]
    assert status == PASS

  for non_canonical in non_canonical_names:
    print(f'Test FAIL with "{non_canonical}" ...')
    status, message = list(check(non_canonical))[-1]
    assert status == FAIL


def test_check_003():
  """ Does DESCRIPTION file contain broken links ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_003 as check,
                                                     description,
                                                     descfile)
  good_desc = description(descfile("data/test/cabin/"))
  print('Test PASS with description file that has no links...')
  status, message = list(check(good_desc))[-1]
  assert status == PASS

  good_desc += ("<a href='http://example.com'>Good Link</a>"
                "<a href='http://fonts.google.com'>Another Good One</a>")
  print('Test PASS with description file that has good links...')
  status, message = list(check(good_desc))[-1]
  assert status == PASS

  good_desc += "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
  print('Test FAIL with a description file containing a mailto links...')
  status, message = list(check(good_desc))[-1]
  assert status == PASS

  bad_desc = good_desc + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
  print('Test FAIL with a description file containing a known-bad URL...')
  status, message = list(check(bad_desc))[-1]
  assert status == FAIL


def test_check_004():
  """ DESCRIPTION file is a propper HTML snippet ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_004 as check,
                                                     descfile, description)
  good_descfile = descfile("data/test/nunito/")
  good_desc = description(good_descfile)
  print('Test PASS with description file that contains a good HTML snippet...')
  status, message = list(check(good_descfile, good_desc))[-1]
  assert status == PASS

  bad_descfile = "data/test/cabin/FONTLOG.txt" # :-)
  bad_desc = description(bad_descfile)
  print('Test FAIL with a known-bad file (a txt file without HTML snippets)...')
  status, message = list(check(bad_descfile, bad_desc))[-1]
  assert status == FAIL


def test_check_005():
  """ DESCRIPTION.en_us.html must have more than 200 bytes. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_005 as check

  bad_length = 'a' * 199
  print('Test FAIL with 199-byte buffer...')
  status, message = list(check(bad_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 200
  print('Test FAIL with 200-byte buffer...')
  status, message = list(check(bad_length))[-1]
  assert status == FAIL

  good_length = 'a' * 201
  print('Test PASS with 201-byte buffer...')
  status, message = list(check(good_length))[-1]
  assert status == PASS


def test_check_006():
  """ DESCRIPTION.en_us.html must have less than 1000 bytes. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_006 as check

  bad_length = 'a' * 1001
  print('Test FAIL with 1001-byte buffer...')
  status, message = list(check(bad_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 1000
  print('Test FAIL with 1000-byte buffer...')
  status, message = list(check(bad_length))[-1]
  assert status == FAIL

  good_length = 'a' * 999
  print('Test PASS with 999-byte buffer...')
  status, message = list(check(good_length))[-1]
  assert status == PASS


def test_check_007():
  """ Font designer field in METADATA.pb must not be 'unknown'. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_007 as check,
                                                     family_metadata)
  good = family_metadata("data/test/merriweather/")
  print('Test PASS with a good METADATA.pb file...')
  status, message = list(check(good))[-1]
  assert status == PASS

  bad = family_metadata("data/test/merriweather/")
  bad.designer = "unknown"
  print('Test FAIL with a bad METADATA.pb file...')
  status, message = list(check(bad))[-1]
  assert status == FAIL


def test_check_011(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal numbers of glyphs ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_011 as check

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs.
  status, message = list(check(mada_ttFonts))[-1]
  assert status == FAIL


def test_check_012(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal glyph names ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_012 as check

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs (that extra glyph
  # causes the check to fail).
  status, message = list(check(mada_ttFonts))[-1]
  assert status == FAIL


def test_check_016():
  """ Checking OS/2 fsType """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_016 as check

  print('Test PASS with good font without DRM.')
  # our reference Cabin family is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # modify the OS/2 fsType value to something different than zero:
  ttFont['OS/2'].fsType = 1

  print('Test FAIL with fonts that enable DRM restrictions via non-zero fsType bits.')
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_018():
  """ Checking OS/2 achVendID """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_018 as check,
                                                     registered_vendor_ids)
  registered_ids = registered_vendor_ids()

  # Let's start with our reference Cabin Regular
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")

  print('Test FAIL with bad vid.')
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  for bad_vid in bad_vids:
    ttFont['OS/2'].achVendID = bad_vid
    status, message = list(check(ttFont, registered_ids))[-1]
    assert status == FAIL and message.code == "bad"

  print('Test FAIL with font missing vendor id info.')
  ttFont['OS/2'].achVendID = None
  status, message = list(check(ttFont, registered_ids))[-1]
  assert status == FAIL and message.code == "not set"

  print('Test WARN with unknwon vendor id.')
  ttFont['OS/2'].achVendID = "????"
  status, message = list(check(ttFont, registered_ids))[-1]
  assert status == WARN and message.code == "unknown"

  print('Test PASS with good font.')
  # we now change the fields into a known good vendor id:
  ttFont['OS/2'].achVendID = "APPL"
  status, message = list(check(ttFont, registered_ids))[-1]
  assert status == PASS

  print('As of July 2018, MLAG: "Michael LaGattuta" must show up in the list...')
  assert "MLAG" in registered_ids


def test_check_019():
  """ Substitute copyright, registered and trademark
      symbols in name table entries. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_019 as check

  print('Test FAIL with a bad font...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == FAIL

  print('Test PASS with a good font...')
  # Our reference Cabin Regular is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == PASS


def test_check_020():
  """ Checking OS/2 usWeightClass. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_020 as check,
                                                     style)
  # Our reference Mada Regular is know to be bad here.
  font = "data/test/mada/Mada-Regular.ttf"
  print(f"Test FAIL with bad font '{font}' ...")
  ttFont = TTFont(font)
  status, message = list(check(font, ttFont, style(font)))[-1]
  assert status == FAIL

  # All fonts in our reference Cabin family are know to be good here.
  for font in cabin_fonts:
    print(f"Test PASS with good font '{font}' ...")
    ttFont = TTFont(font)
    status, message = list(check(font, ttFont, style(font)))[-1]
    assert status == PASS

  font = "data/test/montserrat/Montserrat-Thin.ttf"
  ttFont = TTFont(font)
  ttFont["OS/2"].usWeightClass = 100
  print("Test WARN with a Thin:100 TTF...")
  status, message = list(check(font, ttFont, style(font)))[-1]
  assert status == WARN

  font = "data/test/montserrat/Montserrat-ExtraLight.ttf"
  ttFont = TTFont(font)
  ttFont["OS/2"].usWeightClass = 200
  print("Test WARN with an ExtraLight:200 TTF...")
  status, message = list(check(font, ttFont, style(font)))[-1]
  assert status == WARN

  # TODO: test FAIL with a Thin:100 OTF
  # TODO: test FAIL with an ExtraLight:200 OTF


def test_check_028():
  """ Check font project has a license. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_028 as check,
                                                     licenses)
  print('Test FAIL with multiple licenses...')
  detected_licenses = licenses("data/test/028/multiple/")
  status, message = list(check(detected_licenses))[-1]
  assert status == FAIL and message.code == "multiple"

  print('Test FAIL with no license...')
  detected_licenses = licenses("data/test/028/none/")
  status, message = list(check(detected_licenses))[-1]
  assert status == FAIL and message.code == "none"

  print('Test PASS with a single OFL license...')
  detected_licenses = licenses("data/test/028/pass_ofl/")
  status, message = list(check(detected_licenses))[-1]
  assert status == PASS

  print('Test PASS with a single Apache license...')
  detected_licenses = licenses("data/test/028/pass_apache/")
  status, message = list(check(detected_licenses))[-1]
  assert status == PASS


def test_check_029(mada_ttFonts):
  """ Check copyright namerecords match license file. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_029 as check
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION

  # Our reference Mada family has its copyright name records properly set
  # identifying it as being licensed under the Open Font License
  license = 'OFL.txt'
  wrong_license = 'LICENSE.txt' # Apache

  print('Test PASS with good fonts ...')
  for ttFont in mada_ttFonts:
    status, message = list(check(ttFont, license))[-1]
    assert status == PASS

  print('Test FAIL with wrong entry values ...')
  for ttFont in mada_ttFonts:
    status, message = list(check(ttFont, wrong_license))[-1]
    assert status == FAIL and message.code == 'wrong'

  print('Test FAIL with missing copyright namerecords ...')
  for ttFont in mada_ttFonts:
    delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
    status, message = list(check(ttFont, license))[-1]
    assert status == FAIL and message.code == 'missing'


def NOT_IMPLEMENTED_test_check_030():
  """ License URL matches License text on name table? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_030 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, code="ufl"
  # - FAIL, code="licensing-inconsistency"
  # - FAIL, code="no-license-found"
  # - FAIL, code="bad-entries"
  # - PASS


def test_check_032():
  """ Description strings in the name table
      must not exceed 200 characters.
  """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_032 as check
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Here we add strings to NAMEID_DESCRIPTION with exactly 100 chars,
  # so it should still PASS:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 200).encode(name.getEncoding())

  print('Test PASS with a 200 char string...')
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # And here we make the strings longer than 200 chars
  # in order to make the check emit a WARN:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 201).encode(name.getEncoding())

  print('Test WARN with a too long description string...')
  status, message = list(check(ttFont))[-1]
  assert status == WARN


def test_check_054():
  """ Show hinting filesize impact. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_054 as check,
                                                     ttfautohint_stats)
  font = "data/test/mada/Mada-Regular.ttf"

  print('Test this check always emits an INFO result...')
  status, message = list(check(TTFont(font), ttfautohint_stats(font)))[-1]
  assert status == INFO


def test_check_055():
  """ Version format is correct in 'name' table ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_055 as check
  from fontbakery.constants import NAMEID_VERSION_STRING

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # then we introduce bad strings in all version-string entries:
  print ("Test FAIL with bad version format in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      invalid = "invalid-version-string".encode(name.getEncoding())
      ttFont["name"].names[i].string = invalid
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "bad-version-strings"

  # and finally we remove all version-string entries:
  print ("Test FAIL with font lacking version string entries in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      del ttFont["name"].names[i]
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "no-version-string"


def NOT_IMPLEMENTED_test_check_056():
  """ Font has old ttfautohint applied? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_056 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, code="lacks-version-strings"
  # - INFO, "Could not detect which version of ttfautohint was used in this font."
  # - WARN, "detected an old ttfa version"
  # - PASS
  # - FAIL, code="parse-error"


def NOT_IMPLEMENTED_test_check_has_ttfautohint_params():
  """ Font has ttfautohint params? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_has_ttfautohint_params as check
  # TODO: Implement-me!


def test_check_061():
  """ EPAR table present in font ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_061 as check

  # Our reference Mada Regular lacks an EPAR table:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must emit an INFO message inviting the designers
  # to learn more about it:
  print ("Test INFO with a font lacking an EPAR table...")
  status, message = list(check(ttFont))[-1]
  assert status == INFO

  print ("Test PASS with a good font...")
  # add a fake EPAR table to validate the PASS code-path:
  ttFont["EPAR"] = "foo"
  status, message = list(check(ttFont))[-1]
  assert status == PASS


def NOT_IMPLEMENTED_test_check_062():
  """ Is GASP table correctly set? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_062 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "GASP.gaspRange method value have wrong type."
  # - FAIL, "GASP does not have 0xFFFF gaspRange."
  # - FAIL, "GASP should only have 0xFFFF gaspRange, but another one was also found."
  # - WARN, "All flags in GASP range 0xFFFF (i.e. all font sizes) must be set to 1"
  # - PASS, "GASP table is correctly set."
  # - FAIL, "Font is missing the GASP table."


def test_check_067():
  """ Make sure family name does not begin with a digit. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_067 as check
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME

  # Our reference Mada Regular is known to be good
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # alter the family-name prepending a digit:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      ttFont["name"].names[i].string = "1badname".encode(name.getEncoding())

  # and make sure the check FAILs:
  print ("Test FAIL with a font in which the family name begins with a digit...")
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_070():
  """ Font has all expected currency sign characters ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_070 as check

  # Our reference Mada Medium is known to be good
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # And FamilySans Regular is known to be bad
  ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")

  # So it must FAIL the check:
  print ("Test FAIL with a bad font...")
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_074():
  """ Are there non-ASCII characters in ASCII-only NAME table entries? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_074 as check
  from fontbakery.constants import (NAMEID_COPYRIGHT_NOTICE,
                                    NAMEID_POSTSCRIPT_NAME)

  # Our reference Merriweather Regular is known to be good
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  #  The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
  #  For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that
  #  string should be the same in CFF fonts which also have this
  #  requirement in the OpenType spec.

  # Let's check detection of both. First nameId 6:
  print ("Test FAIL with non-ascii on nameID 6 entry (Postscript name)...")
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_POSTSCRIPT_NAME:
      ttFont['name'].names[i].string = "Infração".encode(encoding="utf-8")
  results = list(check(ttFont))
  info_status, message = results[-2]
  final_status, message = results[-1]
  assert info_status == INFO
  assert final_status == FAIL

  # Then reload the good font
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")

  # And check detection of a problem on nameId 0:
  print ("Test FAIL with non-ascii on nameID 0 entry (Copyright notice)...")
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = "Infração".encode(encoding="utf-8")
  results = list(check(ttFont))
  info_status, message = results[-2]
  final_status, message = results[-1]
  assert info_status == INFO
  assert final_status == FAIL

  # Reload the good font once more:
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")

  #  Note:
  #  A common place where we find non-ASCII strings is on name table
  #  entries with NameID > 18, which are expressly for localising
  #  the ASCII-only IDs into Hindi / Arabic / etc.

  # Let's check a good case of a non-ascii on the name table then!
  # Choose an arbitrary name entry to mess up with:
  index = 5

  print ("Test PASS with non-ascii on entries with nameId > 18...")
  ttFont['name'].names[index].nameID = 19
  ttFont['name'].names[index].string = "Fantástico!".encode(encoding="utf-8")
  status, message = list(check(ttFont))[-1]
  assert status == PASS


def test_check_081():
  """ METADATA.pb: Fontfamily is listed on Google Fonts API? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_081 as check,
                                                     listed_on_gfonts_api,
                                                     family_metadata)

  print ("Test WARN with a family that is not listed on Google Fonts...")
  # Our reference FamilySans family is a just a generic example
  # and thus is not really hosted (nor will ever be hosted) at Google Fonts servers:
  family_directory = "data/test/familysans/"
  listed = listed_on_gfonts_api(family_metadata(family_directory))
  # For that reason, we expect to get a WARN in this case:
  status, message = list(check(listed))[-1]
  assert status == WARN

  print ("Test PASS with a family that is available...")
  # Our reference Merriweather family is available on the Google Fonts collection:
  family_directory = "data/test/merriweather/"
  listed = listed_on_gfonts_api(family_metadata(family_directory))
  # So it must PASS:
  status, message = list(check(listed))[-1]
  assert status == PASS


# FIXME: This check is currently disabled:
# - Review and re-enable.
# - Implement the test.
def NOT_IMPLEMENTED_test_check_082():
  """ METADATA.pb: Designer exists in Google Fonts profiles.csv? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_082 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # ...


def test_check_083():
  """ METADATA.pb: check if fonts field only has unique "full_name" values. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_083 as check,
                                                     family_metadata)
  print ("Test PASS with a good family...")
  # Our reference FamilySans family is good:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)
  status, message = list(check(md))[-1]
  assert status == PASS

  # then duplicate a full_name entry to make it FAIL:
  md.fonts[0].full_name = md.fonts[1].full_name
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_084():
  """ METADATA.pb: check if fonts field only contains unique style:weight pairs. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_084 as check,
                                                     family_metadata)
  print ("Test PASS with a good family...")
  # Our reference FamilySans family is good:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)
  status, message = list(check(md))[-1]
  assert status == PASS

  # then duplicate a pair of style & weight entries to make it FAIL:
  md.fonts[0].style = md.fonts[1].style
  md.fonts[0].weight = md.fonts[1].weight
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_085():
  """ METADATA.pb license is "APACHE2", "UFL" or "OFL"? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_085 as check,
                                                     family_directory,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  fonts = ["data/test/familysans/FamilySans-Regular.ttf"]
  md = family_metadata(family_directory(fonts))

  good_licenses = ["APACHE2", "UFL", "OFL"]
  some_bad_values = ["APACHE", "Apache", "Ufl", "Ofl", "Open Font License"]

  for good in good_licenses:
    print(f"Test PASS: {good}")
    md.license = good
    status, message = list(check(md))[-1]
    assert status == PASS

  for bad in some_bad_values:
    print(f"Test FAIL: {bad}")
    md.license = bad
    status, message = list(check(md))[-1]
    assert status == FAIL


def test_check_086():
  """ METADATA.pb should contain at least "menu" and "latin" subsets. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_086 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  good_cases = [
    ["menu", "latin"],
    ["menu", "cyrillic", "latin"],
  ]

  bad_cases = [
    ["menu"],
    ["latin"],
    [""],
    ["latin", "cyrillyc"],
    ["khmer"]
  ]

  for good in good_cases:
    print(f"Test PASS: {good}")
    del md.subsets[:]
    md.subsets.extend(good)
    status, message = list(check(md))[-1]
    assert status == PASS

  for bad in bad_cases:
    print(f"Test FAIL: {bad}")
    del md.subsets[:]
    md.subsets.extend(bad)
    status, message = list(check(md))[-1]
    assert status == FAIL


def test_check_087():
  """ METADATA.pb subsets should be alphabetically ordered. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_087 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  good_cases = [
    ["latin", "menu"],
    ["cyrillic", "latin", "menu"],
    ["cyrillic", "khmer", "latin", "menu"],
  ]

  bad_cases = [
    ["menu", "latin"],
    ["latin", "cyrillic", "menu"],
    ["cyrillic", "menu", "khmer", "latin"],
  ]

  for good in good_cases:
    print(f"Test PASS: {good}")
    del md.subsets[:]
    md.subsets.extend(good)
    status, message = list(check(md))[-1]
    assert status == PASS

  for bad in bad_cases:
    print(f"Test FAIL: {bad}")
    del md.subsets[:]
    md.subsets.extend(bad)
    status, message = list(check(md))[-1]
    assert status == FAIL


def test_check_088():
  """ METADATA.pb: Copyright notice is the same in all fonts? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_088 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  # We know its copyright notices are consistent, so the check should PASS:
  print("Test PASS: Consistent copyright notices on FamilySans...")
  status, message = list(check(md))[-1]
  assert status == PASS

  # Now we make them diverge:
  md.fonts[1].copyright = md.fonts[0].copyright + " arbitrary suffix!" # to make it different

  # And now the check must FAIL:
  print("Test FAIL: With diverging copyright notice strings...")
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_089():
  """ Check that METADATA.pb family values are all the same. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_089 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  # We know its family name entries on METADATA.pb are consistent, so the check should PASS:
  print("Test PASS: Consistent family name...")
  status, message = list(check(md))[-1]
  assert status == PASS

  # Now we make them diverge:
  md.fonts[1].name = md.fonts[0].name + " arbitrary suffix!" # to make it different

  # And now the check must FAIL:
  print("Test FAIL: With diverging Family name metadata entries...")
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_090():
  """ METADATA.pb: According Google Fonts standards, families should have a Regular style. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_090 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  # We know that Family Sans has got a regular declares in its METADATA.pb file, so the check should PASS:
  print("Test PASS: Family Sans has regular style...")
  status, message = list(check(md))[-1]
  assert status == PASS

  # We remove the regular:
  for i, font in enumerate(md.fonts):
    if font.filename == "FamilySans-Regular.ttf":
      del md.fonts[i]

  # and make sure the check now FAILs:
  print("Test FAIL: METADATA.pb without a regular...")
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_091():
  """ METADATA.pb: Regular should be 400. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_091 as check,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  family_directory = "data/test/familysans/"
  md = family_metadata(family_directory)

  # We know that Family Sans' Regular has a weight value equal to 400, so the check should PASS:
  print("Test PASS: Family Sans has regular=400...")
  status, message = list(check(md))[-1]
  assert status == PASS

  # The we change the value for its regular:
  for i, font in enumerate(md.fonts):
    if font.filename == "FamilySans-Regular.ttf":
      md.fonts[i].weight = 500

  # and make sure the check now FAILs:
  print("Test FAIL: METADATA.pb without a regular...")
  status, message = list(check(md))[-1]
  assert status == FAIL


def test_check_092():
  """ Checks METADATA.pb font.name field matches
      family name declared on the name table. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_092 as check,
                                                     font_metadata,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  font = "data/test/familysans/FamilySans-Regular.ttf"
  family_directory = "data/test/familysans/"
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, font)
  ttFont = TTFont(font)

  # We know that Family Sans Regular is good here:
  print("Test PASS...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # Then cause it to fail:
  font_meta.name = "Foo"
  print("Test FAIL...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "mismatch"

  # TODO: the failure-mode below seems more generic than the scope
  #       of this individual check. This could become a check by itself!
  #
  # code-paths:
  # - FAIL code="missing", "Font lacks a FONT_FAMILY_NAME entry"


def test_check_093():
  """ Checks METADATA.pb font.post_script_name matches
      postscript name declared on the name table. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_093 as check,
                                                     font_metadata,
                                                     family_metadata)

  # Let's start with the METADATA.pb file from our reference FamilySans family:
  font = "data/test/familysans/FamilySans-Regular.ttf"
  family_directory = "data/test/familysans/"
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, font)
  ttFont = TTFont(font)

  # We know that Family Sans Regular is good here:
  print("Test PASS...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # Then cause it to fail:
  font_meta.post_script_name = "Foo"
  print("Test FAIL...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "mismatch"

  # TODO: the failure-mode below seems more generic than the scope
  #       of this individual check. This could become a check by itself!
  #
  # code-paths:
  # - FAIL code="missing", "Font lacks a POSTSCRIPT_NAME"


def test_check_094():
  """ METADATA.pb font.fullname value matches fullname declared on the name table ? """
  from fontbakery.specifications.googlefonts import font_metadata, family_metadata
  from fontbakery.specifications.googlefonts import com_google_fonts_check_094 as check
  from fontbakery.constants import NAMEID_FULL_FONT_NAME
  import os

  # Our reference Merriweather-Regular is know to be good here
  font = "data/test/merriweather/Merriweather-Regular.ttf"
  family_directory = os.path.dirname(font)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, font)
  ttFont = TTFont(font)

  print('Test PASS with a good font...')
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  print('Test FAIL with mismatching fullname values...')
  good = font_meta.full_name
  # here we change the font.fullname on the METADATA.pb
  # to introduce a "mismatch" error condition:
  font_meta.full_name = good + "bad-suffix"
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "mismatch"

  # and restore the good value prior to the next test case:
  font_meta.full_name = good

  print('Test FAIL when a font lacks FULL_FONT_NAME entries in its name table...')
  # And here we remove all FULL_FONT_NAME entries
  # in order to get a "lacks-entry" error condition:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      del ttFont["name"].names[i]
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "lacks-entry"


def test_check_095():
  """ METADATA.pb font.name value should be same as the family name declared on the name table. """
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_095 as check,
                                                     family_metadata,
                                                     font_metadata,
                                                     style)
  print('Test PASS with a good font...')
  # Our reference Merriweather-Regular is know to have good fullname metadata
  font = "data/test/merriweather/Merriweather-Regular.ttf"
  ttFont = TTFont(font)
  family_directory = os.path.dirname(font)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, font)
  font_style = style(font)
  status, message = list(check(ttFont, font_style, font_meta))[-1]
  assert status == PASS

  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      good = name.string.decode(name.getEncoding()) # keep a copy of the good value
      print("Test FAIL with a bad FULL_FONT_NAME entry...")
      ttFont["name"].names[i].string = (good + "bad-suffix").encode(name.getEncoding())
      status, message = list(check(ttFont, font_style, font_meta))[-1]
      assert status == FAIL
      ttFont["name"].names[i].string = good # restore good value


def test_check_096():
  """ METADATA.pb family.full_name and family.post_script_name
      fields have equivalent values ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_096 as check,
                                                     font_metadata,
                                                     family_metadata)

  regular_font = "data/test/merriweather/Merriweather-Regular.ttf"
  lightitalic_font = "data/test/merriweather/Merriweather-LightItalic.ttf"
  family_meta = family_metadata("data/test/merriweather/")

  regular_meta = font_metadata(family_meta, regular_font)
  lightitalic_meta = font_metadata(family_meta, lightitalic_font)

  print('Test PASS with good entries (Merriweather-LightItalic)...')
  # Note:
  #       post_script_name: "Merriweather-LightItalic"
  #       full_name:        "Merriweather Light Italic"
  status, message = list(check(lightitalic_meta))[-1]
  assert status == PASS


  # TODO: Verify why/whether "Regular" cannot be omited on font.full_name
  #       There's some relevant info at:
  #       https://github.com/googlefonts/fontbakery/issues/1517
  #
  # FIXME: com.google.fonts/check/094 ties the full_name values from the
  #        METADATA.pb file and the internal name table entry (FULL_FONT_NAME)
  #        to be strictly identical. So it seems that the test below is
  #        actually wrong (as well as the current implementation):
  #
  print('Test FAIL with bad entries (Merriweather-Regular)...')
  # Note:
  #       post_script_name: "Merriweather-Regular"
  #       full_name:        "Merriweather"
  status, message = list(check(regular_meta))[-1]
  assert status == FAIL


  # fix the regular metadata:
  regular_meta.full_name = "Merriweather Regular"


  print('Test PASS with good entries (Merriweather-Regular after full_name fix)...')
  # Note:
  #       post_script_name: "Merriweather-Regular"
  #       full_name:        "Merriweather Regular"
  status, message = list(check(regular_meta))[-1]
  assert status == PASS


  # introduce an error in the metadata:
  regular_meta.full_name = "MistakenFont Regular"


  print('Test FAIL with a mismatch...')
  # Note:
  #       post_script_name: "Merriweather-Regular"
  #       full_name:        "MistakenFont Regular"
  status, message = list(check(regular_meta))[-1]
  assert status == FAIL


def NOT_IMPLEMENTED_test_check_097():
  """ METADATA.pb family.filename and family.post_script_name
      fields have equivalent values? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_097 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "METADATA.pb filename does not match post_script_name"
  # - PASS


MONTSERRAT_RIBBI = [
  "data/test/montserrat/Montserrat-Regular.ttf",
  "data/test/montserrat/Montserrat-Italic.ttf",
  "data/test/montserrat/Montserrat-Bold.ttf",
  "data/test/montserrat/Montserrat-BoldItalic.ttf"
]
MONTSERRAT_NON_RIBBI = [
  "data/test/montserrat/Montserrat-BlackItalic.ttf",
  "data/test/montserrat/Montserrat-Black.ttf",
  "data/test/montserrat/Montserrat-ExtraBoldItalic.ttf",
  "data/test/montserrat/Montserrat-ExtraBold.ttf",
  "data/test/montserrat/Montserrat-ExtraLightItalic.ttf",
  "data/test/montserrat/Montserrat-ExtraLight.ttf",
  "data/test/montserrat/Montserrat-LightItalic.ttf",
  "data/test/montserrat/Montserrat-Light.ttf",
  "data/test/montserrat/Montserrat-MediumItalic.ttf",
  "data/test/montserrat/Montserrat-Medium.ttf",
  "data/test/montserrat/Montserrat-SemiBoldItalic.ttf",
  "data/test/montserrat/Montserrat-SemiBold.ttf",
  "data/test/montserrat/Montserrat-ThinItalic.ttf",
  "data/test/montserrat/Montserrat-Thin.ttf"
]

def test_check_098():
  """ METADATA.pb font.name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_098 as check,
                                                     style,
                                                     family_metadata,
                                                     font_metadata,
                                                     font_familynames,
                                                     typographic_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)
    font_fnames = font_familynames(ttFont)
    font_tfnames = []

    # So it must PASS the check:
    print (f"Test PASS with a good RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_fnames = ["WrongFamilyName"]
    print (f"Test FAIL with a bad RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL

  #we do the same for NON-RIBBI styles:
  for fontfile in MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)
    font_fnames = []
    font_tfnames = typographic_familynames(ttFont)

    # So it must PASS the check:
    print (f"Test PASS with a good NON-RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_tfnames = ["WrongFamilyName"]
    print (f"Test FAIL with a bad NON_RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL


def test_check_099():
  """ METADATA.pb font.full_name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_099 as check,
                                                     style,
                                                     family_metadata,
                                                     font_metadata,
                                                     font_familynames,
                                                     typographic_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)
    font_fnames = font_familynames(ttFont)
    font_tfnames = []

    # So it must PASS the check:
    print (f"Test PASS with a good RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_fnames = ["WrongFamilyName"]
    print (f"Test FAIL with a bad RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL

  #we do the same for NON-RIBBI styles:
  for fontfile in MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)
    font_fnames = []
    font_tfnames = typographic_familynames(ttFont)

    # So it must PASS the check:
    print (f"Test PASS with a good NON-RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_tfnames = ["WrongFamilyName"]
    print (f"Test FAIL with a bad NON_RIBBI font ({fontfile})...")
    status, message = list(check(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL


def test_check_100():
  """ METADATA.pb font.filename field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_100 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
    family_directory = os.path.dirname(fontfile)
    meta = family_metadata(family_directory)
    font_meta = font_metadata(meta, fontfile)

    # So it must PASS the check:
    print (f"Test PASS with a good font ({fontfile})...")
    status, message = list(check(fontfile, font_meta))[-1]
    assert status == PASS

    # And fail if it finds a bad filename:
    font_meta.filename = "WrongFileName"
    print (f"Test FAIL with a bad font ({fontfile})...")
    status, message = list(check(fontfile, font_meta))[-1]
    assert status == FAIL


def test_check_101():
  """ METADATA.pb font.post_script_name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_101 as check,
                                                     family_metadata,
                                                     font_metadata,
                                                     font_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:

    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)
    ttFont = TTFont(fontfile)
    font_fnames = font_familynames(ttFont)

    # So it must PASS the check:
    print (f"Test PASS with a good font ({fontfile})...")
    status, message = list(check(font_meta, font_fnames))[-1]
    assert status == PASS

    # And fail if it finds a bad filename:
    font_meta.post_script_name = "WrongPSName"
    print (f"Test FAIL with a bad font ({fontfile})...")
    status, message = list(check(font_meta, font_fnames))[-1]
    assert status == FAIL


def test_check_102():
  """ Copyright notice on METADATA.pb matches canonical pattern ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_102 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be bad
  # Since it provides an email instead of a git URL:
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must FAIL the check:
  print ("Test FAIL with a bad copyright notice string...")
  status, message = list(check(font_meta))[-1]
  assert status == FAIL

  # Then we change it into a good string (example extracted from Archivo Black):
  font_meta.copyright = "Copyright 2017 The Archivo Black Project Authors (https://github.com/Omnibus-Type/ArchivoBlack)"
  print ("Test PASS with a good copyright notice string...")
  status, message = list(check(font_meta))[-1]
  assert status == PASS


def test_check_103():
  """ Copyright notice on METADATA.pb should not contain Reserved Font Name. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_103 as check,
                                                     family_metadata,
                                                     font_metadata)
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  print ("Test PASS with a good copyright notice string...")
  status, message = list(check(font_meta))[-1]
  assert status == PASS

  # Then we make it bad:
  font_meta.copyright += "Reserved Font Name"

  print ("Test WARN with a notice containing 'Reserved Font Name'...")
  status, message = list(check(font_meta))[-1]
  assert status == WARN


def test_check_104():
  """ METADATA.pb: Copyright notice shouldn't exceed 500 chars. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_104 as check,
                                                     family_metadata,
                                                     font_metadata)
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  print ("Test PASS with a 500-char copyright notice string...")
  font_meta.copyright = 500 * "x"
  status, message = list(check(font_meta))[-1]
  assert status == PASS

  print ("Test FAIL with a 501-char copyright notice string...")
  font_meta.copyright = 501 * "x"
  status, message = list(check(font_meta))[-1]
  assert status == FAIL


def test_check_105():
  """ METADATA.pb: Filename is set canonically? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_105 as check,
                                                     family_metadata,
                                                     font_metadata,
                                                     canonical_filename)
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  test_cases = [
  #expected, weight, style,    filename
    [PASS,   100,    "normal", "Cabin-Thin.ttf"],
    [PASS,   100,    "italic", "Cabin-ThinItalic.ttf"],
    [PASS,   200,    "normal", "Cabin-ExtraLight.ttf"],
    [PASS,   200,    "italic", "Cabin-ExtraLightItalic.ttf"],
    [PASS,   300,    "normal", "Cabin-Light.ttf"],
    [PASS,   300,    "italic", "Cabin-LightItalic.ttf"],
    [PASS,   400,    "normal", "Cabin-Regular.ttf"],
    [PASS,   400,    "italic", "Cabin-Italic.ttf"],
    [FAIL,   400,    "italic", "Cabin-RegularItalic.ttf"],
    [PASS,   500,    "normal", "Cabin-Medium.ttf"],
    [PASS,   500,    "italic", "Cabin-MediumItalic.ttf"],
    [PASS,   600,    "normal", "Cabin-SemiBold.ttf"],
    [PASS,   600,    "italic", "Cabin-SemiBoldItalic.ttf"],
    [PASS,   700,    "normal", "Cabin-Bold.ttf"],
    [PASS,   700,    "italic", "Cabin-BoldItalic.ttf"],
    [PASS,   800,    "normal", "Cabin-ExtraBold.ttf"],
    [PASS,   800,    "italic", "Cabin-ExtraBoldItalic.ttf"],
    [PASS,   900,    "normal", "Cabin-Black.ttf"],
    [PASS,   900,    "italic", "Cabin-BlackItalic.ttf"]
  ]

  for expected, weight, style, filename in test_cases:
    print (("Test {} with style:'{}',"
            " weight:{} and filename:'{}'...").format(expected,
                                                      style,
                                                      weight,
                                                      filename))
    font_meta.style = style
    font_meta.weight = weight
    font_meta.filename = filename
    status, message = list(check(font_meta, canonical_filename(font_meta)))[-1]
    assert status == expected


def test_check_106():
  """ METADATA.pb font.style "italic" matches font internals ? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    MACSTYLE_ITALIC)
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_106 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Merriweather Italic is known to good
  fontfile = "data/test/merriweather/Merriweather-Italic.ttf"
  ttFont = TTFont(fontfile)
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # now let's introduce issues on the FULL_FONT_NAME entries
  # to test the "bad-fullfont-name" codepath:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "BAD VALUE".encode(name.getEncoding())
      print ("Test FAIL with a bad NAMEID_FULL_FONT_NAME entry...")
      status, message = list(check(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "bad-fullfont-name"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And, finally, let's flip off that italic bit
  # and get a "bad-macstyle" FAIL (so much fun!):
  print ("Test FAIL with bad macstyle bit value...")
  ttFont['head'].macStyle &= ~MACSTYLE_ITALIC
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "bad-macstyle"


def test_check_107():
  """ METADATA.pb font.style "normal" matches font internals ? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    MACSTYLE_ITALIC)
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_107 as check,
                                                     family_metadata,
                                                     font_metadata)
  # This one is pretty similar to check/106
  # You may want to take a quick look above...
  # Our reference Merriweather Regular is known to be good here.
  fontfile = "data/test/merriweather/Merriweather-Regular.ttf"
  ttFont = TTFont(fontfile)
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # now we sadically insert brokenness into
  # each occurrence of the FONT_FAMILY_NAME nameid:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
      print ("Test FAIL with a non-italic font that has a '-Italic' in FONT_FAMILY_NAME...")
      status, message = list(check(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "familyname-italic"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # now let's do the same with
  # occurrences of the FULL_FONT_NAME nameid:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
      print ("Test FAIL with a non-italic font that has a '-Italic' in FULL_FONT_NAME...")
      status, message = list(check(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "fullfont-italic"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And, finally, again, we flip a bit and
  # get a "bad-macstyle" error:
  print ("Test FAIL with bad macstyle bit value...")
  # But this time the boolean logic is the quite opposite in
  # comparison to test_check_106 above. Here we have to set the
  # bit back to 1 to get a wrongful "this font is an italic" setting:
  ttFont['head'].macStyle |= MACSTYLE_ITALIC
  status, message = list(check(ttFont, font_meta))[-1]
  # Not it's not! FAIL! :-D
  assert status == FAIL and message.code == "bad-macstyle"


def test_check_108():
  """ METADATA.pb font.name and font.full_name fields match the values declared on the name table? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME)
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_108 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Merriweather Regular is known to be good here.
  fontfile = "data/test/merriweather/Merriweather-Regular.ttf"
  ttFont = TTFont(fontfile)
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # There we go again:
  # breaking FULL_FONT_NAME entries
  # one by one:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "This is utterly wrong!".encode(name.getEncoding())
      print ("Test FAIL with a METADATA.pb / FULL_FONT_NAME mismatch...")
      status, message = list(check(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "fullname-mismatch"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And then we do the same with FONT_FAMILY_NAME entries:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "I'm listening to deadmau5 :-)".encode(name.getEncoding())
      print ("Test FAIL with a METADATA.pb / FONT_FAMILY_NAME mismatch...")
      status, message = list(check(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "familyname-mismatch"
      # and restore the good value:
      ttFont['name'].names[i].string = backup


def test_check_109():
  """ METADATA.pb: Check if fontname is not camel cased. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_109 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(font_meta))[-1]
  assert status == PASS

  # Then we FAIL with a CamelCased name:
  font_meta.name = "GollyGhost"
  print ("Test FAIL with a bad font (CamelCased font name)...")
  status, message = list(check(font_meta))[-1]
  assert status == FAIL

  # And we also make sure the check PASSes with a few known good names:
  good_names = ["VT323", "PT Sans", "Amatic SC"]
  for good_name in good_names:
    font_meta.name = good_name
    print (f"Test PASS with a good font name '{good_name}'...")
    status, message = list(check(font_meta))[-1]
    assert status == PASS


def test_check_110():
  """ METADATA.pb: Check font name is the same as family name. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_110 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(family_meta, font_meta))[-1]
  assert status == PASS

  # Then we FAIL with mismatching names:
  family_meta.name = "Some Fontname"
  font_meta.name = "Something Else"
  print ("Test FAIL with a bad font...")
  status, message = list(check(family_meta, font_meta))[-1]
  assert status == FAIL


def test_check_111():
  """ METADATA.pb: Check that font weight has a canonical value. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_111 as check,
                                                     family_metadata,
                                                     font_metadata)
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  for w in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
    print (f"Test PASS with a good weight value ({w})...")
    font_meta.weight = w
    status, message = list(check(font_meta))[-1]
    assert status == PASS

  for w in [150, 250, 350, 450, 550, 650, 750, 850]:
    print (f"Test FAIL with a bad weight value ({w})...")
    font_meta.weight = w
    status, message = list(check(font_meta))[-1]
    assert status == FAIL


def test_check_112():
  """ Checking OS/2 usWeightClass matches weight specified at METADATA.pb """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_112 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    print (f"Test PASS with a good font ({fontfile})...")
    status, message = list(check(ttFont, font_meta))[-1]
    assert status == PASS

    # And fail if it finds a bad weight value:
    good_value = font_meta.weight
    bad_value = good_value + 50
    font_meta.weight = bad_value
    print (f"Test FAIL with a bad font ({fontfile})...")
    status, message = list(check(ttFont, font_meta))[-1]
    assert status == FAIL


def NOT_IMPLEMENTED_test_check_113():
  """ METADATA.pb: Metadata weight matches postScriptName. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_113 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "METADATA.pb: Font weight value is invalid."
  # - FAIL, "METADATA.pb: Mismatch between postScriptName and weight value."
  # - PASS


def NOT_IMPLEMENTED_test_check_115():
  """ METADATA.pb: Font styles are named canonically? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_115 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - SKIP, "Applicable only to font styles declared as 'italic' or 'regular' on METADATA.pb."
  # - FAIL, "Font style should be italic."
  # - FAIL, "Font style should be normal."
  # - PASS, "Font styles are named canonically."


def test_check_116():
  """ Is font em size (ideally) equal to 1000? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_116 as check

  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  ttFont = TTFont(fontfile)

  print ("Test PASS with unitsPerEm = 1000...")
  ttFont["head"].unitsPerEm = 1000
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print ("Test WARN with unitsPerEm = 1024...")
  ttFont["head"].unitsPerEm = 1024
  status, message = list(check(ttFont))[-1]
  assert status == WARN


def NOT_IMPLEMENTED_test_check_117():
  """ Version number has increased since previous release on Google Fonts? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_117 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "Version number is equal to version on Google Fonts."
  # - FAIL, "Version number is less than version on Google Fonts."
  # - FAIL, "Version number is equal to version on Google Fonts GitHub repo."
  # - FAIL, "Version number is less than version on Google Fonts GitHub repo."
  # - PASS


def NOT_IMPLEMENTED_test_check_118():
  """ Glyphs are similiar to Google Fonts version? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_118 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN, "Following glyphs differ greatly from Google Fonts version"
  # - PASS, "Glyphs are similar"


def NOT_IMPLEMENTED_test_check_119():
  """ TTFAutohint x-height increase value is same as in
      previous release on Google Fonts? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_119 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN ("fpgm" in ttFont)
  # - WARN ("fpgm" in api_gfonts_ttFont)
  # - FAIL, "TTFAutohint --increase-x-height should match the previous version's value"
  # - PASS


def NOT_IMPLEMENTED_test_check_129():
  """ Checking OS/2 fsSelection value. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_129 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # ...


def test_check_130():
  """ Checking post.italicAngle value. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_130 as check
  from fontbakery.utils import assert_results_contain

  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  ttFont = TTFont(fontfile)

  # italic-angle, style, fail_message
  test_cases = [
    [1, "Italic", "positive"],
    [0, "Regular", None], # This must PASS as it is a non-italic
    [-21, "ThinItalic", ">20 degrees"],
    [0, "Italic", "zero-italic"],
    [-1,"ExtraBold", "non-zero-normal"]
  ]

  for value, style, expected_fail_msg in test_cases:
    ttFont["post"].italicAngle = value
    results = list(check(ttFont, style))

    if expected_fail_msg:
      print (("Test FAIL '{}' with"
              " italic-angle:{} style:{}...").format(expected_fail_msg,
                                                     value,
                                                     style))
      assert_results_contain(results, FAIL, expected_fail_msg)
    else:
      print (("Test PASS with"
              " italic-angle:{} style:{}...").format(value, style))
      status, message = results[-1]
      assert status == PASS


def test_check_131():
  """ Checking head.macStyle value. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_131 as check
  from fontbakery.utils import assert_results_contain
  from fontbakery.constants import (MACSTYLE_ITALIC,
                                    MACSTYLE_BOLD)

  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  ttFont = TTFont(fontfile)

  # macStyle-value, style, expected
  test_cases = [
    [0, "Thin", PASS],
    [0, "Bold", "bad-BOLD"],
    [0, "Italic", "bad-ITALIC"],
    [MACSTYLE_ITALIC, "Italic", PASS],
    [MACSTYLE_ITALIC, "Thin", "bad-ITALIC"],
    [MACSTYLE_BOLD, "Bold", PASS],
    [MACSTYLE_BOLD, "Thin", "bad-BOLD"],
    [MACSTYLE_BOLD|MACSTYLE_ITALIC, "BoldItalic", PASS]
  ]

  for macStyle_value, style, expected in test_cases:
    ttFont["head"].macStyle = macStyle_value
    results = list(check(ttFont, style))

    if expected == PASS:
      print (("Test PASS with"
              " macStyle:{} style:{}...").format(macStyle_value,
                                                 style))
      status, message = results[-1]
      assert status == PASS
    else:
      print (("Test FAIL '{}' with"
              " macStyle:{} style:{}...").format(expected,
                                                 macStyle_value,
                                                 style))
      assert_results_contain(results, FAIL, expected)


def test_check_153(montserrat_ttFonts):
  """Check glyphs contain the recommended contour count"""
  from fontbakery.specifications.googlefonts import com_google_fonts_check_153 as check

  # Montserrat should PASS this check since it was used to assemble the glyph data
  for ttFont in montserrat_ttFonts:
    status, message = list(check(ttFont))[-1]
    assert status == PASS

  # Lets swap the glyf a (2 contours) with glyf c (1 contour)
  for ttFont in montserrat_ttFonts:
    ttFont['glyf']['a'] = ttFont['glyf']['c']
    status, message = list(check(ttFont))[-1]
    assert status == WARN


# FIXME! This works fine locally, but crashes on Travis
# See: https://travis-ci.org/googlefonts/fontbakery/builds/341946880
# and also: https://github.com/googlefonts/fontbakery/issues/1712
#
def DISABLED_test_check_154(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    from fontbakery.specifications.googlefonts import (com_google_fonts_check_154 as check,
                                                       api_gfonts_ttFont,
                                                       remote_styles,
                                                       family_metadata)
    font = cabin_ttFonts[-1]
    print(cabin_ttFonts)
    style = font['name'].getName(2, 1, 0, 0)

    family_meta = family_metadata("data/test/regression/cabin/")
    gfonts_remote_styles = remote_styles(family_meta)
    gfont = api_gfonts_ttFont(str(style), gfonts_remote_styles)

    # Cabin font hosted on fonts.google.com contains
    # all the glyphs for the font in data/test/cabin
    status, message = list(check(font, gfont))[-1]
    assert status == PASS

    # Take A glyph out of font
    font['cmap'].getcmap(3, 1).cmap.pop(ord('A'))
    font['glyf'].glyphs.pop('A')

    status, message = list(check(font, gfont))[-1]
    assert status == FAIL


def test_check_155():
  """ Copyright field for this font on METADATA.pb matches
      all copyright notice entries on the name table ? """
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_155 as check,
                                                     family_metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  fontfile = "data/test/cabin/Cabin-Regular.ttf"
  ttFont = TTFont(fontfile)
  family_directory = os.path.dirname(fontfile)
  family_meta = family_metadata(family_directory)
  font_meta = font_metadata(family_meta, fontfile)

  # So it must PASS the check:
  print ("Test PASS with a good METADATA.pb for this font...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == PASS

  # Then we FAIL with mismatching names:
  good_value = get_name_entry_strings(ttFont, NAMEID_COPYRIGHT_NOTICE)[0]
  font_meta.copyright = good_value + "something bad"
  print ("Test FAIL with a bad METADATA.pb (with a copyright string not matching this font)...")
  status, message = list(check(ttFont, font_meta))[-1]
  assert status == FAIL


def test_check_156():
  """ Font has all mandatory 'name' table entries ? """
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  from fontbakery.specifications.googlefonts import com_google_fonts_check_156 as check

  # We'll check both RIBBI and non-RIBBI fonts
  # so that we cover both cases for FAIL/PASS scenarios

  #First with a RIBBI font:
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  style = "Regular"

  # So it must PASS the check:
  print ("Test PASS with a good RIBBI font...")
  status, message = list(check(ttFont, style))[-1]
  assert status == PASS

  mandatory_entries = [NAMEID_FONT_FAMILY_NAME,
                       NAMEID_FONT_SUBFAMILY_NAME,
                       NAMEID_FULL_FONT_NAME,
                       NAMEID_POSTSCRIPT_NAME]

  # then we "remove" each mandatory entry one by one:
  for mandatory in mandatory_entries:
    ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
    for i, name in enumerate(ttFont['name'].names):
      if name.nameID == mandatory:
        ttFont['name'].names[i].nameID = 0 # not really removing it, but replacing it
                                           # by something else completely irrelevant
                                           # for the purposes of this specific check
    print (f"Test FAIL with a missing madatory (RIBBI) name entry (id={mandatory})...")
    status, message = list(check(ttFont, style))[-1]
    assert status == FAIL

  #And now a non-RIBBI font:
  # Our reference Merriweather Black is known to be good
  ttFont = TTFont("data/test/merriweather/Merriweather-Black.ttf")
  style = "Black"

  # So it must PASS the check:
  print ("Test PASS with a good non-RIBBI font...")
  status, message = list(check(ttFont, style))[-1]
  assert status == PASS

  mandatory_entries = [NAMEID_FONT_FAMILY_NAME,
                       NAMEID_FONT_SUBFAMILY_NAME,
                       NAMEID_FULL_FONT_NAME,
                       NAMEID_POSTSCRIPT_NAME,
                       NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                       NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME]

  # then we (again) "remove" each mandatory entry one by one:
  for mandatory in mandatory_entries:
    ttFont = TTFont("data/test/merriweather/Merriweather-Black.ttf")
    for i, name in enumerate(ttFont['name'].names):
      if name.nameID in mandatory_entries:
        ttFont['name'].names[i].nameID = 0 # not really removing it, but replacing it
                                           # by something else completely irrelevant
                                           # for the purposes of this specific check
    print ("Test FAIL with a missing madatory (non-RIBBI) name entry (id={mandatory})...")
    status, message = list(check(ttFont, style))[-1]
    assert status == FAIL


def test_check_157():
  """ Check name table: FONT_FAMILY_NAME entries. """
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    PLATFORM_ID__MACINTOSH,
                                    PLATFORM_ID__WINDOWS)
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_157 as check,
                                                     familyname,
                                                     familyname_with_spaces,
                                                     style)
  test_cases = [
    (PASS, "data/test/cabin/Cabin-Regular.ttf",               "Cabin", "Cabin"),
    (FAIL, "data/test/cabin/Cabin-Regular.ttf",               "Wrong", "Cabin"),
    (PASS, "data/test/overpassmono/OverpassMono-Regular.ttf", "Overpass Mono", "Overpass Mono"),
    (PASS, "data/test/overpassmono/OverpassMono-Bold.ttf",    "Overpass Mono", "Overpass Mono"),
    (FAIL, "data/test/overpassmono/OverpassMono-Regular.ttf", "Overpass Mono", "Foo"),
    (PASS, "data/test/merriweather/Merriweather-Black.ttf", "Merriweather", "Merriweather Black"),
    (PASS, "data/test/merriweather/Merriweather-LightItalic.ttf", "Merriweather", "Merriweather Light"),
    (FAIL, "data/test/merriweather/Merriweather-LightItalic.ttf", "Merriweather", "Merriweather Light Italic"),
  ]

  for expected, filename, mac_value, win_value in test_cases:
    ttFont = TTFont(filename)
    for i, name in enumerate(ttFont['name'].names):
      if name.platformID == PLATFORM_ID__MACINTOSH:
        value = mac_value
      if name.platformID == PLATFORM_ID__WINDOWS:
        value = win_value
      assert value

      if name.nameID == NAMEID_FONT_FAMILY_NAME:
          ttFont['name'].names[i].string = value.encode(name.getEncoding())
    print (f"Test {expected} with filename='{filename}', value='{value}', style='{style(filename)}'...")
    status, message = list(check(ttFont,
                                 style(filename),
                                 familyname_with_spaces(familyname(filename))))[-1]
    assert status == expected


def NOT_IMPLEMENTED_test_check_158():
  """ Check name table: FONT_SUBFAMILY_NAME entries. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_158 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "Style name inferred from filename is not canonical."
  # - FAIL, "Font should not have a certain name table entry."
  # - FAIL, "Bad familyname value on a FONT_SUBFAMILY_NAME entry."
  # - PASS


def test_check_159():
  """ Check name table: FULL_FONT_NAME entries. """
  from fontbakery.constants import NAMEID_FULL_FONT_NAME
  from fontbakery.specifications.googlefonts import com_google_fonts_check_159 as check

  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good Regular font...")
  status, message = list(check(ttFont, "Regular", "Cabin"))[-1]
  assert status == PASS

  # Let's now test the Regular exception
  # ('Regular' can be optionally ommited on the FULL_FONT_NAME entry):
  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont["name"].names[index].string = "Cabin".encode(name.getEncoding())
      print ("Test WARN with a good Regular font that omits 'Regular' on FULL_FONT_NAME...")
      status, message = list(check(ttFont, "Regular", "Cabin"))[-1]
      assert status == WARN
      # restore it:
      ttFont["name"].names[index].string = backup

  # Let's also make sure our good reference Cabin BoldItalic PASSes the check.
  # This also tests the splitting of filename infered style with a space char
  ttFont = TTFont("data/test/cabin/Cabin-BoldItalic.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good Bold Italic font...")
  status, message = list(check(ttFont, "BoldItalic", "Cabin"))[-1]
  assert status == PASS

  # And here we test the FAIL codepath:
  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont["name"].names[index].string = "MAKE IT FAIL".encode(name.getEncoding())
      print ("Test FAIL with a bad FULL_FONT_NAME entry...")
      status, message = list(check(ttFont, "BoldItalic", "Cabin"))[-1]
      assert status == FAIL
      # restore it:
      ttFont["name"].names[index].string = backup


def NOT_IMPLEMENTED_test_check_160():
  """ Check name table: POSTSCRIPT_NAME entries. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_160 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL
  # - PASS


def NOT_IMPLEMENTED_test_check_161():
  """ Check name table: TYPOGRAPHIC_FAMILY_NAME entries. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_161 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN
  # - FAIL
  # - PASS


def NOT_IMPLEMENTED_test_check_162():
  """ Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries. """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_162 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN
  # - FAIL
  # - PASS


def test_check_164():
  """ Length of copyright notice must not exceed 500 characters. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_164 as check
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE

  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  print('Test PASS with 499-byte copyright notice string...')
  good_entry = 'a' * 499
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print('Test PASS with 500-byte copyright notice string...')
  good_entry = 'a' * 500
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  print('Test FAIL with 501-byte copyright notice string...')
  bad_entry = 'a' * 501
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = bad_entry.encode(entry.getEncoding())
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_165():
  """ Familyname is unique according to namecheck.fontdata.com """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_165 as check,
                                                     familyname)

  print('Test INFO with an already used name...')
  # We dont FAIL because this is meant as a merely informative check
  # There may be frequent cases when fonts are being updated and thus
  # already have a public family name registered on the
  # namecheck.fontdata.com database.
  font = "data/test/cabin/Cabin-Regular.ttf"
  ttFont = TTFont(font)
  status, message = list(check(ttFont, familyname(font)))[-1]
  assert status == INFO

  print('Test PASS with a unique family name...')
  # Here we know that FamilySans has not been (and will not be)
  # registered as a real family.
  font = "data/test/familysans/FamilySans-Regular.ttf"
  ttFont = TTFont(font)
  status, message = list(check(ttFont, familyname(font)))[-1]
  assert status == PASS


def test_check_166():
  """ Check for font-v versioning """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_166 as check
  from fontbakery.constants import NAMEID_VERSION_STRING
  from fontv.libfv import FontVersion

  print('Test INFO for font that does not follow'
        ' the suggested font-v versioning scheme ...')
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(check(ttFont))[-1]
  assert status == INFO

  print('Test PASS with one that follows the suggested scheme ...')
  fv = FontVersion(ttFont)
  fv.set_state_git_commit_sha1(development=True)
  version_string = fv.get_name_id5_version_string()
  for record in ttFont['name'].names:
    if record.nameID == NAMEID_VERSION_STRING:
      record.string = version_string
  status, message = list(check(ttFont))[-1]
  assert status == PASS


# Temporarily disabling this code-test since check/173 itself
# is disabled waiting for an implementation targetting the
# actual root cause of the issue.
#
# See also comments at googlefons.py as well as at
# https://github.com/googlefonts/fontbakery/issues/1727
def disabled_test_check_173():
  """ Check that advance widths cannot be inferred as negative. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_173 as check

  # Our reference Cabin Regular is good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS
  print('Test PASS with a good font...')
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # We then change values in an arbitrary glyph
  # in the glyf table in order to cause the problem:
  glyphName = "J"
  coords = ttFont["glyf"].glyphs[glyphName].coordinates

# FIXME:
# Note: I thought this was the proper way to induce the
# issue, but now I think I'll need to look more
# carefully at sample files providedby MarcFoley
# to see what's really at play here and how the relevant
# data is encoded into the affected OpenType files.
  rightSideX = coords[-3][0]
  # leftSideX: (make right minus left a negative number)
  coords[-4][0] = rightSideX + 1

  ttFont["glyf"].glyphs[glyphName].coordinates = coords

  # and now this should FAIL:
  print('Test FAIL with bad coordinates on the glyf table...')
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_174():
  """ Check a static ttf can be generated from a variable font. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_174 as check

  ttFont = TTFont('data/test/cabinvfbeta/CabinVFBeta.ttf')
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Removing a table to deliberately break variable font
  del ttFont['fvar']
  status, message = list(check(ttFont))[-1]
  assert status == FAIL


def test_check_040(mada_ttFonts):
  """ Checking OS/2 usWinAscent & usWinDescent. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_040 as check
  from fontbakery.specifications.shared_conditions import vmetrics

  # Our reference Mada Regular is know to be bad here.
  vm = vmetrics(mada_ttFonts)
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But we fix it first to test the PASS code-path:
  print('Test PASS with a good font...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(check(ttFont, vm))[-1]
  assert status == PASS

  # Then we break it:
  print('Test FAIL with a bad OS/2.usWinAscent...')
  ttFont['OS/2'].usWinAscent = vm['ymax'] - 1
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(check(ttFont, vm))[-1]
  assert status == FAIL and message.code == "ascent"

  print('Test FAIL with a bad OS/2.usWinDescent...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin']) - 1
  status, message = list(check(ttFont, vm))[-1]
  assert status == FAIL and message.code == "descent"


def test_check_042(mada_ttFonts):
  """ Checking OS/2 Metrics match hhea Metrics. """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_042 as check

  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Now we break it:
  print('Test FAIL with a bad OS/2.sTypoAscender font...')
  correct = ttFont['hhea'].ascent
  ttFont['OS/2'].sTypoAscender = correct + 1
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "ascender"

  # Restore good value:
  ttFont['OS/2'].sTypoAscender = correct

  # And break it again, now on sTypoDescender value:
  print('Test FAIL with a bad OS/2.sTypoDescender font...')
  correct = ttFont['hhea'].descent
  ttFont['OS/2'].sTypoDescender = correct + 1
  status, message = list(check(ttFont))[-1]
  assert status == FAIL and message.code == "descender"


def test_check_072():
  """ Font enables smart dropout control in "prep" table instructions? """
  from fontbakery.specifications.googlefonts import com_google_fonts_check_072 as check

  test_font_path = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

  # - PASS, "Program at 'prep' table contains instructions enabling smart dropout control."
  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  # - FAIL, "Font does not contain TrueType instructions enabling
  #          smart dropout control in the 'prep' table program."
  import array
  test_font["prep"].program.bytecode = array.array('B', [0])
  status, _ = list(check(test_font))[-1]
  assert status == FAIL


def test_check_vtt_clean():
  """ There must not be VTT Talk sources in the font. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_check_vtt_clean as check,
                                                     vtt_talk_sources)

  good_font = TTFont(os.path.join("data", "test", "mada", "Mada-Regular.ttf"))
  bad_font = TTFont(os.path.join("data", "test", "hinting", "Roboto-VF.ttf"))

  status, _ = list(check(good_font, vtt_talk_sources(good_font)))[-1]
  assert status == PASS

  status, _ = list(check(bad_font, vtt_talk_sources(bad_font)))[-1]
  assert status == FAIL
