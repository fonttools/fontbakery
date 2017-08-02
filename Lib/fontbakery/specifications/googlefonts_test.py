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
  from fontbakery.specifications.googlefonts import \
                                  check_file_is_named_canonically
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
    status, message = list(check_file_is_named_canonically(canonical))[-1]
    assert status == PASS

  print('Test FAIL ...')
  for non_canonical in non_canonical_names:
    status, message = list(check_file_is_named_canonically(non_canonical))[-1]
    assert status == FAIL


def test_id_002():
  """ Fonts are all in the same directory. """
  from fontbakery.specifications.googlefonts import \
                                  check_all_files_in_a_single_directory
  same_dir = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  multiple_dirs = [
    "data/test/mada/Mada-Regular.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  print('Test PASS with same dir: {}'.format(same_dir))
  status, message = list(check_all_files_in_a_single_directory(same_dir))[-1]
  assert status == PASS

  print('Test FAIL with multiple dirs: {}'.format(multiple_dirs))
  status, message = list(check_all_files_in_a_single_directory(multiple_dirs))[-1]
  assert status == FAIL


def test_id_003():
  """ Does DESCRIPTION file contain broken links ? """
  from unidecode import unidecode
  from fontbakery.specifications.googlefonts import \
                                  (check_DESCRIPTION_file_contains_no_broken_links,
                                   description,
                                   descfile)

  good_desc = description(descfile("data/test/cabin/"))
  print('Test PASS with description file that has no links...')
  status, message = list(check_DESCRIPTION_file_contains_no_broken_links(good_desc))[-1]
  assert status == PASS

  good_desc = unidecode(good_desc.decode("utf8")) + \
     "<a href='http://example.com'>Good Link</a>" + \
     "<a href='http://fonts.google.com'>Another Good One</a>"
  print('Test PASS with description file that has good links...')
  status, message = list(check_DESCRIPTION_file_contains_no_broken_links(good_desc))[-1]
  assert status == PASS

  good_desc += "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
  print('Test FAIL with a description file containing a mailto links...')
  status, message = list(check_DESCRIPTION_file_contains_no_broken_links(good_desc))[-1]
  assert status == PASS

  bad_desc = good_desc + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
  print('Test FAIL with a description file containing a known-bad URL...')
  status, message = list(check_DESCRIPTION_file_contains_no_broken_links(bad_desc))[-1]
  assert status == FAIL


def test_id_004():
  """ DESCRIPTION file is a propper HTML snippet ? """
  from fontbakery.specifications.googlefonts import \
                                  (check_DESCRIPTION_is_propper_HTML_snippet,
                                   descfile)

  good_descfile = descfile("data/test/nunito/")
  print('Test PASS with description file that contains a good HTML snippet...')
  status, message = list(check_DESCRIPTION_is_propper_HTML_snippet(good_descfile))[-1]
  assert status == PASS

  bad_descfile = "data/test/cabin/FONTLOG.txt" # :-)
  print('Test FAIL with a known-bad file (a txt file without HTML snippets)...')
  status, message = list(check_DESCRIPTION_is_propper_HTML_snippet(bad_descfile))[-1]
  assert status == FAIL


def test_id_005():
  """ DESCRIPTION.en_us.html must have more than 200 bytes. """
  from fontbakery.specifications.googlefonts import \
                                  check_DESCRIPTION_min_length
  good_length = 'a' * 199
  print('Test FAIL with 199-byte buffer...')
  status, message = list(check_DESCRIPTION_min_length(good_length))[-1]
  assert status == FAIL

  good_length = 'a' * 200
  print('Test FAIL with 200-byte buffer...')
  status, message = list(check_DESCRIPTION_min_length(good_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 201
  print('Test PASS with 201-byte buffer...')
  status, message = list(check_DESCRIPTION_min_length(bad_length))[-1]
  assert status == PASS


def test_id_006():
  """ DESCRIPTION.en_us.html must have less than 1000 bytes. """
  from fontbakery.specifications.googlefonts import \
                                  check_DESCRIPTION_max_length
  bad_length = 'a' * 1001
  print('Test FAIL with 1001-byte buffer...')
  status, message = list(check_DESCRIPTION_max_length(bad_length))[-1]
  assert status == FAIL

  bad_length = 'a' * 1000
  print('Test FAIL with 1000-byte buffer...')
  status, message = list(check_DESCRIPTION_max_length(bad_length))[-1]
  assert status == FAIL

  good_length = 'a' * 999
  print('Test PASS with 999-byte buffer...')
  status, message = list(check_DESCRIPTION_max_length(good_length))[-1]
  assert status == PASS


def test_id_007():
  """ Font designer field in METADATA.pb must not be 'unknown'. """
  from fontbakery.specifications.googlefonts import \
                                  (check_font_designer_field_is_not_unknown,
                                   metadata)
  good = metadata("data/test/merriweather/")
  print('Test PASS with a good METADATA.pb file...')
  status, message = list(check_font_designer_field_is_not_unknown(good))[-1]
  assert status == PASS

  bad = metadata("data/test/merriweather/")
  bad.designer = "unknown"
  print('Test FAIL with a bad METADATA.pb file...')
  status, message = list(check_font_designer_field_is_not_unknown(bad))[-1]
  assert status == FAIL


def test_id_008(mada_ttFonts):
  """ Fonts have consistent underline thickness ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_underline_thickness

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_underline_thickness(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wronge value in one of the font files:
  value = mada_ttFonts[0]['post'].underlineThickness
  incorrect_value = value + 1
  mada_ttFonts[0]['post'].underlineThickness = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_underline_thickness(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_009(mada_ttFonts):
  """ Fonts have consistent PANOSE proportion ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_PANOSE_proportion

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_PANOSE_proportion(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bProportion
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bProportion = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_PANOSE_proportion(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_010(mada_ttFonts):
  """ Fonts have consistent PANOSE family type ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_PANOSE_family_type

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_PANOSE_family_type(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bFamilyType
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bFamilyType = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_PANOSE_family_type(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_011(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal numbers of glyphs ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_numbers_of_glyphs

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check_fonts_have_equal_numbers_of_glyphs(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs.
  status, message = list(check_fonts_have_equal_numbers_of_glyphs(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_012(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal glyph names ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_glyph_names

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check_fonts_have_equal_glyph_names(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs (that extra glyph
  # causes the test to fail).
  status, message = list(check_fonts_have_equal_glyph_names(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_013(mada_ttFonts):
  """ Fonts have equal unicode encodings ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_unicode_encodings
  from fontbakery.constants import (PLAT_ENC_ID_SYMBOL,
                                    PLAT_ENC_ID_UCS2)
  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(check_fonts_have_equal_unicode_encodings(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce mismatching encodings into the first 2 font files:
  for i, encoding in enumerate([PLAT_ENC_ID_SYMBOL,
                                PLAT_ENC_ID_UCS2]):
    for table in bad_ttFonts[i]['cmap'].tables:
      if table.format == 4:
        table.platEncID = encoding

  print('Test FAIL with fonts that diverge on unicode encoding.')
  status, message = list(check_fonts_have_equal_unicode_encodings(bad_ttFonts))[-1]
  assert status == FAIL


def test_id_014(mada_ttFonts):
  """ Make sure all font files have the same version value. """
  from fontbakery.specifications.googlefonts import \
                                  check_all_fontfiles_have_same_version
  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(check_all_fontfiles_have_same_version(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce a mismatching version value into the second font file:
  version = bad_ttFonts[0]['head'].fontRevision
  bad_ttFonts[1]['head'].fontRevision = version + 1

  print('Test WARN with fonts that diverge on the fontRevision field value.')
  status, message = list(check_all_fontfiles_have_same_version(bad_ttFonts))[-1]
  assert status == WARN


def test_id_015():
  """ Font has post table version 2 ? """
  from fontbakery.specifications.googlefonts import \
                                  check_font_has_post_table_version_2
  print('Test PASS with good font.')
  # our reference Mada family is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check_font_has_post_table_version_2(ttFont))[-1]
  assert status == PASS

  # modify the post table version
  ttFont['post'].formatType = 3

  print('Test FAIL with fonts that diverge on the fontRevision field value.')
  status, message = list(check_font_has_post_table_version_2(ttFont))[-1]
  assert status == FAIL


def test_id_016():
  """ Checking OS/2 fsType """
  from fontbakery.specifications.googlefonts import check_OS2_fsType
  print('Test PASS with good font.')
  # our reference Cabin family is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(check_OS2_fsType(ttFont))[-1]
  assert status == PASS

  # modify the OS/2 fsType value to something different than zero:
  ttFont['OS/2'].fsType = 1

  print('Test FAIL with fonts that diverge on the fontRevision field value.')
  status, message = list(check_OS2_fsType(ttFont))[-1]
  assert status == FAIL

#TODO: test/017

def test_id_018():
  """ Checking OS/2 achVendID """
  from fontbakery.specifications.googlefonts import (check_OS2_achVendID,
                                                     registered_vendor_ids)
  from fontbakery.constants import NAMEID_MANUFACTURER_NAME
  registered_ids = registered_vendor_ids()

  print('Test WARN with mismatching vendor id.')
  # Our reference Cabin family is know to have mismatching value of
  # Vendor ID ('STC ') and Manufacturer Name ('Eben Sorkin').
  ttFont = TTFont("data/test/merriweather/Merriweather-Regular.ttf")
  status, message = list(check_OS2_achVendID(ttFont, registered_ids))[-1]
  assert status == WARN and message.code == "mismatch"

  print('Test FAIL with bad vid.')
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  for bad_vid in bad_vids:
    ttFont['OS/2'].achVendID = bad_vid
    status, message = list(check_OS2_achVendID(ttFont, registered_ids))[-1]
    assert status == FAIL and message.code == "bad"

  print('Test FAIL with font missing vendor id info.')
  ttFont['OS/2'].achVendID = None
  status, message = list(check_OS2_achVendID(ttFont, registered_ids))[-1]
  assert status == FAIL and message.code == "not set"

  print('Test WARN with unknwon vendor id.')
  ttFont['OS/2'].achVendID = "????"
  status, message = list(check_OS2_achVendID(ttFont, registered_ids))[-1]
  assert status == WARN and message.code == "unknown"

  print('Test PASS with good font.')
  # we change the fields into a known good combination
  # of vendor id and manufacturer name here:
  ttFont['OS/2'].achVendID = "APPL"
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_MANUFACTURER_NAME:
      ttFont['name'].names[i].string = "Apple".encode(name.getEncoding())
  status, message = list(check_OS2_achVendID(ttFont, registered_ids))[-1]
  assert status == PASS


def test_id_019():
  """ Substitute copyright, registered and trademark
      symbols in name table entries. """
  from fontbakery.specifications.googlefonts import check_name_entries_symbol_substitutions

  print('Test FAIL with a bad font...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check_name_entries_symbol_substitutions(ttFont))[-1]
  assert status == FAIL

  print('Test PASS with a good font...')
  # Our reference Cabin Regular is know to be good here.
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")
  status, message = list(check_name_entries_symbol_substitutions(ttFont))[-1]
  assert status == PASS


def test_id_020():
  """ Checking OS/2 usWeightClass. """
  from fontbakery.specifications.googlefonts import (check_OS2_usWeightClass,
                                                     style)
  print('Test FAIL with a bad font...')
  # Our reference Mada Regular is know to be bad here.
  font = "data/test/mada/Mada-Regular.ttf"
  status, message = list(check_OS2_usWeightClass(TTFont(font), style(font)))[-1]
  assert status == FAIL

  print('Test PASS with a good font...')
  # All fonts in our reference Cabin family are know to be good here.
  for font in cabin_fonts:
    status, message = list(check_OS2_usWeightClass(TTFont(font), style(font)))[-1]
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
  from fontbakery.specifications.googlefonts import (check_font_has_a_license,
                                                     licenses)

  print('Test FAIL with multiple licenses...')
  detected_licenses = licenses("data/test/028/multiple/")
  status, message = list(check_font_has_a_license(detected_licenses))[-1]
  assert status == FAIL and message.code == "multiple"

  print('Test FAIL with no license...')
  detected_licenses = licenses("data/test/028/none/")
  status, message = list(check_font_has_a_license(detected_licenses))[-1]
  assert status == FAIL and message.code == "none"

  print('Test PASS with a single OFL license...')
  detected_licenses = licenses("data/test/028/pass_ofl/")
  status, message = list(check_font_has_a_license(detected_licenses))[-1]
  assert status == PASS

  print('Test PASS with a single Apache license...')
  detected_licenses = licenses("data/test/028/pass_apache/")
  status, message = list(check_font_has_a_license(detected_licenses))[-1]
  assert status == PASS


def test_id_029(mada_ttFonts):
  """ Check copyright namerecords match license file. """
  from fontbakery.specifications.googlefonts import \
                                  check_copyright_entries_match_license
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION

  # Our reference Mada family has its copyright name records properly set
  # identifying it as being licensed under the Open Font License
  license = 'OFL.txt'
  wrong_license = 'LICENSE.txt' # Apache

  print('Test PASS with good fonts ...')
  for ttFont in mada_ttFonts:
    status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
    assert status == PASS

  print('Test FAIL with wrong entry values ...')
  for ttFont in mada_ttFonts:
    status, message = list(check_copyright_entries_match_license(ttFont, wrong_license))[-1]
    assert status == FAIL and message.code == 'wrong'

  print('Test FAIL with missing copyright namerecords ...')
  for ttFont in mada_ttFonts:
    delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
    status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
    assert status == FAIL and message.code == 'missing'

# TODO: test_id_030

def test_id_031():
  """ Description strings in the name table
      must not contain copyright info.
  """
  from fontbakery.specifications.googlefonts import \
                                  check_description_strings_in_name_table
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check_description_strings_in_name_table(ttFont))[-1]
  assert status == PASS

  # here we add a "Copyright" string to a NAMEID_DESCRIPTION
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = "Copyright".encode(name.getEncoding())

  print('Test FAIL with a bad font...')
  status, message = list(check_description_strings_in_name_table(ttFont))[-1]
  assert status == FAIL


def test_id_032():
  """ Description strings in the name table
      must not exceed 100 characters.
  """
  from fontbakery.specifications.googlefonts import \
                   check_description_strings_do_not_exceed_100_chars
  from fontbakery.constants import NAMEID_DESCRIPTION

  print('Test PASS with a good font...')
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  status, message = list(check_description_strings_do_not_exceed_100_chars(ttFont))[-1]
  assert status == PASS

  # Here we add strings to NAMEID_DESCRIPTION with exactly 100 chars,
  # so it should still PASS:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 100).encode(name.getEncoding())

  print('Test PASS with a 100 char string...')
  status, message = list(check_description_strings_do_not_exceed_100_chars(ttFont))[-1]
  assert status == PASS

  # And here we make the strings longer than 100 chars in order to FAIL the test:
  for i, name in enumerate(ttFont['name'].names):
    if name.nameID == NAMEID_DESCRIPTION:
      ttFont['name'].names[i].string = ('a' * 101).encode(name.getEncoding())

  print('Test FAIL with a bad font...')
  status, message = list(check_description_strings_do_not_exceed_100_chars(ttFont))[-1]
  assert status == FAIL

# TODO: test_id_033
# TODO: test_id_034
# TODO: test_id_035
# TODO: test_id_036
# TODO: test_id_037
# TODO: test_id_038
# TODO: test_id_039

def test_id_040(mada_ttFonts):
  """ Checking OS/2 usWinAscent & usWinDescent. """
  from fontbakery.specifications.googlefonts import \
                                  (check_OS2_usWinAscent_and_Descent,
                                   vmetrics)
  # Our reference Mada Regular is know to be bad here.
  vm = vmetrics(mada_ttFonts)
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But we fix it first to test the PASS code-path:
  print('Test PASS with a good font...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(check_OS2_usWinAscent_and_Descent(ttFont, vm))[-1]
  assert status == PASS

  # Then we break it:
  print('Test FAIL with a bad OS/2.usWinAscent...')
  ttFont['OS/2'].usWinAscent = vm['ymax'] + 1
  ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
  status, message = list(check_OS2_usWinAscent_and_Descent(ttFont, vm))[-1]
  assert status == FAIL and message.code == "ascent"

  print('Test FAIL with a bad OS/2.usWinDescent...')
  ttFont['OS/2'].usWinAscent = vm['ymax']
  ttFont['OS/2'].usWinDescent = abs(vm['ymin']) + 1
  status, message = list(check_OS2_usWinAscent_and_Descent(ttFont, vm))[-1]
  assert status == FAIL and message.code == "descent"


def test_id_041():
  """ Checking Vertical Metric Linegaps. """
  from fontbakery.specifications.googlefonts import \
                                  check_Vertical_Metric_Linegaps

  print('Test FAIL with non-zero hhea.lineGap...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But just to be sure we explicitely set the values we're testing for:
  ttFont['hhea'].lineGap = 1
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(check_Vertical_Metric_Linegaps(ttFont))[-1]
  assert status == WARN and message.code == "hhea"

  # Then we test with a non-zero OS/2.sTypoLineGap:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 1
  status, message = list(check_Vertical_Metric_Linegaps(ttFont))[-1]
  assert status == WARN and message.code == "OS/2"

  # And finaly we fix it by making both values equal to zero:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(check_Vertical_Metric_Linegaps(ttFont))[-1]
  assert status == PASS


def test_id_042(mada_ttFonts):
  """ Checking OS/2 Metrics match hhea Metrics. """
  from fontbakery.specifications.googlefonts import \
                                  check_OS2_Metrics_match_hhea_Metrics
  # Our reference Mada Regular is know to be good here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print("Test PASS with a good font...")
  status, message = list(check_OS2_Metrics_match_hhea_Metrics(ttFont))[-1]
  assert status == PASS

  # Now we break it:
  print('Test FAIL with a bad OS/2.sTypoAscender font...')
  correct = ttFont['hhea'].ascent
  ttFont['OS/2'].sTypoAscender = correct + 1
  status, message = list(check_OS2_Metrics_match_hhea_Metrics(ttFont))[-1]
  assert status == FAIL and message.code == "ascender"

  # Restore good value:
  ttFont['OS/2'].sTypoAscender = correct

  # And break it again, now on sTypoDescender value:
  print('Test FAIL with a bad OS/2.sTypoDescender font...')
  correct = ttFont['hhea'].descent
  ttFont['OS/2'].sTypoDescender = correct + 1
  status, message = list(check_OS2_Metrics_match_hhea_Metrics(ttFont))[-1]
  assert status == FAIL and message.code == "descender"


def test_id_043():
  """ Checking unitsPerEm value is reasonable. """
  from fontbakery.specifications.googlefonts import \
                                  check_unitsPerEm_value_is_reasonable
  # In this test we'll forge several known-good and known-bad values.
  # We'll use Mada Regular to start with:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  for good_value in [1000, 16, 32, 64, 128, 256,
                     512, 1024, 2048, 4096, 8192, 16384]:
    print("Test PASS with a good value of unitsPerEm = {} ...".format(good_value))
    ttFont['head'].unitsPerEm = good_value
    status, message = list(check_unitsPerEm_value_is_reasonable(ttFont))[-1]
    assert status == PASS

  # These are arbitrarily chosen bad values:
  for bad_value in [0, 1, 2, 4, 8, 10, 100, 10000, 32768]:
    print("Test FAIL with a bad value of unitsPerEm = {} ...".format(bad_value))
    ttFont['head'].unitsPerEm = bad_value
    status, message = list(check_unitsPerEm_value_is_reasonable(ttFont))[-1]
    assert status == FAIL

# TODO: test_id_044

def test_id_045():
  """ Does the font have a DSIG table ? """
  from fontbakery.specifications.googlefonts import \
                                  check_Digital_Signature_exists
  # Our reference Cabin Regular font is good (theres a DSIG table declared):
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(check_Digital_Signature_exists(ttFont))[-1]
  assert status == PASS

  # Then we remove the DSIG table so that we get a FAIL:
  print ("Test FAIL with a font lacking a DSIG table...")
  del ttFont['DSIG']
  status, message = list(check_Digital_Signature_exists(ttFont))[-1]
  assert status == FAIL

# TODO: test_id_046

def test_id_047():
  """ Font contains glyphs for whitespace characters ? """
  from fontbakery.specifications.googlefonts import \
                                  (check_font_contains_glyphs_for_whitespace_chars,
                                   missing_whitespace_chars)
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
  missing = missing_whitespace_chars(ttFont)

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(check_font_contains_glyphs_for_whitespace_chars(ttFont, missing))[-1]
  assert status == PASS

  # Then we remove the nbsp char (0x00A0) so that we get a FAIL:
  print ("Test FAIL with a font lacking a nbsp (0x00A0)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(check_font_contains_glyphs_for_whitespace_chars(ttFont, missing))[-1]
  assert status == FAIL

  # restore original Mada Regular font:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # And finally remove the space character (0x0020) to get another FAIL:
  print ("Test FAIL with a font lacking a space (0x0020)...")
  for table in ttFont['cmap'].tables:
    if 0x00A0 in table.cmap:
      del table.cmap[0x00A0]

  missing = missing_whitespace_chars(ttFont)
  status, message = list(check_font_contains_glyphs_for_whitespace_chars(ttFont, missing))[-1]
  assert status == FAIL


def test_id_048():
  """ Font has **proper** whitespace glyph names ? """
  from fontbakery.specifications.googlefonts import \
                                  check_font_has_proper_whitespace_glyph_names
  from fontbakery.utils import deleteGlyphEncodings

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(check_font_has_proper_whitespace_glyph_names(ttFont))[-1]
  assert status == PASS

  print ("Test SKIP with post.formatType == 3.0 ...")
  value = ttFont["post"].formatType
  ttFont["post"].formatType = 3.0
  status, message = list(check_font_has_proper_whitespace_glyph_names(ttFont))[-1]
  assert status == SKIP
  # and restore good value:
  ttFont["post"].formatType = value

  print ("Test FAIL with bad glyph name for char 0x0020 ...")
  deleteGlyphEncodings(ttFont, 0x0020)
  status, message = list(check_font_has_proper_whitespace_glyph_names(ttFont))[-1]
  assert status == FAIL and message.code == "bad20"

  # restore the original font object in preparation for the next test-case:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  print ("Test FAIL with bad glyph name for char 0x00A0 ...")
  deleteGlyphEncodings(ttFont, 0x00A0)
  status, message = list(check_font_has_proper_whitespace_glyph_names(ttFont))[-1]
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
  from fontbakery.specifications.googlefonts import \
                                  check_font_contains_all_required_tables
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
  status, message = list(check_font_contains_all_required_tables(ttFont))[-1]
  assert status == PASS

  # We now remove required tables one-by-one to validate the FAIL code-path:
  for required in required_tables:
    print ("Test FAIL with missing mandatory table {} ...".format(required))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    if required in ttFont.reader.tables:
      del ttFont.reader.tables[required]
    status, message = list(check_font_contains_all_required_tables(ttFont))[-1]
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
    status, message = list(check_font_contains_all_required_tables(ttFont))[-2]
    assert status == INFO
    # remove the one we've just inserted before trying the next one:
    del ttFont.reader.tables[optional]


def test_id_053():
  """ Are there unwanted tables ? """
  from fontbakery.specifications.googlefonts import \
                                  check_for_unwanted_tables
  unwanted_tables = ["FFTM", "TTFA", "prop"]
  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(check_for_unwanted_tables(ttFont))[-1]
  assert status == PASS

  # We now add unwanted tables one-by-one to validate the FAIL code-path:
  for unwanted in unwanted_tables:
    print ("Test FAIL with unwanted table {} ...".format(unwanted))
    ttFont = TTFont("data/test/mada/Mada-Regular.ttf")
    ttFont.reader.tables[unwanted] = "foo"
    status, message = list(check_for_unwanted_tables(ttFont))[-1]
    assert status == FAIL

# TODO: test_id_054

def test_id_055():
  """ Version format is correct in NAME table ? """
  from fontbakery.specifications.googlefonts import \
                   check_version_format_is_correct_in_NAME_table
  from fontbakery.constants import NAMEID_VERSION_STRING

  # Our reference Mada Regular font is good here:
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # So it must PASS the test:
  print ("Test PASS with a good font...")
  status, message = list(check_version_format_is_correct_in_NAME_table(ttFont))[-1]
  assert status == PASS

  # then we introduce bad strings in all version-string entries:
  print ("Test FAIL with bad version format in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      invalid = "invalid-version-string".encode(name.getEncoding())
      ttFont["name"].names[i].string = invalid
  status, message = list(check_version_format_is_correct_in_NAME_table(ttFont))[-1]
  assert status == FAIL and message.code == "bad-version-strings"

  # and finally we remove all version-string entries:
  print ("Test FAIL with font lacking version string entries in name table...")
  for i, name in enumerate(ttFont["name"].names):
    if name.nameID == NAMEID_VERSION_STRING:
      del ttFont["name"].names[i]
  status, message = list(check_version_format_is_correct_in_NAME_table(ttFont))[-1]
  assert status == FAIL and message.code == "no-version-string"


def test_id_153(montserrat_ttFonts):
  """Check glyphs contain the recommended contour count"""
  from fontbakery.specifications.googlefonts import \
    check_glyphs_have_recommended_contour_count

  # Montserrat should pass this test since it was used to assemble the glyph data
  for ttFont in montserrat_ttFonts:
    status, message = list(check_glyphs_have_recommended_contour_count(ttFont))[-1]
    assert status == PASS

  # Lets swap the glyf a (2 contours) with glyf c (1 contour)
  for ttFont in montserrat_ttFonts:
    ttFont['glyf']['a'] = ttFont['glyf']['c']
    status, message = list(check_glyphs_have_recommended_contour_count(ttFont))[-1]
    assert status == WARN


def test_id_154(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    from fontbakery.specifications.googlefonts import (
                                      check_regression_missing_glyphs,
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
    status, message = list(check_regression_missing_glyphs(font, gfont))[-1]
    assert status == PASS

    # Take A glyph out of font
    font['cmap'].getcmap(3, 1).cmap.pop(ord('A'))
    font['glyf'].glyphs.pop('A')

    status, message = list(check_regression_missing_glyphs(font, gfont))[-1]
    assert status == FAIL

