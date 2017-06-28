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

      , LICENSE_URL
      , PLACEHOLDER_LICENSING_TEXT
      , STYLE_NAMES
      , RIBBI_STYLE_NAMES
      , PLATFORM_ID_MACINTOSH
      , PLATFORM_ID_WINDOWS
      , NAMEID_STR
      , PLATID_STR
      , WEIGHTS
)

from fontbakery.utils import(
        get_FamilyProto_Message
      , get_name_string
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
)
def check_main_entries_in_the_name_table(fb, ttFont):
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

# DEPRECATED: 021 - "Checking fsSelection REGULAR bit"
#             025 - "Checking fsSelection ITALIC bit"
#             027 - "Checking fsSelection BOLD bit"
#
# Replaced by 129 - "Checking OS/2.fsSelection value"

# DEPRECATED: 022 - "Checking that italicAngle <= 0"
#             023 - "Checking that italicAngle is less than 20 degrees"
#             024 - "Checking if italicAngle matches font style"
#
# Replaced by 130 - "Checking post.italicAngle value"

# DEPRECATED: 026 - "Checking macStyle ITALIC bit"
#             ??? - "Checking macStyle BOLD bit"
#
# Replaced by 131 - "Checking head.macStyle value"

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
def license(licenses):
  """Get license path"""
  # return license if there is exactly one license
  return licenses[0] if len(licenses) == 1 else None


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
    id='com.google.fonts/test/030'
  , conditions=['license']
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

