# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import pytest

from fontbakery.testrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , ENDTEST
            )

test_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

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


def test_example_testrunner_based(cabin_regular_path):
  """ This is just an example test. We'll probably need something like
      this setup in a testrunner_test.py testsuite.
      Leave it here for the moment until we implemented a real case.

      This test is run via the testRunner and demonstrate how to get
      (mutable) objects from the conditions cache and change them.

      NOTE: the actual fontbakery tests of conditions should never change
      a condition object.
  """
  from fontbakery.testrunner import TestRunner
  from fontbakery.specifications.googlefonts import specification
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION
  values = dict(fonts=[cabin_regular_path])
  runner = TestRunner(specification, values, explicit_tests=['com.google.fonts/test/029'])

  print('Test PASS ...')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == PASS
     break

  # we could also reuse the `iterargs` that was assigned in the previous
  # for loop, but this here is more explicit
  iterargs = ((u'font', 0),)
  ttFont = runner.get('ttFont', iterargs)

  print('Test failing entry ...')
  # prepare
  change_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION, 'failing entry')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == FAIL and last_test_message.code == 'wrong'
     break

  print('Test missing entry ...')
  # prepare
  delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == FAIL and last_test_message.code == 'missing'
     break


def test_id_001():
  """ Files are named canonically. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_001 as test
  canonical_names = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf",
    "data/test/cabin/Cabin-Light.ttf",
    "data/test/cabin/Cabin-Regular.ttf",
    "data/test/cabin/Cabin-Medium.ttf",
    "data/test/cabin/Cabin-SemiBold.ttf",
    "data/test/cabin/Cabin-Bold.ttf",
    "data/test/cabin/Cabin-ExtraBold.ttf",
    "data/test/cabin/Cabin-Black.ttf",
    "data/test/cabin/Cabin-ThinItalic.ttf",
    "data/test/cabin/Cabin-ExtraLightItalic.ttf",
    "data/test/cabin/Cabin-LightItalic.ttf",
    "data/test/cabin/Cabin-Italic.ttf",
    "data/test/cabin/Cabin-MediumItalic.ttf",
    "data/test/cabin/Cabin-SemiBoldItalic.ttf",
    "data/test/cabin/Cabin-BoldItalic.ttf",
    "data/test/cabin/Cabin-ExtraBoldItalic.ttf",
    "data/test/cabin/Cabin-BlackItalic.ttf"
  ]
  non_canonical_names = [
    "data/test/cabin/Cabin.ttf",
    "data/test/cabin/Cabin-semibold.ttf"
  ]

  print('Test PASS ...')
  for canonical in canonical_names:
    status, message = list(test(canonical))[-1]
    assert status == PASS

  print('Test FAIL ...')
  for non_canonical in non_canonical_names:
    status, message = list(test(non_canonical))[-1]
    assert status == FAIL


def test_id_002():
  """ Fonts are all in the same directory. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_002 as test
  same_dir = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  multiple_dirs = [
    "data/test/mada/Mada-Regular.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  print('Test PASS with same dir: {}'.format(same_dir))
  status, message = list(test(same_dir))[-1]
  assert status == PASS

  print('Test FAIL with multiple dirs: {}'.format(multiple_dirs))
  status, message = list(test(multiple_dirs))[-1]
  assert status == FAIL


def test_id_003():
  """ Does DESCRIPTION file contain broken links ? """
  from unidecode import unidecode
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_003 as test,
                                                     description,
                                                     descfile)
  good_desc = description(descfile("data/test/cabin/"))
  print('Test PASS with description file that has no links...')
  status, message = list(test(good_desc))[-1]
  assert status == PASS

  good_desc = unidecode(good_desc.decode("utf8")) + \
     "<a href='http://example.com'>Good Link</a>" + \
     "<a href='http://fonts.google.com'>Another Good One</a>"
  print('Test PASS with description file that has good links...')
  status, message = list(test(good_desc))[-1]
  assert status == PASS

  good_desc += "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
  print('Test FAIL with a description file containing a mailto links...')
  status, message = list(test(good_desc))[-1]
  assert status == PASS

  bad_desc = good_desc + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
  print('Test FAIL with a description file containing a known-bad URL...')
  status, message = list(test(bad_desc))[-1]
  assert status == FAIL


def test_id_004():
  """ DESCRIPTION file is a propper HTML snippet ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_004 as test,
                                                     descfile)
  good_descfile = descfile("data/test/nunito/")
  print('Test PASS with description file that contains a good HTML snippet...')
  status, message = list(test(good_descfile))[-1]
  assert status == PASS

  bad_descfile = "data/test/cabin/FONTLOG.txt" # :-)
  print('Test FAIL with a known-bad file (a txt file without HTML snippets)...')
  status, message = list(test(bad_descfile))[-1]
  assert status == FAIL


def test_id_005():
  """ DESCRIPTION.en_us.html must have more than 200 bytes. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_005 as test

  bad_length = 'a' * 199
  print('Test FAIL with 199-byte buffer...')
  status, message = list(test(bad_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 200
  print('Test FAIL with 200-byte buffer...')
  status, message = list(test(bad_length))[-1]
  assert status == FAIL

  good_length = 'a' * 201
  print('Test PASS with 201-byte buffer...')
  status, message = list(test(good_length))[-1]
  assert status == PASS


def test_id_006():
  """ DESCRIPTION.en_us.html must have less than 1000 bytes. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_006 as test

  bad_length = 'a' * 1001
  print('Test FAIL with 1001-byte buffer...')
  status, message = list(test(bad_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 1000
  print('Test FAIL with 1000-byte buffer...')
  status, message = list(test(bad_length))[-1]
  assert status == FAIL

  good_length = 'a' * 999
  print('Test PASS with 999-byte buffer...')
  status, message = list(test(good_length))[-1]
  assert status == PASS


def test_id_007():
  """ Font designer field in METADATA.pb must not be 'unknown'. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_007 as test,
                                                     metadata)
  good = metadata("data/test/merriweather/")
  print('Test PASS with a good METADATA.pb file...')
  status, message = list(test(good))[-1]
  assert status == PASS

  bad = metadata("data/test/merriweather/")
  bad.designer = "unknown"
  print('Test FAIL with a bad METADATA.pb file...')
  status, message = list(test(bad))[-1]
  assert status == FAIL


def test_id_008(mada_ttFonts):
  """ Fonts have consistent underline thickness ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_008 as test

  print('Test PASS with good family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wronge value in one of the font files:
  value = mada_ttFonts[0]['post'].underlineThickness
  incorrect_value = value + 1
  mada_ttFonts[0]['post'].underlineThickness = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_009(mada_ttFonts):
  """ Fonts have consistent PANOSE proportion ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_009 as test

  print('Test PASS with good family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bProportion
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bProportion = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_010(mada_ttFonts):
  """ Fonts have consistent PANOSE family type ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_010 as test

  print('Test PASS with good family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bFamilyType
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bFamilyType = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(test(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_011(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal numbers of glyphs ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_011 as test

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(test(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs.
  status, message = list(test(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_012(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal glyph names ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_012 as test

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(test(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs (that extra glyph
  # causes the test to fail).
  status, message = list(test(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_013(mada_ttFonts):
  """ Fonts have equal unicode encodings ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_013 as test
  from fontbakery.constants import (PLAT_ENC_ID__SYMBOL,
                                    PLAT_ENC_ID__UCS2)
  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(test(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce mismatching encodings into the first 2 font files:
  for i, encoding in enumerate([PLAT_ENC_ID__SYMBOL,
                                PLAT_ENC_ID__UCS2]):
    for table in bad_ttFonts[i]['cmap'].tables:
      if table.format == 4:
        table.platEncID = encoding

  print('Test FAIL with fonts that diverge on unicode encoding.')
  status, message = list(test(bad_ttFonts))[-1]
  assert status == FAIL


def test_id_014(mada_ttFonts):
  """ Make sure all font files have the same version value. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_014 as test

  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(test(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce a mismatching version value into the second font file:
  version = bad_ttFonts[0]['head'].fontRevision
  bad_ttFonts[1]['head'].fontRevision = version + 1

  print('Test WARN with fonts that diverge on the fontRevision field value.')
  status, message = list(test(bad_ttFonts))[-1]
  assert status == WARN


def test_id_015():
  """ Font has post table version 2 ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_015 as test

  print('Test PASS with good font.')
  # our reference Mada family is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # modify the post table version
  ttFont['post'].formatType = 3

  print('Test FAIL with fonts that diverge on the fontRevision field value.')
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def test_id_016():
  """ Checking OS/2 fsType """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_016 as test

  print('Test PASS with good font.')
  # our reference Cabin family is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # modify the OS/2 fsType value to something different than zero:
  ttFont['OS/2'].fsType = 1

  print('Test FAIL with fonts that diverge on the fontRevision field value.')
  status, message = list(test(ttFont))[-1]
  assert status == FAIL

# DEPRECATED CHECK:
# com.google.fonts/test/017 - "Assure valid format for the main entries in the name table."
#
# REPLACED BY:
# com.google.fonts/test/156 - "Font has all mandatory 'name' table entries ?"
# com.google.fonts/test/157 - "Check name table: FONT_FAMILY_NAME entries."
# com.google.fonts/test/158 - "Check name table: FONT_SUBFAMILY_NAME entries."
# com.google.fonts/test/159 - "Check name table: FULL_FONT_NAME entries."
# com.google.fonts/test/160 - "Check name table: POSTSCRIPT_NAME entries."
# com.google.fonts/test/161 - "Check name table: TYPOGRAPHIC_FAMILY_NAME entries."
# com.google.fonts/test/162 - "Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries."

def test_id_018():
  """ Checking OS/2 achVendID """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_018 as test,
                                                     registered_vendor_ids)
  from fontbakery.constants import NAMEID_MANUFACTURER_NAME
  registered_ids = registered_vendor_ids()

  print('Test WARN with mismatching vendor id.')
  # Our reference Cabin family is know to have mismatching value of
  # Vendor ID ('STC ') and Manufacturer Name ('Eben Sorkin').
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  status, message = list(test(ttFont, registered_ids))[-1]
  assert status == WARN and message.code == "mismatch"

  print('Test FAIL with bad vid.')
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  for bad_vid in bad_vids:
    ttFont['OS/2'].achVendID = bad_vid
    status, message = list(test(ttFont, registered_ids))[-1]
    assert status == FAIL and message.code == "bad"

  print('Test FAIL with font missing vendor id info.')
  ttFont['OS/2'].achVendID = None
  status, message = list(test(ttFont, registered_ids))[-1]
  assert status == FAIL and message.code == "not set"

  print('Test WARN with unknwon vendor id.')
  ttFont['OS/2'].achVendID = "????"
  status, message = list(test(ttFont, registered_ids))[-1]
  assert status == WARN and message.code == "unknown"

  print('Test PASS with good font.')
  # we change the fields into a known good combination
  # of vendor id and manufacturer name here:
  ttFont['OS/2'].achVendID = "APPL"
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_MANUFACTURER_NAME:
      ttFont['name'].names[i].string = "Apple".encode(name.getEncoding())
  status, message = list(test(ttFont, registered_ids))[-1]
  assert status == PASS


def test_id_019():
  """ Substitute copyright, registered and trademark
      symbols in name table entries. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_019 as test

  print('Test FAIL with a bad font...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL

  print('Test PASS with a good font...')
  # Our reference Cabin Regular is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == PASS


def test_id_020():
  """ Checking OS/2 usWeightClass. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_020 as test,
                                                     style)
  print('Test FAIL with a bad font...')
  # Our reference Mada Regular is know to be bad here.
  font = "data/test/mada/Mada-Regular.ttf"
  status, message = list(test(TTFont(font), style(font)))[-1]
  assert status == FAIL

  print('Test PASS with a good font...')
  # All fonts in our reference Cabin family are know to be good here.
  for font in cabin_fonts:
    status, message = list(test(TTFont(font), style(font)))[-1]
    assert status == PASS

# DEPRECATED CHECKS:                                             | REPLACED BY:
# com.google.fonts/test/??? - "Checking macStyle BOLD bit"       | com.google.fonts/test/131 - "Checking head.macStyle value"
# com.google.fonts/test/021 - "Checking fsSelection REGULAR bit" | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/test/022 - "italicAngle <= 0 ?"               | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/023 - "italicAngle is < 20 degrees ?"    | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/024 - "italicAngle matches font style ?" | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/025 - "Checking fsSelection ITALIC bit"  | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/test/026 - "Checking macStyle ITALIC bit"     | com.google.fonts/test/131 - "Checking head.macStyle value"
# com.google.fonts/test/027 - "Checking fsSelection BOLD bit"    | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"

def test_id_028():
  """ Check font project has a license. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_028 as test,
                                                     licenses)
  print('Test FAIL with multiple licenses...')
  detected_licenses = licenses("data/test/028/multiple/")
  status, message = list(test(detected_licenses))[-1]
  assert status == FAIL and message.code == "multiple"

  print('Test FAIL with no license...')
  detected_licenses = licenses("data/test/028/none/")
  status, message = list(test(detected_licenses))[-1]
  assert status == FAIL and message.code == "none"

  print('Test PASS with a single OFL license...')
  detected_licenses = licenses("data/test/028/pass_ofl/")
  status, message = list(test(detected_licenses))[-1]
  assert status == PASS

  print('Test PASS with a single Apache license...')
  detected_licenses = licenses("data/test/028/pass_apache/")
  status, message = list(test(detected_licenses))[-1]
  assert status == PASS


def test_id_029(mada_ttFonts):
  """ Check copyright namerecords match license file. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_029 as test
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION

  # Our reference Mada family has its copyright name records properly set
  # identifying it as being licensed under the Open Font License
  license = 'OFL.txt'
  wrong_license = 'LICENSE.txt' # Apache

  print('Test PASS with good fonts ...')
  for ttFont in mada_ttFonts:
    status, message = list(test(ttFont, license))[-1]
    assert status == PASS

  print('Test FAIL with wrong entry values ...')
  for ttFont in mada_ttFonts:
    status, message = list(test(ttFont, wrong_license))[-1]
    assert status == FAIL and message.code == 'wrong'

  print('Test FAIL with missing copyright namerecords ...')
  for ttFont in mada_ttFonts:
    delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
    status, message = list(test(ttFont, license))[-1]
    assert status == FAIL and message.code == 'missing'

# TODO: test_id_030

def test_id_031():
  """ Description strings in the name table
      must not contain copyright info.
  """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_031 as test
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # here we add a "Copyright" string to a NAMEID_DESCRIPTION
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = "Copyright".encode(name.getEncoding())

  print('Test FAIL with a bad font...')
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def test_id_032():
  """ Description strings in the name table
      must not exceed 100 characters.
  """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_032 as test
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # Here we add strings to NAMEID_DESCRIPTION with exactly 100 chars,
  # so it should still PASS:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 100).encode(name.getEncoding())

  print('Test PASS with a 100 char string...')
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # And here we make the strings longer than 100 chars in order to FAIL the test:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 101).encode(name.getEncoding())

  print('Test FAIL with a bad font...')
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


# If we ever reuse this helper function,
# then move it into fontbakery.utils:
def results_contain(results, expected_status, expected_code):
  for status, message in results:
    if status == expected_status and message.code == expected_code:
      return True
  # else
  return False


def test_id_033():
  """ Checking correctness of monospaced metadata. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_033 as test,
                                                     monospace_stats)
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

  # This test has a large number of code-paths
  # We'll make sure to test them all here.
  #
  # --------------------------------------------
  # Starting with non-monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good non-monospace font...')
  # Our reference Mada Regular is a non-monospace font
  # know to have good metadata for this test.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  stats = monospace_stats(ttFont)
  status, message = list(test(ttFont, stats))[-1]
  assert status == PASS and message.code == "good"

  # We'll mark it as monospaced on the post table and make sure it fails:
  print('Test FAIL with a non-monospaced font with bad post.isFixedPitch value ...')
  ttFont["post"].isFixedPitch = IS_FIXED_WIDTH__MONOSPACED
  status, message = list(test(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-post-isFixedPitch"

  # restore good value:
  ttFont["post"].isFixedPitch = IS_FIXED_WIDTH__NOT_MONOSPACED

  # Now we mark it as monospaced on the OS/2 and it should also fail:
  print('Test FAIL with a non-monospaced font with bad OS/2.panose.bProportion value (MONOSPACED) ...')
  ttFont["OS/2"].panose.bProportion = PANOSE_PROPORTION__MONOSPACED
  status, message = list(test(ttFont, stats))[-1]
  assert status == FAIL and message.code == "bad-panose-proportion"

  # --------------------------------------------
  # And now we test the monospaced code-paths:
  # --------------------------------------------

  print('Test PASS with a good monospaced font...')
  # Our reference OverpassMono Regular is know to be
  # a monospaced font with good metadata here.
  ttFont = TTFont("data/test/overpassmono/OverpassMono-Regular.ttf")
  stats = monospace_stats(ttFont)
  status, message = list(test(ttFont, stats))[-1]
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
  results = list(test(ttFont, stats))
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
    print('Test FAIL with a monospaced font with bad OS/2.panose.bProportion value ({}) ...'.format(bad_value))
    ttFont["OS/2"].panose.bProportion = bad_value
    # again, we search the expected FAIL because we may algo get an outliers WARN here:
    results = list(test(ttFont, stats))
    assert results_contain(results, FAIL, "mono-bad-panose-proportion")


# TODO: test_id_034
# TODO: test_id_035
# TODO: test_id_036

def test_id_037():
  """ MS Font Validator checks """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_037 as test

  font = "data/test/mada/Mada-Regular.ttf"
  RASTER_EXCEPTION_MESSAGE = ("MS-FonVal: An exception occurred"
                              " during rasterization testing")
  # we want to run all FValidator tests only once,
  # so here we cache all results:
  fval_results = list(test(font))

  # Then we make sure that the freetype backend we're using
  # supports the hinting instructions validation tests,
  # which are refered to as "rasterization testing":
  # (See also: https://github.com/googlefonts/fontbakery/issues/1524)
  for status, message in fval_results:
    assert RASTER_EXCEPTION_MESSAGE not in message

  # and finaly, we make sure that there wasn't an ERROR
  # which would mean FontValidator is not properly installed:
  assert status != ERROR

# TODO: test_id_038
# TODO: test_id_039

def test_id_040(mada_ttFonts):
  """ Checking OS/2 usWinAscent & usWinDescent. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_040 as test,
                                                     vmetrics)
  # Our reference Mada Regular is know to be bad here.
  vm = vmetrics(mada_ttFonts)
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But we fix it first to test the PASS code-path:
  print('Test PASS with a good font...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(test(ttFont, vm))[-1]
  assert status == PASS

  # Then we break it:
  print('Test FAIL with a bad OS/2.usWinAscent...')
  ttFont['OS/2'].usWinAscent = vm['ymax'] + 1
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(test(ttFont, vm))[-1]
  assert status == FAIL and message.code == "ascent"

  print('Test FAIL with a bad OS/2.usWinDescent...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin']) + 1
  status, message = list(test(ttFont, vm))[-1]
  assert status == FAIL and message.code == "descent"


def test_id_041():
  """ Checking Vertical Metric Linegaps. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_041 as test

  print('Test FAIL with non-zero hhea.lineGap...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But just to be sure we explicitely set the values we're testing for:
  ttFont['hhea'].lineGap = 1
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(test(ttFont))[-1]
  assert status == WARN and message.code == "hhea"

  # Then we test with a non-zero OS/2.sTypoLineGap:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 1
  status, message = list(test(ttFont))[-1]
  assert status == WARN and message.code == "OS/2"

  # And finaly we fix it by making both values equal to zero:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(test(ttFont))[-1]
  assert status == PASS


def test_id_042(mada_ttFonts):
  """ Checking OS/2 Metrics match hhea Metrics. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_042 as test

  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # Now we break it:
  print('Test FAIL with a bad OS/2.sTypoAscender font...')
  correct = ttFont['hhea'].ascent
  ttFont['OS/2'].sTypoAscender = correct + 1
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "ascender"

  # Restore good value:
  ttFont['OS/2'].sTypoAscender = correct

  # And break it again, now on sTypoDescender value:
  print('Test FAIL with a bad OS/2.sTypoDescender font...')
  correct = ttFont['hhea'].descent
  ttFont['OS/2'].sTypoDescender = correct + 1
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "descender"


def test_id_043():
  """ Checking unitsPerEm value is reasonable. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_043 as test

  # In this test we'll forge several known-good and known-bad values.
  # We'll use Mada Regular to start with:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  for good_value in [1000, 16, 32, 64, 128, 256,
                     512, 1024, 2048, 4096, 8192, 16384]:
    print("Test PASS with a good value of unitsPerEm = {} ...".format(good_value))
    ttFont['head'].unitsPerEm = good_value
    status, message = list(test(ttFont))[-1]
    assert status == PASS

  # These are arbitrarily chosen bad values:
  for bad_value in [0, 1, 2, 4, 8, 10, 100, 10000, 32768]:
    print("Test FAIL with a bad value of unitsPerEm = {} ...".format(bad_value))
    ttFont['head'].unitsPerEm = bad_value
    status, message = list(test(ttFont))[-1]
    assert status == FAIL

# TODO: test_id_044

def test_id_045():
  """ Does the font have a DSIG table ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_045 as test

  # Our reference Cabin Regular font is good (theres a DSIG table declared):
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # Then we remove the DSIG table so that we get a FAIL:
  print ("Test FAIL with a font lacking a DSIG table...")
  del ttFont['DSIG']
  status, message = list(test(ttFont))[-1]
  assert status == FAIL

# TODO: test_id_046

def test_id_047():
  """ Font contains glyphs for whitespace characters ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_047 as test,
                                                     missing_whitespace_chars)
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  missing = missing_whitespace_chars(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont, missing))[-1]
  assert status == PASS

  # Then we remove the nbsp char (0x00A0) so that we get a FAIL:
  print ("Test FAIL with a font lacking a nbsp (0x00A0)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(test(ttFont, missing))[-1]
  assert status == FAIL

  # restore original Mada Regular font:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # And finally remove the space character (0x0020) to get another FAIL:
  print ("Test FAIL with a font lacking a space (0x0020)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(test(ttFont, missing))[-1]
  assert status == FAIL


def test_id_048():
  """ Font has **proper** whitespace glyph names ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_048 as test
  from fontbakery.utils import deleteGlyphEncodings

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  print ("Test SKIP with post.formatType == 3.0 ...")
  value = ttFont["post"].formatType
  ttFont["post"].formatType = 3.0
  status, message = list(test(ttFont))[-1]
  assert status == SKIP
  # and restore good value:
  ttFont["post"].formatType = value

  print ("Test FAIL with bad glyph name for char 0x0020 ...")
  deleteGlyphEncodings(ttFont, 0x0020)
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "bad20"

  # restore the original font object in preparation for the next test-case:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print ("Test FAIL with bad glyph name for char 0x00A0 ...")
  deleteGlyphEncodings(ttFont, 0x00A0)
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "badA0"

# TODO: test_id_049
# TODO: test_id_050 (the original test itself has unclear semantics, so that needs to be reviewed first)

# DEPRECATED:
# com.google.fonts/test/051 - "Checking with pyfontaine"
#
# Replaced by:
# com.google.fonts/test/132 - "Checking Google Cyrillic Historical glyph coverage"
# com.google.fonts/test/133 - "Checking Google Cyrillic Plus glyph coverage"
# com.google.fonts/test/134 - "Checking Google Cyrillic Plus (Localized Forms) glyph coverage"
# com.google.fonts/test/135 - "Checking Google Cyrillic Pro glyph coverage"
# com.google.fonts/test/136 - "Checking Google Greek Ancient Musical Symbols glyph coverage"
# com.google.fonts/test/137 - "Checking Google Greek Archaic glyph coverage"
# com.google.fonts/test/138 - "Checking Google Greek Coptic glyph coverage"
# com.google.fonts/test/139 - "Checking Google Greek Core glyph coverage"
# com.google.fonts/test/140 - "Checking Google Greek Expert glyph coverage"
# com.google.fonts/test/141 - "Checking Google Greek Plus glyph coverage"
# com.google.fonts/test/142 - "Checking Google Greek Pro glyph coverage"
# com.google.fonts/test/143 - "Checking Google Latin Core glyph coverage"
# com.google.fonts/test/144 - "Checking Google Latin Expert glyph coverage"
# com.google.fonts/test/145 - "Checking Google Latin Plus glyph coverage"
# com.google.fonts/test/146 - "Checking Google Latin Plus (Optional Glyphs) glyph coverage"
# com.google.fonts/test/147 - "Checking Google Latin Pro glyph coverage"
# com.google.fonts/test/148 - "Checking Google Latin Pro (Optional Glyphs) glyph coverage"


def test_id_052():
  """ Font contains all required tables ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_052 as test

  required_tables = ["cmap", "head", "hhea", "hmtx",
                     "maxp", "name", "OS/2", "post"]
  optional_tables = ["cvt ", "fpgm", "loca", "prep",
                     "VORG", "EBDT", "EBLC", "EBSC",
                     "BASE", "GPOS", "GSUB", "JSTF",
                     "DSIG", "gasp", "hdmx", "kern",
                     "LTSH", "PCLT", "VDMX", "vhea",
                     "vmtx"]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # We now remove required tables one-by-one to validate the FAIL code-path:
  for required in required_tables:
    print ("Test FAIL with missing mandatory table {} ...".format(required))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    if required in ttFont.reader.tables:
      del ttFont.reader.tables[required]
    status, message = list(test(ttFont))[-1]
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
    status, message = list(test(ttFont))[-2]
    assert status == INFO
    # remove the one we've just inserted before trying the next one:
    del ttFont.reader.tables[optional]


def test_id_053():
  """ Are there unwanted tables ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_053 as test

  unwanted_tables = ["FFTM", "TTFA", "prop"]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # We now add unwanted tables one-by-one to validate the FAIL code-path:
  for unwanted in unwanted_tables:
    print ("Test FAIL with unwanted table {} ...".format(unwanted))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    ttFont.reader.tables[unwanted] = "foo"
    status, message = list(test(ttFont))[-1]
    assert status == FAIL

# TODO: test_id_054

def test_id_055():
  """ Version format is correct in 'name' table ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_055 as test
  from fontbakery.constants import NAMEID_VERSION_STRING

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # then we introduce bad strings in all version-string entries:
  print ("Test FAIL with bad version format in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      invalid = "invalid-version-string".encode(name.getEncoding())
      ttFont["name"].names[i].string = invalid
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "bad-version-strings"

  # and finally we remove all version-string entries:
  print ("Test FAIL with font lacking version string entries in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      del ttFont["name"].names[i]
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "no-version-string"

# TODO: test_id_056

def test_id_057():
  """ Name table entries should not contain line-breaks. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_057 as test

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  print ("Test FAIL with name entries containing a linebreak...")
  for i in range(len(ttFont["name"].names)):
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    encoding = ttFont["name"].names[i].getEncoding()
    ttFont["name"].names[i].string = "bad\nstring".encode(encoding)
    status, message = list(test(ttFont))[-1]
    assert status == FAIL

# TODO: test_id_058
# TODO: test_id_059
# TODO: test_id_060

def test_id_061():
  """ EPAR table present in font ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_061 as test

  # Our reference Mada Regular lacks an EPAR table:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must emit an INFO message inviting the designers
  # to learn more about it:
  print ("Test INFO with a font lacking an EPAR table...")
  status, message = list(test(ttFont))[-1]
  assert status == INFO

  print ("Test PASS with a good font...")
  # add a fake EPAR table to validate the PASS code-path:
  ttFont["EPAR"] = "foo"
  status, message = list(test(ttFont))[-1]
  assert status == PASS

# TODO: test_id_062

def test_id_063():
  """ Does GPOS table have kerning information ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_063 as test

  # Our reference Mada Regular is known to have kerning-info
  # exclusively on an extension subtable
  # (lookup type = 9 / ext-type = 2):
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a font that has got kerning info...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # delete all Pair Adjustment lookups:
  while True:
    found = False
    for l, lookup in enumerate(ttFont["GPOS"].table.LookupList.Lookup):
      #if lookup.LookupType == 2:  # type 2 = Pair Adjustment
      #  del ttFont["GPOS"].table.LookupList.Lookup[l]
      #  found = True
      if lookup.LookupType == 9:  # type 9 = Extension subtable
        for e, ext in enumerate(lookup.SubTable):
          if ext.ExtensionLookupType == 2:  # type 2 = Pair Adjustment
            del ttFont["GPOS"].table.LookupList.Lookup[l].SubTable[e]
            found = True
    if not found:
      break

  print ("Test WARN with a font lacking kerning info...")
  status, message = list(test(ttFont))[-1]
  assert status == WARN

  # setup a fake type=2 Pair Adjustment lookup
  ttFont["GPOS"].table.LookupList.Lookup[0].LookupType = 2
  # and make sure the test emits a PASS result:
  print ("Test PASS with kerning info on a type=2 lookup...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # remove the GPOS table and make sure to get a WARN:
  del ttFont["GPOS"]
  print ("Test WARN with a font lacking a GPOS table...")
  status, message = list(test(ttFont))[-1]
  assert status == WARN


def test_id_064():
  """ Is there a caret position declared for every ligature ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_064 as test,
                                                     ligatures)

  # TODO: We currently lack a reference family that PASSes this test!

  # Our reference Mada Medium is known to be bad
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")
  lig = ligatures(ttFont)

  # So it must emit a WARN:
  print ("Test WARN with a bad font...")
  status, message = list(test(ttFont, lig))[-1]
  assert status == WARN and message.code == "lacks-caret-pos"

  # And FamilySans Regular is known to be bad
  ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")
  lig = ligatures(ttFont)

  # So it must emit a WARN:
  print ("Test WARN with a bad font...")
  status, message = list(test(ttFont, lig))[-1]
  assert status == WARN and message.code == "GDEF-missing"

  # TODO: test the WARN "incomplete-caret-pos-data" codepath


def test_id_065():
  """ Is there kerning info for non-ligated sequences ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_065 as test,
                                                     has_kerning_info,
                                                     ligatures)
  # Our reference Mada Medium is known to be good
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")
  lig = ligatures(ttFont)
  has_kinfo = has_kerning_info(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont, lig, has_kinfo))[-1]
  assert status == PASS

  # And Merriweather Regular is known to be bad
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  lig = ligatures(ttFont)
  has_kinfo = has_kerning_info(ttFont)

  # So it must FAIL the test:
  print ("Test FAIL with a bad font...")
  status, message = list(test(ttFont, lig, has_kinfo))[-1]
  assert status == FAIL


def test_id_066():
  """ Is there a "KERN" table declared in the font ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_066 as test

  # Our reference Mada Regular is known to be good
  # (does not have a KERN table):
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a font without a KERN table...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # add a fake KERN table:
  ttFont["KERN"] = "foo"

  # and make sure the test FAILs:
  print ("Test FAIL with a font containing a KERN table...")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def test_id_067():
  """ Make sure family name does not begin with a digit. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_067 as test
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME

  # Our reference Mada Regular is known to be good
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # alter the family-name prepending a digit:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      ttFont["name"].names[i].string = "1badname".encode(name.getEncoding())

  # and make sure the test FAILs:
  print ("Test FAIL with a font in which the family name begins with a digit...")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def test_id_068():
  """ Does full font name begin with the font family name ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_068 as test
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME)
  # Our reference Mada Regular is known to be good
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # alter the full-font-name prepending a bad prefix:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      ttFont["name"].names[i].string = "bad-prefix".encode(name.getEncoding())

  # and make sure the test FAILs:
  print ("Test FAIL with a font in which the family name begins with a digit...")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "does-not"

  print ("Test FAIL with no FULL_FONT_NAME entries...")
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      del ttFont["name"].names[i]
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "no-full-font-name"

  print ("Test FAIL with no FONT_FAMILY_NAME entries...")
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      del ttFont["name"].names[i]
  status, message = list(test(ttFont))[-1]
  assert status == FAIL and message.code == "no-font-family-name"

# TODO: test/069

def test_id_070():
  """ Font has all expected currency sign characters ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_070 as test

  # Our reference Mada Medium is known to be good
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # And FamilySans Regular is known to be bad
  ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")

  # So it must FAIL the test:
  print ("Test FAIL with a bad font...")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def assert_name_table_check_result(ttFont, index, name, test, value, expected_result):
  backup = name.string
  # set value
  ttFont["name"].names[index].string = value.encode(name.getEncoding())
  # run test
  status, message = list(test(ttFont))[-1]
  # restore value
  ttFont["name"].names[index].string = backup
  assert status == expected_result


def test_id_071():
  """ Font follows the family naming recommendations ? """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_071 as test
  from fontbakery.constants import (NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  # Our reference Mada Medium is known to be good
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # We'll test rule violations in all entries one-by-one
  for index, name in enumerate(ttFont["name"].names):
    # and we'll test all INFO/PASS code-paths for each of the rules:
    def name_test(value, expected):
      assert_name_table_check_result(ttFont, index, name, test, value, expected) #pylint: disable=cell-var-from-loop

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

  for w in range(0, 1000, 50):
    ttFont["OS/2"].usWeightClass = w
    if w < 250 or w > 900:
      print ("Test FAIL: Weight out of acceptable range of values (from 250 to 900)...")
      status, message = list(test(ttFont))[-1]
      assert status == INFO
    else:
      print ("Test PASS: Weight value is between 250 and 900 (including the extreme values)...")
      status, message = list(test(ttFont))[-1]
      assert status == PASS

  for w in [251, 275, 325, 425, 775, 825, 899]:
    ttFont["OS/2"].usWeightClass = w
    print ("Test FAIL: Weight value is not multiple of 50...")
    status, message = list(test(ttFont))[-1]
    assert status == INFO

# TODO: tests 072 to 093

def test_id_094():
  """ METADATA.pb font.fullname value matches fullname declared on the name table ? """
  from fontbakery.specifications.googlefonts import font_metadata
  from fontbakery.specifications.googlefonts import com_google_fonts_test_094 as test
  from fontbakery.constants import NAMEID_FULL_FONT_NAME

  print('Test PASS with a good font...')
  # Our reference Merriweather-Regular is know to be good here
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  font_meta = font_metadata(ttFont)
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == PASS

  print('Test FAIL with mismatching fullname values...')
  good = font_meta.full_name
  # here we change the font.fullname on the METADATA.pb
  # to introduce a "mismatch" error condition:
  font_meta.full_name = good + "bad-suffix"
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "mismatch"

  # and restore the good value prior to the next test case:
  font_meta.full_name = good

  print('Test FAIL when a font lacks FULL_FONT_NAME entries in its name table...')
  # And here we remove all FULL_FONT_NAME entries
  # in order to get a "lacks-entry" error condition:
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      del ttFont["name"].names[i]
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "lacks-entry"


def test_id_095():
  """ METADATA.pb font.name value should be same as the family name declared on the name table. """
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_095 as test,
                                                     font_metadata,
                                                     style)
  print('Test PASS with a good font...')
  # Our reference Merriweather-Regular is know to have good fullname metadata
  font = "data/test/merriweather/Merriweather-Regular.ttf"
  ttFont = TTFont(font)
  font_meta = font_metadata(ttFont)
  font_style = style(font)
  status, message = list(test(ttFont, font_style, font_meta))[-1]
  assert status == PASS

  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      good = name.string.decode(name.getEncoding()) # keep a copy of the good value
      print("Test FAIL with a bad FULL_FONT_NAME entry...")
      ttFont["name"].names[i].string = (good + "bad-suffix").encode(name.getEncoding())
      status, message = list(test(ttFont, font_style, font_meta))[-1]
      assert status == FAIL
      ttFont["name"].names[i].string = good # restore good value

# TODO: test/096

# TODO: test/097

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

def test_id_098():
  """ METADATA.pb font.name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_098 as test,
                                                     style,
                                                     font_metadata,
                                                     font_familynames,
                                                     typographic_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(ttFont.reader.file.name)
    font_meta = font_metadata(ttFont)
    font_fnames = font_familynames(ttFont)
    font_tfnames = []

    # So it must PASS the test:
    print ("Test PASS with a good RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_fnames = ["WrongFamilyName"]
    print ("Test FAIL with a bad RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL

  #we do the same for NON-RIBBI styles:
  for fontfile in MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(ttFont.reader.file.name)
    font_meta = font_metadata(ttFont)
    font_fnames = []
    font_tfnames = typographic_familynames(ttFont)

    # So it must PASS the test:
    print ("Test PASS with a good NON-RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_tfnames = ["WrongFamilyName"]
    print ("Test FAIL with a bad NON_RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL


def test_id_099():
  """ METADATA.pb font.full_name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_099 as test,
                                                     style,
                                                     font_metadata,
                                                     font_familynames,
                                                     typographic_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(ttFont.reader.file.name)
    font_meta = font_metadata(ttFont)
    font_fnames = font_familynames(ttFont)
    font_tfnames = []

    # So it must PASS the test:
    print ("Test PASS with a good RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_fnames = ["WrongFamilyName"]
    print ("Test FAIL with a bad RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL

  #we do the same for NON-RIBBI styles:
  for fontfile in MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_style = style(ttFont.reader.file.name)
    font_meta = font_metadata(ttFont)
    font_fnames = []
    font_tfnames = typographic_familynames(ttFont)

    # So it must PASS the test:
    print ("Test PASS with a good NON-RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == PASS

    # And fail if it finds a bad font_familyname:
    font_tfnames = ["WrongFamilyName"]
    print ("Test FAIL with a bad NON_RIBBI font ({})...".format(fontfile))
    status, message = list(test(font_style, font_meta, font_fnames, font_tfnames))[-1]
    assert status == FAIL


def test_id_100():
  """ METADATA.pb font.filename field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_100 as test,
                                                     font_metadata)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_meta = font_metadata(ttFont)

    # So it must PASS the test:
    print ("Test PASS with a good font ({})...".format(fontfile))
    status, message = list(test(ttFont, font_meta))[-1]
    assert status == PASS

    # And fail if it finds a bad filename:
    font_meta.filename = "WrongFileName"
    print ("Test FAIL with a bad font ({})...".format(fontfile))
    status, message = list(test(ttFont, font_meta))[-1]
    assert status == FAIL


def test_id_101():
  """ METADATA.pb font.post_script_name field contains font name in right format ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_101 as test,
                                                     font_metadata,
                                                     font_familynames)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_meta = font_metadata(ttFont)
    font_fnames = font_familynames(ttFont)

    # So it must PASS the test:
    print ("Test PASS with a good font ({})...".format(fontfile))
    status, message = list(test(font_meta, font_fnames))[-1]
    assert status == PASS

    # And fail if it finds a bad filename:
    font_meta.post_script_name = "WrongPSName"
    print ("Test FAIL with a bad font ({})...".format(fontfile))
    status, message = list(test(font_meta, font_fnames))[-1]
    assert status == FAIL


def test_id_102():
  """ Copyright notice on METADATA.pb matches canonical pattern ? """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_102 as test,
                                                     metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be bad
  # Since it provides an email instead of a git URL:
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  font_meta = font_metadata(ttFont)

  # So it must FAIL the test:
  print ("Test FAIL with a bad copyright notice string...")
  status, message = list(test(font_meta))[-1]
  assert status == FAIL

  # Then we change it into a good string (example extracted from Archivo Black):
  font_meta.copyright = "Copyright 2017 The Archivo Black Project Authors (https://github.com/Omnibus-Type/ArchivoBlack)"
  print ("Test PASS with a good copyright notice string...")
  status, message = list(test(font_meta))[-1]
  assert status == PASS

# TODO: test/103
# TODO: test/104
# TODO: test/105

def test_id_106():
  """ METADATA.pb font.style "italic" matches font internals ? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    MACSTYLE_ITALIC)
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_106 as test,
                                                     font_metadata)
  # Our reference Merriweather Italic is known to good
  ttFont = TTFont("data/test/merriweather/Merriweather-Italic.ttf")
  font_meta = font_metadata(ttFont)

  # So it must PASS:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == PASS

  # now let's introduce issues on the FULL_FONT_NAME entries
  # to test the "bad-fullfont-name codepath:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "BAD VALUE".encode(name.getEncoding())
      print ("Test FAIL with a bad NAMEID_FULL_FONT_NAME entry...")
      status, message = list(test(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "bad-fullfont-name"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And, finally, let's flip off that italic bit
  # and get a "bad-macstyle" error (so much fun!):
  print ("Test FAIL with bad macstyle bit value...")
  ttFont['head'].macStyle &= ~MACSTYLE_ITALIC
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == FAIL and message.code == "bad-macstyle"


def test_id_107():
  """ METADATA.pb font.style "normal" matches font internals ? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    MACSTYLE_ITALIC)
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_107 as test,
                                                     font_metadata)
  # This one is pretty similar to test/106
  # You may want to take a quick look above...
  # Our reference Merriweather Regular is known to be good here.
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  font_meta = font_metadata(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == PASS

  # now we sadically insert brokenness into
  # each occurrence of the FONT_FAMILY_NAME nameid:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
      print ("Test FAIL with a non-italic font that has a '-Italic' in FONT_FAMILY_NAME...")
      status, message = list(test(ttFont, font_meta))[-1]
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
      status, message = list(test(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "fullfont-italic"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And, finally, again, we flip a bit and
  # get a "bad-macstyle" error:
  print ("Test FAIL with bad macstyle bit value...")
  # But this time the boolean logic is the quite opposite in
  # comparition to the 106 selt-test above. Here we have to set the
  # bit back to 1 to get a wrongful "this font is an italic" setting:
  ttFont['head'].macStyle |= MACSTYLE_ITALIC
  status, message = list(test(ttFont, font_meta))[-1]
  # Not it's not! FAIL! :-D
  assert status == FAIL and message.code == "bad-macstyle"

def test_id_108():
  """ METADATA.pb font.name and font.full_name fields match the values declared on the name table? """
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME)
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_108 as test,
                                                     font_metadata)
  # Our reference Merriweather Regular is known to be good here.
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  font_meta = font_metadata(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == PASS

  # There we go again:
  # breaking FULL_FONT_NAME entries
  # one by one:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "This is utterly wrong!".encode(name.getEncoding())
      print ("Test FAIL with a METADATA.pb / FULL_FONT_NAME mismatch...")
      status, message = list(test(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "fullname-mismatch"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

  # And then we do the same with FONT_FAMILY_NAME entries:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_FONT_FAMILY_NAME:
      backup = name.string
      ttFont['name'].names[i].string = "I'm listening to deadmau5 :-)".encode(name.getEncoding())
      print ("Test FAIL with a METADATA.pb / FONT_FAMILY_NAME mismatch...")
      status, message = list(test(ttFont, font_meta))[-1]
      assert status == FAIL and message.code == "familyname-mismatch"
      # and restore the good value:
      ttFont['name'].names[i].string = backup

def test_id_109():
  """ Check if fontname is not camel cased. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_109 as test,
                                                     metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  font_meta = font_metadata(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(font_meta))[-1]
  assert status == PASS

  # Then we FAIL with a CamelCased name:
  font_meta.name = "GollyGhost"
  print ("Test FAIL with a bad font (CamelCased font name)...")
  status, message = list(test(font_meta))[-1]
  assert status == FAIL

  # And we also make sure the test passes with a few known good names:
  good_names = ["VT323", "PT Sans", "Amatic SC"]
  for good_name in good_names:
    font_meta.name = good_name
    print ("Test PASS with a good font name '{}'...".format(good_name))
    status, message = list(test(font_meta))[-1]
    assert status == PASS


def test_id_110():
  """ Check font name is the same as family name. """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_110 as test,
                                                     metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  font_meta = font_metadata(ttFont)
  family_meta = metadata("data/test/cabin/")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(family_meta, font_meta))[-1]
  assert status == PASS

  # Then we FAIL with mismatching names:
  family_meta.name = "Some Fontname"
  font_meta.name = "Something Else"
  print ("Test FAIL with a bad font...")
  status, message = list(test(family_meta, font_meta))[-1]
  assert status == FAIL

# TODO: test/111

def test_id_112():
  """ Checking OS/2 usWeightClass matches weight specified at METADATA.pb """
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_112 as test,
                                                     font_metadata)
  # Our reference Montserrat family is a good 18-styles family:
  for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
    ttFont = TTFont(fontfile)
    font_meta = font_metadata(ttFont)

    # So it must PASS the test:
    print ("Test PASS with a good font ({})...".format(fontfile))
    status, message = list(test(ttFont, font_meta))[-1]
    assert status == PASS

    # And fail if it finds a bad weight value:
    good_value = font_meta.weight
    bad_value = good_value + 50
    font_meta.weight = bad_value
    print ("Test FAIL with a bad font ({})...".format(fontfile))
    status, message = list(test(ttFont, font_meta))[-1]
    assert status == FAIL

# TODO: test/113

# DEPRECATED: com.google.fonts/test/114

# TODO: tests 115 to 131

# DEPRECATED CHECKS:
# com.google.fonts/test/132 - "Checking Cyrillic Historical glyph coverage."
# com.google.fonts/test/133 - "Checking Google Cyrillic Plus glyph coverage."
# com.google.fonts/test/134 - "Checking Google Cyrillic Plus (Localized Forms) glyph coverage."
# com.google.fonts/test/135 - "Checking Google Cyrillic Pro glyph coverage."
# com.google.fonts/test/136 - "Checking Google Greek Ancient Musical Symbols glyph coverage."
# com.google.fonts/test/137 - "Checking Google Greek Archaic glyph coverage."
# com.google.fonts/test/138 - "Checking Google Greek Coptic glyph coverage."
# com.google.fonts/test/139 - "Checking Google Greek Core glyph coverage."
# com.google.fonts/test/140 - "Checking Google Greek Expert glyph coverage."
# com.google.fonts/test/141 - "Checking Google Greek Plus glyph coverage."
# com.google.fonts/test/142 - "Checking Google Greek Pro glyph coverage."
# com.google.fonts/test/143 - "Checking Google Latin Core glyph coverage."
# com.google.fonts/test/144 - "Checking Google Latin Expert glyph coverage."
# com.google.fonts/test/145 - "Checking Google Latin Plus glyph coverage."
# com.google.fonts/test/146 - "Checking Google Latin Plus (Optional Glyphs) glyph coverage."
# com.google.fonts/test/147 - "Checking Google Latin Pro glyph coverage."
# com.google.fonts/test/148 - "Checking Google Latin Pro (Optional Glyphs) glyph coverage."
# com.google.fonts/test/149 - "Checking Google Arabic glyph coverage."
# com.google.fonts/test/150 - "Checking Google Vietnamese glyph coverage."
# com.google.fonts/test/151 - "Checking Google Extras glyph coverage."

# TODO: test_id_152

def test_id_153(montserrat_ttFonts):
  """Check glyphs contain the recommended contour count"""
  from fontbakery.specifications.googlefonts import com_google_fonts_test_153 as test

  # Montserrat should pass this test since it was used to assemble the glyph data
  for ttFont in montserrat_ttFonts:
    status, message = list(test(ttFont))[-1]
    assert status == PASS

  # Lets swap the glyf a (2 contours) with glyf c (1 contour)
  for ttFont in montserrat_ttFonts:
    ttFont['glyf']['a'] = ttFont['glyf']['c']
    status, message = list(test(ttFont))[-1]
    assert status == WARN


def test_id_154(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    from fontbakery.specifications.googlefonts import (com_google_fonts_test_154 as test,
                                                       gfonts_ttFont,
                                                       remote_styles,
                                                       metadata)
    font = cabin_ttFonts[-1]
    print(cabin_ttFonts)
    style = font['name'].getName(2, 1, 0, 0)

    meta = metadata("data/test/regression/cabin/")
    gfonts_remote_styles = remote_styles(meta)
    gfont = gfonts_ttFont(str(style), gfonts_remote_styles)

    # Cabin font hosted on fonts.google.com contains all the glyphs for the font in
    # data/test/cabin
    status, message = list(test(font, gfont))[-1]
    assert status == PASS

    # Take A glyph out of font
    font['cmap'].getcmap(3, 1).cmap.pop(ord('A'))
    font['glyf'].glyphs.pop('A')

    status, message = list(test(font, gfont))[-1]
    assert status == FAIL


def test_id_155():
  """ Copyright field for this font on METADATA.pb matches
      all copyright notice entries on the name table ? """
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.specifications.googlefonts import (com_google_fonts_test_155 as test,
                                                     metadata,
                                                     font_metadata)
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  font_meta = font_metadata(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good METADATA.pb for this font...")
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == PASS

  # Then we FAIL with mismatching names:
  good_value = get_name_entry_strings(ttFont, NAMEID_COPYRIGHT_NOTICE)[0]
  font_meta.copyright = good_value + "something bad"
  print ("Test FAIL with a bad METADATA.pb (with a copyright string not matching this font)...")
  status, message = list(test(ttFont, font_meta))[-1]
  assert status == FAIL


def test_id_156():
  """ Font has all mandatory 'name' table entries ? """
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  from fontbakery.specifications.googlefonts import com_google_fonts_test_156 as test

  # We'll check both RIBBI and non-RIBBI fonts
  # so that we cover both cases for FAIL/PASS scenarios

  #First with a RIBBI font:
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  style = "Regular"

  # So it must PASS the test:
  print ("Test PASS with a good RIBBI font...")
  status, message = list(test(ttFont, style))[-1]
  assert status == PASS

  mandatory_entries = [NAMEID_FONT_FAMILY_NAME,
                       NAMEID_FONT_SUBFAMILY_NAME,
                       NAMEID_FULL_FONT_NAME,
                       NAMEID_POSTSCRIPT_NAME]

  # then we remove each mandatory entry
  # one by one:
  for mandatory in [mandatory_entries]:
    for i, name in enumerate(ttFont['name'].names):
      if name.nameID == mandatory:
        del ttFont['name'].names[i]
        print ("Test FAIL with a missing madatory (RIBBI) name entry...")
        status, message = list(test(ttFont, style))[-1]
        assert status == FAIL

  #And now a non-RIBBI font:
  # Our reference Merriweather Black is known to be good
  ttFont = TTFont("data/test/merriweather/Merriweather-Black.ttf")
  style = "Black"

  # So it must PASS the test:
  print ("Test PASS with a good non-RIBBI font...")
  status, message = list(test(ttFont, style))[-1]
  assert status == PASS

  mandatory_entries = [NAMEID_FONT_FAMILY_NAME,
                       NAMEID_FONT_SUBFAMILY_NAME,
                       NAMEID_FULL_FONT_NAME,
                       NAMEID_POSTSCRIPT_NAME,
                       NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                       NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME]

  # then we (again) remove each mandatory entry
  # one by one:
  for mandatory in [mandatory_entries]:
    for i, name in enumerate(ttFont['name'].names):
      if name.nameID == mandatory:
        del ttFont['name'].names[i]
        print ("Test FAIL with a missing madatory (non-RIBBI) name entry...")
        status, message = list(test(ttFont, style))[-1]
        assert status == FAIL

# TODO: test_id_157
# TODO: test_id_158

def test_id_159():
  """ Check name table: FULL_FONT_NAME entries. """
  from fontbakery.constants import NAMEID_FULL_FONT_NAME
  from fontbakery.specifications.googlefonts import com_google_fonts_test_159 as test

  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good Regular font...")
  status, message = list(test(ttFont, "Regular", "Cabin"))[-1]
  assert status == PASS

  # Let's now test the Regular exception
  # ('Regular' can be optionally ommited on the FULL_FONT_NAME entry):
  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont["name"].names[index].string = "Cabin".encode(name.getEncoding())
      print ("Test WARN with a good Regular font that omits 'Regular' on FULL_FONT_NAME...")
      status, message = list(test(ttFont, "Regular", "Cabin"))[-1]
      assert status == WARN
      # restore it:
      ttFont["name"].names[index].string = backup

  # Let's also make sure our good reference Cabin BoldItalic PASSes the test:
  # This also tests the splitting of filename infered style with a space char
  ttFont = TTFont("data/test/cabin/Cabin-BoldItalic.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good Bold Italic font...")
  status, message = list(test(ttFont, "BoldItalic", "Cabin"))[-1]
  assert status == PASS

  # And here we test the FAIL codepath:
  for index, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_FULL_FONT_NAME:
      backup = name.string
      ttFont["name"].names[index].string = "MAKE IT FAIL".encode(name.getEncoding())
      print ("Test FAIL with a bad FULL_FONT_NAME entry...")
      status, message = list(test(ttFont, "BoldItalic", "Cabin"))[-1]
      assert status == FAIL
      # restore it:
      ttFont["name"].names[index].string = backup

# TODO: test_id_160
# TODO: test_id_161
# TODO: test_id_162

def test_id_163():
  """ Check font name is the same as family name. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_163 as test
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME)
  # Our reference Cabin Regular is known to be good
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  # Then we FAIL with the long family/style names
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

  print ("Test FAIL with a bad font...")
  status, message = list(test(ttFont))[-1]
  assert status == FAIL


def test_id_164():
  """ Length of copyright notice must not exceed 500 characters. """
  from fontbakery.specifications.googlefonts import com_google_fonts_test_164 as test
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE

  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  print('Test PASS with 499-byte copyright notice string...')
  good_entry = 'a' * 499
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  print('Test PASS with 500-byte copyright notice string...')
  good_entry = 'a' * 500
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
  status, message = list(test(ttFont))[-1]
  assert status == PASS

  print('Test FAIL with 501-byte copyright notice string...')
  bad_entry = 'a' * 501
  for i, entry in enumerate(ttFont['name'].names):
    if entry.nameID == NAMEID_COPYRIGHT_NOTICE:
      ttFont['name'].names[i].string = bad_entry.encode(entry.getEncoding())
  status, message = list(test(ttFont))[-1]
  assert status == FAIL
