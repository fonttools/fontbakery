# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from fontbakery.testrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , distribute_generator
            , Section
            , TestRunner
            , Spec
            )

from fontbakery.callable import condition, test
from fontbakery.testadapters.oldstyletest import old_style_test

import os
import re
import requests
import tempfile
from bs4 import BeautifulSoup
from unidecode import unidecode
import defusedxml.lxml
from lxml.html import HTMLParser
from fontTools.ttLib import TTFont

from fontbakery.constants import(
        # TODO: priority levels are not yet part of the new runner/reporters.
        # How did we ever use this information?
        # Check priority levels:
        TRIVIAL
      , LOW
      , NORMAL
      , IMPORTANT
      , CRITICAL

      , NAMEID_DESCRIPTION
      , NAMEID_LICENSE_DESCRIPTION
      , NAMEID_LICENSE_INFO_URL
      , NAMEID_FONT_FAMILY_NAME
      , NAMEID_FONT_SUBFAMILY_NAME
      , NAMEID_FULL_FONT_NAME
      , NAMEID_POSTSCRIPT_NAME
      , NAMEID_TYPOGRAPHIC_FAMILY_NAME
      , NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME
      , NAMEID_MANUFACTURER_NAME
      , NAMEID_VERSION_STRING

      , LICENSE_URL
      , PLACEHOLDER_LICENSING_TEXT
      , STYLE_NAMES
      , RIBBI_STYLE_NAMES
      , PLATFORM_ID_MACINTOSH
      , PLATFORM_ID_WINDOWS
      , NAMEID_STR
      , PLATID_STR
      , WEIGHTS
      , IS_FIXED_WIDTH_MONOSPACED
      , IS_FIXED_WIDTH_NOT_MONOSPACED
      , PANOSE_PROPORTION_MONOSPACED
      , PANOSE_PROPORTION_ANY
      , WHITESPACE_CHARACTERS
      , REQUIRED_TABLES
      , UNWANTED_TABLES
)

TTFAUTOHINT_MISSING_MSG = (
  "ttfautohint is not available!"
  " You really MUST check the fonts with this tool."
  " To install it, see https://github.com"
  "/googlefonts/gf-docs/blob/master"
  "/ProjectChecklist.md#ttfautohint")

from fontbakery.utils import(
        get_FamilyProto_Message
      , get_name_string
      , get_bounding_box
      , getGlyph
      , glyphHasInk
)

default_section = Section('Default')
specificiation = Spec(
    default_section=default_section
  , iterargs={'font': 'fonts'}
  , derived_iterables={'ttFonts': ('ttFont', True)}
  #, sections=[]
)

register_test = specificiation.register_test
register_condition = specificiation.register_condition

# -------------------------------------------------------------------

@register_condition
@condition
def ttFont(font):
  return TTFont(font)


@register_test
@old_style_test(
    id='com.google.fonts/test/001'
  , priority=CRITICAL
)
def check_file_is_named_canonically(fb, font):
  """Checking file is named canonically

  A font's filename must be composed in the following manner:

  <familyname>-<stylename>.ttf

  e.g Nunito-Regular.ttf, Oswald-BoldItalic.ttf
  """
  file_path, filename = os.path.split(font)
  basename = os.path.splitext(filename)[0]
  # remove spaces in style names
  style_file_names = [name.replace(' ', '') for name in STYLE_NAMES]
  if '-' in basename and basename.split('-')[1] in style_file_names:
    fb.ok("{} is named canonically".format(font))
    return True
  else:
    fb.error(('Style name used in "{}" is not canonical.'
              ' You should rebuild the font using'
              ' any of the following'
              ' style names: "{}".').format(font,
                                            '", "'.join(STYLE_NAMES)))
    return False


@register_test
@old_style_test(
    id='com.google.fonts/test/002',
    priority=CRITICAL
)
def check_all_files_in_a_single_directory(fb, fonts):
  '''Checking all files are in the same directory

     If the set of font files passed in the command line
     is not all in the same directory, then we warn the user
     since the tool will interpret the set of files
     as belonging to a single family (and it is unlikely
     that the user would store the files from a single family
     spreaded in several separate directories).
  '''

  failed = False
  target_dir = None
  for target_file in fonts:
    if target_dir is None:
      target_dir = os.path.split(target_file)[0]
    else:
      if target_dir != os.path.split(target_file)[0]:
        failed = True
        break

  if not failed:
    fb.ok("All files are in the same directory.")
  else:
    fb.error("Not all fonts passed in the command line"
             " are in the same directory. This may lead to"
             " bad results as the tool will interpret all"
             " font files as belonging to a single font family.")


@register_condition
@condition
def family_directory(fonts):
  """Get the path of font project directory."""
  if len(fonts) == 0:
    # We're being extra-careful here. But probably
    #  the only situation in which fonts would be an
    #  empty would really indicate bad user input on the
    #  commandline. So perhaps we should detect this earlier.
    return None
  else:
    return os.path.dirname(fonts[0])


@register_condition
@condition
def descfile(family_directory):
  """Get the path of the DESCRIPTION file of a given font project."""
  if family_directory:
    descfilepath = os.path.join(family_directory, "DESCRIPTION.en_us.html")
    if os.path.exists(descfilepath):
      return descfilepath


@register_condition
@condition
def description(descfile):
  """Get the contents of the DESCRIPTION file of a font project."""
  if not descfile:
    return
  contents = open(descfile).read()
  return contents


@register_test
@old_style_test(
    id='com.google.fonts/test/003'
  , conditions=['description']
)
def check_DESCRIPTION_file_contains_no_broken_links(fb, description):
  """Does DESCRIPTION file contain broken links ?"""
  doc = defusedxml.lxml.fromstring(description, parser=HTMLParser())
  broken_links = []
  for link in doc.xpath('//a/@href'):
    try:
      response = requests.head(link, allow_redirects=True, timeout=10)
      code = response.status_code
      if code != requests.codes.ok:
        broken_links.append(("url: '{}' "
                             "status code: '{}'").format(link, code))
    except requests.exceptions.Timeout:
      fb.warning(("Timedout while attempting to access: '{}'."
                  " Please verify if that's a broken link.").format(link))
    except requests.exceptions.RequestException:
      broken_links.append(link)

  if len(broken_links) > 0:
    fb.error(("The following links are broken"
              " in the DESCRIPTION file:"
              " '{}'").format("', '".join(broken_links)))
  else:
    fb.ok("All links in the DESCRIPTION file look good!")


@register_test
@old_style_test(
    id='com.google.fonts/test/004'
  , conditions=['descfile']
)
def check_DESCRIPTION_is_propper_HTML_snippet(fb, descfile):
  """Is this a propper HTML snippet ?

  When packaging families for google/fonts, if there is no
  DESCRIPTION.en_us.html file, the add_font.py metageneration tool will
  insert a dummy description file which contains invalid html.
  This file needs to either be replaced with an existing description file
  or edited by hand."""
  try:
    import magic
    contenttype = magic.from_file(descfile)
    if "HTML" not in contenttype:
      data = open(descfile).read()
      if "<p>" in data and "</p>" in data:
        fb.ok(("{} is a propper"
               " HTML snippet.").format(descfile))
      else:
        fb.error(("{} is not a propper"
                  " HTML snippet.").format(descfile))
    else:
      fb.ok("{} is a propper HTML file.".format(descfile))
  except AttributeError:
     fb.skip("python magic version mismatch: "
             "This check was skipped because the API of the python"
             " magic module version installed in your system does not"
             " provide the from_file method used in"
             " the check implementation.")
  except ImportError:
     fb.skip("This check depends on the magic python module which"
             " does not seem to be currently installed on your system.")


@register_test
@old_style_test(
    id='com.google.fonts/test/005'
  , conditions=['descfile']
)
def check_DESCRIPTION_max_length(fb, descfile):
  """DESCRIPTION.en_us.html is more than 200 bytes ?"""
  statinfo = os.stat(descfile)
  if statinfo.st_size <= 200:
    fb.error("{} must have size larger than 200 bytes".format(descfile))
  else:
    fb.ok("{} is larger than 200 bytes".format(descfile))


@register_test
@old_style_test(
    id='com.google.fonts/test/006'
  , conditions=['descfile']
)
def check_DESCRIPTION_min_length(fb, descfile):
  """DESCRIPTION.en_us.html is less than 1000 bytes ?"""
  statinfo = os.stat(descfile)
  if statinfo.st_size >= 1000:
    fb.error("{} must have size smaller than 1000 bytes".format(descfile))
  else:
    fb.ok("{} is smaller than 1000 bytes".format(descfile))


@register_condition
@condition
def metadata(family_directory):
  if family_directory:
    pb_file = os.path.join(family_directory, "METADATA.pb")
    if os.path.exists(pb_file):
      return get_FamilyProto_Message(pb_file)


@register_test
@old_style_test(
    id='com.google.fonts/test/007'
  , conditions=['metadata']
)
def check_font_designer_field_is_not_unknown(fb, metadata):
  """Font designer field in METADATA.pb must not be 'unknown'."""
  if metadata.designer.lower() == 'unknown':
    fb.error("Font designer field is '{}'.".format(metadata.designer))
  else:
    fb.ok("Font designer field is not 'unknown'.")


@register_test
@old_style_test(
    id='com.google.fonts/test/008'
)
def check_fonts_have_consistent_underline_thickness(fb, ttFonts):
  """Fonts have consistent underline thickness?"""
  fail = False
  uWeight = None
  for ttfont in ttFonts:
    if uWeight is None:
      uWeight = ttfont['post'].underlineThickness
    if uWeight != ttfont['post'].underlineThickness:
      fail = True

  if fail:
    # FIXME: more info would be great! Which fonts are the outliers
    fb.error("Thickness of the underline is not"
             " the same accross this family. In order to fix this,"
             " please make sure that the underlineThickness value"
             " is the same in the 'post' table of all of this family"
             " font files.")
  else:
    fb.ok("Fonts have consistent underline thickness.")


@register_test
@old_style_test(
    id='com.google.fonts/test/009'
)
def check_fonts_have_consistent_PANOSE_proportion(fb, ttFonts):
  """Fonts have consistent PANOSE proportion?"""
  fail = False
  proportion = None
  for ttfont in ttFonts:
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


@register_test
@old_style_test(
    id='com.google.fonts/test/010'
)
def check_fonts_have_consistent_PANOSE_family_type(fb, ttFonts):
  """Fonts have consistent PANOSE family type?"""
  fail = False
  familytype = None
  for ttfont in ttFonts:
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


@register_test
@old_style_test(
    id='com.google.fonts/test/011'
)
def check_fonts_have_equal_numbers_of_glyphs(fb, ttFonts):
  """Fonts have equal numbers of glyphs?"""
  counts = {}
  glyphs_count = None
  fail = False
  for ttfont in ttFonts:
    this_count = len(ttfont['glyf'].glyphs)
    if glyphs_count is None:
      glyphs_count = this_count
    if glyphs_count != this_count:
      fail = True
    counts[ttfont.reader.file.name] = this_count

  if fail:
    results_table = ""
    for key in counts.keys():
      results_table += "| {} | {} |\n".format(key,
                                              counts[key])

    fb.error('Fonts have different numbers of glyphs:\n\n'
             '{}'.format(results_table))
  else:
    fb.ok("Fonts have equal numbers of glyphs.")


@register_test
@old_style_test(
    id='com.google.fonts/test/012'
)
def check_fonts_have_equal_glyph_names(fb, ttFonts):
  """Fonts have equal glyph names?"""
  glyphs = None
  fail = False
  for ttfont in ttFonts:
    if not glyphs:
      glyphs = ttfont['glyf'].glyphs
    if glyphs.keys() != ttfont['glyf'].glyphs.keys():
      fail = True
  if fail:
    fb.error('Fonts have different glyph names.')
  else:
    fb.ok("Fonts have equal glyph names.")


@register_test
@old_style_test(
    id='com.google.fonts/test/013'
)
def check_fonts_have_equal_unicode_encodings(fb, ttFonts):
  """Fonts have equal unicode encodings?"""
  encoding = None
  fail = False
  for ttfont in ttFonts:
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


@register_test
@old_style_test(
    id='com.google.fonts/test/014'
)
def check_all_fontfiles_have_same_version(fb, ttFonts):
  """Make sure all font files have the same version value."""
  all_detected_versions = []
  fontfile_versions = {}
  for ttfont in ttFonts:
    v = ttfont['head'].fontRevision
    fontfile_versions[ttfont] = v

    if v not in all_detected_versions:
      all_detected_versions.append(v)
  if len(all_detected_versions) != 1:
    versions_list = ""
    for v in fontfile_versions.keys():
      versions_list += "* {}: {}\n".format(v.reader.file.name,
                                           fontfile_versions[v])
    fb.warning(("version info differs among font"
                " files of the same font project.\n"
                "These were the version values found:\n"
                "{}").format(versions_list))
  else:
    fb.ok("All font files have the same version.")


@register_test
@old_style_test(
    id='com.google.fonts/test/015'
)
def check_font_has_post_table_version_2(fb, ttFont):
  """Font has post table version 2 ?"""
  if ttFont['post'].formatType != 2:
    fb.error(("Post table should be version 2 instead of {}."
              " More info at https://github.com/google/fonts/"
              "issues/215").format(ttFont['post'].formatType))
  else:
    fb.ok("Font has post table version 2.")


@register_test
@old_style_test(
    id='com.google.fonts/test/016'
)
def check_OS2_fsType(fb, ttFont):
  """Checking OS/2 fsType

  Fonts must have their fsType bit set to 0. This setting is known as
  Installable Embedding,
  https://www.microsoft.com/typography/otspec/os2.htm#fst"""

  if ttFont['OS/2'].fsType != 0:
    fb.error("OS/2 fsType is a legacy DRM-related field from the 80's"
             " and must be zero (disabled) in all fonts.")
  else:
    fb.ok("OS/2 fsType is properly set to zero (80's DRM scheme is disabled).")


@register_test
@old_style_test(
    id='com.google.fonts/test/017'
  , priority=IMPORTANT
  , conditions=['style']
  # TODO:
  # Thes above is equivalent to requiring a canonical filename.
  # Can we have something like "passed com.google.fonts/test/001" as a condition ?
)
def check_main_entries_in_the_name_table(fb, ttFont, style):
  """Assure valid format for the main entries in the name table.

     Each entry in the name table has a criteria for validity and
     this check tests if all entries in the name table are
     in conformance with that. This check applies only
     to name IDs 1, 2, 4, 6, 16, 17, 18.
     It must run before any of the other name table related checks.
  """

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

  filename = os.path.split(ttFont.reader.file.name)[1]
  filename_base = os.path.splitext(filename)[0]
  fname = filename_base.split('-')[0]
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
    if len(get_name_string(ttFont, nameId)) == 0:
      failed = True
      fb.error(("Font lacks entry with"
                " nameId={} ({})").format(nameId,
                                          NAMEID_STR[nameId]))
  for name in ttFont['name'].names:
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


@register_condition
@condition
def registered_vendor_ids():
  """Get a list of vendor IDs from Microsoft's website."""
  url = 'https://www.microsoft.com/typography/links/vendorlist.aspx'
  registered_vendor_ids = {}
  CACHE_VENDOR_LIST = os.path.join(tempfile.gettempdir(),
                                   'fontbakery-microsoft-vendorlist.cache')
  if os.path.exists(CACHE_VENDOR_LIST):
    content = open(CACHE_VENDOR_LIST).read()
  else:
    content = requests.get(url, auth=('user', 'pass')).content
    open(CACHE_VENDOR_LIST, 'w').write(content)

  soup = BeautifulSoup(content, 'html.parser')
  table = soup.find(id="VendorList")
  for row in table.findAll('tr'):
    cells = row.findAll('td')
    # pad the code to make sure it is a 4 char string,
    # otherwise eg "CF  " will not be matched to "CF"
    code = cells[0].string.strip()
    code = code + (4 - len(code)) * ' '
    labels = [label for label in cells[1].stripped_strings]
    registered_vendor_ids[code] = labels[0]

  return registered_vendor_ids


@register_test
@old_style_test(
    id='com.google.fonts/test/018'
  , conditions=['registered_vendor_ids']
)
def check_OS2_achVendID(fb, ttFont, registered_vendor_ids):
  """Checking OS/2 achVendID"""

  SUGGEST_MICROSOFT_VENDORLIST_WEBSITE = (
    " You should set it to your own 4 character code,"
    " and register that code with Microsoft at"
    " https://www.microsoft.com"
  "/typography/links/vendorlist.aspx")

  vid = ttFont['OS/2'].achVendID
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  if vid is None:
    fb.error("OS/2 VendorID is not set." +
             SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif vid in bad_vids:
    fb.error("OS/2 VendorID is '{}', a font editor default.".format(vid) +
             SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif len(registered_vendor_ids.keys()) > 0:
    if vid not in registered_vendor_ids.keys():
      fb.warning(("OS/2 VendorID value '{}' is not"
                  " a known registered id.").format(vid) +
                 SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
    else:
      failed = False
      for name in ttFont['name'].names:
        if name.nameID == NAMEID_MANUFACTURER_NAME:
          manufacturer = name.string.decode(name.getEncoding()).strip()
          if manufacturer != registered_vendor_ids[vid].strip():
            failed = True
            fb.warning("VendorID '{}' and corresponding registered name '{}'"
                       " does not match the value that is currently set on"
                       " the font nameID {} (Manufacturer Name): '{}'".format(
                         vid,
                         unidecode(registered_vendor_ids[vid]).strip(),
                         NAMEID_MANUFACTURER_NAME,
                         unidecode(manufacturer)))
      if not failed:
        fb.ok("OS/2 VendorID '{}' looks good!".format(vid))


@register_test
@old_style_test(
    id='com.google.fonts/test/019'
)
def check_name_entries_symbol_substitutions(fb, ttFont):
  """Substitute copyright, registered and trademark
     symbols in name table entries"""
  failed = False
  replacement_map = [(u"\u00a9", '(c)'),
                     (u"\u00ae", '(r)'),
                     (u"\u2122", '(tm)')]
  for name in ttFont['name'].names:
    string = unicode(name.string, encoding=name.getEncoding())
    for mark, ascii_repl in replacement_map:
      new_string = string.replace(mark, ascii_repl)
      if string != new_string:
        fb.error(("NAMEID #{} contains symbol that should be"
                  " replaced by '{}'").format(name.nameID,
                                              ascii_repl))
        failed = True
  if not failed:
    fb.ok("No need to substitute copyright, registered and"
          " trademark symbols in name table entries of this font.")


@register_condition
@condition
def style(font):
  """Determine font style from canonical filename."""
  filename = os.path.split(font)[-1]
  if '-' in filename:
    return os.path.splitext(filename)[0].split('-')[1]


@register_test
@old_style_test(
    id='com.google.fonts/test/020'
  , conditions=['style']
)
def check_OS2_usWeightClass(fb, ttFont, style):
  """Checking OS/2 usWeightClass

  The Google Font's API which serves the fonts can only serve
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

  if style == "Italic":
    weight_name = "Regular"
  elif style.endswith("Italic"):
    weight_name = style.replace("Italic", "")
  else:
    weight_name = style

  value = ttFont['OS/2'].usWeightClass
  expected = WEIGHTS[weight_name]
  if value != expected:
    fb.error(("OS/2 usWeightClass expected value for"
              " '{}' is {} but this font has"
              " {}.").format(weight_name, expected, value))
  else:
    fb.ok("OS/2 usWeightClass value looks good!")

# DEPRECATED CHECKS:                                             | REPLACED BY:
# com.google.fonts/test/??? - "Checking macStyle BOLD bit"       | com.google.fonts/test/131 - "Checking head.macStyle value"
# com.google.fonts/test/021 - "Checking fsSelection REGULAR bit" | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/test/022 - "italicAngle <= 0 ?"               | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/023 - "italicAngle is < 20 degrees ?"    | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/024 - "italicAngle matches font style ?" | com.google.fonts/test/130 - "Checking post.italicAngle value"
# com.google.fonts/test/025 - "Checking fsSelection ITALIC bit"  | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/test/026 - "Checking macStyle ITALIC bit"     | com.google.fonts/test/131 - "Checking head.macStyle value"
# com.google.fonts/test/027 - "Checking fsSelection BOLD bit"    | com.google.fonts/test/129 - "Checking OS/2.fsSelection value"

@register_condition
@condition
def licenses(family_directory):
  """Get a list of paths for every license
     file found in a font project."""
  if family_directory:
    licenses = []
    for license in ['OFL.txt', 'LICENSE.txt']:
      license_path = os.path.join(family_directory, license)
      if os.path.exists(license_path):
        licenses.append(license_path)
    return licenses


@register_condition
@condition
def license_path(licenses):
  """Get license path"""
  # return license if there is exactly one license
  return licenses[0] if len(licenses) == 1 else None


@register_condition
@condition
def license(license_path):
  """Get license filename"""
  if license_path:
    return os.path.basename(license_path)


@register_test
@old_style_test(
    id='com.google.fonts/test/028'
)
def check_font_has_a_license(fb, licenses):
  """Check font project has a license"""
  if len(licenses) > 1:
    fb.error("More than a single license file found."
                 " Please review.")
  elif not licenses:
    fb.error("No license file was found."
             " Please add an OFL.txt or a LICENSE.txt file."
             " If you are running fontbakery on a Google Fonts"
             " upstream repo, which is fine, just make sure"
             " there is a temporary license file in the same folder.")
  else:
    fb.ok("Found license at '{}'".format(licenses[0]))


@register_test
@old_style_test(
    id='com.google.fonts/test/029'
  , conditions=['license']
  , priority=CRITICAL
)
def check_copyright_entries_match_license(fb, ttFont, license):
  """Check copyright namerecords match license file"""
  failed = False
  placeholder = PLACEHOLDER_LICENSING_TEXT[license]
  entry_found = False
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
      entry_found = True
      value = nameRecord.string.decode(nameRecord.getEncoding())
      if value != placeholder:
        failed = True
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
  if not entry_found:
    fb.error(("Font lacks NameID {} (LICENSE DESCRIPTION)."
              " A proper licensing entry must be set."
              "").format(NAMEID_LICENSE_DESCRIPTION))
  elif not failed:
    fb.ok("licensing entry on name table is correctly set.")


@register_test
@old_style_test(
    id='com.google.fonts/test/030'
  , priority=CRITICAL
)
def check_font_has_a_valid_license_url(fb, ttFont):
  """"License URL matches License text on name table ?"""
  detected_license = False
  for license in ['OFL.txt', 'LICENSE.txt']:
    placeholder = PLACEHOLDER_LICENSING_TEXT[license]
    for nameRecord in ttFont['name'].names:
      string = nameRecord.string.decode(nameRecord.getEncoding())
      if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION and\
         string == placeholder:
        detected_license = license
        break

  found_good_entry = False
  if detected_license:
    failed = False
    expected = LICENSE_URL[detected_license]
    for nameRecord in ttFont['name'].names:
      if nameRecord.nameID == NAMEID_LICENSE_INFO_URL:
        string = nameRecord.string.decode(nameRecord.getEncoding())
        if string == expected:
          found_good_entry = True
        else:
          failed = True
          fb.error(("Licensing inconsistency in name table entries!"
                    " NameID={} (LICENSE DESCRIPTION) indicates"
                    " {} licensing, but NameID={} (LICENSE URL) has"
                    " '{}'. Expected:"
                    " '{}'").format(NAMEID_LICENSE_DESCRIPTION,
                                    LICENSE_NAME[detected_license],
                                    NAMEID_LICENSE_INFO_URL,
                                    string, expected))
  if not found_good_entry:
    fb.error(("A License URL must be provided in the"
              " NameID {} (LICENSE INFO URL) entry."
              "").format(NAMEID_LICENSE_INFO_URL))
  else:
    if failed:
      fb.error(("Even though a valid license URL was seen in NAME table,"
                " there were also bad entries. Please review"
                " NameIDs {} (LICENSE DESCRIPTION) and {}"
                " (LICENSE INFO URL).").format(NAMEID_LICENSE_DESCRIPTION,
                                               NAMEID_LICENSE_INFO_URL))
    else:
      fb.ok("Font has a valid license URL in NAME table.")


@register_test
@old_style_test(
    id='com.google.fonts/test/031'
  , priority=CRITICAL
)
def check_description_strings_in_name_table(fb, ttFont):
  """Description strings in the name table
  must not contain copyright info."""
  failed = False
  for name in ttFont['name'].names:
    if 'opyright' in name.string.decode(name.getEncoding())\
       and name.nameID == NAMEID_DESCRIPTION:
      failed = True

  if failed:
    fb.error(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
              " should be removed (perhaps these were added by"
              " a longstanding FontLab Studio 5.x bug that"
              " copied copyright notices to them.)"
              "").format(NAMEID_DESCRIPTION))
  else:
    fb.ok("Description strings in the name table"
          " do not contain any copyright string.")

@register_test
@old_style_test(
    id='com.google.fonts/test/032'
)
def check_description_strings_do_not_exceed_100_chars(fb, ttFont):
  """Description strings in the name table"
     must not exceed 100 characters"""
  failed = False
  for name in ttFont['name'].names:
    failed = (name.nameID == NAMEID_DESCRIPTION and
              len(name.string.decode(name.getEncoding())) > 100)
  if failed:
    fb.error(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
              " are longer than 100 characters"
              " and should be removed.").format(NAMEID_DESCRIPTION))
  else:
    fb.ok("Description name records do not exceed 100 characters.")


@register_condition
@condition
def monospace_stats(ttFont):
  """Returns a dict with data related to the set of glyphs
     among which is a boolean indicating whether or not the
     given font is trully monospaced. The source of truth for
     if a font is monospaced is if at least 80% of all glyphs
     have the same width.
  """
  glyphs = ttFont['glyf'].glyphs
  width_occurrences = {}
  width_max = 0
  # count how many times a width occurs
  for glyph_id in glyphs:
      width = ttFont['hmtx'].metrics[glyph_id][0]
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
  # if more than 80% of glyphs have the same width
  # then the font is very likely considered to be monospaced
  seems_monospaced = occurrences > 0.80 * len(glyphs)

  return {
    "seems_monospaced": seems_monospaced,
    "width_max": width_max,
    "most_common_width": most_common_width
  }


@register_test
@old_style_test(
    id='com.google.fonts/test/033'
  , conditions=['monospace_stats']
)
def check_correctness_of_monospaced_metadata(fb, ttFont, monospace_stats):
  """Checking correctness of monospaced metadata.

     There are various metadata in the OpenType spec to specify if
     a font is monospaced or not. If the font is not trully monospaced,
     then no monospaced metadata should be set (as sometimes
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
  """
  failed = False
  # Note: These values are read from the dict here only to
  # reduce the max line length in the test implementation below:
  seems_monospaced = monospace_stats["seems_monospaced"]
  most_common_width = monospace_stats["most_common_width"]
  width_max = monospace_stats['width_max']

  if ttFont['hhea'].advanceWidthMax != width_max:
    failed = True
    fb.error(("Value of hhea.advanceWidthMax"
              " should be set to %d but got"
              " %d instead.").format(width_max,
                                     ttFont['hhea'].advanceWidthMax))
  if seems_monospaced:
    if ttFont['post'].isFixedPitch != IS_FIXED_WIDTH_MONOSPACED:
      failed = True
      fb.error(("On monospaced fonts, the value of"
                "post.isFixedPitch must be set to %d"
                " (fixed width monospaced),"
                " but got %d instead.").format(IS_FIXED_WIDTH_MONOSPACED,
                                               ttFont['post'].isFixedPitch))

    if ttFont['OS/2'].panose.bProportion != PANOSE_PROPORTION_MONOSPACED:
      failed = True
      fb.error(("On monospaced fonts, the value of"
                "OS/2.panose.bProportion must be set to %d"
                " (proportion: monospaced), but got"
                " %d instead.").format(PANOSE_PROPORTION_MONOSPACED,
                                       ttFont['OS/2'].panose.bProportion))

    num_glyphs = len(ttFont['glyf'].glyphs)
    unusually_spaced_glyphs = [
      g for g in ttFont['glyf'].glyphs
      if g not in ['.notdef', '.null', 'NULL']
      and ttFont['hmtx'].metrics[g][0] != most_common_width
    ]
    outliers_ratio = float(len(unusually_spaced_glyphs)) / num_glyphs
    if outliers_ratio > 0:
      failed = True
      fb.warning(("Font is monospaced but {} glyphs"
                  " ({}%) have a different width."
                  " You should check the widths of: {}").format(
                    len(unusually_spaced_glyphs),
                    100.0 * outliers_ratio,
                    unusually_spaced_glyphs))
    if not failed:
      fb.ok("Font is monospaced and all related metadata look good.")
  else:
    # it is a non-monospaced font, so lets make sure
    # that all monospace-related metadata is properly unset.

    if ttFont['post'].isFixedPitch != IS_FIXED_WIDTH_NOT_MONOSPACED:
      failed = True
      fb.error(("On non-monospaced fonts, the"
                " post.isFixedPitch value must be set to %d"
                " (fixed width not monospaced), but got"
                " %d instead.").format(IS_FIXED_WIDTH_NOT_MONOSPACED,
                                       ttFont['post'].isFixedPitch))

    if ttFont['OS/2'].panose.bProportion == PANOSE_PROPORTION_MONOSPACED:
      failed = True
      fb.error(("On non-monospaced fonts, the"
                " OS/2.panose.bProportion value must be set to %d"
                " (proportion: any), but got"
                " %d (proportion: monospaced)"
                " instead.").format(PANOSE_PROPORTION_ANY,
                                    PANOSE_PROPORTION_MONOSPACED))
    if not failed:
      fb.ok("Font is not monospaced and all related metadata look good.")


@register_test
@old_style_test(
    id='com.google.fonts/test/034'
)
def check_OS2_xAvgCharWidth(fb, ttFont):
  """Check if OS/2 xAvgCharWidth is correct."""
  if ttFont['OS/2'].version >= 3:
    width_sum = 0
    count = 0
    for glyph_id in ttFont['glyf'].glyphs:
      width = ttFont['hmtx'].metrics[glyph_id][0]
      if width > 0:
        count += 1
        width_sum += width
    if count == 0:
      fb.error("CRITICAL: Found no glyph width data!")
    else:
      expected_value = int(round(width_sum) / count)

      if ttFont['OS/2'].xAvgCharWidth == expected_value:
        fb.ok("OS/2 xAvgCharWidth is correct.")
      else:
        fb.error(("OS/2 xAvgCharWidth is {} but should be "
                  "{} which corresponds to the "
                  "average of all glyph widths "
                  "in the font").format(ttFont['OS/2'].xAvgCharWidth,
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
    for glyph_id in ttFont['glyf'].glyphs:
      width = ttFont['hmtx'].metrics[glyph_id][0]
      if glyph_id in weightFactors.keys():
        width_sum += (width*weightFactors[glyph_id])
    expected_value = int(width_sum/1000.0 + 0.5)  # round to closest int

    if ttFont['OS/2'].xAvgCharWidth == expected_value:
      fb.ok("OS/2 xAvgCharWidth value is correct.")
    else:
      fb.error(("OS/2 xAvgCharWidth is {} but it should be "
                "{} which corresponds to the weighted "
                "average of the widths of the latin "
                "lowercase glyphs in "
                "the font").format(ttFont['OS/2'].xAvgCharWidth,
                                   expected_value))


@register_test
@old_style_test(
    id='com.google.fonts/test/035'
)
def check_with_ftxvalidator(fb, font):
  """Checking with ftxvalidator."""
  try:
    import subprocess
    ftx_cmd = ["ftxvalidator",
               "-t", "all",  # execute all tests
               font]
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
                 font]
      ftx_output = subprocess.check_output(ftx_cmd,
                                           stderr=subprocess.STDOUT)
      fb.error("ftxvalidator output follows:\n\n{}\n".format(ftx_output))

  except subprocess.CalledProcessError, e:
    fb.info(("ftxvalidator returned an error code. Output follows :"
             "\n\n{}\n").format(e.output))
  except OSError:
    fb.warning("ftxvalidator is not available!")


@register_test
@old_style_test(
    id='com.google.fonts/test/036'
)
def check_with_otsanitise(fb, font):
  """Checking with ots-sanitize."""
  try:
    import subprocess
    ots_output = subprocess.check_output(["ots-sanitize", font],
                                         stderr=subprocess.STDOUT)
    if ots_output != "" and "File sanitized successfully" not in ots_output:
      fb.error("ots-sanitize output follows:\n\n{}".format(ots_output))
    else:
      fb.ok("ots-sanitize passed this file")
  except subprocess.CalledProcessError, e:
      fb.error(("ots-sanitize returned an error code. Output follows :"
                "\n\n{}").format(e.output))
  except OSError, e:
    fb.warning("ots-sanitize is not available!"
               " You really MUST check the fonts with this tool."
               " To install it, see"
               " https://github.com/googlefonts"
               "/gf-docs/blob/master/ProjectChecklist.md#ots"
               " Actual error message was: "
               "'{}'".format(e))


@register_test
@old_style_test(
    id='com.google.fonts/test/037'
)
def check_with_msfontvalidator(fb, font):
  """Checking with Microsoft Font Validator."""
  try:
    import subprocess
    fval_cmd = ["FontValidator.exe",
                "-file", font,
                "-all-tables",
                "-report-in-font-dir"]
    subprocess.check_output(fval_cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError, e:
    filtered_msgs = ""
    for line in e.output.split("\n"):
      if "Validating glyph with index" in line: continue
      if "Table Test:" in line: continue
      filtered_msgs += line + "\n"
    fb.info(("Microsoft Font Validator returned an error code."
             " Output follows :\n\n{}\n").format(filtered_msgs))
  except OSError:
    fb.warning("Mono runtime and/or "
               "Microsoft Font Validator are not available!")
  except IOError:
    fb.warning("Mono runtime and/or "
               "Microsoft Font Validator are not available!")
    return

  xml_report = open("{}.report.xml".format(font), "r").read()
  try:
    os.remove("{}.report.xml".format(font))
    os.remove("{}.report.html".format(font))
  except:
    # Treat failure to delete reports
    # as non-critical. Silently move on.
    pass

  def report_message(msg, details):
    if details:
      return "MS-FonVal: {} DETAILS: {}".format(msg, details)
    else:
      return "MS-FonVal: {}".format(msg)

  doc = defusedxml.lxml.fromstring(xml_report)
  already_reported = []
  for report in doc.iter('Report'):
    msg = report.get("Message")
    details = report.get("Details")
    if [msg, details] not in already_reported:
      # avoid cluttering the output with tons of identical reports
      already_reported.append([msg, details])

      if report.get("ErrorType") == "P":
        fb.ok(report_message(msg, details))
      elif report.get("ErrorType") == "E":
        fb.error(report_message(msg, details))
      elif report.get("ErrorType") == "W":
        fb.warning(report_message(msg, details))
      else:
        fb.info(report_message(msg, details))


@register_condition
@condition
def fontforge_check_results(font):
  if "adobeblank" in font:
    fb.skip("Skipping AdobeBlank since"
            " this font is a very peculiar hack.")
    return None

  import subprocess
  cmd = (
        'import fontforge, sys;'
        'status = fontforge.open("{0}").validate();'
        'sys.stdout.write(status.__str__());'.format
        )

  p = subprocess.Popen(['python', '-c', cmd(font)],
                       stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE
                      )
  ret_val, ff_err_messages = p.communicate()
  try:
    return {
      "validation_state": int(ret_val),
      "ff_err_messages": ff_err_messages
    }
  except:
    return None


@register_test
@old_style_test(
    id='com.google.fonts/test/038'
  , conditions=['fontforge_check_results']
)
def check_fforge_outputs_error_msgs(fb, font, fontforge_check_results):
  """fontforge validation outputs error messages?"""

  filtered_err_msgs = ""
  for line in fontforge_check_results["ff_err_messages"].split('\n'):
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


# TODO: check 039: fontforge checks

@register_condition
@condition
def vmetrics(ttFonts):
  v_metrics = {"ymin": 0, "ymax": 0}
  for ttFont in ttFonts:
    font_ymin, font_ymax = get_bounding_box(ttFont)
    v_metrics["ymin"] = min(font_ymin, v_metrics["ymin"])
    v_metrics["ymax"] = max(font_ymax, v_metrics["ymax"])
  return v_metrics


@register_test
@old_style_test(
    id='com.google.fonts/test/040'
  , conditions=['vmetrics']
)
def check_OS2_usWinAscent_and_Descent(fb, ttFont, vmetrics):
  """Checking OS/2 usWinAscent & usWinDescent

  A font's winAscent and winDescent values should be the same as the
  head table's yMax, abs(yMin) values. By not setting them to these values,
  clipping can occur on Windows platforms,
  https://github.com/RedHatBrand/Overpass/issues/33

  If the font includes tall/deep writing systems such as Arabic or
  Devanagari, the linespacing can appear too loose. To counteract this,
  enabling the OS/2 fsSelection bit 7 (Use_Typo_Metrics), Windows will use
  the OS/2 typo values instead. This means the font developer can control
  the linespacing with the typo values, whilst avoiding clipping by setting
  the win values to the bounding box."""
  failed = False

  # OS/2 usWinAscent:
  if ttFont['OS/2'].usWinAscent != vmetrics['ymax']:
    failed = True
    fb.error(("OS/2.usWinAscent value"
              " should be {}, but got"
              " {} instead").format(vmetrics['ymax'],
                                    ttFont['OS/2'].usWinAscent))
  # OS/2 usWinDescent:
  if ttFont['OS/2'].usWinDescent != abs(vmetrics['ymin']):
    failed = True
    fb.error(("OS/2.usWinDescent value"
              " should be {}, but got"
              " {} instead").format(vmetrics['ymin'],
                                    ttFont['OS/2'].usWinDescent))
  if not failed:
    fb.ok("OS/2 usWinAscent & usWinDescent values look good!")


@register_test
@old_style_test(
    id='com.google.fonts/test/041'
)
def check_Vertical_Metric_Linegaps(fb, ttFont):
  """Checking Vertical Metric Linegaps."""
  if ttFont['hhea'].lineGap != 0:
    fb.warning(("hhea lineGap is not equal to 0"))
  elif ttFont['OS/2'].sTypoLineGap != 0:
    fb.warning(("OS/2 sTypoLineGap is not equal to 0"))
  elif ttFont['OS/2'].sTypoLineGap != ttFont['hhea'].lineGap:
    fb.warning(('OS/2 sTypoLineGap is not equal to hhea lineGap'))
  else:
    fb.ok(('OS/2 sTypoLineGap and hhea lineGap are both 0'))


@register_test
@old_style_test(
    id='com.google.fonts/test/042'
)
def check_OS2_Metrics_match_hhea_Metrics(fb, ttFont):
  """Checking OS/2 Metrics match hhea Metrics.

  OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, Linux and Windows.

  Mac OS X uses the hhea values
  Windows uses OS/2 or Win, depending on the OS or fsSelection bit value"""

  # OS/2 sTypoDescender and sTypoDescender match hhea ascent and descent
  if ttFont['OS/2'].sTypoAscender != ttFont['hhea'].ascent:
    fb.error(("OS/2 sTypoAscender and hhea ascent must be equal"))
  elif ttFont['OS/2'].sTypoDescender != ttFont['hhea'].descent:
    fb.error(("OS/2 sTypoDescender and hhea descent must be equal"))
  else:
    fb.ok("OS/2 sTypoDescender and sTypoDescender match hhea ascent "
          "and descent")


@register_test
@old_style_test(
    id='com.google.fonts/test/043'
)
def check_unitsPerEm_value_is_reasonable(fb, ttFont):
  """Checking unitsPerEm value is reasonable."""
  upem = ttFont['head'].unitsPerEm
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

# TODO: Review this one.
# It is currently failing to parse version strings.
# We must check whether the parser is broken
# or if the fonts are actually bad.
@register_test
@old_style_test(
    id='com.google.fonts/test/044'
)
def check_font_version_fields(fb, ttFont):
  """Checking font version fields"""

  failed = False
  try:
    expected = get_expected_version(fb, ttFont)
  except:
    expected = None
    fb.error("failed to parse font version entries in the name table.")

  if expected is None:
    failed = True
    fb.error("Could not find any font versioning info on the head table"
             " or in the name table entries.")
  else:
    font_revision = str(ttFont['head'].fontRevision)
    expected_str = "{}.{}".format(expected[0],
                                  expected[1])
    if font_revision != expected_str:
      failed = True
      fb.error(("Font revision on the head table ({})"
                " differs from the expected value ({})"
                "").format(font_revision, expected))

    expected_str = "Version {}.{}".format(expected[0],
                                          expected[1])
    for name in ttFont['name'].names:
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
              fb.error(("NAMEID_VERSION_STRING value '{}'"
                        " does not match expected '{}'"
                        "").format(name_version, fix))
          except:
            failed = True  # give up. it's definitely bad :(
            fb.error("Unable to parse font version info"
                     " from name table entries.")
  if not failed:
    fb.ok("All font version fields look good.")


@register_test
@old_style_test(
    id='com.google.fonts/test/045'
)
def check_Digital_Signature_exists(fb, ttFont):
  """Does the font have a DSIG table ?"""
  if "DSIG" in ttFont:
    fb.ok("Digital Signature (DSIG) exists.")
  else:
    fb.error("This font lacks a digital signature (DSIG table)."
             " Some applications may require one (even if only a"
             " dummy placeholder) in order to work properly.")


@register_test
@old_style_test(
    id='com.google.fonts/test/046'
)
def check_font_contains_the_first_few_mandatory_glyphs(fb, ttFont):
  """Font contains the first few mandatory glyphs
     (.null or NULL, CR and space)?"""
  # It would be good to also check
  # for .notdef (codepoint = unspecified)
  null = getGlyph(ttFont, 0x0000)
  CR = getGlyph(ttFont, 0x000D)
  space = getGlyph(ttFont, 0x0020)

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


@register_condition
@condition
def missing_whitespace_chars(ttFont):
  space = getGlyph(ttFont, 0x0020)
  nbsp = getGlyph(ttFont, 0x00A0)
  # tab = getGlyph(ttFont, 0x0009)

  missing = []
  if space is None: missing.append("0x0020")
  if nbsp is None: missing.append("0x00A0")
  # fonts probably don't need an actual tab char
  # if tab is None: missing.append("0x0009")
  return missing


@register_test
@old_style_test(
    id='com.google.fonts/test/047'
  , conditions=['missing_whitespace_chars']
)
def check_font_contains_glyphs_for_whitespace_chars(fb,
                                                    ttFont,
                                                    missing_whitespace_chars):
  """Font contains glyphs for whitespace characters?"""
  if missing_whitespace_chars != []:
    fb.error(("Whitespace glyphs missing for"
              " the following codepoints:"
              " {}.").format(", ".join(missing_whitespace_chars)))
  else:
    fb.ok("Font contains glyphs for whitespace characters.")


@register_test
@old_style_test(
    id='com.google.fonts/test/048'
  , conditions=['missing_whitespace_chars']
)
def check_font_has_proper_whitespace_glyph_names(fb,
                                                 ttFont,
                                                 missing_whitespace_chars):
  """Font has **proper** whitespace glyph names?"""
  if missing_whitespace_chars != []:
    fb.skip("Because some whitespace glyphs are missing. Fix that before!")
  elif ttFont['post'].formatType == 3.0:
    fb.skip("Font has version 3 post table.")
  else:
    failed = False
    space_enc = getGlyphEncodings(ttFont, ["uni0020", "space"])
    nbsp_enc = getGlyphEncodings(ttFont, ["uni00A0",
                                          "nonbreakingspace",
                                          "nbspace",
                                          "nbsp"])
    space = getGlyph(ttFont, 0x0020)
    if 0x0020 not in space_enc:
      failed = True
      fb.error(('Glyph 0x0020 is called "{}":'
                ' Change to "space"'
                ' or "uni0020"').format(space))

    nbsp = getGlyph(ttFont, 0x00A0)
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


@register_test
@old_style_test(
    id='com.google.fonts/test/049'
  , conditions=['missing_whitespace_chars']
)
def check_whitespace_glyphs_have_ink(fb, ttFont, missing_whitespace_chars):
  """Whitespace glyphs have ink?"""
  if missing_whitespace_chars != []:
    fb.skip("Because some whitespace glyphs are missing. Fix that before!")
  else:
    failed = False
    for codepoint in WHITESPACE_CHARACTERS:
      g = getGlyph(font, codepoint)
      if g is not None and glyphHasInk(ttFont, g):
        failed = True
        fb.error(("Glyph \"{}\" has ink."
                  " It needs to be replaced by"
                  " an empty glyph.").format(g))
    if not failed:
      fb.ok("There is no whitespace glyph with ink.")


@register_test
@old_style_test(
    id='com.google.fonts/test/050'
  , conditions=['missing_whitespace_chars']
)
def check_whitespace_glyphs_have_coherent_widths(fb,
                                                 ttFont, 
                                                 missing_whitespace_chars):
  """Whitespace glyphs have coherent widths?"""
  if missing_whitespace_chars != []:
    fb.skip("Because some mandatory whitespace glyphs"
            " are missing. Fix that before!")
  else:
    space = getGlyph(ttFont, 0x0020)
    nbsp = getGlyph(ttFont, 0x00A0)

    spaceWidth = getWidth(ttFont, space)
    nbspWidth = getWidth(ttFont, nbsp)

    if spaceWidth != nbspWidth or nbspWidth < 0:
      if nbspWidth > spaceWidth and spaceWidth >= 0:
        fb.error(("space {} nbsp {}: Space advanceWidth"
                  " needs to be fixed"
                  " to {}.").format(spaceWidth,
                                    nbspWidth,
                                    nbspWidth))
      else:
        fb.error(("space {} nbsp {}: Nbsp advanceWidth"
                  " needs to be fixed "
                  "to {}").format(spaceWidth,
                                  nbspWidth,
                                  spaceWidth))
    else:
      fb.ok("Whitespace glyphs have coherent widths.")


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


@register_test
@old_style_test(
    id='com.google.fonts/test/052'
)
def check_font_contains_all_required_tables(fb, ttFont):
  """Font contains all required tables?"""
  # See https://github.com/googlefonts/fontbakery/issues/617
  tables = set(ttFont.reader.tables.keys())
  glyphs = set(['glyf'] if 'glyf' in ttFont.keys() else ['CFF '])
  if (REQUIRED_TABLES | glyphs) - tables:
    missing_tables = [str(t) for t in (REQUIRED_TABLES | glyphs - tables)]
    desc = (("Font is missing required "
             "tables: [{}]").format(', '.join(missing_tables)))
    if OPTIONAL_TABLES & tables:
      optional_tables = [str(t) for t in (OPTIONAL_TABLES & tables)]
      desc += (" but includes "
               "optional tables [{}]").format(', '.join(optional_tables))
    fb.error(desc)
  else:
    fb.ok("Font contains all required tables.")


@register_test
@old_style_test(
    id='com.google.fonts/test/053'
)
def check_for_unwanted_tables(fb, ttFont):
  """Are there unwanted tables?"""
  unwanted_tables_found = []
  for table in ttFont.keys():
    if table in UNWANTED_TABLES:
      unwanted_tables_found.append(table)

  if len(unwanted_tables_found) > 0:
    fb.error(("Unwanted tables were found"
              " in the font and should be removed:"
              " {}").format(', '.join(unwanted_tables_found)))
  else:
    fb.ok("There are no unwanted tables.")


@register_condition
@condition
def ttfautohint_stats(font):
  try:
    import subprocess
    import tempfile
    hinted_size = os.stat(font).st_size

    dehinted = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
    subprocess.call(["ttfautohint",
                     "--dehint",
                     font,
                     dehinted.name])
    dehinted_size = os.stat(dehinted.name).st_size
    os.unlink(dehinted.name)
  except OSError:
    return {"missing": True}

  ttfa_cmd = ["ttfautohint",
              "-V"]  # print version info
  ttfa_output = subprocess.check_output(ttfa_cmd,
                                        stderr=subprocess.STDOUT)
  installed_ttfa = re.search(r'ttfautohint ([^-\n]*)(-.*)?\n',
                             ttfa_output).group(1)

  return {
    "dehinted_size": dehinted_size,
    "hinted_size": hinted_size,
    "version": installed_ttfa
  }


@register_test
@old_style_test(
    id='com.google.fonts/test/054'
  , conditions=['ttfautohint_stats']
)
def check_hinting_filesize_impact(fb, font, ttfautohint_stats):
  """Show hinting filesize impact.

     Current implementation simply logs useful info
     but there's no fail scenario for this checker."""

  if "missing" in ttfautohint_stats:
    fb.warning(TTFAUTOHINT_MISSING_MSG)
    return

  if ttfautohint_stats["dehinted_size"] == 0:
    fb.warning("ttfautohint --dehint reports that"
               " 'This font has already been processed with ttfautohint'."
               " This is a bug in an old version of ttfautohint."
               " You'll need to upgrade it."
               " See https://github.com/googlefonts/fontbakery/"
               "issues/1043#issuecomment-249035069")
    return

  hinted = ttfautohint_stats["hinted_size"]
  dehinted = ttfautohint_stats["dehinted_size"]
  increase = hinted - dehinted
  change = float(hinted)/dehinted - 1
  change = int(change*10000)/100.0  # round to 2 decimal pts percentage

  def filesize_formatting(s):
    if s < 1024:
      return "{} bytes".format(s)
    elif s < 1024*1024:
      return "{}kb".format(s/1024)
    else:
      return "{}Mb".format(s/(1024*1024))

  hinted_size = filesize_formatting(hinted)
  dehinted_size = filesize_formatting(dehinted)
  increase = filesize_formatting(increase)

  results_table = "Hinting filesize impact:\n\n"
  results_table += "|  | {} |\n".format(font)
  results_table += "|:--- | ---:| ---:|\n"
  results_table += "| Dehinted Size | {} |\n".format(dehinted_size)
  results_table += "| Hinted Size | {} |\n".format(hinted_size)
  results_table += "| Increase | {} |\n".format(increase)
  results_table += "| Change   | {} % |\n".format(change)
  fb.info(results_table)


@register_test
@old_style_test(
    id='com.google.fonts/test/055'
)
def check_version_format_is_correct_in_NAME_table(fb, ttFont):
  """Version format is correct in NAME table?"""

  def is_valid_version_format(value):
    return re.match(r'Version\s0*[1-9]+\.\d+', value)

  failed = False
  version_entries = get_name_string(ttFont, NAMEID_VERSION_STRING)
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


@register_test
@old_style_test(
    id='com.google.fonts/test/056'
  , conditions=['ttfautohint_stats']
)
def check_font_has_latest_ttfautohint_applied(fb, ttFont, ttfautohint_stats):
  """Font has old ttfautohint applied?

     1. find which version was used, by inspecting name table entries

     2. find which version of ttfautohint is installed
        and warn if not available

     3. rehint the font with the latest version of ttfautohint
        using the same options
  """
  def ttfautohint_version(values):
    for value in values:
      results = re.search(r'ttfautohint \(v(.*)\)', value)
      if results:
        return results.group(1)

  def installed_version_is_newer(installed, used):
    installed = map(int, installed.split("."))
    used = map(int, used.split("."))
    return installed > used

  version_strings = get_name_string(ttFont, NAMEID_VERSION_STRING)
  ttfa_version = ttfautohint_version(version_strings)
  if len(version_strings) == 0:
    fb.error("This font file lacks mandatory "
             "version strings in its name table.")
  elif ttfa_version is None:
    fb.info(("Could not detect which version of"
             " ttfautohint was used in this font."
             " It is typically specified as a comment"
             " in the font version entries of the 'name' table."
             " Such font version strings are currently:"
             " {}").format(version_strings))
  elif "missing" in ttfautohint_stats:
    # Even though we skip here, we still have a chance of performing
    # early portions of the check in the 2 error/info scenarios above
    # regardless of the avaiability of ttfautohint.
    fb.skip(TTFAUTOHINT_MISSING_MSG)
  else:
    installed_ttfa = ttfautohint_stats["version"]
    if installed_version_is_newer(installed_ttfa,
                                  ttfa_version):
      fb.warning(("ttfautohint used in font = {};"
                  " installed = {}; Need to re-run"
                  " with the newer version!").format(ttfa_version,
                                                     installed_ttfa))
    else:
      fb.ok("ttfautohint available in the system is older"
            " than the one used in the font.")

@register_test
@old_style_test(
    id='com.google.fonts/test/057'
)
def check_name_table_entries_do_not_contain_linebreaks(fb, ttFont):
  """Name table entries should not contain line-breaks."""
  failed = False
  for name in ttFont['name'].names:
    string = name.string.decode(name.getEncoding())
    if "\n" in string:
      failed = True
      fb.error(("Name entry {} on platform {} contains"
                " a line-break.").format(NAMEID_STR[name.nameID],
                                         PLATID_STR[name.platformID]))
  if not failed:
    fb.ok("Name table entries are all single-line (no line-breaks found).")


@register_test
@old_style_test(
    id='com.google.fonts/test/058'
)
def check_glyph_names_are_all_valid(fb, ttFont):
  """Glyph names are all valid?"""
  bad_names = []
  for _, glyphName in enumerate(ttFont.getGlyphOrder()):
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


@register_condition
@condition
def seems_monospaced(monospace_stats):
  return monospace_stats['seems_monospaced']


@register_test
@old_style_test(
    id='com.google.fonts/test/079'
  , conditions=['seems_monospaced']
)
def check_hhea_table_and_advanceWidth_values(fb, ttFont):
  """Monospace font has hhea.advanceWidthMax
     equal to each glyph's advanceWidth ?"""

  # hhea:advanceWidthMax is treated as source of truth here.
  max_advw = ttFont['hhea'].advanceWidthMax
  outliers = 0
  zero_or_double_detected = False
  glyphs = [
    g for g in ttFont['glyf'].glyphs
      if g not in ['.notdef', '.null', 'NULL']
  ]
  for glyph_id in glyphs:
    width = ttFont['hmtx'].metrics[glyph_id][0]
    if width != max_advw:
      outliers += 1
    if width == 0 or width == 2*max_advw:
      zero_or_double_detected = True

  if outliers > 0:
    outliers_percentage = float(outliers) / len(ttFont['glyf'].glyphs)
    fb.warning(("This seems to be a monospaced font,"
                " so advanceWidth value should be the same"
                " across all glyphs, but {} % of them"
                " have a different value."
                "").format(round(100 * outliers_percentage, 2)))
    if zero_or_double_detected:
      fb.warning("Double-width and/or zero-width glyphs"
                 " were detected. These glyphs should be set"
                 " to the same width as all others"
                 " and then add GPOS single pos lookups"
                 " that zeros/doubles the widths as needed.")
  else:
    fb.ok("hhea.advanceWidthMax is equal"
          " to all glyphs' advanceWidth in this monospaced font.")
