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

@pytest.fixture
def font_1():
  # FIXME: find absolute path via the path of this module
  path = 'data/test/cabin/Cabin-Regular.ttf'
  # return TTFont(path)
  return path


@pytest.fixture
def mada_ttFonts():
  paths = [
    "data/test/mada/Mada-Black.ttf",
    "data/test/mada/Mada-ExtraLight.ttf",
    "data/test/mada/Mada-Medium.ttf",
    "data/test/mada/Mada-SemiBold.ttf",
    "data/test/mada/Mada-Bold.ttf",
    "data/test/mada/Mada-Light.ttf",
    "data/test/mada/Mada-Regular.ttf",
  ]
  return [TTFont(path) for path in paths]


@pytest.fixture
def cabin_ttFonts():
  paths = [
    "data/test/cabin/Cabin-BoldItalic.ttf",
    "data/test/cabin/Cabin-Bold.ttf",
    "data/test/cabin/Cabin-Italic.ttf",
    "data/test/cabin/Cabin-MediumItalic.ttf",
    "data/test/cabin/Cabin-Medium.ttf",
    "data/test/cabin/Cabin-Regular.ttf",
    "data/test/cabin/Cabin-SemiBoldItalic.ttf",
    "data/test/cabin/Cabin-SemiBold.ttf"
  ]
  return [TTFont(path) for path in paths]


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


def test_example_testrunner_based(font_1):
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
  values = dict(fonts=[font_1])
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
