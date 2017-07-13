#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import print_function
import os
import sys
import tempfile
import logging
import requests
import urllib
import csv
import re
import defusedxml.lxml
from fontTools import ttLib
from unidecode import unidecode
import plistlib
from fontbakery.pifont import PiFont
from fontbakery.utils import (
                             get_name_string,
                             check_bit_entry,
                             ttfauto_fpgm_xheight_rounding,
                             glyphs_surface_area,
                             save_FamilyProto_Message,
                             assertExists
                             )
from fontbakery.constants import (
                                 IMPORTANT,
                                 CRITICAL,
                                 STYLE_NAMES,
                                 NAMEID_FONT_FAMILY_NAME,
                                 NAMEID_FONT_SUBFAMILY_NAME,
                                 NAMEID_FULL_FONT_NAME,
                                 NAMEID_VERSION_STRING,
                                 NAMEID_POSTSCRIPT_NAME,
                                 NAMEID_MANUFACTURER_NAME,
                                 NAMEID_DESCRIPTION,
                                 NAMEID_LICENSE_DESCRIPTION,
                                 NAMEID_LICENSE_INFO_URL,
                                 NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                 NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,
                                 NAMEID_STR,
                                 RIBBI_STYLE_NAMES,
                                 PLATFORM_ID_MACINTOSH,
                                 PLATFORM_ID_WINDOWS,
                                 PLATID_STR,
                                 WEIGHT_VALUE_TO_NAME,
                                 FSSEL_ITALIC,
                                 FSSEL_BOLD,
                                 FSSEL_REGULAR,
                                 MACSTYLE_BOLD,
                                 MACSTYLE_ITALIC,
                                 PANOSE_PROPORTION_ANY,
                                 PANOSE_PROPORTION_MONOSPACED,
                                 IS_FIXED_WIDTH_NOT_MONOSPACED,
                                 IS_FIXED_WIDTH_MONOSPACED,
                                 LANG_ID_ENGLISH_USA,
                                 PLACEHOLDER_LICENSING_TEXT,
                                 LICENSE_URL,
                                 LICENSE_NAME,
                                 REQUIRED_TABLES,
                                 OPTIONAL_TABLES,
                                 UNWANTED_TABLES,
                                 WHITESPACE_CHARACTERS,
                                 PLAT_ENC_ID_UCS2
                                 )
try:
  import fontforge  #pylint: disable=unused-import
except ImportError:
  logging.warning("fontforge python module is not available!"
                  " To install it, see"
                  " https://github.com/googlefonts/"
                  "gf-docs/blob/master/ProjectChecklist.md#fontforge")
  pass

# =======================================================================
# The following functions implement each of the individual checks per-se.
# =======================================================================


def check_file_is_named_canonically(fb, font_fname):
  """A font's filename must be composed in the following manner:

  <familyname>-<stylename>.ttf

  e.g Nunito-Regular.ttf, Oswald-BoldItalic.ttf"""
  fb.new_check("001", "Checking file is named canonically")
  fb.set_priority(CRITICAL)

  file_path, filename = os.path.split(font_fname)
  basename = os.path.splitext(filename)[0]
  # remove spaces in style names
  style_file_names = [name.replace(' ', '') for name in STYLE_NAMES]
  if '-' in basename and basename.split('-')[1] in style_file_names:
    fb.ok("{} is named canonically".format(font_fname))
    return True
  else:
    fb.error(('Style name used in "{}" is not canonical.'
              ' You should rebuild the font using'
              ' any of the following'
              ' style names: "{}".').format(font_fname,
                                            '", "'.join(STYLE_NAMES)))
    return False


def check_METADATA_filename_contains_good_fname(fb, f, font_familyname):
  fb.new_check("100", "METADATA.pb 'filename' contains"
                      " font name in right format ?")
  if "".join(str(font_familyname).split()) in f.filename:
    fb.ok("METADATA.pb 'filename' contains"
          " font name in right format.")
  else:
    fb.error(("METADATA.pb filename='{}' does not match"
              " correct font name format.").format(f.filename))


def check_METADATA_postScriptName_contains_good_fname(fb, f, familyname):
  fb.new_check("101", "METADATA.pb 'postScriptName' contains"
                      " font name in right format ?")
  if "".join(str(familyname).split()) in f.post_script_name:
    fb.ok("METADATA.pb 'postScriptName' contains"
          " font name in right format ?")
  else:
    fb.error(("METADATA.pb postScriptName='{}'"
              " does not match correct"
              " font name format.").format(f.post_script_name))


def check_Copyright_notice_matches_canonical_pattern(fb, f):
  fb.new_check("102", "Copyright notice matches canonical pattern?")
  almost_matches = re.search(r'(Copyright\s+20\d{2}.+)',
                             f.copyright)
  does_match = re.search(r'(Copyright\s+20\d{2}\s+.*\(.+@.+\..+\))',
                         f.copyright)
  if (does_match is not None):
    fb.ok("METADATA.pb copyright field matches canonical pattern.")
  else:
    if (almost_matches):
      fb.warning(("METADATA.pb: Copyright notice is okay,"
                  " but it lacks an email address."
                  " Expected pattern is:"
                  " 'Copyright 2016 Author Name (name@site.com)'\n"
                  "But detected copyright string is:"
                  " '{}'").format(unidecode(f.copyright)))
    else:
      fb.error(("METADATA.pb: Copyright notices should match"
                " the folowing pattern:"
                " 'Copyright 2016 Author Name (name@site.com)'\n"
                "But instead we have got:"
                " '{}'").format(unidecode(f.copyright)))


def check_Copyright_notice_does_not_contain_Reserved_Name(fb, f):
  fb.new_check("103", "Copyright notice does not "
                      "contain Reserved Font Name")
  if 'Reserved Font Name' in f.copyright:
    fb.warning(("METADATA.pb: copyright field ('{}')"
                " contains 'Reserved Font Name'."
                " This is an error except in a few specific"
                " rare cases.").format(unidecode(f.copyright)))
  else:
    fb.ok('METADATA.pb copyright field'
          ' does not contain "Reserved Font Name"')


def check_Copyright_notice_does_not_exceed_500_chars(fb, f):
  fb.new_check("104", "Copyright notice shouldn't exceed 500 chars")
  if len(f.copyright) > 500:
    fb.error("METADATA.pb: Copyright notice exceeds"
             " maximum allowed lengh of 500 characteres.")
  else:
    fb.ok("Copyright notice string is"
          " shorter than 500 chars.")


def check_Filename_is_set_canonically(fb, f):
  fb.new_check("105", "Filename is set canonically in METADATA.pb ?")

  def create_canonical_filename(font_metadata):
    style_names = {
     'normal': '',
     'italic': 'Italic'
    }
    familyname = font_metadata.name.replace(' ', '')
    style_weight = '%s%s' % (WEIGHT_VALUE_TO_NAME.get(font_metadata.weight),
                             style_names.get(font_metadata.style))
    if not style_weight:
        style_weight = 'Regular'
    return '%s-%s.ttf' % (familyname, style_weight)

  canonical_filename = create_canonical_filename(f)
  if canonical_filename != f.filename:
    fb.error("METADATA.pb: filename field ('{}')"
             " does not match"
             " canonical name '{}'".format(f.filename,
                                           canonical_filename))
  else:
    fb.ok('Filename in METADATA.pb is set canonically.')


def check_METADATA_font_italic_matches_font_internals(fb, font, f):
  fb.new_check("106", "METADATA.pb font.style `italic`"
                      " matches font internals?")
  if f.style != 'italic':
    fb.skip("This test only applies to italic fonts.")
  else:
    font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
    font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
    if len(font_familyname) == 0 or len(font_fullname) == 0:
      fb.skip("Font lacks familyname and/or"
              " fullname entries in name table.")
      # these fail scenarios were already tested above
      # (passing those previous tests is a prerequisite for this one)
    else:
      font_familyname = font_familyname[0]
      font_fullname = font_fullname[0]

      if not bool(font['head'].macStyle & MACSTYLE_ITALIC):
          fb.error('METADATA.pb style has been set to italic'
                   ' but font macStyle is improperly set')
      elif not font_familyname.split('-')[-1].endswith('Italic'):
          fb.error(('Font macStyle Italic bit is set'
                    ' but nameID %d ("%s")'
                    ' is not ended '
                    'with "Italic"') % (NAMEID_FONT_FAMILY_NAME,
                                        font_familyname))
      elif not font_fullname.split('-')[-1].endswith('Italic'):
          fb.error(('Font macStyle Italic bit is set'
                    ' but nameID %d ("%s")'
                    ' is not ended'
                    ' with "Italic"') % (NAMEID_FULL_FONT_NAME,
                                         font_fullname))
      else:
        fb.ok("OK: METADATA.pb font.style 'italic'"
              " matches font internals.")


def check_METADATA_fontstyle_normal_matches_internals(fb, font, f):
  fb.new_check("107", "METADATA.pb font.style `normal`"
                      " matches font internals?")
  if f.style != 'normal':
    fb.skip("This test only applies to normal fonts.")
  else:
    font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
    font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
    if len(font_familyname) == 0 or len(font_fullname) == 0:
      fb.skip("Font lacks familyname and/or"
              " fullname entries in name table.")
      # these fail scenarios were already tested above
      # (passing those previous tests is a prerequisite for this one)
      return False
    else:
      font_familyname = font_familyname[0]
      font_fullname = font_fullname[0]

      if bool(font['head'].macStyle & MACSTYLE_ITALIC):
          fb.error('METADATA.pb style has been set to normal'
                   ' but font macStyle is improperly set')
      elif font_familyname.split('-')[-1].endswith('Italic'):
          fb.error(('Font macStyle indicates a non-Italic font,'
                    ' but nameID %d (FONT_FAMILY_NAME: "%s") ends'
                    ' with "Italic"').format(NAMEID_FONT_FAMILY_NAME,
                                             font_familyname))
      elif font_fullname.split('-')[-1].endswith('Italic'):
          fb.error('Font macStyle indicates a non-Italic font'
                   ' but nameID %d (FULL_FONT_NAME: "%s") ends'
                   ' with "Italic"'.format(NAMEID_FULL_FONT_NAME,
                                           font_fullname))
      else:
        fb.ok("METADATA.pb font.style 'normal'"
              " matches font internals.")
      return True


def check_Metadata_keyvalue_match_to_table_name_fields(fb, font, f):
  fb.new_check("108", "Metadata key-value match to table name fields?")
  font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)[0]
  font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)[0]
  if font_familyname != f.name:
    fb.error(("METADATA.pb Family name '{}')"
              " does not match name table"
              " entry '{}' !").format(f.name,
                                      font_familyname))
  elif font_fullname != f.full_name:
    fb.error(("METADATA.pb: Fullname ('{}')"
              " does not match name table"
              " entry '{}' !").format(f.full_name,
                                      font_fullname))
  else:
    fb.ok("METADATA.pb familyname and fullName fields"
          " match corresponding name table entries.")


def check_fontname_is_not_camel_cased(fb, f):
  fb.new_check("109", "Check if fontname is not camel cased.")
  if bool(re.match(r'([A-Z][a-z]+){2,}', f.name)):
    fb.error(("METADATA.pb: '%s' is a CamelCased name."
              " To solve this, simply use spaces"
              " instead in the font name.").format(f.name))
  else:
    fb.ok("Font name is not camel-cased.")


def check_font_name_is_the_same_as_family_name(fb, family, f):
  fb.new_check("110", "Check font name is the same as family name.")
  if f.name != family.name:
    fb.error(('METADATA.pb: %s: Family name "%s"'
              ' does not match'
              ' font name: "%s"').format(f.filename,
                                         family.name,
                                         f.name))
  else:
    fb.ok('Font name is the same as family name.')


def check_font_weight_has_a_canonical_value(fb, f):
  fb.new_check("111", "Check that font weight has a canonical value")
  first_digit = f.weight / 100
  if (f.weight % 100) != 0 or (first_digit < 1 or first_digit > 9):
    fb.error(("METADATA.pb: The weight is declared"
              " as {} which is not a "
              "multiple of 100"
              " between 100 and 900.").format(f.weight))
  else:
    fb.ok("Font weight has a canonical value.")


def check_METADATA_weigth_matches_OS2_usWeightClass_value(fb, f):
  fb.new_check("112", "Checking OS/2 usWeightClass"
                      " matches weight specified at METADATA.pb")
  fb.assert_table_entry('OS/2', 'usWeightClass', f.weight)
  fb.log_results("OS/2 usWeightClass matches "
                 "weight specified at METADATA.pb")


weights = {
  'Thin': 100,
  'ThinItalic': 100,
  'ExtraLight': 200,
  'ExtraLightItalic': 200,
  'Light': 300,
  'LightItalic': 300,
  'Regular': 400,
  'Italic': 400,
  'Medium': 500,
  'MediumItalic': 500,
  'SemiBold': 600,
  'SemiBoldItalic': 600,
  'Bold': 700,
  'BoldItalic': 700,
  'ExtraBold': 800,
  'ExtraBoldItalic': 800,
  'Black': 900,
  'BlackItalic': 900,
}


def check_Metadata_weight_matches_postScriptName(fb, f):
  fb.new_check("113", "Metadata weight matches postScriptName")
  pair = []
  for k, weight in weights.items():
    if weight == f.weight:
      pair.append((k, weight))

  if not pair:
    fb.error('METADATA.pb: Font weight'
             ' does not match postScriptName')
  elif not (f.post_script_name.endswith('-' + pair[0][0]) or
            f.post_script_name.endswith('-%s' % pair[1][0])):
    fb.error('METADATA.pb: postScriptName ("{}")'
             ' with weight {} must be '.format(f.post_script_name,
                                               pair[0][1]) +
             'ended with "{}" or "{}"'.format(pair[0][0],
                                              pair[1][0]))
  else:
    fb.ok("Weight value matches postScriptName.")


def check_METADATA_lists_fonts_named_canonicaly(fb, font, f):
  fb.new_check("114", "METADATA.pb lists fonts named canonicaly?")
  font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
  if len(font_familyname) == 0:
    fb.skip("Skipping this test due to the lack"
            " of a FONT_FAMILY_NAME in the name table.")
  else:
    font_familyname = font_familyname[0]

    is_canonical = False
    _weights = []
    for value, intvalue in weights.items():
      if intvalue == font['OS/2'].usWeightClass:
        _weights.append(value)

    for w in _weights:
      canonical_name = "%s %s" % (font_familyname, w)
      if f.full_name == canonical_name:
        is_canonical = True

    if is_canonical:
      fb.ok("METADATA.pb lists fonts named canonicaly.")
    else:
      v = map(lambda x: font_familyname + ' ' + x, _weights)
      fb.error('Canonical name in font: Expected "%s"'
               ' but got "%s" instead.' % ('" or "'.join(v),
                                           f.full_name))


def check_Font_styles_are_named_canonically(fb, font, f):
  fb.new_check("115", "Font styles are named canonically?")

  def find_italic_in_name_table():
    for entry in font['name'].names:
      if 'italic' in entry.string.decode(
       entry.getEncoding()).lower():
        return True
    return False

  def is_italic():
    return (font['head'].macStyle & MACSTYLE_ITALIC or
            font['post'].italicAngle or
            find_italic_in_name_table())

  if f.style not in ['italic', 'normal']:
    fb.skip("This check only applies to font styles declared"
            " as 'italic' or 'regular' on METADATA.pb")
  else:
    if is_italic() and f.style != 'italic':
      fb.error("The font style is %s"
               " but it should be italic" % (f.style))
    elif not is_italic() and f.style != 'normal':
      fb.error(("The font style is %s"
                " but it should be normal") % (f.style))
    else:
      fb.ok("Font styles are named canonically")


def check_font_em_size_is_ideally_equal_to_1000(fb, font, skip_gfonts):
  fb.new_check("116", "Is font em size (ideally) equal to 1000?")
  if skip_gfonts:
    fb.skip("Skipping this Google-Fonts specific check.")
  else:
    upm_height = font['head'].unitsPerEm
    if upm_height != 1000:
      fb.warning(("font em size ({}) is not"
                  " equal to 1000.").format(upm_height))
    else:
      fb.ok("Font em size is equal to 1000.")


def check_regression_v_number_increased(fb, new_font, old_font, f):
  fb.new_check("117", "Version number has increased since previous release?")
  new_v_number = new_font['head'].fontRevision
  old_v_number = old_font['head'].fontRevision
  if new_v_number < old_v_number:
    fb.error(("Version number %s is less than or equal to"
              " old version %s") % (new_v_number, old_v_number))
  else:
    fb.ok(("Version number %s is greater than"
           " old version %s") % (new_v_number, old_v_number))


def check_regression_glyphs_structure(fb, new_font, old_font, f):
  fb.new_check("118", "Glyphs are similiar to old version")
  bad_glyphs = []
  new_glyphs = glyphs_surface_area(new_font)
  old_glyphs = glyphs_surface_area(old_font)

  shared_glyphs = set(new_glyphs) & set(old_glyphs)

  for glyph in shared_glyphs:
    if abs(int(new_glyphs[glyph]) - int(old_glyphs[glyph])) > 8000:
      bad_glyphs.append(glyph)

  if bad_glyphs:
    fb.error("Following glyphs differ greatly from previous version: [%s]" % (
      ', '.join(bad_glyphs)
    ))
  else:
    fb.ok("Yes, the glyphs are similar "
          "in comparison to the previous version.")


def check_regression_ttfauto_xheight_increase(fb, new_font, old_font, f):
  fb.new_check("119", "TTFAutohint x-height increase value is"
                      " same as previouse release?")
  new_inc_xheight = None
  old_inc_xheight = None

  if 'fpgm' in new_font:
    new_fpgm_tbl = new_font['fpgm'].program.getAssembly()
    new_inc_xheight = ttfauto_fpgm_xheight_rounding(fb,
                                                    new_fpgm_tbl,
                                                    "this fontfile")
  if 'fpgm' in old_font:
    old_fpgm_tbl = old_font['fpgm'].program.getAssembly()
    old_inc_xheight = ttfauto_fpgm_xheight_rounding(fb,
                                                    old_fpgm_tbl,
                                                    "previous release")
  if new_inc_xheight != old_inc_xheight:
    fb.error("TTFAutohint --increase-x-height is %s. "
             "It should match the previous version's value %s" %
             (new_inc_xheight, old_inc_xheight)
             )
  else:
    fb.ok("TTFAutohint --increase-x-height is the same as the previous "
          "release, %s" % (new_inc_xheight))


###############################
# Upstream Font Source checks #
###############################

def check_all_fonts_have_matching_glyphnames(fb, folder, directory):
  fb.new_check(120, "Each font in family has matching glyph names?")
  glyphs = None
  failed = False
  for f in directory.get_fonts():
    try:
      font = PiFont(os.path.join(folder, f))
      if glyphs is None:
        glyphs = font.get_glyphs()
      elif glyphs != font.get_glyphs():
        failed = True
        fb.error(("Font '{}' has different glyphs in"
                  " comparison to onther fonts"
                  " in this family.").format(f))
        break
    except:
      failed = True
      fb.error("Failed to load font file: '{}'".format(f))

  if failed is False:
    fb.ok("All fonts in family have matching glyph names.")


def check_glyphs_have_same_num_of_contours(fb, folder, directory):
  fb.new_check("121", "Glyphs have same number of contours across family ?")
  glyphs = {}
  failed = False
  for f in directory.get_fonts():
    font = PiFont(os.path.join(folder, f))
    for glyphcode, glyphname in font.get_glyphs():
      contours = font.get_contours_count(glyphname)
      if glyphcode in glyphs and glyphs[glyphcode] != contours:
        failed = True
        fb.error(("Number of contours of glyph '{}'"
                  " does not match."
                  " Expected {} contours, but actual is"
                  " {} contours").format(glyphname,
                                         glyphs[glyphcode],
                                         contours))
      glyphs[glyphcode] = contours
  if failed is False:
    fb.ok("Glyphs have same number of contours across family.")


def check_glyphs_have_same_num_of_points(fb, folder, directory):
  fb.new_check("122", "Glyphs have same number of points across family ?")
  glyphs = {}
  failed = False
  for f in directory.get_fonts():
    font = PiFont(os.path.join(folder, f))
    for g, glyphname in font.get_glyphs():
      points = font.get_points_count(glyphname)
      if g in glyphs and glyphs[g] != points:
        failed = True
        fb.error(("Number of points of glyph '{}' does not match."
                  " Expected {} points, but actual is"
                  " {} points").format(glyphname,
                                       glyphs[g],
                                       points))
      glyphs[g] = points
  if failed is False:
    fb.ok("Glyphs have same number of points across family.")


def check_font_folder_contains_a_COPYRIGHT_file(fb, folder):
  fb.new_check("123", "Does this font folder contain COPYRIGHT file ?")
  assertExists(fb, folder, "COPYRIGHT.txt",
               "Font folder lacks a copyright file at '{}'",
               "Font folder contains COPYRIGHT.txt")


def check_font_folder_contains_a_DESCRIPTION_file(fb, folder):
  fb.new_check("124", "Does this font folder contain a DESCRIPTION file ?")
  assertExists(fb, folder, "DESCRIPTION.en_us.html",
               "Font folder lacks a description file at '{}'",
               "Font folder should contain DESCRIPTION.en_us.html.")


def check_font_folder_contains_licensing_files(fb, folder):
  fb.new_check("125", "Does this font folder contain licensing files?")
  assertExists(fb, folder, ["LICENSE.txt", "OFL.txt"],
               "Font folder lacks licensing files at '{}'",
               "Font folder should contain licensing files.")


def check_font_folder_contains_a_FONTLOG_txt_file(fb, folder):
  fb.new_check("126", "Font folder should contain FONTLOG.txt")
  assertExists(fb, folder, "FONTLOG.txt",
               "Font folder lacks a fontlog file at '{}'",
               "Font folder should contain a 'FONTLOG.txt' file.")


def check_repository_contains_METADATA_pb_file(fb, f):
  fb.new_check("127", "Repository contains METADATA.pb file?")
  fullpath = os.path.join(f, 'METADATA.pb')
  if not os.path.exists(fullpath):
    fb.error("File 'METADATA.pb' does not exist"
             " in root of upstream repository")
  else:
    fb.ok("Repository contains METADATA.pb file.")


def check_copyright_notice_is_consistent_across_family(fb, folder):
  fb.new_check("128", "Copyright notice is consistent"
                      " across all fonts in this family ?")

  COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)

  def grep_copyright_notice(contents):
    match = COPYRIGHT_REGEX.search(contents)
    if match:
      return match.group(0).strip(',\r\n')
    return

  def lookup_copyright_notice(ufo_folder):
    # current_path = ufo_folder
    try:
      contents = open(os.path.join(ufo_folder,
                                   'fontinfo.plist')).read()
      copyright = grep_copyright_notice(contents)
      if copyright:
        return copyright
    except (IOError, OSError):
      pass

    # TODO: FIX-ME!
    # I'm not sure what's going on here:
    # "?" was originaly "self.operator.path" in the old codebase:
#    while os.path.realpath(?) != current_path:
#      # look for all text files inside folder
#      # read contents from them and compare with copyright notice pattern
#      files = glob.glob(os.path.join(current_path, '*.txt'))
#      files += glob.glob(os.path.join(current_path, '*.ttx'))
#      for filename in files:
#        with open(os.path.join(current_path, filename)) as fp:
#          match = COPYRIGHT_REGEX.search(fp.read())
#          if not match:
#            continue
#          return match.group(0).strip(',\r\n')
#      current_path = os.path.join(current_path, '..')  # go up
#      current_path = os.path.realpath(current_path)
    return

  ufo_dirs = []
  for item in os.walk(folder):
    root = item[0]
    dirs = item[1]
    # files = item[2]
    for d in dirs:
        fullpath = os.path.join(root, d)
        if os.path.splitext(fullpath)[1].lower() == '.ufo':
            ufo_dirs.append(fullpath)
  if len(ufo_dirs) == 0:
    fb.skip("No UFO font file found.")
  else:
    failed = False
    copyright = None
    for ufo_folder in ufo_dirs:
      current_notice = lookup_copyright_notice(ufo_folder)
      if current_notice is None:
        continue
      if copyright is not None and current_notice != copyright:
        failed = True
        fb.error('"{}" != "{}"'.format(current_notice,
                                       copyright))
        break
      copyright = current_notice
    if failed is False:
      fb.ok("Copyright notice is consistent across all fonts in this family.")


def check_OS2_fsSelection(fb, font, style):
  fb.new_check("129", "Checking OS/2 fsSelection value")

  # Checking fsSelection REGULAR bit:
  check_bit_entry(fb, font, "OS/2", "fsSelection",
                  "Regular" in style or
                  (style in STYLE_NAMES and
                   style not in RIBBI_STYLE_NAMES and
                   "Italic" not in style),
                  bitmask=FSSEL_REGULAR,
                  bitname="REGULAR")

  # Checking fsSelection ITALIC bit:
  check_bit_entry(fb, font, "OS/2", "fsSelection",
                  "Italic" in style,
                  bitmask=FSSEL_ITALIC,
                  bitname="ITALIC")

  # Checking fsSelection BOLD bit:
  check_bit_entry(fb, font, "OS/2", "fsSelection",
                  style in ["Bold", "BoldItalic"],
                  bitmask=FSSEL_BOLD,
                  bitname="BOLD")


def check_post_italicAngle(fb, font, style):
  fb.new_check("130", "Checking post.italicAngle value")
  failed = False
  value = font['post'].italicAngle

  # Checking that italicAngle <= 0
  if value > 0:
    failed = True
    if fb.config['autofix']:
      font['post'].italicAngle = -value
      fb.hotfix(("post.italicAngle"
                 " from {} to {}").format(value, -value))
    else:
      fb.error(("post.italicAngle value must be changed"
                " from {} to {}").format(value, -value))
    value = -value

  # Checking that italicAngle is less than 20 degrees:
  if abs(value) > 20:
    failed = True
    if fb.config['autofix']:
      font['post'].italicAngle = -20
      fb.hotfix(("post.italicAngle"
                 " changed from {} to -20").format(value))
    else:
      fb.error(("post.italicAngle value must be"
                " changed from {} to -20").format(value))

  # Checking if italicAngle matches font style:
  if "Italic" in style:
    if font['post'].italicAngle == 0:
      failed = True
      fb.error("Font is italic, so post.italicAngle"
               " should be non-zero.")
  else:
    if font['post'].italicAngle != 0:
      failed = True
      fb.error("Font is not italic, so post.italicAngle"
               " should be equal to zero.")

  if not failed:
    fb.ok("post.italicAngle is {}".format(value))


def check_head_macStyle(fb, font, style):
  fb.new_check("131", "Checking head.macStyle value")

  # Checking macStyle ITALIC bit:
  check_bit_entry(fb, font, "head", "macStyle",
                  "Italic" in style,
                  bitmask=MACSTYLE_ITALIC,
                  bitname="ITALIC")

  # Checking macStyle BOLD bit:
  check_bit_entry(fb, font, "head", "macStyle",
                  style in ["Bold", "BoldItalic"],
                  bitmask=MACSTYLE_BOLD,
                  bitname="BOLD")


def check_with_pyfontaine(fb, font_file, glyphset):
  try:
    import subprocess
    fontaine_output = subprocess.check_output(["pyfontaine",
                                               "--missing",
                                               "--set", glyphset,
                                               font_file],
                                              stderr=subprocess.STDOUT)
    if "Support level: full" not in fontaine_output:
      fb.error(("pyfontaine output follows:\n\n"
                "{}\n").format(fontaine_output))
    else:
      fb.ok("pyfontaine passed this file")
  except subprocess.CalledProcessError, e:
    fb.error(("pyfontaine returned an error code. Output follows :"
              "\n\n{}\n").format(e.output))
  except OSError:
    # This is made very prominent with additional line breaks
    fb.warning("\n\n\npyfontaine is not available!"
               " You really MUST check the fonts with this tool."
               " To install it, see"
               " https://github.com/googlefonts"
               "/gf-docs/blob/master/ProjectChecklist.md#pyfontaine\n\n\n")


def check_glyphset_google_cyrillic_historical(fb, font_file):
  fb.new_check("132", "Checking Cyrillic Historical glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_cyrillic_historical")


def check_glyphset_google_cyrillic_plus(fb, font_file):
  fb.new_check("133", "Checking Google Cyrillic Plus glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_cyrillic_plus")


def check_glyphset_google_cyrillic_plus_locl(fb, font_file):
  fb.new_check("134", "Checking Google Cyrillic Plus"
                      " (Localized Forms) glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_cyrillic_plus_locl")


def check_glyphset_google_cyrillic_pro(fb, font_file):
  fb.new_check("135", "Checking Google Cyrillic Pro glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_cyrillic_pro")


def check_glyphset_google_greek_ancient_musical(fb, font_file):
  fb.new_check("136", "Checking Google Greek Ancient"
                      " Musical Symbols glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_ancient_musical_symbols")


def check_glyphset_google_greek_archaic(fb, font_file):
  fb.new_check("137", "Checking Google Greek Archaic glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_archaic")


def check_glyphset_google_greek_coptic(fb, font_file):
  fb.new_check("138", "Checking Google Greek Coptic glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_coptic")


def check_glyphset_google_greek_core(fb, font_file):
  fb.new_check("139", "Checking Google Greek Core glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_core")


def check_glyphset_google_greek_expert(fb, font_file):
  fb.new_check("140", "Checking Google Greek Expert glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_expert")


def check_glyphset_google_greek_plus(fb, font_file):
  fb.new_check("141", "Checking Google Greek Plus glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_plus")


def check_glyphset_google_greek_pro(fb, font_file):
  fb.new_check("142", "Checking Google Greek Pro glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_greek_pro")


def check_glyphset_google_latin_core(fb, font_file):
  fb.new_check("143", "Checking Google Latin Core glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_core")


def check_glyphset_google_latin_expert(fb, font_file):
  fb.new_check("144", "Checking Google Latin Expert glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_expert")


def check_glyphset_google_latin_plus(fb, font_file):
  fb.new_check("145", "Checking Google Latin Plus glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_plus")


def check_glyphset_google_latin_plus_optional(fb, font_file):
  fb.new_check("146", "Checking Google Latin Plus"
                      " (Optional Glyphs) glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_plus_optional")


def check_glyphset_google_latin_pro(fb, font_file):
  fb.new_check("147", "Checking Google Latin Pro glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_pro")


def check_glyphset_google_latin_pro_optional(fb, font_file):
  fb.new_check("148", "Checking Google Latin Pro"
                      " (Optional Glyphs) glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_latin_pro_optional")


def check_glyphset_google_arabic(fb, font_file):
  fb.new_check("149", "Checking Google Arabic glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_arabic")


def check_glyphset_google_vietnamese(fb, font_file):
  fb.new_check("150", "Checking Google Vietnamese glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_vietnamese")


def check_glyphset_google_extras(fb, font_file):
  fb.new_check("151", "Checking Google Extras glyph coverage")
  check_with_pyfontaine(fb, font_file, "google_extras")
