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
                             getGlyph,
                             getGlyphEncodings,
                             glyphHasInk,
                             getWidth,
                             setWidth,
                             ttfauto_fpgm_xheight_rounding,
                             glyphs_surface_area,
                             save_FamilyProto_Message,
                             parse_version_string,
                             font_key,
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
                                 WEIGHTS,
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


def check_font_designer_field_is_not_unknown(fb, family):
  fb.new_check("007", "Font designer field is 'unknown' ?")
  if family.designer.lower() == 'unknown':
    fb.error("Font designer field is '{}'.".format(family.designer))
  else:
    fb.ok("Font designer field is not 'unknown'.")


def check_fonts_have_consistent_PANOSE_proportion(fb, family, ttf):
  fb.new_check("009", "Fonts have consistent PANOSE proportion?")
  fail = False
  proportion = None
  for f in family.fonts:
    ttfont = ttf[font_key(f)]
    if proportion is None:
      proportion = ttfont['OS/2'].panose.bProportion
    if proportion != ttfont['OS/2'].panose.bProportion:
      fail = True

  if fail:
    fb.error("PANOSE proportion is not"
             " the same accross this family."
             " In order to fix this,"
             " please make sure that the panose.bProportion value"
             " is the same in the OS/2 table of all of this family"
             " font files.")
  else:
    fb.ok("Fonts have consistent PANOSE proportion.")


def check_fonts_have_consistent_PANOSE_family_type(fb, family, ttf):
  fb.new_check("010", "Fonts have consistent PANOSE family type?")
  fail = False
  familytype = None
  for f in family.fonts:
    ttfont = ttf[font_key(f)]
    if familytype is None:
      familytype = ttfont['OS/2'].panose.bFamilyType
    if familytype != ttfont['OS/2'].panose.bFamilyType:
      fail = True

  if fail:
    fb.error("PANOSE family type is not"
             " the same accross this family."
             " In order to fix this,"
             " please make sure that the panose.bFamilyType value"
             " is the same in the OS/2 table of all of this family"
             " font files.")
  else:
    fb.ok("Fonts have consistent PANOSE family type.")


def check_fonts_have_equal_numbers_of_glyphs(fb, family, ttf):
  fb.new_check("011", "Fonts have equal numbers of glyphs?")
  counts = {}
  glyphs_count = None
  fail = False
  for f in family.fonts:
    ttfont = ttf[font_key(f)]
    this_count = len(ttfont['glyf'].glyphs)
    if glyphs_count is None:
      glyphs_count = this_count
    if glyphs_count != this_count:
      fail = True
    counts[f.filename] = this_count

  if fail:
    results_table = ""
    for key in counts.keys():
      results_table += "| {} | {} |\n".format(key,
                                              counts[key])

    fb.error('Fonts have different numbers of glyphs:\n\n'
             '{}\n'.format(results_table))
  else:
    fb.ok("Fonts have equal numbers of glyphs.")


def check_fonts_have_equal_glyph_names(fb, family, ttf):
  fb.new_check("012", "Fonts have equal glyph names?")
  glyphs = None
  fail = False
  for f in family.fonts:
    ttfont = ttf[font_key(f)]
    if not glyphs:
      glyphs = ttfont['glyf'].glyphs
    if glyphs.keys() != ttfont['glyf'].glyphs.keys():
      fail = True
  if fail:
    fb.error('Fonts have different glyph names.')
  else:
    fb.ok("Fonts have equal glyph names.")


def check_fonts_have_equal_unicode_encodings(fb, family, ttf):
  fb.new_check("013", "Fonts have equal unicode encodings?")
  encoding = None
  fail = False
  for f in family.fonts:
    ttfont = ttf[font_key(f)]
    cmap = None
    for table in ttfont['cmap'].tables:
      if table.format == 4:
        cmap = table
        break
    if not encoding:
      encoding = cmap.platEncID
    if encoding != cmap.platEncID:
      fail = True
  if fail:
    fb.error('Fonts have different unicode encodings.')
  else:
    fb.ok("Fonts have equal unicode encodings.")


def check_all_fontfiles_have_same_version(fb, fonts_to_check, ttf_cache):
  fb.new_check("014", "Make sure all font files have the same version value.")
  all_detected_versions = []
  fontfile_versions = {}
  for target in fonts_to_check:
    font = ttf_cache(target)
    v = font['head'].fontRevision
    fontfile_versions[target] = v

    if v not in all_detected_versions:
      all_detected_versions.append(v)
  if len(all_detected_versions) != 1:
    versions_list = ""
    for v in fontfile_versions.keys():
      versions_list += "* {}: {}\n".format(v, fontfile_versions[v])
    fb.warning(("version info differs among font"
                " files of the same font project.\n"
                "These were the version values found:\n"
                "{}").format(versions_list))
  else:
    fb.ok("All font files have the same version.")


def check_OS2_fsType(fb):
  """Fonts must have their fsType bit set to 0. This setting is known as
  Installable Embedding,
  https://www.microsoft.com/typography/otspec/os2.htm#fst"""
  fb.new_check("016", "Checking OS/2 fsType")
  fb.assert_table_entry('OS/2', 'fsType', 0)
  fb.log_results("OS/2 fsType is a legacy DRM-related field from the 80's"
                 " and must be zero (disabled) in all fonts.")


def check_main_entries_in_the_name_table(fb, font, fullpath):
  '''Each entry in the name table has a criteria for validity and
     this check tests if all entries in the name table are
     in conformance with that. This check applies only
     to name IDs 1, 2, 4, 6, 16, 17, 18.
     It must run before any of the other name table related checks.
  '''
  fb.new_check("017", "Assure valid format for the"
                      " main entries in the name table.")
  fb.set_priority(IMPORTANT)

  def family_with_spaces(value):
    FAMILY_WITH_SPACES_EXCEPTIONS = {'VT323': 'VT323',
                                     'PressStart2P': 'Press Start 2P',
                                     'ABeeZee': 'ABeeZee'}
    if value in FAMILY_WITH_SPACES_EXCEPTIONS.keys():
      return FAMILY_WITH_SPACES_EXCEPTIONS[value]
    result = ''
    for c in value:
      if c.isupper():
        result += " "
      result += c
    result = result.strip()

    if result[-3:] == "S C":
      result = result[:-3] + "SC"

    return result

  def get_only_weight(value):
    onlyWeight = {"BlackItalic": "Black",
                  "BoldItalic": "",
                  "ExtraBold": "ExtraBold",
                  "ExtraBoldItalic": "ExtraBold",
                  "ExtraLightItalic": "ExtraLight",
                  "LightItalic": "Light",
                  "MediumItalic": "Medium",
                  "SemiBoldItalic": "SemiBold",
                  "ThinItalic": "Thin"}
    if value in onlyWeight.keys():
      return onlyWeight[value]
    else:
      return value

  filename = os.path.split(fullpath)[1]
  filename_base = os.path.splitext(filename)[0]
  fname, style = filename_base.split('-')
  fname_with_spaces = family_with_spaces(fname)
  style_with_spaces = style.replace('Italic',
                                    ' Italic').strip()
  only_weight = get_only_weight(style)
  required_nameIDs = [NAMEID_FONT_FAMILY_NAME,
                      NAMEID_FONT_SUBFAMILY_NAME,
                      NAMEID_FULL_FONT_NAME,
                      NAMEID_POSTSCRIPT_NAME]

  if style not in RIBBI_STYLE_NAMES:
    required_nameIDs += [NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                         NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME]
  failed = False
  # The font must have at least these name IDs:
  for nameId in required_nameIDs:
    if len(get_name_string(font, nameId)) == 0:
      failed = True
      fb.error(("Font lacks entry with"
                " nameId={} ({})").format(nameId,
                                          NAMEID_STR[nameId]))
  for name in font['name'].names:
    string = name.string.decode(name.getEncoding()).strip()
    nameid = name.nameID
    plat = name.platformID
    expected_value = None

    if nameid == NAMEID_FONT_FAMILY_NAME:
      if plat == PLATFORM_ID_MACINTOSH:
        expected_value = fname_with_spaces
      elif plat == PLATFORM_ID_WINDOWS:
        if style in ['Regular',
                     'Italic',
                     'Bold',
                     'Bold Italic']:
          expected_value = fname_with_spaces
        else:
          expected_value = " ".join([fname_with_spaces,
                                     only_weight]).strip()
      else:
        fb.error(("Font should not have a "
                  "[{}({}):{}({})] entry!").format(NAMEID_STR[nameid],
                                                   nameid,
                                                   PLATID_STR[plat],
                                                   plat))
        continue
    elif nameid == NAMEID_FONT_SUBFAMILY_NAME:
      if style_with_spaces not in STYLE_NAMES:
        fb.error(("Style name '{}' inferred from filename"
                  " is not canonical."
                  " Valid options are: {}").format(style_with_spaces,
                                                   STYLE_NAMES))
        continue
      if plat == PLATFORM_ID_MACINTOSH:
        expected_value = style_with_spaces

      elif plat == PLATFORM_ID_WINDOWS:
        if style_with_spaces in ["Bold", "Bold Italic"]:
          expected_value = style_with_spaces
        else:
          if "Italic" in style:
            expected_value = "Italic"
          else:
            expected_value = "Regular"

    elif name.nameID == NAMEID_FULL_FONT_NAME:
      expected_value = "{} {}".format(fname_with_spaces,
                                      style_with_spaces)

    elif name.nameID == NAMEID_POSTSCRIPT_NAME:
      expected_value = "{}-{}".format(fname, style)

    elif nameid == NAMEID_TYPOGRAPHIC_FAMILY_NAME:
      if style not in ['Regular',
                       'Italic',
                       'Bold',
                       'Bold Italic']:
        expected_value = fname_with_spaces

    elif nameid == NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME:
      if style not in ['Regular',
                       'Italic',
                       'Bold',
                       'Bold Italic']:
        expected_value = style_with_spaces
    else:
      # This ignores any other nameID that might
      # be declared in the name table
      continue
    if expected_value is None:
        fb.warning(("Font is not expected to have a "
                    "[{}({}):{}({})] entry!").format(NAMEID_STR[nameid],
                                                     nameid,
                                                     PLATID_STR[plat],
                                                     plat))
    elif string != expected_value:
      failed = True
      fb.error(("[{}({}):{}({})] entry:"
                " expected '{}'"
                " but got '{}'").format(NAMEID_STR[nameid],
                                        nameid,
                                        PLATID_STR[plat],
                                        plat,
                                        expected_value,
                                        unidecode(string)))
  if failed is False:
    fb.ok("Main entries in the name table"
          " conform to expected format.")


def check_OS2_achVendID(fb, font, registered_vendor_ids):
  fb.new_check("018", "Checking OS/2 achVendID")
  vid = font['OS/2'].achVendID
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  if vid is None:
    fb.error("OS/2 VendorID is not set."
             " You should set it to your own 4 character code,"
             " and register that code with Microsoft at"
             " https://www.microsoft.com"
             "/typography/links/vendorlist.aspx")
  elif vid in bad_vids:
    fb.error(("OS/2 VendorID is '{}', a font editor default."
              " You should set it to your own 4 character code,"
              " and register that code with Microsoft at"
              " https://www.microsoft.com"
              "/typography/links/vendorlist.aspx").format(vid))
  elif len(registered_vendor_ids.keys()) > 0:
    if vid in registered_vendor_ids.keys():
      for name in font['name'].names:
        if name.nameID == NAMEID_MANUFACTURER_NAME:
          manufacturer = name.string.decode(name.getEncoding()).strip()
          if manufacturer != registered_vendor_ids[vid].strip():
            fb.warning("VendorID string '{}' does not match"
                       " nameID {} (Manufacturer Name): '{}'".format(
                         unidecode(registered_vendor_ids[vid]).strip(),
                         NAMEID_MANUFACTURER_NAME,
                         unidecode(manufacturer)))
      fb.ok(("OS/2 VendorID is '{}' and registered to '{}'."
             " Is that legit?"
             ).format(vid,
                      unidecode(registered_vendor_ids[vid])))
    elif vid.lower() in [i.lower() for i in registered_vendor_ids.keys()]:
      fb.error(("OS/2 VendorID is '{}' but this is registered"
                " with different casing."
                " You should check the case.").format(vid))
    else:
      fb.warning(("OS/2 VendorID is '{}' but"
                  " this is not registered with Microsoft."
                  " You should register it at"
                  " https://www.microsoft.com"
                  "/typography/links/vendorlist.aspx").format(vid))
  else:
    fb.warning(("OS/2 VendorID is '{}'"
                " but could not be checked against Microsoft's list."
                " You should check your internet connection"
                " and try again.").format(vid))


def check_name_entries_symbol_substitutions(fb, font):
  fb.new_check("019", "substitute copyright, registered and trademark"
                      " symbols in name table entries")
  failed = False
  replacement_map = [(u"\u00a9", '(c)'),
                     (u"\u00ae", '(r)'),
                     (u"\u2122", '(tm)')]
  for name in font['name'].names:
    new_name = name
    original = unicode(name.string, encoding=name.getEncoding())
    string = unicode(name.string, encoding=name.getEncoding())
    for mark, ascii_repl in replacement_map:
      new_string = string.replace(mark, ascii_repl)
      if string != new_string:
        if fb.config['autofix']:
          fb.hotfix(("NAMEID #{} contains symbol that was"
                     " replaced by '{}'").format(name.nameID,
                                                 ascii_repl))
          string = new_string
        else:
          fb.error(("NAMEID #{} contains symbol that should be"
                    " replaced by '{}'").format(name.nameID,
                                                ascii_repl))
    new_name.string = string.encode(name.getEncoding())
    if string != original:
      failed = True
  if not failed:
    fb.ok("No need to substitute copyright, registered and"
          " trademark symbols in name table entries of this font.")


def check_OS2_usWeightClass(fb, font, style):
  """The Google Font's API which serves the fonts can only serve
  the following weights values with the  corresponding subfamily styles:

  250, Thin
  275, ExtraLight
  300, Light
  400, Regular
  500, Medium
  600, SemiBold
  700, Bold
  800, ExtraBold
  900, Black

  Thin is not set to 100 because of legacy Windows GDI issues:
  https://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html
  """
  fb.new_check("020", "Checking OS/2 usWeightClass")

  if style == "Italic":
    weight_name = "Regular"
  elif style.endswith("Italic"):
    weight_name = style.replace("Italic", "")
  else:
    weight_name = style

  value = font['OS/2'].usWeightClass
  expected = WEIGHTS[weight_name]
  if value != expected:
    if fb.config['autofix']:
      font['OS/2'].usWeightClass = expected
      fb.hotfix(("OS/2 usWeightClass value was"
                 " fixed from {} to {} ({})."
                 "").format(value, expected, weight_name))
    else:
      fb.error(("OS/2 usWeightClass expected value for"
                " '{}' is {} but this font has"
                " {}.").format(weight_name, expected, value))
  else:
    fb.ok("OS/2 usWeightClass value looks good!")


def check_copyright_entries_match_license(fb, found, file_path, font):
  fb.new_check("029", "Check copyright namerecords match license file")
  fb.set_priority(CRITICAL)
  if found == "multiple":
    fb.skip("This check will only run after the"
            " multiple-licensing file issue is fixed.")
  else:
    failed = False
    for license in ['OFL.txt', 'LICENSE.txt']:
      placeholder = PLACEHOLDER_LICENSING_TEXT[license]
      license_path = os.path.join(file_path, license)
      license_exists = os.path.exists(license_path)
      entry_found = False
      for i, nameRecord in enumerate(font['name'].names):
        if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
          entry_found = True
          value = nameRecord.string.decode(nameRecord.getEncoding())
          if value != placeholder and license_exists:
            failed = True
            if fb.config['autofix']:
              fb.hotfix(('License file {} exists but'
                         ' NameID {} (LICENSE DESCRIPTION) value'
                         ' on platform {} ({})'
                         ' is not specified for that.'
                         ' Value was: "{}"'
                         ' Expected: "{}"'
                         '').format(license,
                                    NAMEID_LICENSE_DESCRIPTION,
                                    nameRecord.platformID,
                                    PLATID_STR[nameRecord.platformID],
                                    unidecode(value),
                                    unidecode(placeholder)))
              font['name'].setName(placeholder,
                                   NAMEID_LICENSE_DESCRIPTION,
                                   font['name'].names[i].platformID,
                                   font['name'].names[i].platEncID,
                                   font['name'].names[i].langID)
            else:
              fb.error(('License file {} exists but'
                        ' NameID {} (LICENSE DESCRIPTION) value'
                        ' on platform {} ({})'
                        ' is not specified for that.'
                        ' Value was: "{}"'
                        ' Must be changed to "{}"'
                        '').format(license,
                                   NAMEID_LICENSE_DESCRIPTION,
                                   nameRecord.platformID,
                                   PLATID_STR[nameRecord.platformID],
                                   unidecode(value),
                                   unidecode(placeholder)))

          if value == placeholder and license_exists is False:
            fb.info(('Valid licensing specified'
                     ' on NameID {} (LICENSE DESCRIPTION)'
                     ' on platform {} ({})'
                     ' but a corresponding "{}" file was'
                     ' not found.'
                     '').format(NAMEID_LICENSE_DESCRIPTION,
                                nameRecord.platformID,
                                PLATID_STR[nameRecord.platformID],
                                license))
      if not entry_found and license_exists:
        failed = True
        if fb.config['autofix']:
          font['name'].setName(placeholder,
                               NAMEID_LICENSE_DESCRIPTION,
                               PLATFORM_ID_WINDOWS,
                               PLAT_ENC_ID_UCS2,
                               LANG_ID_ENGLISH_USA)
          fb.hotfix(("Font lacks NameID {} (LICENSE DESCRIPTION)."
                     " A proper licensing entry was set."
                     "").format(NAMEID_LICENSE_DESCRIPTION))
        else:
          fb.error(("Font lacks NameID {} (LICENSE DESCRIPTION)."
                    " A proper licensing entry must be set."
                    "").format(NAMEID_LICENSE_DESCRIPTION))
    if not failed:
      fb.ok("licensing entry on name table is correctly set.")


def check_description_strings_do_not_exceed_100_chars(fb, font):
  fb.new_check("032", ("Description strings in the name table"
                       " (nameID = {}) must not exceed"
                       " 100 characters").format(NAMEID_DESCRIPTION))
  failed = False
  for name in font['name'].names:
    if len(name.string.decode(name.getEncoding())) > 100 \
      and name.nameID == NAMEID_DESCRIPTION:
      if fb.config['autofix']:
        del name
      failed = True
  if failed:
    if fb.config['autofix']:
      fb.hotfix(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                 " were removed because they"
                 " were longer than 100 characters"
                 ".").format(NAMEID_DESCRIPTION))
    else:
      fb.error(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                " are longer than 100 characters"
                " and should be removed.").format(NAMEID_DESCRIPTION))
  else:
    fb.ok("Description name records do not exceed 100 characters.")


def check_font_is_truly_monospaced(fb, font):
  fb.new_check("033", "Checking if the font is truly monospaced")
  ''' There are various metadata in the OpenType spec to specify if
      a font is monospaced or not.

      The source of truth for if a font is monospaced is if 90% of all
      glyphs have the same width. If this is true then these metadata
      must be set.

      If not true, no monospaced metadata should be set (as sometimes
      they mistakenly are...)

      Monospace fonts must:

      * post.isFixedWidth "Set to 0 if the font is proportionally spaced,
        non-zero if the font is not proportionally spaced (monospaced)"
        www.microsoft.com/typography/otspec/post.htm

      * hhea.advanceWidthMax must be correct, meaning no glyph's
       width value is greater.
       www.microsoft.com/typography/otspec/hhea.htm

     * OS/2.panose.bProportion must be set to 9 (monospace). Spec says:
       "The PANOSE definition contains ten digits each of which currently
       describes up to sixteen variations. Windows uses bFamilyType,
       bSerifStyle and bProportion in the font mapper to determine
       family type. It also uses bProportion to determine if the font
       is monospaced."
       www.microsoft.com/typography/otspec/os2.htm#pan
       monotypecom-test.monotype.de/services/pan2

     * OS/2.xAverageWidth must be set accurately.
       "OS/2.xAverageWidth IS used when rendering monospaced fonts,
       at least by Windows GDI"
       http://typedrawers.com/discussion/comment/15397/#Comment_15397

     Also we should report an error for glyphs not of average width
'''
  glyphs = font['glyf'].glyphs
  width_occurrences = {}
  width_max = 0
  # count how many times a width occurs
  for glyph_id in glyphs:
      width = font['hmtx'].metrics[glyph_id][0]
      width_max = max(width, width_max)
      try:
          width_occurrences[width] += 1
      except KeyError:
          width_occurrences[width] = 1
  # find the most_common_width
  occurrences = 0
  for width in width_occurrences.keys():
      if width_occurrences[width] > occurrences:
          occurrences = width_occurrences[width]
          most_common_width = width
  # if more than 80% of glyphs have the same width, set monospaced metadata
  monospace_detected = occurrences > 0.80 * len(glyphs)
  if monospace_detected:
      fb.assert_table_entry('post',
                            'isFixedPitch',
                            IS_FIXED_WIDTH_MONOSPACED)
      fb.assert_table_entry('hhea', 'advanceWidthMax', width_max)
      fb.assert_table_entry('OS/2',
                            'panose.bProportion',
                            PANOSE_PROPORTION_MONOSPACED)
      outliers = len(glyphs) - occurrences
      if outliers > 0:
          # If any glyphs are outliers, note them
          unusually_spaced_glyphs = \
           [g for g in glyphs
            if font['hmtx'].metrics[g][0] != most_common_width]
          outliers_percentage = 100 - (100.0 * occurrences/len(glyphs))

          for glyphname in ['.notdef', '.null', 'NULL']:
            if glyphname in unusually_spaced_glyphs:
              unusually_spaced_glyphs.remove(glyphname)

          fb.log_results(("Font is monospaced but {} glyphs"
                          " ({}%) have a different width."
                          " You should check the widths of: {}").format(
                            outliers,
                            outliers_percentage,
                            unusually_spaced_glyphs))
      else:
          fb.log_results("Font is monospaced.")
  else:
      # it is not monospaced, so unset monospaced metadata
      fb.assert_table_entry('post',
                            'isFixedPitch',
                            IS_FIXED_WIDTH_NOT_MONOSPACED)
      fb.assert_table_entry('hhea', 'advanceWidthMax', width_max)
      if font['OS/2'].panose.bProportion == PANOSE_PROPORTION_MONOSPACED:
          fb.assert_table_entry('OS/2',
                                'panose.bProportion',
                                PANOSE_PROPORTION_ANY)
      fb.log_results("Font is not monospaced.")
  return monospace_detected


def check_OS2_xAvgCharWidth(fb, font):
  fb.new_check("034", "Check if OS/2 xAvgCharWidth is correct.")
  if font['OS/2'].version >= 3:
    width_sum = 0
    count = 0
    for glyph_id in font['glyf'].glyphs:
      width = font['hmtx'].metrics[glyph_id][0]
      if width > 0:
        count += 1
        width_sum += width
    if count == 0:
      fb.error("CRITICAL: Found no glyph width data!")
    else:
      expected_value = int(round(width_sum) / count)
      if font['OS/2'].xAvgCharWidth == expected_value:
        fb.ok("OS/2 xAvgCharWidth is correct.")
      else:
        fb.error(("OS/2 xAvgCharWidth is {} but should be "
                  "{} which corresponds to the "
                  "average of all glyph widths "
                  "in the font").format(font['OS/2'].xAvgCharWidth,
                                        expected_value))
  else:
    weightFactors = {'a': 64, 'b': 14, 'c': 27, 'd': 35,
                     'e': 100, 'f': 20, 'g': 14, 'h': 42,
                     'i': 63, 'j': 3, 'k': 6, 'l': 35,
                     'm': 20, 'n': 56, 'o': 56, 'p': 17,
                     'q': 4, 'r': 49, 's': 56, 't': 71,
                     'u': 31, 'v': 10, 'w': 18, 'x': 3,
                     'y': 18, 'z': 2, 'space': 166}
    width_sum = 0
    for glyph_id in font['glyf'].glyphs:
      width = font['hmtx'].metrics[glyph_id][0]
      if glyph_id in weightFactors.keys():
        width_sum += (width*weightFactors[glyph_id])
    expected_value = int(width_sum/1000.0 + 0.5)  # round to closest int
    if font['OS/2'].xAvgCharWidth == expected_value:
      fb.ok("OS/2 xAvgCharWidth value is correct.")
    else:
      fb.error(("OS/2 xAvgCharWidth is {} but it should be "
                "{} which corresponds to the weighted "
                "average of the widths of the latin "
                "lowercase glyphs in "
                "the font").format(font['OS/2'].xAvgCharWidth,
                                   expected_value))


def check_with_ftxvalidator(fb, font_file):
  fb.new_check("035", "Checking with ftxvalidator")
  try:
    import subprocess
    ftx_cmd = ["ftxvalidator",
               "-t", "all",  # execute all tests
               font_file]
    ftx_output = subprocess.check_output(ftx_cmd,
                                         stderr=subprocess.STDOUT)

    ftx_data = plistlib.readPlistFromString(ftx_output)
    # we accept kATSFontTestSeverityInformation
    # and kATSFontTestSeverityMinorError
    if 'kATSFontTestSeverityFatalError' \
       not in ftx_data['kATSFontTestResultKey']:
      fb.ok("ftxvalidator passed this file")
    else:
      ftx_cmd = ["ftxvalidator",
                 "-T",  # Human-readable output
                 "-r",  # Generate a full report
                 "-t", "all",  # execute all tests
                 font_file]
      ftx_output = subprocess.check_output(ftx_cmd,
                                           stderr=subprocess.STDOUT)
      fb.error("ftxvalidator output follows:\n\n{}\n".format(ftx_output))

  except subprocess.CalledProcessError, e:
    fb.info(("ftxvalidator returned an error code. Output follows :"
             "\n\n{}\n").format(e.output))
  except OSError:
    fb.warning("ftxvalidator is not available!")


def check_with_otsanitise(fb, font_file):
  fb.new_check("036", "Checking with ots-sanitize")
  try:
    import subprocess
    ots_output = subprocess.check_output(["ots-sanitize", font_file],
                                         stderr=subprocess.STDOUT)
    if ots_output != "" and "File sanitized successfully" not in ots_output:
      fb.error("ots-sanitize output follows:\n\n{}\n".format(ots_output))
    else:
      fb.ok("ots-sanitize passed this file")
  except subprocess.CalledProcessError, e:
      fb.error(("ots-sanitize returned an error code. Output follows :"
                "\n\n{}\n").format(e.output))
  except OSError, e:
    # This is made very prominent with additional line breaks
    fb.warning("\n\n\nots-sanitize is not available!"
               " You really MUST check the fonts with this tool."
               " To install it, see"
               " https://github.com/googlefonts"
               "/gf-docs/blob/master/ProjectChecklist.md#ots"
               " Actual error message was: "
               "'{}'\n\n".format(e))


def check_with_msfontvalidator(fb, font_file):
  fb.new_check("037", "Checking with Microsoft Font Validator")
  try:
    import subprocess
    fval_cmd = ["FontValidator.exe",
                "-file", font_file,
                "-all-tables",
                "-report-in-font-dir"]
    subprocess.check_output(fval_cmd, stderr=subprocess.STDOUT)
    xml_report = open("{}.report.xml".format(font_file), "r").read()
    try:
      os.remove("{}.report.xml".format(font_file))
      os.remove("{}.report.html".format(font_file))
    except:
      # Treat failure to delete reports
      # as non-critical. Silently move on.
      pass

    doc = defusedxml.lxml.fromstring(xml_report)
    for report in doc.iter('Report'):
      if report.get("ErrorType") == "P":
        fb.ok("MS-FonVal: {}".format(report.get("Message")))
      elif report.get("ErrorType") == "E":
        fb.error("MS-FonVal: {} DETAILS: {}".format(report.get("Message"),
                                                    report.get("Details")))
      elif report.get("ErrorType") == "W":
        fb.warning("MS-FonVal: {} DETAILS: {}".format(report.get("Message"),
                                                      report.get("Details")))
      else:
        fb.info("MS-FontVal: {}".format(report.get("Message")))
  except subprocess.CalledProcessError, e:
    fb.info(("Microsoft Font Validator returned an error code."
             " Output follows :\n\n{}\n").format(e.output))
  except OSError:
    fb.warning("Mono runtime and/or "
               "Microsoft Font Validator are not available!")
  except IOError:
    fb.warning("Mono runtime and/or "
               "Microsoft Font Validator are not available!")
    return


def check_fforge_outputs_error_msgs(fb, font_file):
  fb.new_check("038", "fontforge validation outputs error messages?")
  if "adobeblank" in font_file:
    fb.skip("Skipping AdobeBlank since"
            " this font is a very peculiar hack.")
    return None


  import subprocess
  cmd = (
        'import fontforge, sys;'
        'status = fontforge.open("{0}").validate();'
        'sys.stdout.write(status.__str__());'.format
        )

  p = subprocess.Popen(['python', '-c', cmd(font_file)],
                       stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE
                      )
  validation_state, ff_err_messages = p.communicate()
  try:
    validation_state = int(validation_state)
  except:
    # None as a value is understood by the fontbakery-check-ttf.py script
    validation_state = None
    pass

  filtered_err_msgs = ""
  for line in ff_err_messages.split('\n'):
    if 'The following table(s) in the font' \
        ' have been ignored by FontForge' in line:
      continue
    if "Ignoring 'DSIG' digital signature table" in line:
      continue
    filtered_err_msgs += line + '\n'

  if len(filtered_err_msgs.strip()) > 0:
    fb.error(("fontforge did print these messages to stderr:\n"
              "{}").format(filtered_err_msgs))
  else:
    fb.ok("fontforge validation did not output any error message.")
  return validation_state


def perform_all_fontforge_checks(fb, validation_state):
  def ff_check(description, condition, err_msg, ok_msg):
    import sha
    m = sha.new()
    m.update(description)
    short_hash = m.hexdigest()[:8]
    fb.new_check("039-{}".format(short_hash),
                 "fontforge-check: {}".format(description))
    if condition is False:
      fb.error("fontforge-check: {}".format(err_msg))
    else:
      fb.ok("fontforge-check: {}".format(ok_msg))

  ff_check("Contours are closed?",
           bool(validation_state & 0x2) is False,
           "Contours are not closed!",
           "Contours are closed.")

  ff_check("Contours do not intersect",
           bool(validation_state & 0x4) is False,
           "There are countour intersections!",
           "Contours do not intersect.")

  ff_check("Contours have correct directions",
           bool(validation_state & 0x8) is False,
           "Contours have incorrect directions!",
           "Contours have correct directions.")

  ff_check("References in the glyph haven't been flipped",
           bool(validation_state & 0x10) is False,
           "References in the glyph have been flipped!",
           "References in the glyph haven't been flipped.")

  ff_check("Glyphs have points at extremas",
           bool(validation_state & 0x20) is False,
           "Glyphs do not have points at extremas!",
           "Glyphs have points at extremas.")

  ff_check("Glyph names referred to from glyphs present in the font",
           bool(validation_state & 0x40) is False,
           "Glyph names referred to from glyphs"
           " not present in the font!",
           "Glyph names referred to from glyphs"
           " present in the font.")

  ff_check("Points (or control points) are not too far apart",
           bool(validation_state & 0x40000) is False,
           "Points (or control points) are too far apart!",
           "Points (or control points) are not too far apart.")

  ff_check("Not more than 1,500 points in any glyph"
           " (a PostScript limit)",
           bool(validation_state & 0x80) is False,
           "There are glyphs with more than 1,500 points!"
           "Exceeds a PostScript limit.",
           "Not more than 1,500 points in any glyph"
           " (a PostScript limit).")

  ff_check("PostScript has a limit of 96 hints in glyphs",
           bool(validation_state & 0x100) is False,
           "Exceeds PostScript limit of 96 hints per glyph",
           "Font respects PostScript limit of 96 hints per glyph")

  ff_check("Font doesn't have invalid glyph names",
           bool(validation_state & 0x200) is False,
           "Font has invalid glyph names!",
           "Font doesn't have invalid glyph names.")

  ff_check("Glyphs have allowed numbers of points defined in maxp",
           bool(validation_state & 0x400) is False,
           "Glyphs exceed allowed numbers of points defined in maxp",
           "Glyphs have allowed numbers of points defined in maxp.")

  ff_check("Glyphs have allowed numbers of paths defined in maxp",
           bool(validation_state & 0x800) is False,
           "Glyphs exceed allowed numbers of paths defined in maxp!",
           "Glyphs have allowed numbers of paths defined in maxp.")

  ff_check("Composite glyphs have allowed numbers"
           " of points defined in maxp?",
           bool(validation_state & 0x1000) is False,
           "Composite glyphs exceed allowed numbers"
           " of points defined in maxp!",
           "Composite glyphs have allowed numbers"
           " of points defined in maxp.")

  ff_check("Composite glyphs have allowed numbers"
           " of paths defined in maxp",
           bool(validation_state & 0x2000) is False,
           "Composite glyphs exceed"
           " allowed numbers of paths defined in maxp!",
           "Composite glyphs have"
           " allowed numbers of paths defined in maxp.")

  ff_check("Glyphs instructions have valid lengths",
           bool(validation_state & 0x4000) is False,
           "Glyphs instructions have invalid lengths!",
           "Glyphs instructions have valid lengths.")

  ff_check("Points in glyphs are integer aligned",
           bool(validation_state & 0x80000) is False,
           "Points in glyphs are not integer aligned!",
           "Points in glyphs are integer aligned.")

  # According to the opentype spec, if a glyph contains an anchor point
  # for one anchor class in a subtable, it must contain anchor points
  # for all anchor classes in the subtable. Even it, logically,
  # they do not apply and are unnecessary.
  ff_check("Glyphs have all required anchors.",
           bool(validation_state & 0x100000) is False,
           "Glyphs do not have all required anchors!",
           "Glyphs have all required anchors.")

  ff_check("Glyph names are unique?",
           bool(validation_state & 0x200000) is False,
           "Glyph names are not unique!",
           "Glyph names are unique.")

  ff_check("Unicode code points are unique?",
           bool(validation_state & 0x400000) is False,
           "Unicode code points are not unique!",
           "Unicode code points are unique.")

  ff_check("Do hints overlap?",
           bool(validation_state & 0x800000) is False,
           "Hints should NOT overlap!",
           "Hinds do not overlap.")


def check_OS2_usWinAscent_and_Descent(fb, vmetrics_ymin, vmetrics_ymax):
  """A font's winAscent and winDescent values should be the same as the
  head table's yMax, abs(yMin) values. By not setting them to these values,
  clipping can occur on Windows platforms,
  https://github.com/RedHatBrand/Overpass/issues/33

  If the font includes tall/deep writing systems such as Arabic or
  Devanagari, the linespacing can appear too loose. To counteract this,
  enabling the OS/2 fsSelection bit 7 (Use_Typo_Metrics), Windows will use
  the OS/2 typo values instead. This means the font developer can control
  the linespacing with the typo values, whilst avoiding clipping by setting
  the win values to the bounding box."""
  fb.new_check("040", "Checking OS/2 usWinAscent & usWinDescent")
  # OS/2 usWinAscent:
  fb.assert_table_entry('OS/2', 'usWinAscent', vmetrics_ymax)
  # OS/2 usWinDescent:
  fb.assert_table_entry('OS/2', 'usWinDescent', abs(vmetrics_ymin))
  fb.log_results("OS/2 usWinAscent & usWinDescent")


def check_Vertical_Metric_Linegaps(fb, font):
  fb.new_check("041", "Checking Vertical Metric Linegaps")
  if font['hhea'].lineGap != 0:
    fb.warning(("hhea lineGap is not equal to 0"))
  elif font['OS/2'].sTypoLineGap != 0:
    fb.warning(("OS/2 sTypoLineGap is not equal to 0"))
  elif font['OS/2'].sTypoLineGap != font['hhea'].lineGap:
    fb.warning(('OS/2 sTypoLineGap is not equal to hhea lineGap'))
  else:
    fb.ok(('OS/2 sTypoLineGap and hhea lineGap are both 0'))


def check_OS2_Metrics_match_hhea_Metrics(fb, font):
  """OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, Linux and Windows.

  Mac OS X uses the hhea values
  Windows uses OS/2 or Win, depending on the OS or fsSelection bit value"""
  fb.new_check("042", "Checking OS/2 Metrics match hhea Metrics")
  # OS/2 sTypoDescender and sTypoDescender match hhea ascent and descent
  if font['OS/2'].sTypoAscender != font['hhea'].ascent:
    fb.error(("OS/2 sTypoAscender and hhea ascent must be equal"))
  elif font['OS/2'].sTypoDescender != font['hhea'].descent:
    fb.error(("OS/2 sTypoDescender and hhea descent must be equal"))
  else:
    fb.ok("OS/2 sTypoDescender and sTypoDescender match hhea ascent "
          "and descent")


def check_unitsPerEm_value_is_reasonable(fb, font):
  fb.new_check("043", "Checking unitsPerEm value is reasonable.")
  upem = font['head'].unitsPerEm
  target_upem = [2**i for i in range(4, 15)]
  target_upem.insert(0, 1000)
  if upem not in target_upem:
    fb.error(("The value of unitsPerEm at the head table"
              " must be either 1000 or a power of "
              "2 between 16 to 16384."
              " Got '{}' instead.").format(upem))
  else:
    fb.ok("unitsPerEm value on the 'head' table is reasonable.")


def get_version_from_name_entry(name):
  string = name.string.decode(name.getEncoding())
  # we ignore any comments that
  # may be present in the version name entries
  if ";" in string:
    string = string.split(";")[0]
  # and we also ignore
  # the 'Version ' prefix
  if "Version " in string:
    string = string.split("Version ")[1]
  return string.split('.')


def get_expected_version(fb, f):
  expected_version = parse_version_string(fb, str(f['head'].fontRevision))
  for name in f['name'].names:
    if name.nameID == NAMEID_VERSION_STRING:
      name_version = get_version_from_name_entry(name)
      if expected_version is None:
        expected_version = name_version
      else:
        if name_version > expected_version:
          expected_version = name_version
  return expected_version


def check_font_version_fields(fb, font):
  fb.new_check("044", "Checking font version fields")
  failed = False
  try:
    expected = get_expected_version(fb, font)
  except:
    expected = None
    fb.error("failed to parse font version entries in the name table.")

  if expected is None:
    failed = True
    fb.error("Could not find any font versioning info on the head table"
             " or in the name table entries.")
  else:
    font_revision = str(font['head'].fontRevision)
    expected_str = "{}.{}".format(expected[0],
                                  expected[1])
    if font_revision != expected_str:
      failed = True
      fb.error(("Font revision on the head table ({})"
                " differs from the expected value ({})"
                "").format(font_revision, expected))

    expected_str = "Version {}.{}".format(expected[0],
                                          expected[1])
    for name in font['name'].names:
      if name.nameID == NAMEID_VERSION_STRING:
        name_version = name.string.decode(name.getEncoding())

        try:
          # change "Version 1.007" to "1.007"
          # (stripping out the "Version " prefix, if any)
          version_stripped = r'(?<=[V|v]ersion )?([0-9]{1,4}\.[0-9]{1,5})'
          version_without_comments = re.search(version_stripped,
                                               name_version).group(0)
        except:
          failed = True
          fb.error(("Unable to parse font version info"
                    " from this name table entry: '{}'").format(name))
          continue

        comments = re.split(r'(?<=[0-9]{1})[;\s]', name_version)[-1]
        if version_without_comments != expected_str:
          # maybe the version strings differ only
          # on floating-point error, so let's
          # also give it a change by rounding and re-checking...

          try:
            rounded_string = round(float(version_without_comments), 3)
            version = round(float(".".join(expected)), 3)
            if rounded_string != version:
              failed = True
              if comments:
                fix = "{};{}".format(expected_str, comments)
              else:
                fix = expected_str
              if fb.config['autofix']:
                fb.hotfix(("NAMEID_VERSION_STRING "
                           "from '{}' to '{}'"
                           "").format(name_version, fix))
                name.string = fix.encode(name.getEncoding())
              else:
                fb.error(("NAMEID_VERSION_STRING value '{}'"
                          " does not match expected '{}'"
                          "").format(name_version, fix))
          except:
            failed = True  # give up. it's definitely bad :(
            fb.error("Unable to parse font version info"
                     " from name table entries.")
  if not failed:
    fb.ok("All font version fields look good.")


def check_Digital_Signature_exists(fb, font, font_file):
  fb.new_check("045", "Digital Signature exists?")
  if "DSIG" in font:
    fb.ok("Digital Signature (DSIG) exists.")
  else:
    try:
      if fb.config['autofix']:
        from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
        newDSIG = ttLib.newTable("DSIG")
        newDSIG.ulVersion = 1
        newDSIG.usFlag = 1
        newDSIG.usNumSigs = 1
        sig = SignatureRecord()
        sig.ulLength = 20
        sig.cbSignature = 12
        sig.usReserved2 = 0
        sig.usReserved1 = 0
        sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
        sig.ulFormat = 1
        sig.ulOffset = 20
        newDSIG.signatureRecords = [sig]
        font.tables["DSIG"] = newDSIG
        fb.hotfix("The font does not have an existing digital"
                  " signature (DSIG), so we just added a dummy"
                  " placeholder that should be enough for the"
                  " applications that require its presence in"
                  " order to work properly.")
      else:
        fb.error("This font lacks a digital signature (DSIG table)."
                 " Some applications may require one (even if only a"
                 " dummy placeholder) in order to work properly.")
    except ImportError:
      error_message = ("The '{}' font does not have an existing"
                       " digital signature (DSIG), so OpenType features"
                       " will not be available in some applications that"
                       " use its presense as a (stupid) heuristic."
                       " So we need to add one. But for that we'll need"
                       " Fonttools v2.3+ so you need to upgrade it. Try:"
                       " $ pip install --upgrade fontTools; or see"
                       " https://pypi.python.org/pypi/FontTools")
      fb.error(error_message.format(font_file))


def check_font_contains_the_first_few_mandatory_glyphs(fb, font):
  fb.new_check("046", "Font contains the first few mandatory glyphs"
                      " (.null or NULL, CR and space)?")
  # It would be good to also check
  # for .notdef (codepoint = unspecified)
  null = getGlyph(font, 0x0000)
  CR = getGlyph(font, 0x000D)
  space = getGlyph(font, 0x0020)

  missing = []
  if null is None: missing.append("0x0000")
  if CR is None: missing.append("0x000D")
  if space is None: missing.append("0x0020")
  if missing != []:
    fb.warning(("Font is missing glyphs for"
                " the following mandatory codepoints:"
                " {}.").format(", ".join(missing)))
  else:
    fb.ok("Font contains the first few mandatory glyphs"
          " (.null or NULL, CR and space).")


def check_font_contains_glyphs_for_whitespace_chars(fb, font):
  fb.new_check("047", "Font contains glyphs for whitespace characters?")
  space = getGlyph(font, 0x0020)
  nbsp = getGlyph(font, 0x00A0)
  # tab = getGlyph(font, 0x0009)

  missing = []
  if space is None: missing.append("0x0020")
  if nbsp is None: missing.append("0x00A0")
  # fonts probably don't need an actual tab char
  # if tab is None: missing.append("0x0009")
  if missing != []:
    fb.error(("Whitespace glyphs missing for"
              " the following codepoints:"
              " {}.").format(", ".join(missing)))
  else:
    fb.ok("Font contains glyphs for whitespace characters.")
  return missing


def check_font_has_proper_whitespace_glyph_names(fb, font, missing):
  fb.new_check("048", "Font has **proper** whitespace glyph names?")
  if missing != []:
    fb.skip("Because some whitespace glyphs are missing. Fix that before!")
  elif font['post'].formatType == 3.0:
    fb.skip("Font has version 3 post table.")
    # Any further checks for glyph names are pointless
    # because you are really checking names generated by FontTools
    # (or whatever else) that are not actually present in the font.
  else:
    failed = False
    space_enc = getGlyphEncodings(font, ["uni0020", "space"])
    nbsp_enc = getGlyphEncodings(font, ["uni00A0",
                                        "nonbreakingspace",
                                        "nbspace",
                                        "nbsp"])
    space = getGlyph(font, 0x0020)
    if 0x0020 not in space_enc:
      failed = True
      fb.error(('Glyph 0x0020 is called "{}":'
                ' Change to "space"'
                ' or "uni0020"').format(space))

    nbsp = getGlyph(font, 0x00A0)
    if 0x00A0 not in nbsp_enc:
      if 0x00A0 in space_enc:
        # This is OK.
        # Some fonts use the same glyph for both space and nbsp.
        pass
      else:
        failed = True
        fb.error(('Glyph 0x00A0 is called "{}":'
                  ' Change to "nbsp"'
                  ' or "uni00A0"').format(nbsp))

    if failed is False:
      fb.ok('Font has **proper** whitespace glyph names.')


def check_whitespace_glyphs_have_ink(fb, font, missing):
  fb.new_check("049", "Whitespace glyphs have ink?")
  if missing != []:
    fb.skip("Because some whitespace glyphs are missing. Fix that before!")
  else:
    failed = False
    for codepoint in WHITESPACE_CHARACTERS:
      g = getGlyph(font, codepoint)
      if g is not None and glyphHasInk(font, g):
        failed = True
        if fb.config['autofix']:
          fb.hotfix(('Glyph "{}" has ink.'
                     ' Fixed: Overwritten by'
                     ' an empty glyph').format(g))
          # overwrite existing glyph with an empty one
          font['glyf'].glyphs[g] = ttLib.getTableModule('glyf').Glyph()
        else:
          fb.error(('Glyph "{}" has ink.'
                    ' It needs to be replaced by'
                    ' an empty glyph').format(g))
    if not failed:
      fb.ok("There is no whitespace glyph with ink.")


def check_whitespace_glyphs_have_coherent_widths(fb, font, missing):
  fb.new_check("050", "Whitespace glyphs have coherent widths?")
  if missing != []:
    fb.skip("Because some mandatory whitespace glyphs"
            " are missing. Fix that before!")
  else:
    space = getGlyph(font, 0x0020)
    nbsp = getGlyph(font, 0x00A0)

    spaceWidth = getWidth(font, space)
    nbspWidth = getWidth(font, nbsp)

    if spaceWidth != nbspWidth or nbspWidth < 0:
      setWidth(font, nbsp, min(nbspWidth, spaceWidth))
      setWidth(font, space, min(nbspWidth, spaceWidth))

      if nbspWidth > spaceWidth and spaceWidth >= 0:
        if fb.config['autofix']:
          msg = 'space {} nbsp {}: Fixed space advanceWidth to {}'
          fb.hotfix(msg.format(spaceWidth, nbspWidth, nbspWidth))
        else:
          msg = ('space {} nbsp {}: Space advanceWidth'
                 ' needs to be fixed to {}')
          fb.error(msg.format(spaceWidth, nbspWidth, nbspWidth))
      else:
        if fb.config['autofix']:
          msg = 'space {} nbsp {}: Fixed nbsp advanceWidth to {}'
          fb.hotfix(msg.format(spaceWidth, nbspWidth, spaceWidth))
        else:
          msg = ('space {} nbsp {}: Nbsp advanceWidth'
                 ' needs to be fixed to {}')
          fb.error(msg.format(spaceWidth, nbspWidth, spaceWidth))
    else:
      fb.ok("Whitespace glyphs have coherent widths.")

# DEPRECATED: 051 - "Checking with pyfontaine"
# Replaced by 132 - "Checking Google Cyrillic Historical glyph coverage"
# Replaced by 133 - "Checking Google Cyrillic Plus glyph coverage"
# Replaced by 134 - "Checking Google Cyrillic Plus (Localized Forms) glyph coverage"
# Replaced by 135 - "Checking Google Cyrillic Pro glyph coverage"
# Replaced by 136 - "Checking Google Greek Ancient Musical Symbols glyph coverage"
# Replaced by 137 - "Checking Google Greek Archaic glyph coverage"
# Replaced by 138 - "Checking Google Greek Coptic glyph coverage"
# Replaced by 139 - "Checking Google Greek Core glyph coverage"
# Replaced by 140 - "Checking Google Greek Expert glyph coverage"
# Replaced by 141 - "Checking Google Greek Plus glyph coverage"
# Replaced by 142 - "Checking Google Greek Pro glyph coverage"
# Replaced by 143 - "Checking Google Latin Core glyph coverage"
# Replaced by 144 - "Checking Google Latin Expert glyph coverage"
# Replaced by 145 - "Checking Google Latin Plus glyph coverage"
# Replaced by 146 - "Checking Google Latin Plus (Optional Glyphs) glyph coverage"
# Replaced by 147 - "Checking Google Latin Pro glyph coverage"
# Replaced by 148 - "Checking Google Latin Pro (Optional Glyphs) glyph coverage"

def check_no_problematic_formats(fb, font):
  fb.new_check("052", "Check no problematic formats")
  # See https://github.com/googlefonts/fontbakery/issues/617
  # Font contains all required tables?
  tables = set(font.reader.tables.keys())
  glyphs = set(['glyf'] if 'glyf' in font.keys() else ['CFF '])
  if (REQUIRED_TABLES | glyphs) - tables:
    missing_tables = [str(t) for t in (REQUIRED_TABLES | glyphs - tables)]
    desc = (("Font is missing required "
             "tables: [{}]").format(', '.join(missing_tables)))
    if OPTIONAL_TABLES & tables:
      optional_tables = [str(t) for t in (OPTIONAL_TABLES & tables)]
      desc += (" but includes "
               "optional tables [{}]").format(', '.join(optional_tables))
    fb.fixes.append(desc)
  fb.log_results("Check no problematic formats. ", hotfix=False)


def check_for_unwanted_tables(fb, font):
  fb.new_check("053", "Are there unwanted tables?")
  unwanted_tables_found = []
  for table in font.keys():
    if table in UNWANTED_TABLES:
      unwanted_tables_found.append(table)
      del font[table]

  if len(unwanted_tables_found) > 0:
    if fb.config['autofix']:
      fb.hotfix(("Unwanted tables were present"
                 " in the font and were removed:"
                 " {}").format(', '.join(unwanted_tables_found)))
    else:
      fb.error(("Unwanted tables were found"
                " in the font and should be removed:"
                " {}").format(', '.join(unwanted_tables_found)))
  else:
    fb.ok("There are no unwanted tables.")


def check_hinting_filesize_impact(fb, fullpath, filename):
  fb.new_check("054", "Show hinting filesize impact")
  # current implementation simply logs useful info
  # but there's no fail scenario for this checker.
  ttfautohint_missing = False
  try:
    import subprocess
    statinfo = os.stat(fullpath)
    hinted_size = statinfo.st_size

    dehinted = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
    subprocess.call(["ttfautohint",
                     "--dehint",
                     fullpath,
                     dehinted.name])
    statinfo = os.stat(dehinted.name)
    dehinted_size = statinfo.st_size
    os.unlink(dehinted.name)

    if dehinted_size == 0:
      fb.skip("ttfautohint --dehint reports that"
              " 'This font has already been processed with ttfautohint'."
              " This is a bug in an old version of ttfautohint."
              " You'll need to upgrade it."
              " See https://github.com/googlefonts/fontbakery/"
              "issues/1043#issuecomment-249035069")
    else:
      increase = hinted_size - dehinted_size
      change = float(hinted_size)/dehinted_size - 1
      change = int(change*10000)/100.0  # round to 2 decimal pts percentage

      def filesize_formatting(s):
        if s < 1024:
          return "{} bytes".format(s)
        elif s < 1024*1024:
          return "{}kb".format(s/1024)
        else:
          return "{}Mb".format(s/(1024*1024))

      hinted_size = filesize_formatting(hinted_size)
      dehinted_size = filesize_formatting(dehinted_size)
      increase = filesize_formatting(increase)

      results_table = "Hinting filesize impact:\n\n"
      results_table += "|  | {} |\n".format(filename)
      results_table += "|:--- | ---:| ---:|\n"
      results_table += "| Dehinted Size | {} |\n".format(dehinted_size)
      results_table += "| Hinted Size | {} |\n".format(hinted_size)
      results_table += "| Increase | {} |\n".format(increase)
      results_table += "| Change   | {} % |\n".format(change)
      fb.info(results_table)

  except OSError:
    # This is made very prominent with additional line breaks
    ttfautohint_missing = True
    fb.warning("\n\n\nttfautohint is not available!"
               " You really MUST check the fonts with this tool."
               " To install it, see"
               " https://github.com/googlefonts"
               "/gf-docs/blob/master/"
               "ProjectChecklist.md#ttfautohint\n\n\n")
  return ttfautohint_missing


def check_version_format_is_correct_in_NAME_table(fb, font):
  fb.new_check("055", "Version format is correct in NAME table?")

  def is_valid_version_format(value):
    return re.match(r'Version\s0*[1-9]+\.\d+', value)

  failed = False
  version_entries = get_name_string(font, NAMEID_VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    fb.error(("Font lacks a NAMEID_VERSION_STRING (nameID={})"
              " entry").format(NAMEID_VERSION_STRING))
  for ventry in version_entries:
    if not is_valid_version_format(ventry):
      failed = True
      fb.error(('The NAMEID_VERSION_STRING (nameID={}) value must '
                'follow the pattern Version X.Y between 1.000 and 9.999.'
                ' Current value: {}').format(NAMEID_VERSION_STRING,
                                             ventry))
  if not failed:
    fb.ok('Version format in NAME table entries is correct.')


def check_font_has_latest_ttfautohint_applied(fb, font, ttfautohint_missing):
  fb.new_check("056", "Font has old ttfautohint applied?")
  ''' ----------------------------------------------------
     Font has old ttfautohint applied ?

     1. find which version was used, grepping the name table or reading
        the ttfa table (which are created if the `-I` or `-t` args
        respectively were passed to ttfautohint, to record its args in
        the ttf file) (there is a pypi package
        https://pypi.python.org/pypi/font-ttfa for reading the ttfa table,
        although per https://github.com/source-foundry/font-ttfa/issues/1
        it might be better to inline the code... :)

     2. find which version of ttfautohint is installed
        and warn if not available, similar to ots check above

     3. rehint the font with the latest version of ttfautohint
        using the same options
  '''

  def ttfautohint_version(values):
    for value in values:
      results = re.search(r'ttfautohint \(v(.*)\)', value)
      if results:
        return results.group(1)

  def installed_ttfa_version(value):
    return re.search(r'ttfautohint ([^-\n]*)(-.*)?\n', value).group(1)

  def installed_version_is_newer(installed, used):
    installed = map(int, installed.split("."))
    used = map(int, used.split("."))
    return installed > used

  version_strings = get_name_string(font, NAMEID_VERSION_STRING)
  ttfa_version = ttfautohint_version(version_strings)
  if len(version_strings) == 0:
    fb.error("This font file lacks mandatory "
             "version strings in its name table.")
  elif ttfa_version is None:
    fb.info(("Could not detect which version of"
             " ttfautohint was used in this font."
             " It is typically specified as a comment"
             " in the font version entry of the 'name' table."
             " Font version string is: '{}'").format(version_strings[0]))
  elif ttfautohint_missing:
    fb.skip("This check requires ttfautohint"
            " to be available in the system.")
  else:
    import subprocess
    ttfa_cmd = ["ttfautohint",
                "-V"]  # print version info
    ttfa_output = subprocess.check_output(ttfa_cmd,
                                          stderr=subprocess.STDOUT)
    installed_ttfa = installed_ttfa_version(ttfa_output)
    try:
      if installed_version_is_newer(installed_ttfa,
                                    ttfa_version):
        fb.info(("ttfautohint used in font = {};"
                 " installed = {}; Need to re-run"
                 " with the newer version!").format(ttfa_version,
                                                    installed_ttfa))
      else:
        fb.ok("ttfautohint available in the system is older"
              " than the one used in the font.")
    except:
      fb.error(("failed to parse ttfautohint version strings:\n"
                "  * installed = '{}'\n"
                "  * used = '{}'").format(installed_ttfa,
                                          ttfa_version))


def check_name_table_entries_do_not_contain_linebreaks(fb, font):
  fb.new_check("057", "Name table entries should not contain line-breaks")
  failed = False
  for name in font['name'].names:
    string = name.string.decode(name.getEncoding())
    if "\n" in string:
      failed = True
      fb.error(("Name entry {} on platform {} contains"
                " a line-break.").format(NAMEID_STR[name.nameID],
                                         PLATID_STR[name.platformID]))
  if not failed:
    fb.ok("Name table entries are all single-line (no line-breaks found).")


def check_glyph_names_are_all_valid(fb, font):
  fb.new_check("058", "Glyph names are all valid?")
  bad_names = []
  for _, glyphName in enumerate(font.getGlyphOrder()):
    if glyphName in ['.null', '.notdef']:
      # These 2 names are explicit exceptions
      # in the glyph naming rules
      continue
    if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
      bad_names.append(glyphName)

  if len(bad_names) == 0:
    fb.ok('Glyph names are all valid.')
  else:
    fb.error(('The following glyph names do not comply'
              ' with naming conventions: {}'
              ' A glyph name may be up to 31 characters in length,'
              ' must be entirely comprised of characters from'
              ' the following set:'
              ' A-Z a-z 0-9 .(period) _(underscore). and must not'
              ' start with a digit or period.'
              ' There are a few exceptions'
              ' such as the special character ".notdef".'
              ' The glyph names "twocents", "a1", and "_"'
              ' are all valid, while'
              ' "2cents" and ".twocents" are not.').format(bad_names))


def check_font_has_unique_glyph_names(fb, font):
  ''' Duplicate glyph names prevent font installation on Mac OS X.'''
  fb.new_check("059", "Font contains unique glyph names?")

  glyphs = []
  duplicated_glyphIDs = []
  for _, g in enumerate(font.getGlyphOrder()):
    glyphID = re.sub(r'#\w+', '', g)
    if glyphID in glyphs:
      duplicated_glyphIDs.append(glyphID)
    else:
      glyphs.append(glyphID)

  if len(duplicated_glyphIDs) == 0:
    fb.ok("Font contains unique glyph names.")
  else:
    fb.error(("The following glyph IDs"
              " occur twice: {}").format(duplicated_glyphIDs))


def check_no_glyph_is_incorrectly_named(fb, font):
  fb.new_check("060", "No glyph is incorrectly named?")
  bad_glyphIDs = []
  for _, g in enumerate(font.getGlyphOrder()):
    if re.search(r'#\w+$', g):
      glyphID = re.sub(r'#\w+', '', g)
      bad_glyphIDs.append(glyphID)

  if len(bad_glyphIDs) == 0:
    fb.ok("Font does not have any incorrectly named glyph.")
  else:
    fb.error(("The following glyph IDs"
              " are incorrectly named: {}").format(bad_glyphIDs))


def check_EPAR_table_is_present(fb, font):
  fb.new_check("061", "EPAR table present in font?")
  if 'EPAR' not in font:
    fb.ok('EPAR table not present in font.'
          ' To learn more see'
          ' https://github.com/googlefonts/'
          'fontbakery/issues/818')
  else:
    fb.ok("EPAR table present in font.")


def check_GASP_table_is_correctly_set(fb, font):
  fb.new_check("062", "Is GASP table correctly set?")
  try:
    if not isinstance(font["gasp"].gaspRange, dict):
      fb.error("GASP.gaspRange method value have wrong type")
    else:
      failed = False
      if 0xFFFF not in font["gasp"].gaspRange:
        fb.error("GASP does not have 0xFFFF gaspRange")
      else:
        for key in font["gasp"].gaspRange.keys():
          if key != 0xFFFF:
            fb.hotfix(("GASP shuld only have 0xFFFF gaspRange,"
                       " but {} gaspRange was also found"
                       " and has been removed.").format(hex(key)))
            del font["gasp"].gaspRange[key]
            failed = True
          else:
            value = font["gasp"].gaspRange[key]
            if value != 0x0F:
              failed = True
              if fb.config['autofix']:
                font["gasp"].gaspRange[0xFFFF] = 0x0F
                fb.hotfix("gaspRange[0xFFFF]"
                          " value ({}) is not 0x0F".format(hex(value)))
              else:
                fb.warning(" All flags in GASP range 0xFFFF (i.e. all font"
                           " sizes) must be set to 1.\n"
                           " Rationale:\n"
                           " Traditionally version 0 GASP tables were set"
                           " so that font sizes below 8 ppem had no grid"
                           " fitting but did have antialiasing. From 9-16"
                           " ppem, just grid fitting. And fonts above"
                           " 17ppem had both antialiasing and grid fitting"
                           " toggled on. The use of accelerated graphics"
                           " cards and higher resolution screens make this"
                           " appraoch obsolete. Microsoft's DirectWrite"
                           " pushed this even further with much improved"
                           " rendering built into the OS and apps. In this"
                           " scenario it makes sense to simply toggle all"
                           " 4 flags ON for all font sizes.")
        if not failed:
          fb.ok("GASP table is correctly set.")
  except KeyError:
    fb.error("Font is missing the GASP table."
             " Try exporting the font with autohinting enabled.")


def check_GPOS_table_has_kerning_info(fb, font):
  fb.new_check("063", "Does GPOS table have kerning information?")
  try:
    has_kerning_info = False
    for lookup in font["GPOS"].table.LookupList.Lookup:
      if lookup.LookupType == 2:  # type 2 = Pair Adjustment
        has_kerning_info = True
        break  # avoid reading all kerning info
      elif lookup.LookupType == 9:
        if lookup.SubTable[0].ExtensionLookupType == 2:
          has_kerning_info = True
          break
    if not has_kerning_info:
      fb.warning("GPOS table lacks kerning information")
    else:
      fb.ok("GPOS table has got kerning information.")
  except KeyError:
    fb.error('Font is missing a "GPOS" table')
  return has_kerning_info


def get_all_ligatures(font):
  all_ligatures = {}
  try:
    for lookup in font["GSUB"].table.LookupList.Lookup:
      # fb.info("lookup.LookupType: {}".format(lookup.LookupType))
      if lookup.LookupType == 4:  # type 4 = Ligature Substitution
        for subtable in lookup.SubTable:
          for firstGlyph in subtable.ligatures.keys():
            all_ligatures[firstGlyph] = []
            for lig in subtable.ligatures[firstGlyph]:
              if lig.Component[0] not in all_ligatures[firstGlyph]:
                all_ligatures[firstGlyph].append(lig.Component[0])
  except:
    # sometimes font["GSUB"].table.LookupList.Lookup is not there.
    pass

  return all_ligatures


def check_all_ligatures_have_corresponding_caret_positions(fb, font):
  ''' All ligatures in a font must have corresponding caret (text cursor)
      positions defined in the GDEF table, otherwhise, users may experience
      issues with caret rendering.
  '''
  fb.new_check("064", "Is there a caret position declared for every ligature?")
  all_ligatures = get_all_ligatures(font)
  if len(all_ligatures) == 0:
    fb.ok("This font does not have ligatures.")
    return

  if "GDEF" not in font:
    fb.error("GDEF table is missing, but it is mandatory to declare it"
             " on fonts that provide ligature glyphs because the caret"
             " (text cursor) positioning for each ligature must be"
             " provided in this table.")
  else:
    # TODO: After getting a sample of a good font,
    #       resume the implementation of this routine:
    lig_caret_list = font["GDEF"].table.LigCaretList
    if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
      fb.error("This font lacks caret position values for ligature"
               " glyphs on its GDEF table.")
    elif lig_caret_list.LigGlyphCount != len(all_ligatures):
      fb.warning(("It seems that this font lacks caret positioning values"
                  " for some of its ligature glyphs on the GDEF table."
                  " There's a total of {} ligatures, but only {} sets of"
                  " caret positioning values."
                  "").format(len(all_ligatures),
                             lig_caret_list.LigGlyphCount))
    else:
      # Should we also actually check each individual entry here?
      fb.ok("Looks good!")


def check_nonligated_sequences_kerning_info(fb, font, has_kerning_info):
  ''' Fonts with ligatures should have kerning on the corresponding
      non-ligated sequences for text where ligatures aren't used.
  '''
  fb.new_check("065", "Is there kerning info for non-ligated sequences?")
  if has_kerning_info is False:
    fb.skip("This font lacks kerning info.")
  else:
    all_ligatures = get_all_ligatures(font)

    def look_for_nonligated_kern_info(table):
      for pairpos in table.SubTable:
        for i, glyph in enumerate(pairpos.Coverage.glyphs):
          if glyph in all_ligatures.keys():
            try:
              for pairvalue in pairpos.PairSet[i].PairValueRecord:
                if pairvalue.SecondGlyph in all_ligatures[glyph]:
                  del all_ligatures[glyph]
            except:
              # Sometimes for unknown reason an exception
              # is raised for accessing pairpos.PairSet
              pass

    for lookup in font["GPOS"].table.LookupList.Lookup:
      if lookup.LookupType == 2:  # type 2 = Pair Adjustment
        look_for_nonligated_kern_info(lookup)
      # elif lookup.LookupType == 9:
      #   if lookup.SubTable[0].ExtensionLookupType == 2:
      #     look_for_nonligated_kern_info(lookup.SubTable[0])

    def ligatures_str(ligatures):
      result = []
      for first in ligatures:
        result.extend(["{}_{}".format(first, second)
                       for second in ligatures[first]])
      return result

    if all_ligatures != {}:
      fb.error(("GPOS table lacks kerning info for the following"
                " non-ligated sequences: "
                "{}").format(ligatures_str(all_ligatures)))
    else:
      fb.ok("GPOS table provides kerning info for "
            "all non-ligated sequences.")


def check_there_is_no_KERN_table_in_the_font(fb, font):
  """Fonts should have their kerning implemented in the GPOS table"""
  fb.new_check("066", "Is there a 'KERN' table declared in the font?")
  try:
    font["KERN"]
    fb.error("Font should not have a 'KERN' table")
  except KeyError:
    fb.ok("Font does not declare a 'KERN' table.")


def check_familyname_does_not_begin_with_a_digit(fb, font):
  """Font family names which start with a numeral are often not
  discoverable in Windows applications."""
  fb.new_check("067", "Make sure family name"
                      " does not begin with a digit.")

  failed = False
  for name in get_name_string(font, NAMEID_FONT_FAMILY_NAME):
    digits = map(str, range(0, 10))
    if name[0] in digits:
      fb.error(("Font family name '{}'"
                " begins with a digit!").format(name))
      failed = True
  if failed is False:
    fb.ok("Font family name first character is not a digit.")


def check_fullfontname_begins_with_the_font_familyname(fb, font):
  fb.new_check("068", "Does full font name begin with the font family name?")
  familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
  fullfontname = get_name_string(font, NAMEID_FULL_FONT_NAME)

  if len(familyname) == 0:
    fb.error('Font lacks a NAMEID_FONT_FAMILY_NAME entry'
             ' in the name table.')
  elif len(fullfontname) == 0:
    fb.error('Font lacks a NAMEID_FULL_FONT_NAME entry'
             ' in the name table.')
  else:
    # we probably should check all found values are equivalent.
    # and, in that case, then performing the rest of the check
    # with only the first occurences of the name entries
    # will suffice:
    fullfontname = fullfontname[0]
    familyname = familyname[0]

    if not fullfontname.startswith(familyname):
      fb.error(" On the NAME table, the full font name"
               " (NameID {} - FULL_FONT_NAME: '{}')"
               " does not begin with font family name"
               " (NameID {} - FONT_FAMILY_NAME:"
               " '{}')".format(NAMEID_FULL_FONT_NAME,
                               familyname,
                               NAMEID_FONT_FAMILY_NAME,
                               fullfontname))
    else:
      fb.ok('Full font name begins with the font family name.')


def check_unused_data_at_the_end_of_glyf_table(fb, font):
  fb.new_check("069", "Is there any unused data at the end of the glyf table?")
  if 'CFF ' in font:
    fb.skip("This check does not support CFF fonts.")
  else:
    # -1 because https://www.microsoft.com/typography/otspec/loca.htm
    expected = len(font['loca']) - 1
    actual = len(font['glyf'])
    diff = actual - expected

    # allow up to 3 bytes of padding
    if diff > 3:
      fb.error(("Glyf table has unreachable data at"
                " the end of the table."
                " Expected glyf table length {}"
                " (from loca table), got length"
                " {} (difference: {})").format(expected, actual, diff))
    elif diff < 0:
      fb.error(("Loca table references data beyond"
                " the end of the glyf table."
                " Expected glyf table length {}"
                " (from loca table), got length"
                " {} (difference: {})").format(expected, actual, diff))
    else:
      fb.ok("There is no unused data at"
            " the end of the glyf table.")


def check_font_has_EURO_SIGN_character(fb, font):
  fb.new_check("070", "Font has 'EURO SIGN' character?")

  def font_has_char(font, c):
    if c in font['cmap'].buildReversed():
      return len(font['cmap'].buildReversed()[c]) > 0
    else:
      return False

  if font_has_char(font, 'Euro'):
    fb.ok("Font has 'EURO SIGN' character.")
  else:
    fb.error("Font lacks the '%s' character." % 'EURO SIGN')


def check_font_follows_the_family_naming_recommendations(fb, font):
  fb.new_check("071", "Font follows the family naming recommendations?")
  # See http://forum.fontlab.com/index.php?topic=313.0
  bad_entries = []

  # <Postscript name> may contain only a-zA-Z0-9
  # and one hyphen
  regex = re.compile(r'[a-z0-9-]+', re.IGNORECASE)
  for name in get_name_string(font, NAMEID_POSTSCRIPT_NAME):
    if not regex.match(name):
      bad_entries.append({'field': 'PostScript Name',
                          'rec': 'May contain only a-zA-Z0-9'
                                 ' characters and an hyphen'})
    if name.count('-') > 1:
      bad_entries.append({'field': 'Postscript Name',
                          'rec': 'May contain not more'
                                 ' than a single hyphen'})

  for name in get_name_string(font, NAMEID_FULL_FONT_NAME):
    if len(name) >= 64:
      bad_entries.append({'field': 'Full Font Name',
                          'rec': 'exceeds max length (64)'})

  for name in get_name_string(font, NAMEID_POSTSCRIPT_NAME):
    if len(name) >= 30:
      bad_entries.append({'field': 'PostScript Name',
                          'rec': 'exceeds max length (30)'})

  for name in get_name_string(font, NAMEID_FONT_FAMILY_NAME):
    if len(name) >= 32:
      bad_entries.append({'field': 'Family Name',
                          'rec': 'exceeds max length (32)'})

  for name in get_name_string(font, NAMEID_FONT_SUBFAMILY_NAME):
    if len(name) >= 32:
      bad_entries.append({'field': 'Style Name',
                          'rec': 'exceeds max length (32)'})

  for name in get_name_string(font, NAMEID_TYPOGRAPHIC_FAMILY_NAME):
    if len(name) >= 32:
      bad_entries.append({'field': 'OT Family Name',
                          'rec': 'exceeds max length (32)'})

  for name in get_name_string(font, NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME):
    if len(name) >= 32:
      bad_entries.append({'field': 'OT Style Name',
                          'rec': 'exceeds max length (32)'})
  weight_value = None
  if 'OS/2' in font:
    field = 'OS/2 usWeightClass'
    weight_value = font['OS/2'].usWeightClass
  if 'CFF' in font:
    field = 'CFF Weight'
    weight_value = font['CFF'].Weight

  if weight_value is not None:
    # <Weight> value >= 250 and <= 900 in steps of 50
    if weight_value % 50 != 0:
      bad_entries.append({"field": field,
                          "rec": "Value should idealy be a multiple of 50."})
    full_info = " "
    " 'Having a weightclass of 100 or 200 can result in a \"smear bold\" or"
    " (unintentionally) returning the style-linked bold. Because of this,"
    " you may wish to manually override the weightclass setting for all"
    " extra light, ultra light or thin fonts'"
    " - http://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html"
    if weight_value < 250:
      bad_entries.append({"field": field,
                          "rec": "Value should idealy be 250 or more." +
                                 full_info})
    if weight_value > 900:
      bad_entries.append({"field": field,
                          "rec": "Value should idealy be 900 or less."})
  if len(bad_entries) > 0:
    table = "| Field | Recommendation |\n"
    table += "|:----- |:-------------- |\n"
    for bad in bad_entries:
      table += "| {} | {} |\n".format(bad["field"], bad["rec"])
    fb.info(("Font does not follow "
             "some family naming recommendations:\n\n"
             "{}").format(table))
  else:
    fb.ok("Font follows the family naming recommendations.")


def check_font_enables_smart_dropout_control(fb, font):
  ''' Font enables smart dropout control in 'prep' table instructions?

      B8 01 FF    PUSHW 0x01FF
      85          SCANCTRL (unconditinally turn on
                            dropout control mode)
      B0 04       PUSHB 0x04
      8D          SCANTYPE (enable smart dropout control)

      Smart dropout control means activating rules 1, 2 and 5:
      Rule 1: If a pixel's center falls within the glyph outline,
              that pixel is turned on.
      Rule 2: If a contour falls exactly on a pixel's center,
              that pixel is turned on.
      Rule 5: If a scan line between two adjacent pixel centers
              (either vertical or horizontal) is intersected
              by both an on-Transition contour and an off-Transition
              contour and neither of the pixels was already turned on
              by rules 1 and 2, turn on the pixel which is closer to
              the midpoint between the on-Transition contour and
              off-Transition contour. This is "Smart" dropout control.
  '''
  fb.new_check("072", "Font enables smart dropout control"
                      " in 'prep' table instructions?")
  instructions = "\xb8\x01\xff\x85\xb0\x04\x8d"
  if "CFF " in font:
    fb.skip("Not applicable to a CFF font.")
  else:
    try:
      bytecode = font['prep'].program.getBytecode()
    except KeyError:
      bytecode = ''

    if instructions in bytecode:
      fb.ok("Program at 'prep' table contains instructions"
            " enabling smart dropout control.")
    else:
      fb.warning("Font does not contain TrueType instructions enabling"
                 " smart dropout control in the 'prep' table program."
                 " Please try exporting the font with autohinting enabled.")


def check_MaxAdvanceWidth_is_consistent_with_Hmtx_and_Hhea_tables(fb, font):
  fb.new_check("073", "MaxAdvanceWidth is consistent with values"
                      " in the Hmtx and Hhea tables?")
  hhea_advance_width_max = font['hhea'].advanceWidthMax
  hmtx_advance_width_max = None
  for g in font['hmtx'].metrics.values():
    if hmtx_advance_width_max is None:
      hmtx_advance_width_max = max(0, g[0])
    else:
      hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

  if hmtx_advance_width_max is None:
    fb.error("Failed to find advance width data in HMTX table!")
  elif hmtx_advance_width_max != hhea_advance_width_max:
    fb.error("AdvanceWidthMax mismatch: expected %s (from hmtx);"
             " got %s (from hhea)") % (hmtx_advance_width_max,
                                       hhea_advance_width_max)
  else:
    fb.ok("MaxAdvanceWidth is consistent"
          " with values in the Hmtx and Hhea tables.")


def check_non_ASCII_chars_in_ASCII_only_NAME_table_entries(fb, font):
  fb.new_check("074", "Are there non-ASCII characters"
                      " in ASCII-only NAME table entries ?")
  bad_entries = []
  for name in font['name'].names:
    # Items with NameID > 18 are expressly for localising
    # the ASCII-only IDs into Hindi / Arabic / etc.
    if name.nameID >= 0 and name.nameID <= 18:
      string = name.string.decode(name.getEncoding())
      try:
        string.encode('ascii')
      except:
        bad_entries.append(name)
  if len(bad_entries) > 0:
    fb.error(('There are {} strings containing'
              ' non-ASCII characters in the ASCII-only'
              ' NAME table entries.').format(len(bad_entries)))
  else:
    fb.ok('None of the ASCII-only NAME table entries'
          ' contain non-ASCII characteres.')

##########################################################
##  Checks ported from:                                 ##
##  https://github.com/mekkablue/Glyphs-Scripts/        ##
##  blob/447270c7a82fa272acc312e120abb20f82716d08/      ##
##  Test/Preflight%20Font.py                            ##
##########################################################


def check_for_points_out_of_bounds(fb, font):
  fb.new_check("075", "Check for points out of bounds")
  failed = False
  for glyphName in font['glyf'].keys():
    glyph = font['glyf'][glyphName]
    coords = glyph.getCoordinates(font['glyf'])[0]
    for x, y in coords:
      if x < glyph.xMin or x > glyph.xMax or \
         y < glyph.yMin or y > glyph.yMax or \
         abs(x) > 32766 or abs(y) > 32766:
        failed = True
        fb.warning(("Glyph '{}' coordinates ({},{})"
                    " out of bounds."
                    " This happens a lot when points are not extremes,"
                    " which is usually bad. However, fixing this alert"
                    " by adding points on extremes may do more harm"
                    " than good, especially with italics,"
                    " calligraphic-script, handwriting, rounded and"
                    " other fonts. So it is common to"
                    " ignore this message.").format(glyphName, x, y))
  if not failed:
    fb.ok("All glyph paths have coordinates within bounds!")


def check_glyphs_have_unique_unicode_codepoints(fb, font):
  fb.new_check("076", "Check glyphs have unique unicode codepoints")
  failed = False
  for subtable in font['cmap'].tables:
    if subtable.isUnicode():
      codepoints = {}
      for codepoint, name in subtable.cmap.items():
        codepoints.setdefault(codepoint, set()).add(name)
      for value in codepoints.keys():
        if len(codepoints[value]) >= 2:
          failed = True
          fb.error(("These glyphs carry the same"
                    " unicode value {}:"
                    " {}").format(value,
                                  ", ".join(codepoints[value])))
  if not failed:
    fb.ok("All glyphs have unique unicode codepoint assignments.")


def check_all_glyphs_have_codepoints_assigned(fb, font):
  fb.new_check("077", "Check all glyphs have codepoints assigned")
  failed = False
  for subtable in font['cmap'].tables:
    if subtable.isUnicode():
      for item in subtable.cmap.items():
        codepoint = item[0]
        if codepoint is None:
          failed = True
          fb.error(("Glyph {} lacks a unicode"
                    " codepoint assignment").format(codepoint))
  if not failed:
    fb.ok("All glyphs have a codepoint value assigned.")


def check_that_glyph_names_do_not_exceed_max_length(fb, font):
  fb.new_check("078", "Check that glyph names do not exceed max length")
  failed = False
  for subtable in font['cmap'].tables:
    for item in subtable.cmap.items():
      name = item[1]
      if len(name) > 109:
        failed = True
        fb.error(("Glyph name is too long:"
                  " '{}'").format(name))
  if not failed:
    fb.ok("No glyph names exceed max allowed length.")


def check_hhea_table_and_advanceWidth_values(fb, font, monospace_detected):
  fb.new_check("079", "Monospace font has hhea.advanceWidthMax"
                      " equal to each glyph's advanceWidth ?")
  if not monospace_detected:
    fb.skip("Skipping monospace-only check.")
    return

  # hhea:advanceWidthMax is treated as source of truth here.
  max_advw = font['hhea'].advanceWidthMax
  outliers = 0
  zero_or_double_detected = False
  for glyph_id in font['glyf'].glyphs:
    width = font['hmtx'].metrics[glyph_id][0]
    if width != max_advw:
      outliers += 1
    if width == 0 or width == 2*max_advw:
      zero_or_double_detected = True

  if outliers > 0:
    outliers_percentage = float(outliers) / len(font['glyf'].glyphs)
    msg = ('This is a monospaced font, so advanceWidth'
           ' value should be the same across all glyphs,'
           ' but {} % of them have a different'
           ' value.').format(round(100 * outliers_percentage, 2))
    if zero_or_double_detected:
      msg += (' Double-width and/or zero-width glyphs were detected.'
              ' These glyphs should be set to the same width as all'
              ' others and then add GPOS single pos lookups that'
              ' zeros/doubles the widths as needed.')
    fb.warning(msg)
  else:
    fb.ok("hhea.advanceWidthMax is equal"
          " to all glyphs' advanceWidth in this monospaced font.")


def check_METADATA_Ensure_designer_simple_short_name(fb, family):
  fb.new_check("080", "METADATA.pb: Ensure designer simple short name.")
  if len(family.designer.split(' ')) >= 4 or\
     ' and ' in family.designer or\
     '.' in family.designer or\
     ',' in family.designer:
    fb.error('`designer` key must be simple short name')
  else:
    fb.ok('Designer is a simple short name')


def check_family_is_listed_in_GFDirectory(fb, family):
  fb.new_check("081", "METADATA.pb: Fontfamily is listed"
                      " in Google Font Directory ?")
  url = ('http://fonts.googleapis.com'
         '/css?family=%s') % family.name.replace(' ', '+')
  try:
    r = requests.get(url)
    if r.status_code != 200:
      fb.error('No family found in GWF in %s' % url)
    else:
      fb.ok('Font is properly listed in Google Font Directory.')
      return url
  except:
    fb.warning("Failed to query GWF at {}".format(url))


def check_METADATA_Designer_exists_in_GWF_profiles_csv(fb, family):
  fb.new_check("082", "METADATA.pb: Designer exists in GWF profiles.csv ?")
  PROFILES_GIT_URL = ('https://github.com/google/'
                      'fonts/blob/master/designers/profiles.csv')
  PROFILES_RAW_URL = ('https://raw.githubusercontent.com/google/'
                      'fonts/master/designers/profiles.csv')
  if family.designer == "":
    fb.error('METADATA.pb field "designer" MUST NOT be empty!')
  elif family.designer == "Multiple Designers":
    fb.skip("Found 'Multiple Designers' at METADATA.pb, which is OK,"
            "so we won't look for it at profiles.cvs")
  else:
    try:
      handle = urllib.urlopen(PROFILES_RAW_URL)
      designers = []
      for row in csv.reader(handle):
        if not row:
          continue
        designers.append(row[0].decode('utf-8'))
      if family.designer not in designers:
        fb.warning(("METADATA.pb: Designer '{}' is not listed"
                    " in profiles.csv"
                    " (at '{}')").format(family.designer,
                                         PROFILES_GIT_URL))
      else:
        fb.ok(("Found designer '{}'"
               " at profiles.csv").format(family.designer))
    except:
      fb.warning("Failed to fetch '{}'".format(PROFILES_RAW_URL))


def check_METADATA_has_unique_full_name_values(fb, family):
  fb.new_check("083", "METADATA.pb: check if fonts field"
                      " only has unique 'full_name' values")
  fonts = {}
  for x in family.fonts:
    fonts[x.full_name] = x
  if len(set(fonts.keys())) != len(family.fonts):
    fb.error("Found duplicated 'full_name' values"
             " in METADATA.pb fonts field")
  else:
    fb.ok("METADATA.pb 'fonts' field only has unique 'full_name' values")


def check_METADATA_check_style_weight_pairs_are_unique(fb, family):
  fb.new_check("084", "METADATA.pb: check if fonts field"
                      " only contains unique style:weight pairs")
  pairs = {}
  for f in family.fonts:
    styleweight = '%s:%s' % (f.style, f.weight)
    pairs[styleweight] = 1
  if len(set(pairs.keys())) != len(family.fonts):
    logging.error("Found duplicated style:weight pair"
                  " in METADATA.pb fonts field")
  else:
    fb.ok("METADATA.pb 'fonts' field only has unique style:weight pairs")


def check_METADATA_license_is_APACHE2_UFL_or_OFL(fb, family):
  fb.new_check("085", "METADATA.pb license is 'APACHE2', 'UFL' or 'OFL' ?")
  licenses = ['APACHE2', 'OFL', 'UFL']
  if family.license in licenses:
    fb.ok(("Font license is declared"
           " in METADATA.pb as '{}'").format(family.license))
  else:
    fb.error(("METADATA.pb license field ('{}')"
              " must be one of the following: {}").format(
                family.license,
                licenses))


def check_METADATA_contains_at_least_menu_and_latin_subsets(fb, family):
  fb.new_check("086", "METADATA.pb should contain at least"
                      " 'menu' and 'latin' subsets.")
  missing = []
  for s in ["menu", "latin"]:
    if s not in list(family.subsets):
      missing.append(s)

  if missing != []:
    fb.error(("Subsets 'menu' and 'latin' are mandatory, but METADATA.pb"
              " is missing '{}'").format(' and '.join(missing)))
  else:
    fb.ok("METADATA.pb contains 'menu' and 'latin' subsets.")


def check_METADATA_subsets_alphabetically_ordered(fb, path, family):
  fb.new_check("087", "METADATA.pb subsets should be alphabetically ordered.")
  expected = list(sorted(family.subsets))

  if list(family.subsets) != expected:
    if fb.config["autofix"]:
      fb.hotfix(("METADATA.pb subsets were not sorted "
                 "in alphabetical order: ['{}']"
                 " We're hotfixing that"
                 " to ['{}']").format("', '".join(family.subsets),
                                      "', '".join(expected)))
      del family.subsets[:]
      family.subsets.extend(expected)

      save_FamilyProto_Message(path, family)
    else:
      fb.error(("METADATA.pb subsets are not sorted "
                "in alphabetical order: Got ['{}']"
                " and expected ['{}']").format("', '".join(family.subsets),
                                               "', '".join(expected)))
  else:
    fb.ok("METADATA.pb subsets are sorted in alphabetical order")


def check_Copyright_notice_is_the_same_in_all_fonts(fb, family):
  fb.new_check("088", "Copyright notice is the same in all fonts ?")
  copyright = ''
  fail = False
  for font_metadata in family.fonts:
    if copyright and font_metadata.copyright != copyright:
      fail = True
    copyright = font_metadata.copyright
  if fail:
    fb.error('METADATA.pb: Copyright field value'
             ' is inconsistent across family')
  else:
    fb.ok('Copyright is consistent across family')


def check_METADATA_family_values_are_all_the_same(fb, family):
  fb.new_check("089", "Check that METADATA family values are all the same")
  name = ''
  fail = False
  for font_metadata in family.fonts:
    if name and font_metadata.name != name:
      fail = True
    name = font_metadata.name
  if fail:
    fb.error("METADATA.pb: Family name is not the same"
             " in all metadata 'fonts' items.")
  else:
    fb.ok("METADATA.pb: Family name is the same"
          " in all metadata 'fonts' items.")


def check_font_has_regular_style(fb, family):
  fb.new_check("090", "According GWF standards"
                      " font should have Regular style.")
  found = False
  for f in family.fonts:
    if f.weight == 400 and f.style == 'normal':
      found = True
  if found:
    fb.ok("Font has a Regular style.")
  else:
    fb.error("This font lacks a Regular"
             " (style: normal and weight: 400)"
             " as required by GWF standards.")
  return found


def check_regular_is_400(fb, family, found):
  fb.new_check("091", "Regular should be 400")
  if not found:
    fb.skip("This test will only run if font has a Regular style")
  else:
    badfonts = []
    for f in family.fonts:
      if f.full_name.endswith('Regular') and f.weight != 400:
        badfonts.append("{} (weight: {})".format(f.filename, f.weight))
    if len(badfonts) > 0:
      fb.error(('METADATA.pb: Regular font weight must be 400.'
                ' Please fix: {}').format(', '.join(badfonts)))
    else:
      fb.ok('Regular has weight=400')


def check_font_on_disk_and_METADATA_have_same_family_name(fb, font, f):
  fb.new_check("092", "Font on disk and in METADATA.pb"
                      " have the same family name ?")
  familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
  if len(familynames) == 0:
    fb.error(("This font lacks a FONT_FAMILY_NAME entry"
              " (nameID={}) in the name"
              " table.").format(NAMEID_FONT_FAMILY_NAME))
  else:
    if f.name not in familynames:
      fb.error(('Unmatched family name in font:'
                ' TTF has "{}" while METADATA.pb'
                ' has "{}"').format(familynames, f.name))
    else:
      fb.ok(("Family name '{}' is identical"
             " in METADATA.pb and on the"
             " TTF file.").format(f.name))


def check_METADATA_postScriptName_matches_name_table_value(fb, font, f):
  fb.new_check("093", "Checks METADATA.pb 'postScriptName'"
                      " matches TTF 'postScriptName'")
  postscript_names = get_name_string(font, NAMEID_POSTSCRIPT_NAME)
  if len(postscript_names) == 0:
    fb.error(("This font lacks a POSTSCRIPT_NAME"
              " entry (nameID={}) in the "
              "name table.").format(NAMEID_POSTSCRIPT_NAME))
  else:
    postscript_name = postscript_names[0]

    if postscript_name != f.post_script_name:
      fb.error(('Unmatched postscript name in font:'
                ' TTF has "{}" while METADATA.pb has'
                ' "{}"').format(postscript_name,
                                f.post_script_name))
    else:
      fb.ok(("Postscript name '{}' is identical"
             " in METADATA.pb and on the"
             " TTF file.").format(f.post_script_name))


def check_METADATA_fullname_matches_name_table_value(fb, font, f):
  fb.new_check("094", "METADATA.pb 'fullname' value"
                      " matches internal 'fullname' ?")
  full_fontnames = get_name_string(font, NAMEID_FULL_FONT_NAME)
  if len(full_fontnames) == 0:
    fb.error(("This font lacks a FULL_FONT_NAME"
              " entry (nameID={}) in the "
              "name table.").format(NAMEID_FULL_FONT_NAME))
  else:
    full_fontname = full_fontnames[0]

    if full_fontname != f.full_name:
      fb.error(('Unmatched fullname in font:'
                ' TTF has "{}" while METADATA.pb'
                ' has "{}"').format(full_fontname, f.full_name))
    else:
      fb.ok(("Full fontname '{}' is identical"
             " in METADATA.pb and on the "
             "TTF file.").format(full_fontname))


def check_METADATA_fonts_name_matches_font_familyname(fb, font, f):
  fb.new_check("095", "METADATA.pb fonts 'name' property"
                      " should be same as font familyname")
  font_familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
  if len(font_familynames) == 0:
    fb.error(("This font lacks a FONT_FAMILY_NAME entry"
              " (nameID={}) in the "
              "name table.").format(NAMEID_FONT_FAMILY_NAME))
  else:
    font_familyname = font_familynames[0]

    if font_familyname not in f.name:
      fb.error(('Unmatched familyname in font:'
                ' TTF has "{}" while METADATA.pb has'
                ' name="{}"').format(font_familyname, f.name))
    else:
      fb.ok(("OK: Family name '{}' is identical"
             " in METADATA.pb and on the"
             " TTF file.").format(f.name))


def check_METADATA_fullName_matches_postScriptName(fb, f):
  fb.new_check("096", "METADATA.pb 'fullName' matches 'postScriptName' ?")
  regex = re.compile(r'\W')
  post_script_name = regex.sub('', f.post_script_name)
  fullname = regex.sub('', f.full_name)
  if fullname != post_script_name:
    fb.error(('METADATA.pb full_name="{0}"'
              ' does not match post_script_name ='
              ' "{1}"').format(f.full_name,
                               f.post_script_name))
  else:
    fb.ok("METADATA.pb fields 'fullName' and"
          " 'postScriptName' have the same value.")


def check_METADATA_filename_matches_postScriptName(fb, f):
  fb.new_check("097", "METADATA.pb 'filename' matches 'postScriptName' ?")
  regex = re.compile(r'\W')
  post_script_name = regex.sub('', f.post_script_name)
  filename = regex.sub('', os.path.splitext(f.filename)[0])
  if filename != post_script_name:
    msg = ('METADATA.pb filename="{0}" does not match '
           'post_script_name="{1}."')
    fb.error(msg.format(f.filename, f.post_script_name))
  else:
    fb.ok("METADATA.pb fields 'filename' and"
          " 'postScriptName' have matching values.")


def check_METADATA_name_contains_good_font_name(fb, font, f):
  fb.new_check("098", "METADATA.pb 'name' contains font name"
                      " in right format ?")
  font_familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
  if len(font_familynames) == 0:
    fb.error("A corrupt font that lacks a font_family"
             " nameID entry caused a whole sequence"
             " of tests to be skipped.")
    return None
  else:
    font_familyname = font_familynames[0]

    if font_familyname in f.name:
      fb.ok("METADATA.pb 'name' contains font name"
            " in right format.")
    else:
      fb.error(("METADATA.pb name='{}' does not match"
                " correct font name format.").format(f.name))
    return font_familyname


def check_METADATA_fullname_contains_good_fname(fb, f, font_familyname):
  fb.new_check("099", "METADATA.pb 'full_name' contains"
                      " font name in right format ?")
  if font_familyname in f.name:
    fb.ok("METADATA.pb 'full_name' contains"
          " font name in right format.")
  else:
    fb.error(("METADATA.pb full_name='{}' does not match"
              " correct font name format.").format(f.full_name))


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
