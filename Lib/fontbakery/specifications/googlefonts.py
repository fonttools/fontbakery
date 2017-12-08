# -*- coding: utf-8 -*-
from __future__ import (absolute_import,
                        print_function,
                        unicode_literals,
                        division)

from fontbakery.checkrunner import (
              INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , Section
            , Spec
            )
import os
from fontbakery.callable import condition, check
from fontbakery.message import Message
from fontbakery.constants import(
        # TODO: priority levels are not yet part of the new runner/reporters.
        # How did we ever use this information?
        # Check priority levels:
        CRITICAL
      , IMPORTANT
#     , NORMAL
#     , LOW
#     , TRIVIAL
)

default_section = Section('Default')


class FontsSpec(Spec):
  def setup_argparse(self, argument_parser):
    """
    Set up custom arguments needed for this spec.
    """
    import glob
    import logging
    import argparse
    def get_fonts(pattern):

      fonts_to_check = []
      # use glob.glob to accept *.ttf

      for fullpath in glob.glob(pattern):
        if fullpath.endswith(".ttf"):
          fonts_to_check.append(fullpath)
        else:
          logging.warning("Skipping '{}' as it does not seem "
                            "to be valid TrueType font file.".format(fullpath))
      return fonts_to_check


    class MergeAction(argparse.Action):
      def __call__(self, parser, namespace, values, option_string=None):
        target = [item for l in values for item in l]
        setattr(namespace, self.dest, target)

    argument_parser.add_argument('fonts', nargs='+', type=get_fonts,
                        action=MergeAction, help='font file path(s) to check.'
                                            ' Wildcards like *.ttf are allowed.')
    return ('fonts', )

specification = FontsSpec(
    default_section=default_section
  , iterargs={'font': 'fonts'}
  , derived_iterables={'ttFonts': ('ttFont', True)}
  #, sections=[]
)

register_check = specification.register_check
register_condition = specification.register_condition

# -------------------------------------------------------------------

@register_condition
@condition
def ttFont(font):
  from fontTools.ttLib import TTFont
  return TTFont(font)


@register_check
@check(
    id = 'com.google.fonts/check/001'
  , priority=CRITICAL
)
def com_google_fonts_check_001(font):
  """Checking file is named canonically

  A font's filename must be composed in the following manner:
  <familyname>-<stylename>.ttf

  e.g Nunito-Regular.ttf, Oswald-BoldItalic.ttf
  """
  from fontbakery.constants import STYLE_NAMES

  file_path, filename = os.path.split(font)
  basename = os.path.splitext(filename)[0]
  # remove spaces in style names
  style_file_names = [name.replace(' ', '') for name in STYLE_NAMES]
  if '-' in basename and basename.split('-')[1] in style_file_names:
    yield PASS, "{} is named canonically.".format(font)
  else:
    yield FAIL, ('Style name used in "{}" is not canonical.'
                 ' You should rebuild the font using'
                 ' any of the following'
                 ' style names: "{}".').format(font,
                                               '", "'.join(STYLE_NAMES))


@register_check
@check(
    id = 'com.google.fonts/check/002',
    priority=CRITICAL
)
def com_google_fonts_check_002(fonts):
  """Checking all files are in the same directory

     If the set of font files passed in the command line
     is not all in the same directory, then we warn the user
     since the tool will interpret the set of files
     as belonging to a single family (and it is unlikely
     that the user would store the files from a single family
     spreaded in several separate directories).
  """

  directories = []
  for target_file in fonts:
    directory = os.path.dirname(target_file)
    if directory not in directories:
      directories.append(directory)

  if len(directories) == 1:
    yield PASS, "All files are in the same directory."
  else:
    yield FAIL, ("Not all fonts passed in the command line"
                 " are in the same directory. This may lead to"
                 " bad results as the tool will interpret all"
                 " font files as belonging to a single"
                 " font family. The detected directories are:"
                 " {}".format(directories))


@register_condition
@condition
def family_directory(fonts):
  """Get the path of font project directory."""
  if fonts:
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


@register_check
@check(
    id = 'com.google.fonts/check/003'
  , conditions=['description']
)
def com_google_fonts_check_003(description):
  """Does DESCRIPTION file contain broken links ?"""
  from lxml.html import HTMLParser
  import defusedxml.lxml
  import requests
  doc = defusedxml.lxml.fromstring(description, parser=HTMLParser())
  broken_links = []
  for link in doc.xpath('//a/@href'):
    if link.startswith("mailto:") and \
       "@" in link and \
       "." in link.split("@")[1]:
      yield INFO, ("Found an email address: {}".format(link))
      continue

    try:
      response = requests.head(link, allow_redirects=True, timeout=10)
      code = response.status_code
      if code != requests.codes.ok:
        broken_links.append(("url: '{}' "
                             "status code: '{}'").format(link, code))
    except requests.exceptions.Timeout:
      yield WARN, ("Timedout while attempting to access: '{}'."
                   " Please verify if that's a broken link.").format(link)
    except requests.exceptions.RequestException:
      broken_links.append(link)

  if len(broken_links) > 0:
    yield FAIL, ("The following links are broken"
                 " in the DESCRIPTION file:"
                 " '{}'").format("', '".join(broken_links))
  else:
    yield PASS, "All links in the DESCRIPTION file look good!"


@register_check
@check(
    id = 'com.google.fonts/check/004'
  , conditions=['descfile']
)
def com_google_fonts_check_004(descfile):
  """Is this a propper HTML snippet ?

  When packaging families for google/fonts, if there is no
  DESCRIPTION.en_us.html file, the add_font.py metageneration tool will
  insert a dummy description file which contains invalid html.
  This file needs to either be replaced with an existing description file
  or edited by hand."""
  data = open(descfile).read().decode("utf-8")
  if "<p>" not in data or "</p>" not in data:
    yield FAIL, "{} does not look like a propper HTML snippet.".format(descfile)
  else:
    yield PASS, "{} is a propper HTML file.".format(descfile)


@register_check
@check(
    id = 'com.google.fonts/check/005'
  , conditions=['description']
)
def com_google_fonts_check_005(description):
  """ DESCRIPTION.en_us.html must have more than 200 bytes. """
  if len(description) <= 200:
    yield FAIL, ("DESCRIPTION.en_us.html must"
                 " have size larger than 200 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is larger than 200 bytes."


@register_check
@check(
    id = 'com.google.fonts/check/006'
  , conditions=['description']
)
def com_google_fonts_check_006(description):
  """ DESCRIPTION.en_us.html must have less than 1000 bytes. """
  if len(description) >= 1000:
    yield FAIL, ("DESCRIPTION.en_us.html must"
                 " have size smaller than 1000 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is smaller than 1000 bytes."


@register_condition
@condition
def metadata(family_directory):
  from fontbakery.utils import get_FamilyProto_Message

  if family_directory:
    pb_file = os.path.join(family_directory, "METADATA.pb")
    if os.path.exists(pb_file):
      return get_FamilyProto_Message(pb_file)


@register_check
@check(
    id = 'com.google.fonts/check/007'
  , conditions=['metadata']
)
def com_google_fonts_check_007(metadata):
  """Font designer field in METADATA.pb must not be 'unknown'."""
  if metadata.designer.lower() == 'unknown':
    yield FAIL, "Font designer field is '{}'.".format(metadata.designer)
  else:
    yield PASS, "Font designer field is not 'unknown'."


@register_check
@check(
    id = 'com.google.fonts/check/008'
)
def com_google_fonts_check_008(ttFonts):
  """Fonts have consistent underline thickness?"""
  failed = False
  uWeight = None
  for ttfont in ttFonts:
    if uWeight is None:
      uWeight = ttfont['post'].underlineThickness
    if uWeight != ttfont['post'].underlineThickness:
      failed = True

  if failed:
    # FIXME: more info would be great! Which fonts are the outliers
    yield FAIL, ("Thickness of the underline is not"
                 " the same accross this family. In order to fix this,"
                 " please make sure that the underlineThickness value"
                 " is the same in the 'post' table of all of this family"
                 " font files.")
  else:
    yield PASS, "Fonts have consistent underline thickness."


@register_check
@check(
    id = 'com.google.fonts/check/009'
)
def com_google_fonts_check_009(ttFonts):
  """Fonts have consistent PANOSE proportion?"""
  failed = False
  proportion = None
  for ttFont in ttFonts:
    if proportion is None:
      proportion = ttFont['OS/2'].panose.bProportion
    if proportion != ttFont['OS/2'].panose.bProportion:
      failed = True

  if failed:
    yield FAIL, ("PANOSE proportion is not"
                 " the same accross this family."
                 " In order to fix this,"
                 " please make sure that the panose.bProportion value"
                 " is the same in the OS/2 table of all of this family"
                 " font files.")
  else:
    yield PASS, "Fonts have consistent PANOSE proportion."


@register_check
@check(
    id = 'com.google.fonts/check/010'
)
def com_google_fonts_check_010(ttFonts):
  """Fonts have consistent PANOSE family type?"""
  failed = False
  familytype = None
  for ttfont in ttFonts:
    if familytype is None:
      familytype = ttfont['OS/2'].panose.bFamilyType
    if familytype != ttfont['OS/2'].panose.bFamilyType:
      failed = True

  if failed:
    yield FAIL, ("PANOSE family type is not"
                 " the same accross this family."
                 " In order to fix this,"
                 " please make sure that the panose.bFamilyType value"
                 " is the same in the OS/2 table of all of this family"
                 " font files.")
  else:
    yield PASS, "Fonts have consistent PANOSE family type."


@register_check
@check(
    id = 'com.google.fonts/check/011'
)
def com_google_fonts_check_011(ttFonts):
  """Fonts have equal numbers of glyphs?"""
  counts = {}
  glyphs_count = None
  failed = False
  for ttfont in ttFonts:
    this_count = len(ttfont['glyf'].glyphs)
    if glyphs_count is None:
      glyphs_count = this_count
    if glyphs_count != this_count:
      failed = True
    counts[ttfont.reader.file.name] = this_count

  if failed:
    results_table = ""
    for key in counts.keys():
      results_table += "| {} | {} |\n".format(key,
                                              counts[key])

    yield FAIL, ("Fonts have different numbers of glyphs:\n\n"
                 "{}".format(results_table))
  else:
    yield PASS, "Fonts have equal numbers of glyphs."


@register_check
@check(
    id = 'com.google.fonts/check/012'
)
def com_google_fonts_check_012(ttFonts):
  """Fonts have equal glyph names?"""
  glyphs = None
  failed = False
  for ttFont in ttFonts:
    if not glyphs:
      glyphs = ttFont["glyf"].glyphs
    if glyphs.keys() != ttFont["glyf"].glyphs.keys():
      failed = True

  if failed:
    yield FAIL, "Fonts have different glyph names."
  else:
    yield PASS, "Fonts have equal glyph names."


@register_check
@check(
    id = 'com.google.fonts/check/013'
)
def com_google_fonts_check_013(ttFonts):
  """Fonts have equal unicode encodings?"""
  encoding = None
  failed = False
  for ttFont in ttFonts:
    cmap = None
    for table in ttFont['cmap'].tables:
      if table.format == 4:
        cmap = table
        break
    # Could a font lack a format 4 cmap table ?
    # If we ever find one of those, it would crash the check here.
    # Then we'd have to yield a FAIL regarding the missing table entry.
    if not encoding:
      encoding = cmap.platEncID
    if encoding != cmap.platEncID:
      failed = True
  if failed:
    yield FAIL, "Fonts have different unicode encodings."
  else:
    yield PASS, "Fonts have equal unicode encodings."


@register_check
@check(
    id = 'com.google.fonts/check/014'
)
def com_google_fonts_check_014(ttFonts):
  """Make sure all font files have the same version value."""
  all_detected_versions = []
  fontfile_versions = {}
  for ttFont in ttFonts:
    v = ttFont['head'].fontRevision
    fontfile_versions[ttFont] = v

    if v not in all_detected_versions:
      all_detected_versions.append(v)
  if len(all_detected_versions) != 1:
    versions_list = ""
    for v in fontfile_versions.keys():
      versions_list += "* {}: {}\n".format(v.reader.file.name,
                                           fontfile_versions[v])
    yield WARN, ("version info differs among font"
                 " files of the same font project.\n"
                 "These were the version values found:\n"
                 "{}").format(versions_list)
  else:
    yield PASS, "All font files have the same version."


@register_check
@check(
    id = 'com.google.fonts/check/015'
)
def com_google_fonts_check_015(ttFont):
  """Font has post table version 2 ?"""
  if ttFont['post'].formatType != 2:
    yield FAIL, ("Post table should be version 2 instead of {}."
                 " More info at https://github.com/google/fonts/"
                 "issues/215").format(ttFont['post'].formatType)
  else:
    yield PASS, "Font has post table version 2."


@register_check
@check(
    id = 'com.google.fonts/check/016'
)
def com_google_fonts_check_016(ttFont):
  """Checking OS/2 fsType

  Fonts must have their fsType bit set to 0. This setting is known as
  Installable Embedding,
  https://www.microsoft.com/typography/otspec/os2.htm#fst"""

  if ttFont['OS/2'].fsType != 0:
    yield FAIL, ("OS/2 fsType is a legacy DRM-related field from the 80's"
                 " and must be zero (disabled) in all fonts.")
  else:
    yield PASS, ("OS/2 fsType is properly set to zero "
                 "(80's DRM scheme is disabled).")

# DEPRECATED CHECK:
# com.google.fonts/check/017 - "Assure valid format for the main entries in the name table."
#
# REPLACED BY:
# com.google.fonts/check/156 - "Font has all mandatory 'name' table entries ?"
# com.google.fonts/check/157 - "Check name table: FONT_FAMILY_NAME entries."
# com.google.fonts/check/158 - "Check name table: FONT_SUBFAMILY_NAME entries."
# com.google.fonts/check/159 - "Check name table: FULL_FONT_NAME entries."
# com.google.fonts/check/160 - "Check name table: POSTSCRIPT_NAME entries."
# com.google.fonts/check/161 - "Check name table: TYPOGRAPHIC_FAMILY_NAME entries."
# com.google.fonts/check/162 - "Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries."

@register_condition
@condition
def registered_vendor_ids():
  """Get a list of vendor IDs from Microsoft's website."""
  import tempfile
  import requests
  from bs4 import BeautifulSoup
  from pkg_resources import resource_filename

  registered_vendor_ids = {}
  CACHED = resource_filename('fontbakery',
                             'data/fontbakery-microsoft-vendorlist.cache')
  content = open(CACHED).read()
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


@register_check
@check(
    id = 'com.google.fonts/check/018'
  , conditions=['registered_vendor_ids']
)
def com_google_fonts_check_018(ttFont, registered_vendor_ids):
  """Checking OS/2 achVendID"""
  from unidecode import unidecode
  from fontbakery.constants import NAMEID_MANUFACTURER_NAME

  SUGGEST_MICROSOFT_VENDORLIST_WEBSITE = (
    " You should set it to your own 4 character code,"
    " and register that code with Microsoft at"
    " https://www.microsoft.com"
  "/typography/links/vendorlist.aspx")

  vid = ttFont['OS/2'].achVendID
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  if vid is None:
    yield FAIL, Message("not set", "OS/2 VendorID is not set." +
                                   SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif vid in bad_vids:
    yield FAIL, Message("bad", ("OS/2 VendorID is '{}',"
                                " a font editor default.").format(vid) +
                                SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif len(registered_vendor_ids.keys()) > 0:
    if vid not in registered_vendor_ids.keys():
      yield WARN, Message("unknown", ("OS/2 VendorID value '{}' is not"
                                      " a known registered id.").format(vid) +
                                      SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
    else:
      failed = False
      for name in ttFont['name'].names:
        if name.nameID == NAMEID_MANUFACTURER_NAME:
          manufacturer = name.string.decode(name.getEncoding()).strip()
          if manufacturer != registered_vendor_ids[vid].strip():
            failed = True
            yield WARN, Message("mismatch",
                                "VendorID '{}' and corresponding"
                                " registered name '{}' does not"
                                " match the value that is"
                                " currently set"
                                " on the font nameID"
                                " {} (Manufacturer Name):"
                                " '{}'".format(
                                vid,
                                unidecode(registered_vendor_ids[vid]).strip(),
                                NAMEID_MANUFACTURER_NAME,
                                unidecode(manufacturer)))
      if not failed:
        yield PASS, "OS/2 VendorID '{}' looks good!".format(vid)


@register_check
@check(
    id = 'com.google.fonts/check/019'
)
def com_google_fonts_check_019(ttFont):
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
        yield FAIL, ("NAMEID #{} contains symbol that should be"
                     " replaced by '{}'").format(name.nameID,
                                                 ascii_repl)
        failed = True
  if not failed:
    yield PASS, ("No need to substitute copyright, registered and"
                 " trademark symbols in name table entries of this font.")


@register_condition
@condition
def style(font):
  """Determine font style from canonical filename."""
  from fontbakery.constants import STYLE_NAMES
  filename = os.path.split(font)[-1]
  if '-' in filename:
    stylename = os.path.splitext(filename)[0].split('-')[1]
    if stylename in [name.replace(' ', '') for name in STYLE_NAMES]:
      return stylename


@register_check
@check(
    id = 'com.google.fonts/check/020'
  , conditions=['style']
)
def com_google_fonts_check_020(ttFont, style):
  """Checking OS/2 usWeightClass

  The Google Font's API which serves the fonts can only serve
  the following weights values with the corresponding subfamily styles:

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
  # Weight name to value mapping:
  GF_API_WEIGHTS = {"Thin": 250,
                    "ExtraLight": 275,
                    "Light": 300,
                    "Regular": 400,
                    "Medium": 500,
                    "SemiBold": 600,
                    "Bold": 700,
                    "ExtraBold": 800,
                    "Black": 900}
  if style == "Italic":
    weight_name = "Regular"
  elif style.endswith("Italic"):
    weight_name = style.replace("Italic", "")
  else:
    weight_name = style

  value = ttFont['OS/2'].usWeightClass
  expected = GF_API_WEIGHTS[weight_name]
  if value != expected:
    yield FAIL, ("OS/2 usWeightClass expected value for"
                 " '{}' is {} but this font has"
                 " {}.").format(weight_name, expected, value)
  else:
    yield PASS, "OS/2 usWeightClass value looks good!"

# DEPRECATED CHECKS:                                             | REPLACED BY:
# com.google.fonts/check/??? - "Checking macStyle BOLD bit"       | com.google.fonts/check/131 - "Checking head.macStyle value"
# com.google.fonts/check/021 - "Checking fsSelection REGULAR bit" | com.google.fonts/check/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/check/022 - "italicAngle <= 0 ?"               | com.google.fonts/check/130 - "Checking post.italicAngle value"
# com.google.fonts/check/023 - "italicAngle is < 20 degrees ?"    | com.google.fonts/check/130 - "Checking post.italicAngle value"
# com.google.fonts/check/024 - "italicAngle matches font style ?" | com.google.fonts/check/130 - "Checking post.italicAngle value"
# com.google.fonts/check/025 - "Checking fsSelection ITALIC bit"  | com.google.fonts/check/129 - "Checking OS/2.fsSelection value"
# com.google.fonts/check/026 - "Checking macStyle ITALIC bit"     | com.google.fonts/check/131 - "Checking head.macStyle value"
# com.google.fonts/check/027 - "Checking fsSelection BOLD bit"    | com.google.fonts/check/129 - "Checking OS/2.fsSelection value"

@register_condition
@condition
def licenses(family_directory):
  """Get a list of paths for every license
     file found in a font project."""
  licenses = []
  if family_directory:
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


@register_check
@check(
    id = 'com.google.fonts/check/028'
)
def com_google_fonts_check_028(licenses):
  """Check font has a license."""
  if len(licenses) > 1:
    yield FAIL, Message("multiple",
                        ("More than a single license file found."
                         " Please review."))
  elif not licenses:
    yield FAIL, Message("none",
                        ("No license file was found."
                         " Please add an OFL.txt or a LICENSE.txt file."
                         " If you are running fontbakery on a Google Fonts"
                         " upstream repo, which is fine, just make sure"
                         " there is a temporary license file in"
                         " the same folder."))
  else:
    yield PASS, "Found license at '{}'".format(licenses[0])


@register_check
@check(
    id = 'com.google.fonts/check/029'
  , conditions=['license']
  , priority=CRITICAL
)
def com_google_fonts_check_029(ttFont, license):
  """Check copyright namerecords match license file"""
  from fontbakery.constants import (NAMEID_LICENSE_DESCRIPTION,
                                    NAMEID_LICENSE_INFO_URL,
                                    PLACEHOLDER_LICENSING_TEXT,
                                    NAMEID_STR,
                                    PLATID_STR)
  from unidecode import unidecode
  failed = False
  placeholder = PLACEHOLDER_LICENSING_TEXT[license]
  entry_found = False
  for i, nameRecord in enumerate(ttFont["name"].names):
    if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
      entry_found = True
      value = nameRecord.string.decode(nameRecord.getEncoding())
      if value != placeholder:
        failed = True
        yield FAIL, Message("wrong", \
                            ("License file {} exists but"
                             " NameID {} (LICENSE DESCRIPTION) value"
                             " on platform {} ({})"
                             " is not specified for that."
                             " Value was: \"{}\""
                             " Must be changed to \"{}\""
                             "").format(license,
                                        NAMEID_LICENSE_DESCRIPTION,
                                        nameRecord.platformID,
                                        PLATID_STR[nameRecord.platformID],
                                        unidecode(value),
                                        unidecode(placeholder)))
  if not entry_found:
    yield FAIL, Message("missing", \
                        ("Font lacks NameID {} "
                         "(LICENSE DESCRIPTION). A proper licensing entry"
                         " must be set.").format(NAMEID_LICENSE_DESCRIPTION))
  elif not failed:
    yield PASS, "Licensing entry on name table is correctly set."


@register_check
@check(
    id = 'com.google.fonts/check/030'
  , priority=CRITICAL
)
def com_google_fonts_check_030(ttFont):
  """"License URL matches License text on name table ?"""
  from fontbakery.constants import (NAMEID_LICENSE_DESCRIPTION,
                                    NAMEID_LICENSE_INFO_URL,
                                    PLACEHOLDER_LICENSING_TEXT)
  LICENSE_URL = {
    'OFL.txt': u'http://scripts.sil.org/OFL',
    'LICENSE.txt': u'http://www.apache.org/licenses/LICENSE-2.0'
  }
  LICENSE_NAME = {
    'OFL.txt': u'Open Font',
    'LICENSE.txt': u'Apache'
  }
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
          yield FAIL, ("Licensing inconsistency in name table entries!"
                       " NameID={} (LICENSE DESCRIPTION) indicates"
                       " {} licensing, but NameID={} (LICENSE URL) has"
                       " '{}'. Expected:"
                       " '{}'").format(NAMEID_LICENSE_DESCRIPTION,
                                       LICENSE_NAME[detected_license],
                                       NAMEID_LICENSE_INFO_URL,
                                       string, expected)
  if not found_good_entry:
    yield FAIL, ("A License URL must be provided in the"
                 " NameID {} (LICENSE INFO URL) entry."
                 "").format(NAMEID_LICENSE_INFO_URL)
  else:
    if failed:
      yield FAIL, ("Even though a valid license URL was seen in NAME table,"
                   " there were also bad entries. Please review"
                   " NameIDs {} (LICENSE DESCRIPTION) and {}"
                   " (LICENSE INFO URL).").format(NAMEID_LICENSE_DESCRIPTION,
                                                  NAMEID_LICENSE_INFO_URL)
    else:
      yield PASS, "Font has a valid license URL in NAME table."


@register_check
@check(
    id = 'com.google.fonts/check/031'
  , priority=CRITICAL
)
def com_google_fonts_check_031(ttFont):
  """Description strings in the name table
  must not contain copyright info."""
  from fontbakery.constants import NAMEID_DESCRIPTION
  failed = False
  for name in ttFont['name'].names:
    if 'opyright' in name.string.decode(name.getEncoding())\
       and name.nameID == NAMEID_DESCRIPTION:
      failed = True

  if failed:
    yield FAIL, ("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                 " should be removed (perhaps these were added by"
                 " a longstanding FontLab Studio 5.x bug that"
                 " copied copyright notices to them.)"
                 "").format(NAMEID_DESCRIPTION)
  else:
    yield PASS, ("Description strings in the name table"
                 " do not contain any copyright string.")

@register_check
@check(
    id = 'com.google.fonts/check/032'
)
def com_google_fonts_check_032(ttFont):
  """Description strings in the name table"
     must not exceed 100 characters"""
  from fontbakery.constants import NAMEID_DESCRIPTION
  failed = False
  for name in ttFont['name'].names:
    if (name.nameID == NAMEID_DESCRIPTION and
        len(name.string.decode(name.getEncoding())) > 100):
      failed = True
      break

  if failed:
    yield FAIL, ("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                 " are longer than 100 characters"
                 " and should be removed.").format(NAMEID_DESCRIPTION)
  else:
    yield PASS, "Description name records do not exceed 100 characters."


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


@register_check
@check(
    id = 'com.google.fonts/check/033'
  , conditions=['monospace_stats'
              , 'not whitelist_librebarcode'] # See: https://github.com/graphicore/librebarcode/issues/3
)
def com_google_fonts_check_033(ttFont, monospace_stats):
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
  from fontbakery.constants import (IS_FIXED_WIDTH__MONOSPACED,
                                    IS_FIXED_WIDTH__NOT_MONOSPACED,
                                    PANOSE_PROPORTION__MONOSPACED,
                                    PANOSE_PROPORTION__ANY)
  failed = False
  # Note: These values are read from the dict here only to
  # reduce the max line length in the check implementation below:
  seems_monospaced = monospace_stats["seems_monospaced"]
  most_common_width = monospace_stats["most_common_width"]
  width_max = monospace_stats['width_max']

  if ttFont['hhea'].advanceWidthMax != width_max:
    failed = True
    yield FAIL, Message("bad-advanceWidthMax",
                        ("Value of hhea.advanceWidthMax"
                         " should be set to {} but got"
                         " {} instead."
                         "").format(width_max,
                                    ttFont['hhea'].advanceWidthMax))
  if seems_monospaced:
    if ttFont['post'].isFixedPitch != IS_FIXED_WIDTH__MONOSPACED:
      failed = True
      yield FAIL, Message("mono-bad-post-isFixedPitch",
                          ("On monospaced fonts, the value of"
                           " post.isFixedPitch must be set to {}"
                           " (fixed width monospaced),"
                           " but got {} instead."
                           "").format(IS_FIXED_WIDTH__MONOSPACED,
                                      ttFont['post'].isFixedPitch))

    if ttFont['OS/2'].panose.bProportion != PANOSE_PROPORTION__MONOSPACED:
      failed = True
      yield FAIL, Message("mono-bad-panose-proportion",
                          ("On monospaced fonts, the value of"
                           " OS/2.panose.bProportion must be set to {}"
                           " (proportion: monospaced), but got"
                           " {} instead."
                           "").format(PANOSE_PROPORTION__MONOSPACED,
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
      yield WARN, Message("mono-outliers",
                          ("Font is monospaced but {} glyphs"
                           " ({}%) have a different width."
                           " You should check the widths of:"
                           " {}").format(
                             len(unusually_spaced_glyphs),
                             100.0 * outliers_ratio,
                             unusually_spaced_glyphs))
    if not failed:
      yield PASS, Message("mono-good",
                          ("Font is monospaced and all"
                           " related metadata look good."))
  else:
    # it is a non-monospaced font, so lets make sure
    # that all monospace-related metadata is properly unset.

    if ttFont['post'].isFixedPitch == IS_FIXED_WIDTH__MONOSPACED:
      failed = True
      yield FAIL, Message("bad-post-isFixedPitch",
                          ("On non-monospaced fonts, the"
                           " post.isFixedPitch value must be set to {}"
                           " (not monospaced), but got {} instead."
                           "").format(IS_FIXED_WIDTH__NOT_MONOSPACED,
                                      ttFont['post'].isFixedPitch))

    if ttFont['OS/2'].panose.bProportion == PANOSE_PROPORTION__MONOSPACED:
      failed = True
      yield FAIL, Message("bad-panose-proportion",
                          ("On non-monospaced fonts, the"
                           " OS/2.panose.bProportion value can be set to "
                           " any value except 9 (proportion: monospaced)"
                           " which is the bad value we got in this font."))
    if not failed:
      yield PASS, Message("good",
                          ("Font is not monospaced and"
                           " all related metadata look good."))


@register_check
@check(
    id = 'com.google.fonts/check/034'
)
def com_google_fonts_check_034(ttFont):
  """Check if OS/2 xAvgCharWidth is correct."""
  current_value = ttFont['OS/2'].xAvgCharWidth
  ACCEPTABLE_ERROR = 10 # This is how much we're willing to accept

  if ttFont['OS/2'].version >= 3:
    width_sum = 0
    count = 0
    for glyph_id in ttFont['glyf'].glyphs:
      width = ttFont['hmtx'].metrics[glyph_id][0]
      if width > 0:
        count += 1
        width_sum += width
    if count == 0:
      yield FAIL, "CRITICAL: Found no glyph width data!"
    else:
      expected_value = int(round(width_sum / count))
      if current_value == expected_value:
        yield PASS, "OS/2 xAvgCharWidth is correct."
      elif abs(current_value - expected_value) < ACCEPTABLE_ERROR:
        yield WARN, ("OS/2 xAvgCharWidth is {} but should be"
                     " {} which corresponds to the"
                     " average of all glyph widths"
                     " in the font. These are similar values, which"
                     " may be a symptom of the slightly different"
                     " calculation of the xAvgCharWidth value in"
                     " font editors. There's further discussion on"
                     " this at https://github.com/googlefonts/fontbakery"
                     "/issues/1622").format(current_value,
                                            expected_value)
      else:
        yield FAIL, ("OS/2 xAvgCharWidth is {} but should be "
                     "{} which corresponds to the "
                     "average of all glyph widths "
                     "in the font").format(current_value,
                                           expected_value)
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

    if current_value == expected_value:
      yield PASS, "OS/2 xAvgCharWidth value is correct."
    elif abs(current_value - expected_value) < ACCEPTABLE_ERROR:
      yield WARN, ("OS/2 xAvgCharWidth is {} but should be"
                   " {} which corresponds to the weighted"
                   " average of the widths of the latin"
                   " lowercase glyphs in the font."
                   " These are similar values, which"
                   " may be a symptom of the slightly different"
                   " calculation of the xAvgCharWidth value in"
                   " font editors. There's further discussion on"
                   " this at https://github.com/googlefonts/fontbakery"
                   "/issues/1622").format(current_value,
                                          expected_value)
    else:
      yield FAIL, ("OS/2 xAvgCharWidth is {} but it should be "
                   "{} which corresponds to the weighted "
                   "average of the widths of the latin "
                   "lowercase glyphs in "
                   "the font").format(current_value,
                                      expected_value)


@register_check
@check(
    id = 'com.google.fonts/check/035'
)
def com_google_fonts_check_035(font):
  """Checking with ftxvalidator."""
  import plistlib
  try:
    import subprocess
    ftx_cmd = ["ftxvalidator",
               "-t", "all",  # execute all checks
               font]
    ftx_output = subprocess.check_output(ftx_cmd,
                                         stderr=subprocess.STDOUT)

    ftx_data = plistlib.readPlistFromString(ftx_output)
    # we accept kATSFontTestSeverityInformation
    # and kATSFontTestSeverityMinorError
    if 'kATSFontTestSeverityFatalError' \
       not in ftx_data['kATSFontTestResultKey']:
      yield PASS, "ftxvalidator passed this file"
    else:
      ftx_cmd = ["ftxvalidator",
                 "-T",  # Human-readable output
                 "-r",  # Generate a full report
                 "-t", "all",  # execute all checks
                 font]
      ftx_output = subprocess.check_output(ftx_cmd,
                                           stderr=subprocess.STDOUT)
      yield FAIL, "ftxvalidator output follows:\n\n{}\n".format(ftx_output)

  except subprocess.CalledProcessError as e:
    yield INFO, ("ftxvalidator returned an error code. Output follows :"
                 "\n\n{}\n").format(e.output)
  except OSError:
    yield ERROR, "ftxvalidator is not available!"


@register_check
@check(
    id = 'com.google.fonts/check/036'
)
def com_google_fonts_check_036(font):
  """Checking with ots-sanitize."""
  try:
    import subprocess
    ots_output = subprocess.check_output(["ots-sanitize", font],
                                         stderr=subprocess.STDOUT)
    if ots_output != "" and "File sanitized successfully" not in ots_output:
      yield FAIL, "ots-sanitize output follows:\n\n{}".format(ots_output)
    else:
      yield PASS, "ots-sanitize passed this file"
  except subprocess.CalledProcessError as e:
      yield FAIL, ("ots-sanitize returned an error code. Output follows :"
                   "\n\n{}").format(e.output)
  except OSError as e:
    yield ERROR, ("ots-sanitize is not available!"
                  " You really MUST check the fonts with this tool."
                  " To install it, see"
                  " https://github.com/googlefonts"
                  "/gf-docs/blob/master/ProjectChecklist.md#ots"
                  " Actual error message was: "
                  "'{}'").format(e)


@register_check
@check(
    id = 'com.google.fonts/check/037'
)
def com_google_fonts_check_037(font):
  """Checking with Microsoft Font Validator."""
  try:
    import subprocess
    fval_cmd = ["FontValidator.exe",
                "-file", font,
                "-all-tables",
                "-report-in-font-dir",
                "+raster-tests"]
    subprocess.check_output(fval_cmd,
                            stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    filtered_msgs = ""
    for line in e.output.split("\n"):
      if "Validating glyph with index" in line: continue
      if "Table Test:" in line: continue
      filtered_msgs += line + "\n"
    yield INFO, ("Microsoft Font Validator returned an error code."
                 " Output follows :\n\n{}\n").format(filtered_msgs)
  except OSError:
    yield ERROR, ("Mono runtime and/or "
                  "Microsoft Font Validator are not available!")
    return
  except IOError:
    yield ERROR, ("Mono runtime and/or "
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

  import defusedxml.lxml
  doc = defusedxml.lxml.fromstring(xml_report)
  already_reported = []
  for report in doc.iter('Report'):
    msg = report.get("Message")
    details = report.get("Details")
    if [msg, details] not in already_reported:
      # avoid cluttering the output with tons of identical reports
      already_reported.append([msg, details])

      if report.get("ErrorType") == "P":
        yield PASS, report_message(msg, details)
      elif report.get("ErrorType") == "E":
        yield FAIL, report_message(msg, details)
      elif report.get("ErrorType") == "W":
        yield WARN, report_message(msg, details)
      else:
        yield INFO, report_message(msg, details)


@register_condition
@condition
def fontforge_check_results(font):
  if "adobeblank" in font:
    return SKIP, ("Skipping AdobeBlank since"
                  " this font is a very peculiar hack.")

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


@register_check
@check(
    id = 'com.google.fonts/check/038'
  , conditions=['fontforge_check_results']
)
def com_google_fonts_check_038(font, fontforge_check_results):
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
    yield FAIL, ("fontforge did print these messages to stderr:\n"
                 "{}").format(filtered_err_msgs)
  else:
    yield PASS, "fontforge validation did not output any error message."


@register_check
@check(
    id = 'com.google.fonts/check/039'
  , conditions=['fontforge_check_results']
)
def com_google_fonts_check_039(fontforge_check_results,
                              whitelist_librebarcode):
  """FontForge checks"""

  def ff_check(description, condition, err_msg, ok_msg):
    if condition is False:
      return FAIL, "fontforge-check: {}".format(err_msg)
    else:
      return PASS, "fontforge-check: {}".format(ok_msg)

  validation_state = fontforge_check_results["validation_state"]

  yield ff_check("Contours are closed?",
           bool(validation_state & 0x2) is False,
           "Contours are not closed!",
           "Contours are closed.")

  yield ff_check("Contours do not intersect",
           bool(validation_state & 0x4) is False,
           "There are countour intersections!",
           "Contours do not intersect.")

  yield ff_check("Contours have correct directions",
           bool(validation_state & 0x8) is False,
           "Contours have incorrect directions!",
           "Contours have correct directions.")

  yield ff_check("References in the glyph haven't been flipped",
           bool(validation_state & 0x10) is False,
           "References in the glyph have been flipped!",
           "References in the glyph haven't been flipped.")

  if not whitelist_librebarcode: # See: https://github.com/graphicore/librebarcode/issues/3
    yield ff_check("Glyphs have points at extremas",
             bool(validation_state & 0x20) is False,
             "Glyphs do not have points at extremas!",
             "Glyphs have points at extremas.")

  yield ff_check("Glyph names referred to from glyphs present in the font",
           bool(validation_state & 0x40) is False,
           "Glyph names referred to from glyphs"
           " not present in the font!",
           "Glyph names referred to from glyphs"
           " present in the font.")

  yield ff_check("Points (or control points) are not too far apart",
           bool(validation_state & 0x40000) is False,
           "Points (or control points) are too far apart!",
           "Points (or control points) are not too far apart.")

  yield ff_check("Not more than 1,500 points in any glyph"
           " (a PostScript limit)",
           bool(validation_state & 0x80) is False,
           "There are glyphs with more than 1,500 points!"
           "Exceeds a PostScript limit.",
           "Not more than 1,500 points in any glyph"
           " (a PostScript limit).")

  yield ff_check("PostScript has a limit of 96 hints in glyphs",
           bool(validation_state & 0x100) is False,
           "Exceeds PostScript limit of 96 hints per glyph",
           "Font respects PostScript limit of 96 hints per glyph")

  if not whitelist_librebarcode: # See: https://github.com/graphicore/librebarcode/issues/3
    yield ff_check("Font doesn't have invalid glyph names",
             bool(validation_state & 0x200) is False,
             "Font has invalid glyph names!",
             "Font doesn't have invalid glyph names.")

  yield ff_check("Glyphs have allowed numbers of points defined in maxp",
           bool(validation_state & 0x400) is False,
           "Glyphs exceed allowed numbers of points defined in maxp",
           "Glyphs have allowed numbers of points defined in maxp.")

  yield ff_check("Glyphs have allowed numbers of paths defined in maxp",
           bool(validation_state & 0x800) is False,
           "Glyphs exceed allowed numbers of paths defined in maxp!",
           "Glyphs have allowed numbers of paths defined in maxp.")

  yield ff_check("Composite glyphs have allowed numbers"
           " of points defined in maxp?",
           bool(validation_state & 0x1000) is False,
           "Composite glyphs exceed allowed numbers"
           " of points defined in maxp!",
           "Composite glyphs have allowed numbers"
           " of points defined in maxp.")

  yield ff_check("Composite glyphs have allowed numbers"
           " of paths defined in maxp",
           bool(validation_state & 0x2000) is False,
           "Composite glyphs exceed"
           " allowed numbers of paths defined in maxp!",
           "Composite glyphs have"
           " allowed numbers of paths defined in maxp.")

  yield ff_check("Glyphs instructions have valid lengths",
           bool(validation_state & 0x4000) is False,
           "Glyphs instructions have invalid lengths!",
           "Glyphs instructions have valid lengths.")

  yield ff_check("Points in glyphs are integer aligned",
           bool(validation_state & 0x80000) is False,
           "Points in glyphs are not integer aligned!",
           "Points in glyphs are integer aligned.")

  # According to the opentype spec, if a glyph contains an anchor point
  # for one anchor class in a subtable, it must contain anchor points
  # for all anchor classes in the subtable. Even it, logically,
  # they do not apply and are unnecessary.
  yield ff_check("Glyphs have all required anchors.",
           bool(validation_state & 0x100000) is False,
           "Glyphs do not have all required anchors!",
           "Glyphs have all required anchors.")

  yield ff_check("Glyph names are unique?",
           bool(validation_state & 0x200000) is False,
           "Glyph names are not unique!",
           "Glyph names are unique.")

  yield ff_check("Unicode code points are unique?",
           bool(validation_state & 0x400000) is False,
           "Unicode code points are not unique!",
           "Unicode code points are unique.")

  yield ff_check("Do hints overlap?",
           bool(validation_state & 0x800000) is False,
           "Hints should NOT overlap!",
           "Hinds do not overlap.")


@register_condition
@condition
def vmetrics(ttFonts):
  from fontbakery.utils import get_bounding_box
  v_metrics = {"ymin": 0, "ymax": 0}
  for ttFont in ttFonts:
    font_ymin, font_ymax = get_bounding_box(ttFont)
    v_metrics["ymin"] = min(font_ymin, v_metrics["ymin"])
    v_metrics["ymax"] = max(font_ymax, v_metrics["ymax"])
  return v_metrics


@register_check
@check(
    id = 'com.google.fonts/check/040'
  , conditions=['vmetrics']
)
def com_google_fonts_check_040(ttFont, vmetrics):
  """Checking OS/2 usWinAscent & usWinDescent

  A font's winAscent and winDescent values should be greater than the
  head table's yMax, abs(yMin) values. If they are less than these
  values, clipping can occur on Windows platforms,
  https://github.com/RedHatBrand/Overpass/issues/33

  If the font includes tall/deep writing systems such as Arabic or
  Devanagari, the winAscent and winDescent can be greater than the yMax and
  abs(yMin) to accommodate vowel marks.

  When the win Metrics are significantly greater than the upm, the
  linespacing can appear too loose. To counteract this, enabling the
  OS/2 fsSelection bit 7 (Use_Typo_Metrics), will force Windows to use the
  OS/2 typo values instead. This means the font developer can control the
  linespacing with the typo values, whilst avoiding clipping by setting
  the win values to values greater than the yMax and abs(yMin)."""
  failed = False

  # OS/2 usWinAscent:
  if ttFont['OS/2'].usWinAscent < vmetrics['ymax']:
    failed = True
    yield FAIL, Message("ascent",
                 ("OS/2.usWinAscent value"
                  " should be equal or greater than {}, but got"
                  " {} instead").format(vmetrics['ymax'],
                                        ttFont['OS/2'].usWinAscent))
  # OS/2 usWinDescent:
  if ttFont['OS/2'].usWinDescent < abs(vmetrics['ymin']):
    failed = True
    yield FAIL, Message("descent",
                 ("OS/2.usWinDescent value"
                  " should be equal or greater than {}, but got"
                  " {} instead").format(abs(vmetrics['ymin']),
                                        ttFont['OS/2'].usWinDescent))
  if not failed:
    yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"


@register_check
@check(
    id = 'com.google.fonts/check/041'
)
def com_google_fonts_check_041(ttFont):
  """Checking Vertical Metric Linegaps."""
  if ttFont["hhea"].lineGap != 0:
    yield WARN, Message("hhea", "hhea lineGap is not equal to 0.")
  elif ttFont["OS/2"].sTypoLineGap != 0:
    yield WARN, Message("OS/2", "OS/2 sTypoLineGap is not equal to 0.")
  else:
    yield PASS, "OS/2 sTypoLineGap and hhea lineGap are both 0."


@register_check
@check(
    id = 'com.google.fonts/check/042'
)
def com_google_fonts_check_042(ttFont):
  """Checking OS/2 Metrics match hhea Metrics.

  OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, Linux and Windows.

  Mac OS X uses the hhea values
  Windows uses OS/2 or Win, depending on the OS or fsSelection bit value."""

  # OS/2 sTypoAscender and sTypoDescender match hhea ascent and descent
  if ttFont["OS/2"].sTypoAscender != ttFont["hhea"].ascent:
    yield FAIL, Message("ascender",
                        "OS/2 sTypoAscender and hhea ascent must be equal.")
  elif ttFont["OS/2"].sTypoDescender != ttFont["hhea"].descent:
    yield FAIL, Message("descender",
                        "OS/2 sTypoDescender and hhea descent must be equal.")
  else:
    yield PASS, ("OS/2.sTypoAscender/Descender"
                 " match hhea.ascent/descent.")


@register_check
@check(
    id = 'com.google.fonts/check/043'
)
def com_google_fonts_check_043(ttFont):
  """Checking unitsPerEm value is reasonable."""
  upem = ttFont['head'].unitsPerEm
  target_upem = [2**i for i in range(4, 15)]
  target_upem.insert(0, 1000)
  if upem not in target_upem:
    yield FAIL, ("The value of unitsPerEm at the head table"
                 " must be either 1000 or a power of"
                 " 2 between 16 to 16384."
                 " Got '{}' instead.").format(upem)
  else:
    yield PASS, "unitsPerEm value on the 'head' table is reasonable."


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


def parse_version_string(s):
  """ Tries to parse a version string as used
      in ttf versioning metadata fields.
      Example of expected format is:
        'Version 01.003; Comments'
  """
  suffix = ''
  # DC: I think this may be wrong, the ; isnt the only separator,
  # anything not an int is ok
  if ';' in s:
    fields = s.split(';')
    s = fields[0]
    fields.pop(0)
    suffix = ';'.join(fields)

  substrings = s.split('.')
  minor = substrings[-1]
  if ' ' in substrings[-2]:
    major = substrings[-2].split(' ')[-1]
  else:
    major = substrings[-2]

  if suffix:
    return major, minor, suffix
  else:
    return major, minor


def get_expected_version(f):
  from fontbakery.constants import NAMEID_VERSION_STRING
  expected_version = parse_version_string(str(f["head"].fontRevision))
  for name in f["name"].names:
    if name.nameID == NAMEID_VERSION_STRING:
      name_version = get_version_from_name_entry(name)
      if expected_version is None:
        expected_version = name_version
      else:
        if name_version > expected_version:
          expected_version = name_version
  return expected_version


@register_check
@check(
    id = 'com.google.fonts/check/044'
)
def com_google_fonts_check_044(ttFont):
  """Checking font version fields"""
  import re
  from fontbakery.constants import NAMEID_VERSION_STRING
  failed = False
  try:
    expected = get_expected_version(ttFont)
  except:
    expected = None
    yield FAIL, "failed to parse font version entries in the name table."

  if expected is None:
    failed = True
    yield FAIL, ("Could not find any font versioning info on the head table"
                 " or in the name table entries.")
  else:
    font_revision = str(ttFont['head'].fontRevision)
    expected_str = "{}.{}".format(expected[0],
                                  expected[1])
    if font_revision != expected_str:
      failed = True
      yield FAIL, ("Font revision on the head table ({})"
                   " differs from the expected value ({})"
                   "").format(font_revision, expected)

    expected_str = "Version {}.{}".format(expected[0],
                                          expected[1])
    for name in ttFont["name"].names:
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
          yield FAIL, ("Unable to parse font version info"
                       " from this name table entry: '{}'").format(name)
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
              yield FAIL, ("NAMEID_VERSION_STRING value '{}'"
                           " does not match expected '{}'"
                           "").format(name_version, fix)
          except:
            failed = True  # give up. it's definitely bad :(
            yield FAIL, ("Unable to parse font version info"
                         " from name table entries.")
  if not failed:
    yield PASS, "All font version fields look good."


@register_check
@check(
    id = 'com.google.fonts/check/045'
)
def com_google_fonts_check_045(ttFont):
  """Does the font have a DSIG table ?"""
  if "DSIG" in ttFont:
    yield PASS, "Digital Signature (DSIG) exists."
  else:
    yield FAIL, ("This font lacks a digital signature (DSIG table)."
                 " Some applications may require one (even if only a"
                 " dummy placeholder) in order to work properly.")


@register_check
@check(
    id = 'com.google.fonts/check/046'
)
def com_google_fonts_check_046(ttFont):
  """Font contains the first few mandatory glyphs
     (.null or NULL, CR and space)?"""
  from fontbakery.utils import getGlyph

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
    yield WARN, ("Font is missing glyphs for"
                 " the following mandatory codepoints:"
                 " {}.").format(", ".join(missing))
  else:
    yield PASS, ("Font contains the first few mandatory glyphs"
                 " (.null or NULL, CR and space).")


@register_condition
@condition
def missing_whitespace_chars(ttFont):
  from fontbakery.utils import getGlyph
  space = getGlyph(ttFont, 0x0020)
  nbsp = getGlyph(ttFont, 0x00A0)
  # tab = getGlyph(ttFont, 0x0009)

  missing = []
  if space is None: missing.append("0x0020")
  if nbsp is None: missing.append("0x00A0")
  # fonts probably don't need an actual tab char
  # if tab is None: missing.append("0x0009")
  return missing


@register_check
@check(
    id = 'com.google.fonts/check/047'
)
def com_google_fonts_check_047(ttFont, missing_whitespace_chars):
  """Font contains glyphs for whitespace characters?"""
  if missing_whitespace_chars != []:
    yield FAIL, ("Whitespace glyphs missing for"
                 " the following codepoints:"
                 " {}.").format(", ".join(missing_whitespace_chars))
  else:
    yield PASS, "Font contains glyphs for whitespace characters."


@register_check
@check(
    id = 'com.google.fonts/check/048'
  , conditions=['not missing_whitespace_chars']
)
def com_google_fonts_check_048(ttFont):
  """Font has **proper** whitespace glyph names?"""
  from fontbakery.utils import getGlyph

  def getGlyphEncodings(font, names):
    result = set()
    for subtable in font['cmap'].tables:
        if subtable.isUnicode():
            for codepoint, name in subtable.cmap.items():
                if name in names:
                    result.add(codepoint)
    return result

  if ttFont['post'].formatType == 3.0:
    yield SKIP, "Font has version 3 post table."
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
      yield FAIL, Message("bad20",
                          ("Glyph 0x0020 is called \"{}\":"
                           " Change to \"space\""
                           " or \"uni0020\"").format(space))

    nbsp = getGlyph(ttFont, 0x00A0)
    if 0x00A0 not in nbsp_enc:
      if 0x00A0 in space_enc:
        # This is OK.
        # Some fonts use the same glyph for both space and nbsp.
        pass
      else:
        failed = True
        yield FAIL, Message("badA0",
                            ("Glyph 0x00A0 is called \"{}\":"
                             " Change to \"nbsp\""
                             " or \"uni00A0\"").format(nbsp))

    if failed is False:
      yield PASS, "Font has **proper** whitespace glyph names."


@register_check
@check(
    id = 'com.google.fonts/check/049'
  , conditions=['not whitelist_librebarcode'] # See: https://github.com/graphicore/librebarcode/issues/3
)
def com_google_fonts_check_049(ttFont):
  """Whitespace glyphs have ink?"""
  from fontbakery.utils import getGlyph

  def glyphHasInk(font, name):
    """Checks if specified glyph has any ink.
    That is, that it has at least one defined contour associated.
    Composites are considered to have ink if any of their components have ink.
    Args:
        font:       the font
        glyph_name: The name of the glyph to check for ink.
    Returns:
        True if the font has at least one contour associated with it.
    """
    glyph = font['glyf'].glyphs[name]
    glyph.expand(font['glyf'])
    if not glyph.isComposite():
      if glyph.numberOfContours == 0:
        return False
      (coords, _, _) = glyph.getCoordinates(font['glyf'])
      # you need at least 3 points to draw
      return len(coords) > 2

    # composite is blank if composed of blanks
    # if you setup a font with cycles you are just a bad person
    # Dave: lol, bad people exist, so put a recursion in this recursion
    for glyph_name in glyph.getComponentNames(glyph.components):
      if glyphHasInk(font, glyph_name):
        return True
    return False

  # code-points for all "whitespace" chars:
  WHITESPACE_CHARACTERS = [
    0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x0020,
    0x0085, 0x00A0, 0x1680, 0x2000, 0x2001, 0x2002,
    0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
    0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F,
    0x3000, 0x180E, 0x200B, 0x2060, 0xFEFF
  ]
  failed = False
  for codepoint in WHITESPACE_CHARACTERS:
    g = getGlyph(ttFont, codepoint)
    if g is not None and glyphHasInk(ttFont, g):
      failed = True
      yield FAIL, ("Glyph \"{}\" has ink."
                   " It needs to be replaced by"
                   " an empty glyph.").format(g)
  if not failed:
    yield PASS, "There is no whitespace glyph with ink."


@register_check
@check(
    id = 'com.google.fonts/check/050'
  , conditions=['not missing_whitespace_chars']
)
def com_google_fonts_check_050(ttFont):
  """Whitespace glyphs have coherent widths?"""
  from fontbakery.utils import getGlyph

  def getGlyphWidth(font, glyph):
    return font['hmtx'][glyph][0]

  space = getGlyph(ttFont, 0x0020)
  nbsp = getGlyph(ttFont, 0x00A0)

  spaceWidth = getGlyphWidth(ttFont, space)
  nbspWidth = getGlyphWidth(ttFont, nbsp)

  if spaceWidth != nbspWidth or nbspWidth < 0:
    if nbspWidth > spaceWidth and spaceWidth >= 0:
      yield FAIL, Message("bad_space",
                          ("space {} nbsp {}: Space advanceWidth"
                           " needs to be fixed"
                           " to {}.").format(spaceWidth,
                                             nbspWidth,
                                             nbspWidth))
    else:
      yield FAIL, Message("bad_nbsp",
                          ("space {} nbsp {}: Nbsp advanceWidth"
                           " needs to be fixed "
                           "to {}").format(spaceWidth,
                                           nbspWidth,
                                           spaceWidth))
  else:
    yield PASS, "Whitespace glyphs have coherent widths."


# DEPRECATED:
# com.google.fonts/check/051 - "Checking with pyfontaine"
#
# Replaced by:
# com.google.fonts/check/132 - "Checking Google Cyrillic Historical glyph coverage"
# com.google.fonts/check/133 - "Checking Google Cyrillic Plus glyph coverage"
# com.google.fonts/check/134 - "Checking Google Cyrillic Plus (Localized Forms) glyph coverage"
# com.google.fonts/check/135 - "Checking Google Cyrillic Pro glyph coverage"
# com.google.fonts/check/136 - "Checking Google Greek Ancient Musical Symbols glyph coverage"
# com.google.fonts/check/137 - "Checking Google Greek Archaic glyph coverage"
# com.google.fonts/check/138 - "Checking Google Greek Coptic glyph coverage"
# com.google.fonts/check/139 - "Checking Google Greek Core glyph coverage"
# com.google.fonts/check/140 - "Checking Google Greek Expert glyph coverage"
# com.google.fonts/check/141 - "Checking Google Greek Plus glyph coverage"
# com.google.fonts/check/142 - "Checking Google Greek Pro glyph coverage"
# com.google.fonts/check/143 - "Checking Google Latin Core glyph coverage"
# com.google.fonts/check/144 - "Checking Google Latin Expert glyph coverage"
# com.google.fonts/check/145 - "Checking Google Latin Plus glyph coverage"
# com.google.fonts/check/146 - "Checking Google Latin Plus (Optional Glyphs) glyph coverage"
# com.google.fonts/check/147 - "Checking Google Latin Pro glyph coverage"
# com.google.fonts/check/148 - "Checking Google Latin Pro (Optional Glyphs) glyph coverage"


@register_check
@check(
    id = 'com.google.fonts/check/052'
)
def com_google_fonts_check_052(ttFont):
  """Font contains all required tables?"""
  REQUIRED_TABLES = set(["cmap", "head", "hhea", "hmtx",
                         "maxp", "name", "OS/2", "post"])
  OPTIONAL_TABLES = set(["cvt ", "fpgm", "loca", "prep",
                         "VORG", "EBDT", "EBLC", "EBSC",
                         "BASE", "GPOS", "GSUB", "JSTF",
                         "DSIG", "gasp", "hdmx", "kern",
                         "LTSH", "PCLT", "VDMX", "vhea",
                         "vmtx"])
  # See https://github.com/googlefonts/fontbakery/issues/617
  tables = set(ttFont.reader.tables.keys())
  if OPTIONAL_TABLES & tables:
    optional_tables = [str(t) for t in (OPTIONAL_TABLES & tables)]
    yield INFO, ("This font contains the following"
                 " optional tables [{}]").format(", ".join(optional_tables))

  glyphs = set(["glyf"] if "glyf" in ttFont.keys() else ["CFF "])
  if (REQUIRED_TABLES | glyphs) - tables:
    missing_tables = [str(t) for t in (REQUIRED_TABLES | glyphs - tables)]
    yield FAIL, ("This font is missing the following required tables:"
                 " [{}]").format(", ".join(missing_tables))
  else:
    yield PASS, "Font contains all required tables."


@register_check
@check(
    id = 'com.google.fonts/check/053'
)
def com_google_fonts_check_053(ttFont):
  """Are there unwanted tables?"""
  UNWANTED_TABLES = set(['FFTM', 'TTFA', 'prop',
                         'TSI0', 'TSI1', 'TSI2', 'TSI3'])
  unwanted_tables_found = []
  for table in ttFont.keys():
    if table in UNWANTED_TABLES:
      unwanted_tables_found.append(table)

  if len(unwanted_tables_found) > 0:
    yield FAIL, ("Unwanted tables were found"
                 " in the font and should be removed:"
                 " {}").format(", ".join(unwanted_tables_found))
  else:
    yield PASS, "There are no unwanted tables."


@register_condition
@condition
def ttfautohint_stats(font):
  import re
  import subprocess
  import tempfile
  try:
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

TTFAUTOHINT_MISSING_MSG = (
  "ttfautohint is not available!"
  " You really MUST check the fonts with this tool."
  " To install it, see https://github.com"
  "/googlefonts/gf-docs/blob/master"
  "/ProjectChecklist.md#ttfautohint")

@register_check
@check(
    id = 'com.google.fonts/check/054'
  , conditions=['ttfautohint_stats']
)
def com_google_fonts_check_054(font, ttfautohint_stats):
  """Show hinting filesize impact.

     Current implementation simply logs useful info
     but there's no fail scenario for this checker."""

  if "missing" in ttfautohint_stats:
    yield WARN, TTFAUTOHINT_MISSING_MSG
    return

  if ttfautohint_stats["dehinted_size"] == 0:
    yield WARN, ("ttfautohint --dehint reports that"
                 " \"This font has already been processed with ttfautohint\"."
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
  yield INFO, results_table


@register_check
@check(
    id = 'com.google.fonts/check/055'
)
def com_google_fonts_check_055(ttFont):
  """Version format is correct in 'name' table?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_VERSION_STRING
  import re
  def is_valid_version_format(value):
    return re.match(r'Version\s0*[1-9]+\.\d+', value)

  failed = False
  version_entries = get_name_entry_strings(ttFont, NAMEID_VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    yield FAIL, Message("no-version-string",
                        ("Font lacks a NAMEID_VERSION_STRING (nameID={})"
                         " entry").format(NAMEID_VERSION_STRING))
  for ventry in version_entries:
    if not is_valid_version_format(ventry):
      failed = True
      yield FAIL, Message("bad-version-strings",
                          ("The NAMEID_VERSION_STRING (nameID={}) value must "
                           "follow the pattern Version X.Y between 1.000 and 9.999."
                           " Current value: {}").format(NAMEID_VERSION_STRING,
                                                        ventry))
  if not failed:
    yield PASS, "Version format in NAME table entries is correct."


@register_check
@check(
    id = 'com.google.fonts/check/056'
  , conditions=['ttfautohint_stats']
)
def com_google_fonts_check_056(ttFont, ttfautohint_stats):
  """Font has old ttfautohint applied?

     1. find which version was used, by inspecting name table entries

     2. find which version of ttfautohint is installed
        and warn if not available

     3. rehint the font with the latest version of ttfautohint
        using the same options
  """
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_VERSION_STRING

  def ttfautohint_version(values):
    import re
    for value in values:
      results = re.search(r'ttfautohint \(v(.*)\)', value)
      if results:
        return results.group(1)

  def installed_version_is_newer(installed, used):
    installed = map(int, installed.split("."))
    used = map(int, used.split("."))
    return installed > used

  version_strings = get_name_entry_strings(ttFont, NAMEID_VERSION_STRING)
  ttfa_version = ttfautohint_version(version_strings)
  if len(version_strings) == 0:
    yield FAIL, Message("lacks-version-strings",
                        "This font file lacks mandatory "
                        "version strings in its name table.")
  elif ttfa_version is None:
    yield INFO, ("Could not detect which version of"
                 " ttfautohint was used in this font."
                 " It is typically specified as a comment"
                 " in the font version entries of the 'name' table."
                 " Such font version strings are currently:"
                 " {}").format(version_strings)
  elif "missing" in ttfautohint_stats:
    # Even though we skip here, we still have a chance of performing
    # early portions of the check in the 2 error/info scenarios above
    # regardless of the avaiability of ttfautohint.
    yield SKIP, TTFAUTOHINT_MISSING_MSG
  else:
    installed_ttfa = ttfautohint_stats["version"]
    try:
      if installed_version_is_newer(installed_ttfa,
                                    ttfa_version):
        yield WARN, ("ttfautohint used in font = {};"
                     " installed = {}; Need to re-run"
                     " with the newer version!").format(ttfa_version,
                                                        installed_ttfa)
      else:
        yield PASS, ("ttfautohint available in the system is older"
                     " than the one used in the font.")
    except ValueError:
      yield FAIL, Message("parse-error",
                          ("Failed to parse ttfautohint version values:"
                           " installed = '{}';"
                           " used_in_font = '{}'").format(installed_ttfa,
                                                          ttfa_version))


@register_check
@check(
    id = 'com.google.fonts/check/057'
)
def com_google_fonts_check_057(ttFont):
  """Name table entries should not contain line-breaks."""
  from fontbakery.constants import (NAMEID_STR,
                                    PLATID_STR)
  failed = False
  for name in ttFont["name"].names:
    string = name.string.decode(name.getEncoding())
    if "\n" in string:
      failed = True
      yield FAIL, ("Name entry {} on platform {} contains"
                   " a line-break.").format(NAMEID_STR[name.nameID],
                                            PLATID_STR[name.platformID])
  if not failed:
    yield PASS, ("Name table entries are all single-line"
                 " (no line-breaks found).")


@register_check
@check(
    id = 'com.google.fonts/check/058'
)
def com_google_fonts_check_058(ttFont):
  """Glyph names are all valid?"""
  import re
  bad_names = []
  for _, glyphName in enumerate(ttFont.getGlyphOrder()):
    if glyphName in [".null", ".notdef"]:
      # These 2 names are explicit exceptions
      # in the glyph naming rules
      continue
    if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
      bad_names.append(glyphName)

  if len(bad_names) == 0:
    yield PASS, "Glyph names are all valid."
  else:
    yield FAIL, ("The following glyph names do not comply"
                 " with naming conventions: {}"
                 " A glyph name may be up to 31 characters in length,"
                 " must be entirely comprised of characters from"
                 " the following set:"
                 " A-Z a-z 0-9 .(period) _(underscore). and must not"
                 " start with a digit or period."
                 " There are a few exceptions"
                 " such as the special character \".notdef\"."
                 " The glyph names \"twocents\", \"a1\", and \"_\""
                 " are all valid, while \"2cents\""
                 " and \".twocents\" are not.").format(bad_names)


@register_check
@check(
    id = 'com.google.fonts/check/059'
)
def com_google_fonts_check_059(ttFont):
  """Font contains unique glyph names?
     Duplicate glyph names prevent font installation on Mac OS X."""
  import re
  glyphs = []
  duplicated_glyphIDs = []
  for _, g in enumerate(ttFont.getGlyphOrder()):
    glyphID = re.sub(r'#\w+', '', g)
    if glyphID in glyphs:
      duplicated_glyphIDs.append(glyphID)
    else:
      glyphs.append(glyphID)

  if len(duplicated_glyphIDs) == 0:
    yield PASS, "Font contains unique glyph names."
  else:
    yield FAIL, ("The following glyph IDs"
                 " occur twice: {}").format(duplicated_glyphIDs)


@register_check
@check(
    id = 'com.google.fonts/check/060'
)
def com_google_fonts_check_060(ttFont):
  """No glyph is incorrectly named?"""
  import re
  bad_glyphIDs = []
  for _, g in enumerate(ttFont.getGlyphOrder()):
    if re.search(r'#\w+$', g):
      glyphID = re.sub(r'#\w+', '', g)
      bad_glyphIDs.append(glyphID)

  if len(bad_glyphIDs) == 0:
    yield PASS, "Font does not have any incorrectly named glyph."
  else:
    yield FAIL, ("The following glyph IDs"
                 " are incorrectly named: {}").format(bad_glyphIDs)

@register_check
@check(
    id = 'com.google.fonts/check/061'
)
def com_google_fonts_check_061(ttFont):
  """EPAR table present in font?"""
  if "EPAR" not in ttFont:
    yield INFO, ("EPAR table not present in font."
                 " To learn more see"
                 " https://github.com/googlefonts/"
                 "fontbakery/issues/818")
  else:
    yield PASS, "EPAR table present in font."


@register_check
@check(
    id = 'com.google.fonts/check/062'
)
def com_google_fonts_check_062(ttFont):
  """Is GASP table correctly set?"""
  try:
    if not isinstance(ttFont["gasp"].gaspRange, dict):
      yield FAIL, "GASP.gaspRange method value have wrong type."
    else:
      failed = False
      if 0xFFFF not in ttFont["gasp"].gaspRange:
        yield FAIL, "GASP does not have 0xFFFF gaspRange."
      else:
        for key in ttFont["gasp"].gaspRange.keys():
          if key != 0xFFFF:
            yield FAIL, ("GASP should only have 0xFFFF gaspRange,"
                          " but {} gaspRange was also found."
                          "").format(hex(key))
            failed = True
          else:
            value = ttFont["gasp"].gaspRange[key]
            if value != 0x0F:
              failed = True
              yield WARN, (" All flags in GASP range 0xFFFF (i.e. all font"
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
          yield PASS, "GASP table is correctly set."
  except KeyError:
    yield FAIL, ("Font is missing the GASP table."
                 " Try exporting the font with autohinting enabled.")


@register_condition
@condition
def has_kerning_info(ttFont):
  """ A font has kerning info if it has a GPOS table
      containing at least one Pair Adjustment lookup
      (eigther directly or through an extension subtable).
  """
  if not "GPOS" in ttFont:
    return False

  if not ttFont["GPOS"].table.LookupList:
    return False

  for lookup in ttFont["GPOS"].table.LookupList.Lookup:
    if lookup.LookupType == 2:  # type 2 = Pair Adjustment
      return True
    elif lookup.LookupType == 9: # type 9 = Extension subtable
      for ext in lookup.SubTable:
        if ext.ExtensionLookupType == 2:  # type 2 = Pair Adjustment
          return True


# TODO: Design special case handling for whitelists/blacklists
# https://github.com/googlefonts/fontbakery/issues/1540
@register_condition
@condition
def whitelist_librebarcode(font):
  font_filenames = [
    "LibreBarcode39-Regular.ttf",
    "LibreBarcode39Text-Regular.ttf",
    "LibreBarcode128-Regular.ttf",
    "LibreBarcode128Text-Regular.ttf"
  ]
  for font_filename in font_filenames:
    if font_filename in font:
      return True


@register_check
@check(
    id = 'com.google.fonts/check/063'
  , conditions=['not whitelist_librebarcode']
)
def com_google_fonts_check_063(ttFont):
  """Does GPOS table have kerning information?"""
  if not has_kerning_info(ttFont):
    yield WARN, "GPOS table lacks kerning information."
  else:
    yield PASS, "GPOS table has got kerning information."


@register_condition
@condition
def ligatures(ttFont):
  all_ligatures = {}
  try:
    if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
      for lookup in ttFont["GSUB"].table.LookupList.Lookup:
        if lookup.LookupType == 4:  # type 4 = Ligature Substitution
          for subtable in lookup.SubTable:
            for firstGlyph in subtable.ligatures.keys():
              all_ligatures[firstGlyph] = []
              for lig in subtable.ligatures[firstGlyph]:
                if lig.Component[0] not in all_ligatures[firstGlyph]:
                  all_ligatures[firstGlyph].append(lig.Component[0])
    return all_ligatures
  except:
    return -1  # Indicate fontTools-related crash...


@register_check
@check(
    id = 'com.google.fonts/check/064'
  , conditions=['ligatures']
)
def com_google_fonts_check_064(ttFont, ligatures):
  """Is there a caret position declared for every ligature?

      All ligatures in a font must have corresponding caret (text cursor)
      positions defined in the GDEF table, otherwhise, users may experience
      issues with caret rendering.
  """
  if ligatures == -1:
    yield FAIL, Message("malformed",
                        "Failed to lookup ligatures."
                        " This font file seems to be malformed."
                        " For more info, read:"
                        " https://github.com"
                        "/googlefonts/fontbakery/issues/1596")
  elif "GDEF" not in ttFont:
    yield WARN, Message("GDEF-missing",
                        ("GDEF table is missing, but it is mandatory"
                         " to declare it on fonts that provide ligature"
                         " glyphs because the caret (text cursor)"
                         " positioning for each ligature must be"
                         " provided in this table."))
  else:
    # TODO: After getting a sample of a good font,
    #       resume the implementation of this routine:
    lig_caret_list = ttFont["GDEF"].table.LigCaretList
    if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
      yield WARN, Message("lacks-caret-pos",
                          ("This font lacks caret position values for"
                           " ligature glyphs on its GDEF table."))
    elif lig_caret_list.LigGlyphCount != len(ligatures):
      yield WARN, Message("incomplete-caret-pos-data",
                          ("It seems that this font lacks caret positioning"
                           " values for some of its ligature glyphs on the"
                           " GDEF table. There's a total of {} ligatures,"
                           " but only {} sets of caret positioning"
                           " values.").format(len(ligatures),
                                              lig_caret_list.LigGlyphCount))
    else:
      # Should we also actually check each individual entry here?
      yield PASS, "Looks good!"


@register_check
@check(
    id = 'com.google.fonts/check/065'
  , rationale = """
      Fonts with ligatures should have kerning on the corresponding
      non-ligated sequences for text where ligatures aren't used
      (eg https://github.com/impallari/Raleway/issues/14).
    """
  , request = 'https://github.com/googlefonts/fontbakery/issues/1145'
  , conditions = ['ligatures',
                  'has_kerning_info']
)
def com_google_fonts_check_065(ttFont, ligatures, has_kerning_info):
  """Is there kerning info for non-ligated sequences?

    Fonts with ligatures should have kerning on the corresponding
    non-ligated sequences for text where ligatures are not used.
  """
  remaining = ligatures
  def look_for_nonligated_kern_info(table):
    for pairpos in table.SubTable:
      for i, glyph in enumerate(pairpos.Coverage.glyphs):
        if glyph in ligatures.keys():
          if not hasattr(pairpos, 'PairSet'):
            continue
          for pairvalue in pairpos.PairSet[i].PairValueRecord:
            if pairvalue.SecondGlyph in ligatures[glyph]:
              del remaining[glyph]

  def ligatures_str(ligs):
    result = []
    for first in ligs:
      result.extend(["{}_{}".format(first, second)
                     for second in ligs[first]])
    return result

  if ligatures == -1:
    yield FAIL, Message("malformed",
                        "Failed to lookup ligatures."
                        " This font file seems to be malformed."
                        " For more info, read:"
                        " https://github.com"
                        "/googlefonts/fontbakery/issues/1596")
  else:
    for lookup in ttFont["GPOS"].table.LookupList.Lookup:
      if lookup.LookupType == 2:  # type 2 = Pair Adjustment
        look_for_nonligated_kern_info(lookup)
      # elif lookup.LookupType == 9:
      #   if lookup.SubTable[0].ExtensionLookupType == 2:
      #     look_for_nonligated_kern_info(lookup.SubTable[0])

    if remaining != {}:
      yield WARN, Message("lacks-kern-info",
                         ("GPOS table lacks kerning info for the following"
                          " non-ligated sequences: "
                          "{}").format(ligatures_str(remaining)))
    else:
      yield PASS, ("GPOS table provides kerning info for "
                   "all non-ligated sequences.")


@register_check
@check(
    id = 'com.google.fonts/check/066'
)
def com_google_fonts_check_066(ttFont):
  """Is there a "kern" table declared in the font?

     Fonts should have their kerning implemented in the GPOS table."""

  if "kern" in ttFont:
    yield FAIL, "Font should not have a \"kern\" table"
  else:
    yield PASS, "Font does not declare a \"kern\" table."


@register_check
@check(
    id = 'com.google.fonts/check/067'
)
def com_google_fonts_check_067(ttFont):
  """Make sure family name does not begin with a digit.

     Font family names which start with a numeral are often not
     discoverable in Windows applications.
  """
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME
  failed = False
  for familyname in get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME):
    digits = map(str, range(0, 10))
    if familyname[0] in digits:
      yield FAIL, ("Font family name '{}'"
                   " begins with a digit!").format(familyname)
      failed = True
  if failed is False:
    yield PASS, "Font family name first character is not a digit."


@register_check
@check(
    id = 'com.google.fonts/check/068'
)
def com_google_fonts_check_068(ttFont):
  """Does full font name begin with the font family name?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME)
  familyname = get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)
  fullfontname = get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME)

  if len(familyname) == 0:
    yield FAIL, Message("no-font-family-name",
                        ("Font lacks a NAMEID_FONT_FAMILY_NAME"
                         " entry in the 'name' table."))
  elif len(fullfontname) == 0:
    yield FAIL, Message("no-full-font-name",
                        ("Font lacks a NAMEID_FULL_FONT_NAME"
                         " entry in the 'name' table."))
  else:
    # we probably should check all found values are equivalent.
    # and, in that case, then performing the rest of the check
    # with only the first occurences of the name entries
    # will suffice:
    fullfontname = fullfontname[0]
    familyname = familyname[0]

    if not fullfontname.startswith(familyname):
      yield FAIL, Message("does-not",
                          (" On the 'name' table, the full font name"
                           " (NameID {} - FULL_FONT_NAME: '{}')"
                           " does not begin with font family name"
                           " (NameID {} - FONT_FAMILY_NAME:"
                           " '{}')".format(NAMEID_FULL_FONT_NAME,
                                           familyname,
                                           NAMEID_FONT_FAMILY_NAME,
                                           fullfontname)))
    else:
      yield PASS, "Full font name begins with the font family name."


@register_check
@check(
    id = 'com.google.fonts/check/069'
)
def com_google_fonts_check_069(ttFont):
  """Is there any unused data at the end of the glyf table?"""
  if 'CFF ' in ttFont:
    yield SKIP, "This check does not support CFF fonts."
  else:
    # -1 because https://www.microsoft.com/typography/otspec/loca.htm
    expected = len(ttFont['loca']) - 1
    actual = len(ttFont['glyf'])
    diff = actual - expected

    # allow up to 3 bytes of padding
    if diff > 3:
      yield FAIL, ("Glyf table has unreachable data at"
                   " the end of the table."
                   " Expected glyf table length {}"
                   " (from loca table), got length"
                   " {} (difference: {})").format(expected, actual, diff)
    elif diff < 0:
      yield FAIL, ("Loca table references data beyond"
                   " the end of the glyf table."
                   " Expected glyf table length {}"
                   " (from loca table), got length"
                   " {} (difference: {})").format(expected, actual, diff)
    else:
      yield PASS, "There is no unused data at the end of the glyf table."


# TODO: extend this to check for availability of all required currency symbols.
@register_check
@check(
    id = 'com.google.fonts/check/070'
  , conditions=['not whitelist_librebarcode'] # See: https://github.com/graphicore/librebarcode/issues/3
)
def com_google_fonts_check_070(ttFont):
  """Font has all expected currency sign characters?"""

  def font_has_char(ttFont, codepoint):
    for subtable in ttFont['cmap'].tables:
      if codepoint in subtable.cmap:
        return True
    #otherwise
    return False

  failed = False

  OPTIONAL = {
    #TODO: Do we want to check for this one?
    #0x20A0: "EUROPEAN CURRENCY SIGN"
  }
  MANDATORY = {
    0x20AC: "EURO SIGN"
    # TODO: extend this list
  }
  for codepoint, charname in OPTIONAL.items():
    if not font_has_char(ttFont, codepoint):
      failed = True
      yield WARN, "Font lacks \"%s\" character (unicode: 0x%04X)" % (charname, codepoint)

  for codepoint, charname in MANDATORY.items():
    if not font_has_char(ttFont, codepoint):
      failed = True
      yield FAIL, "Font lacks \"%s\" character (unicode: 0x%04X)" % (charname, codepoint)

  if not failed:
    yield PASS, "Font has all expected currency sign characters."


@register_check
@check(
    id = 'com.google.fonts/check/071'
)
def com_google_fonts_check_071(ttFont):
  """Font follows the family naming recommendations?"""
  # See http://forum.fontlab.com/index.php?topic=313.0
  import re
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  bad_entries = []

  # <Postscript name> may contain only a-zA-Z0-9
  # and one hyphen
  bad_psname = re.compile("[^A-Za-z0-9-]")
  for string in get_name_entry_strings(ttFont, NAMEID_POSTSCRIPT_NAME):
    if bad_psname.search(string):
      bad_entries.append({'field': 'PostScript Name',
                          'value': string,
                          'rec': 'May contain only a-zA-Z0-9'
                                 ' characters and an hyphen.'})
    if string.count('-') > 1:
      bad_entries.append({'field': 'Postscript Name',
                          'value': string,
                          'rec': 'May contain not more'
                                 ' than a single hyphen'})

  for string in get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME):
    if len(string) >= 64:
      bad_entries.append({'field': 'Full Font Name',
                          'value': string,
                          'rec': 'exceeds max length (63)'})

  for string in get_name_entry_strings(ttFont, NAMEID_POSTSCRIPT_NAME):
    if len(string) >= 30:
      bad_entries.append({'field': 'PostScript Name',
                          'value': string,
                          'rec': 'exceeds max length (29)'})

  for string in get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({'field': 'Family Name',
                          'value': string,
                          'rec': 'exceeds max length (31)'})

  for string in get_name_entry_strings(ttFont, NAMEID_FONT_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({'field': 'Style Name',
                          'value': string,
                          'rec': 'exceeds max length (31)'})

  for string in get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({'field': 'OT Family Name',
                          'value': string,
                          'rec': 'exceeds max length (31)'})

  for string in get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({'field': 'OT Style Name',
                          'value': string,
                          'rec': 'exceeds max length (31)'})
  weight_value = None
  if "OS/2" in ttFont:
    field = "OS/2 usWeightClass"
    weight_value = ttFont["OS/2"].usWeightClass
  if "CFF " in ttFont:
    field = "CFF Weight"
    weight_value = ttFont["CFF "].Weight

  if weight_value is not None:
    # <Weight> value >= 250 and <= 900 in steps of 50
    if weight_value % 50 != 0:
      bad_entries.append({"field": field,
                          'value': weight_value,
                          "rec": "Value should ideally be a multiple of 50."})
    full_info = " "
    " 'Having a weightclass of 100 or 200 can result in a \"smear bold\" or"
    " (unintentionally) returning the style-linked bold. Because of this,"
    " you may wish to manually override the weightclass setting for all"
    " extra light, ultra light or thin fonts'"
    " - http://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html"
    if weight_value < 250:
      bad_entries.append({"field": field,
                          'value': weight_value,
                          "rec": "Value should ideally be 250 or more." +
                                 full_info})
    if weight_value > 900:
      bad_entries.append({"field": field,
                          'value': weight_value,
                          "rec": "Value should ideally be 900 or less."})
  if len(bad_entries) > 0:
    table = "| Field | Value | Recommendation |\n"
    table += "|:----- |:----- |:-------------- |\n"
    for bad in bad_entries:
      table += "| {} | {} | {} |\n".format(bad["field"], bad["value"], bad["rec"])
    yield INFO, ("Font does not follow "
                 "some family naming recommendations:\n\n"
                 "{}").format(table)
  else:
    yield PASS, "Font follows the family naming recommendations."


@register_check
@check(
    id = 'com.google.fonts/check/072'
)
def com_google_fonts_check_072(ttFont):
  """Font enables smart dropout control in "prep" table instructions?

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
  """
  instructions = b"\xb8\x01\xff\x85\xb0\x04\x8d"
  if "CFF " in ttFont:
    yield SKIP, "Not applicable to a CFF font."
  else:
    if ("prep" in ttFont and
        instructions in ttFont["prep"].program.getBytecode()):
      yield PASS, ("Program at 'prep' table contains instructions"
                   " enabling smart dropout control.")
    else:
      yield WARN, ("Font does not contain TrueType instructions enabling"
                   " smart dropout control in the 'prep' table program."
                   " Please try exporting the font with autohinting enabled.")


@register_check
@check(
    id = 'com.google.fonts/check/073'
)
def com_google_fonts_check_073(ttFont):
  """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""
  hhea_advance_width_max = ttFont['hhea'].advanceWidthMax
  hmtx_advance_width_max = None
  for g in ttFont['hmtx'].metrics.values():
    if hmtx_advance_width_max is None:
      hmtx_advance_width_max = max(0, g[0])
    else:
      hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

  if hmtx_advance_width_max is None:
    yield FAIL, "Failed to find advance width data in HMTX table!"
  elif hmtx_advance_width_max != hhea_advance_width_max:
    yield FAIL, ("AdvanceWidthMax mismatch: expected {} (from hmtx);"
                 " got {} (from hhea)").format(hmtx_advance_width_max,
                                               hhea_advance_width_max)
  else:
    yield PASS, ("MaxAdvanceWidth is consistent"
                 " with values in the Hmtx and Hhea tables.")


@register_check
@check(
    id = 'com.google.fonts/check/074'
  , rationale = """
      The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
      For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that
      string should be the same in CFF fonts which also have this
      requirement in the OpenType spec.

      Note:
      A common place where we find non-ASCII strings is on name table
      entries with NameID > 18, which are expressly for localising
      the ASCII-only IDs into Hindi / Arabic / etc.
    """
  , request = "https://github.com/googlefonts/fontbakery/issues/1663"
)
def com_google_fonts_check_074(ttFont):
  """Are there non-ASCII characters in ASCII-only NAME table entries ?"""
  from fontbakery.constants import (NAMEID_COPYRIGHT_NOTICE,
                                    NAMEID_POSTSCRIPT_NAME)
  bad_entries = []
  for name in ttFont["name"].names:
    if name.nameID == NAMEID_COPYRIGHT_NOTICE or \
       name.nameID == NAMEID_POSTSCRIPT_NAME:
      string = name.string.decode(name.getEncoding())
      try:
        string.encode('ascii')
      except:
        bad_entries.append(name)
        yield INFO, ("Bad string at"
                     " [nameID {}, '{}']:"
                     " '{}'"
                     "").format(name.nameID,
                                name.getEncoding(),
                                string.encode("ascii",
                                              errors='xmlcharrefreplace'))
  if len(bad_entries) > 0:
    yield FAIL, ("There are {} strings containing"
                 " non-ASCII characters in the ASCII-only"
                 " NAME table entries.").format(len(bad_entries))
  else:
    yield PASS, ("None of the ASCII-only NAME table entries"
                 " contain non-ASCII characteres.")


@register_check
@check(
    id = 'com.google.fonts/check/075'
)
def com_google_fonts_check_075(ttFont):
  """Check for points out of bounds."""
  failed = False
  out_of_bounds = []
  for glyphName in ttFont['glyf'].keys():
    glyph = ttFont['glyf'][glyphName]
    coords = glyph.getCoordinates(ttFont['glyf'])[0]
    for x, y in coords:
      if x < glyph.xMin or x > glyph.xMax or \
         y < glyph.yMin or y > glyph.yMax or \
         abs(x) > 32766 or abs(y) > 32766:
        failed = True
        out_of_bounds.append((glyphName, x, y))

  if failed:
      yield WARN, ("The following glyphs have coordinates which are"
                   " out of bounds:\n{}\nThis happens a lot when points"
                   " are not extremes, which is usually bad. However,"
                   " fixing this alert by adding points on extremes may"
                   " do more harm than good, especially with italics,"
                   " calligraphic-script, handwriting, rounded and"
                   " other fonts. So it is common to"
                   " ignore this message".format(out_of_bounds))
  else:
      yield PASS, "All glyph paths have coordinates within bounds!"


@register_check
@check(
    id = 'com.google.fonts/check/076'
)
def com_google_fonts_check_076(ttFont):
  """Check glyphs have unique unicode codepoints"""
  failed = False
  for subtable in ttFont['cmap'].tables:
    if subtable.isUnicode():
      codepoints = {}
      for codepoint, name in subtable.cmap.items():
        codepoints.setdefault(codepoint, set()).add(name)
      for value in codepoints.keys():
        if len(codepoints[value]) >= 2:
          failed = True
          yield FAIL, ("These glyphs carry the same"
                       " unicode value {}:"
                       " {}").format(value,
                                     ", ".join(codepoints[value]))
  if not failed:
    yield PASS, "All glyphs have unique unicode codepoint assignments."


@register_check
@check(
    id = 'com.google.fonts/check/077'
)
def com_google_fonts_check_077(ttFont):
  """Check all glyphs have codepoints assigned"""
  failed = False
  for subtable in ttFont['cmap'].tables:
    if subtable.isUnicode():
      for item in subtable.cmap.items():
        codepoint = item[0]
        if codepoint is None:
          failed = True
          yield FAIL, ("Glyph {} lacks a unicode"
                       " codepoint assignment").format(codepoint)
  if not failed:
    yield PASS, "All glyphs have a codepoint value assigned."


@register_check
@check(
    id = 'com.google.fonts/check/078'
)
def com_google_fonts_check_078(ttFont):
  """Check that glyph names do not exceed max length"""
  failed = False
  for subtable in ttFont['cmap'].tables:
    for item in subtable.cmap.items():
      name = item[1]
      if len(name) > 109:
        failed = True
        yield FAIL, ("Glyph name is too long:"
                     " '{}'").format(name)
  if not failed:
    yield PASS, "No glyph names exceed max allowed length."


@register_condition
@condition
def seems_monospaced(monospace_stats):
  return monospace_stats['seems_monospaced']


@register_check
@check(
    id = 'com.google.fonts/check/079'
  , conditions=['seems_monospaced']
)
def com_google_fonts_check_079(ttFont):
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
    yield WARN, ("This seems to be a monospaced font,"
                 " so advanceWidth value should be the same"
                 " across all glyphs, but {} % of them"
                 " have a different value."
                 "").format(round(100 * outliers_percentage, 2))
    if zero_or_double_detected:
      yield WARN, ("Double-width and/or zero-width glyphs"
                   " were detected. These glyphs should be set"
                   " to the same width as all others"
                   " and then add GPOS single pos lookups"
                   " that zeros/doubles the widths as needed.")
  else:
    yield PASS, ("hhea.advanceWidthMax is equal"
                 " to all glyphs' advanceWidth in this monospaced font.")

@register_check
@check(
    id = 'com.google.fonts/check/080'
  , conditions=['metadata']
)
def com_google_fonts_check_080(metadata):
  """METADATA.pb: Ensure designer simple short name."""
  if len(metadata.designer.split(" ")) >= 4 or \
     " and " in metadata.designer or \
     "." in metadata.designer or \
     "," in metadata.designer:
    yield FAIL, "\"designer\" key must be simple short name"
  else:
    yield PASS, "Designer is a simple short name"


@register_condition
@condition
def listed_on_gfonts_api(metadata):
  if not metadata:
    return False
  import requests
  url = ('http://fonts.googleapis.com'
         '/css?family={}').format(metadata.name.replace(' ', '+'))
  r = requests.get(url)
  return r.status_code == 200

@register_check
@check(
    id = 'com.google.fonts/check/081'
  , conditions=['metadata']
)
def com_google_fonts_check_081(listed_on_gfonts_api):
  """METADATA.pb: Fontfamily is listed on Google Fonts API ?"""
  if not listed_on_gfonts_api:
    yield WARN, "Family not found via Google Fonts API."
  else:
    yield PASS, "Font is properly listed via Google Fonts API."


@register_check
@check(
    id = 'com.google.fonts/check/082'
  , conditions=['metadata']
)
def com_google_fonts_check_082(metadata):
  """METADATA.pb: Designer exists in Google Fonts profiles.csv ?"""
  PROFILES_GIT_URL = ("https://github.com/google/"
                      "fonts/blob/master/designers/profiles.csv")
  PROFILES_RAW_URL = ("https://raw.githubusercontent.com/google/"
                      "fonts/master/designers/profiles.csv")
  if metadata.designer == "":
    yield FAIL, ("METADATA.pb field \"designer\" MUST NOT be empty!")
  elif metadata.designer == "Multiple Designers":
    yield SKIP, ("Found \"Multiple Designers\" at METADATA.pb, which"
                 " is OK, so we won't look for it at profiles.csv")
  else:
    import urllib
    import csv
    try:
      handle = urllib.urlopen(PROFILES_RAW_URL)
      designers = []
      for row in csv.reader(handle):
        if not row:
          continue
        designers.append(row[0].decode("utf-8"))
      if metadata.designer not in designers:
        yield WARN, ("METADATA.pb: Designer \"{}\" is not listed"
                     " in profiles.csv"
                     " (at \"{}\")").format(metadata.designer,
                                            PROFILES_GIT_URL)
      else:
        yield PASS, ("Found designer \"{}\""
                     " at profiles.csv").format(metadata.designer)
    except:
      yield WARN, "Failed to fetch \"{}\"".format(PROFILES_RAW_URL)


@register_check
@check(
    id = 'com.google.fonts/check/083'
  , conditions=['metadata']
)
def com_google_fonts_check_083(metadata):
  """METADATA.pb: check if fonts field only has
     unique "full_name" values."""
  fonts = {}
  for f in metadata.fonts:
    fonts[f.full_name] = f

  if len(set(fonts.keys())) != len(metadata.fonts):
    yield FAIL, ("Found duplicated \"full_name\" values"
                 " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique \"full_name\" values.")


@register_check
@check(
    id = 'com.google.fonts/check/084'
  , conditions=['metadata']
)
def com_google_fonts_check_084(metadata):
  """METADATA.pb: check if fonts field
     only contains unique style:weight pairs."""
  pairs = {}
  for f in metadata.fonts:
    styleweight = "{}:{}".format(f.style, f.weight)
    pairs[styleweight] = 1
  if len(set(pairs.keys())) != len(metadata.fonts):
    yield FAIL, ("Found duplicated style:weight pair"
                 " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique style:weight pairs.")


@register_check
@check(
    id = 'com.google.fonts/check/085'
  , conditions=['metadata']
)
def com_google_fonts_check_085(metadata):
  """METADATA.pb license is "APACHE2", "UFL" or "OFL" ?"""
  licenses = ["APACHE2", "OFL", "UFL"]
  if metadata.license in licenses:
    yield PASS, ("Font license is declared"
                 " in METADATA.pb as \"{}\"").format(metadata.license)
  else:
    yield FAIL, ("METADATA.pb license field (\"{}\")"
                 " must be one of the following:"
                 " {}").format(metadata.license,
                               licenses)


@register_check
@check(
    id = 'com.google.fonts/check/086'
  , conditions=['metadata']
)
def com_google_fonts_check_086(metadata):
  """METADATA.pb should contain at least "menu" and "latin" subsets."""
  missing = []
  for s in ["menu", "latin"]:
    if s not in list(metadata.subsets):
      missing.append(s)

  if missing != []:
    yield FAIL, ("Subsets \"menu\" and \"latin\" are mandatory,"
                 " but METADATA.pb is missing"
                 " \"{}\"").format(" and ".join(missing))
  else:
    yield PASS, "METADATA.pb contains \"menu\" and \"latin\" subsets."


@register_check
@check(
    id = 'com.google.fonts/check/087'
  , conditions=['metadata']
)
def com_google_fonts_check_087(metadata):
  """METADATA.pb subsets should be alphabetically ordered."""
  expected = list(sorted(metadata.subsets))

  if list(metadata.subsets) != expected:
    yield FAIL, ("METADATA.pb subsets are not sorted "
                 "in alphabetical order: Got ['{}']"
                 " and expected ['{}']").format("', '".join(metadata.subsets),
                                                "', '".join(expected))
  else:
    yield PASS, "METADATA.pb subsets are sorted in alphabetical order."


@register_check
@check(
    id = 'com.google.fonts/check/088'
  , conditions=['metadata']
)
def com_google_fonts_check_088(metadata):
  """Copyright notice is the same in all fonts ?"""
  copyright = None
  fail = False
  for f in metadata.fonts:
    if copyright and f.copyright != copyright:
      fail = True
    copyright = f.copyright
  if fail:
    yield FAIL, ("METADATA.pb: Copyright field value"
                 " is inconsistent across family")
  else:
    yield PASS, "Copyright is consistent across family"

@register_check
@check(
    id = 'com.google.fonts/check/089'
  , conditions=['metadata']
)
def com_google_fonts_check_089(metadata):
  """Check that METADATA family values are all the same."""
  name = ""
  fail = False
  for f in metadata.fonts:
    if name and f.name != name:
      fail = True
    name = f.name
  if fail:
    yield FAIL, ("METADATA.pb: Family name is not the same"
                 " in all metadata \"fonts\" items.")
  else:
    yield PASS, ("METADATA.pb: Family name is the same"
                 " in all metadata \"fonts\" items.")


@register_condition
@condition
def has_regular_style(metadata):
  fonts = metadata.fonts if metadata else []
  for f in fonts:
    if f.weight == 400 and f.style == "normal":
      return True
  return False


@register_check
@check(
    id = 'com.google.fonts/check/090'
  , conditions=['metadata']
)
def com_google_fonts_check_090(has_regular_style):
  """According Google Fonts standards,
     families should have a Regular style."""
  if has_regular_style:
    yield PASS, "Family has a Regular style."
  else:
    yield FAIL, ("This family lacks a Regular"
                 " (style: normal and weight: 400)"
                 " as required by Google Fonts standards.")


@register_check
@check(
    id = 'com.google.fonts/check/091'
  , conditions=['metadata',
                'has_regular_style']
)
def com_google_fonts_check_091(metadata):
  """Regular should be 400."""
  badfonts = []
  for f in metadata.fonts:
    if f.full_name.endswith("Regular") and f.weight != 400:
      badfonts.append("{} (weight: {})".format(f.filename, f.weight))
  if len(badfonts) > 0:
    yield FAIL, ("METADATA.pb: Regular font weight must be 400."
                 " Please fix these: {}").format(", ".join(badfonts))
  else:
    yield PASS, "Regular has weight = 400."


@register_condition
@condition
def font_metadata(ttFont):
  from fontbakery.utils import get_FamilyProto_Message

  family_directory = os.path.dirname(ttFont.reader.file.name)
  pb_file = os.path.join(family_directory, "METADATA.pb")
  if not os.path.exists(pb_file):
    return None
  metadata = get_FamilyProto_Message(pb_file)

  if not metadata:
    return None

  for f in metadata.fonts:
    if ttFont.reader.file.name.endswith(f.filename):
      return f


@register_check
@check(
    id = 'com.google.fonts/check/092'
  , conditions=['font_metadata']
)
def com_google_fonts_check_092(ttFont, font_metadata):
  """Checks METADATA.pb font.name field matches
     family name declared on the name table."""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME

  familynames = get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)
  if len(familynames) == 0:
    yield FAIL, ("This font lacks a FONT_FAMILY_NAME entry"
                 " (nameID={}) in the name"
                 " table.").format(NAMEID_FONT_FAMILY_NAME)
  else:
    if font_metadata.name not in familynames:
      yield FAIL, ("Unmatched family name in font:"
                   " TTF has \"{}\" while METADATA.pb"
                   " has \"{}\"").format(familynames[0],
                                         font_metadata.name)
    else:
      yield PASS, ("Family name \"{}\" is identical"
                   " in METADATA.pb and on the"
                   " TTF file.").format(font_metadata.name)

@register_check
@check(
    id = 'com.google.fonts/check/093'
  , conditions=['font_metadata']
)
def com_google_fonts_check_093(ttFont, font_metadata):
  """Checks METADATA.pb font.post_script_name matches
     postscript name declared on the name table."""
  failed = False
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_POSTSCRIPT_NAME

  postscript_names = get_name_entry_strings(ttFont, NAMEID_POSTSCRIPT_NAME)
  if len(postscript_names) == 0:
    failed = True
    yield FAIL, ("This font lacks a POSTSCRIPT_NAME"
                 " entry (nameID={}) in the "
                 "name table.").format(NAMEID_POSTSCRIPT_NAME)
  else:
    for psname in postscript_names:
      if psname != font_metadata.post_script_name:
        failed = True
        yield FAIL, ("Unmatched postscript name in font:"
                     " TTF has \"{}\" while METADATA.pb has"
                     " \"{}\".").format(psname,
                                        font_metadata.post_script_name)
  if not failed:
    yield PASS, ("Postscript name \"{}\" is identical"
                 " in METADATA.pb and on the"
                 " TTF file.").format(font_metadata.post_script_name)


@register_check
@check(
    id = 'com.google.fonts/check/094'
  , conditions=['font_metadata']
)
def com_google_fonts_check_094(ttFont, font_metadata):
  """METADATA.pb font.fullname value matches
     fullname declared on the name table ?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_FULL_FONT_NAME

  full_fontnames = get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME)
  if len(full_fontnames) == 0:
    yield FAIL, Message("lacks-entry",
                        ("This font lacks a FULL_FONT_NAME"
                         " entry (nameID={}) in the"
                         " name table.").format(NAMEID_FULL_FONT_NAME))
  else:
    for full_fontname in full_fontnames:
      if full_fontname != font_metadata.full_name:
        yield FAIL, Message("mismatch",
                            ("Unmatched fullname in font:"
                             " TTF has \"{}\" while METADATA.pb"
                             " has \"{}\".").format(full_fontname,
                                                    font_metadata.full_name))
      else:
        yield PASS, ("Full fontname \"{}\" is identical"
                     " in METADATA.pb and on the"
                     " TTF file.").format(full_fontname)


@register_check
@check(
    id = 'com.google.fonts/check/095'
  , conditions=['font_metadata', 'style']
)
def com_google_fonts_check_095(ttFont, style, font_metadata):
  """METADATA.pb font.name value should be same as
     the family name declared on the name table."""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (RIBBI_STYLE_NAMES,
                                    NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_STR)
  if style in RIBBI_STYLE_NAMES:
    font_familynames = get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)
    nameid = NAMEID_FONT_FAMILY_NAME
  else:
    font_familynames = get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_FAMILY_NAME)
    nameid = NAMEID_TYPOGRAPHIC_FAMILY_NAME

  if len(font_familynames) == 0:
    yield FAIL, Message("lacks-entry",
                        ("This font lacks a {} entry"
                         " (nameID={}) in the"
                         " name table.").format(NAMEID_STR[nameid],
                                                nameid))
  else:
    for font_familyname in font_familynames:
      if font_familyname != font_metadata.name:
        yield FAIL, Message("mismatch",
                            ("Unmatched familyname in font:"
                             " TTF has \"{}\" while METADATA.pb has"
                             " name=\"{}\".").format(font_familyname,
                                                     font_metadata.name))
      else:
        yield PASS, ("OK: Family name \"{}\" is identical"
                     " in METADATA.pb and on the"
                     " TTF file.").format(font_metadata.name)


@register_check
@check(
    id = 'com.google.fonts/check/096'
  , conditions=['font_metadata']
)
def com_google_fonts_check_096(font_metadata):
  """METADATA.pb family.full_name and family.post_script_name
     fields have equivalent values ?"""
  import re
  regex = re.compile(r"\W")
  post_script_name = regex.sub("", font_metadata.post_script_name)
  fullname = regex.sub("", font_metadata.full_name)
  if fullname != post_script_name:
    yield FAIL, ("METADATA.pb full_name=\"{}\""
                 " does not match post_script_name ="
                 " \"{}\"").format(font_metadata.full_name,
                                   font_metadata.post_script_name)
  else:
    yield PASS, ("METADATA.pb fields \"fullName\" and"
                 " \"postScriptName\" have equivalent values.")


@register_check
@check(
    id = 'com.google.fonts/check/097'
  , conditions=['font_metadata']
)
def com_google_fonts_check_097(font_metadata):
  """METADATA.pb family.filename and family.post_script_name
     fields have equivalent values ?"""
  import re
  regex = re.compile(r"\W")
  post_script_name = regex.sub("", font_metadata.post_script_name)
  filename = regex.sub("", os.path.splitext(font_metadata.filename)[0])
  if filename != post_script_name:
    yield FAIL, ("METADATA.pb filename=\"{}\" does not match"
                 " post_script_name=\"{}\"."
                 "").format(font_metadata.filename,
                            font_metadata.post_script_name)
  else:
    yield PASS, ("METADATA.pb fields \"filename\" and"
                 " \"postScriptName\" have equivalent values.")


@register_condition
@condition
def font_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME
  return get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)


@register_condition
@condition
def typographic_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_TYPOGRAPHIC_FAMILY_NAME
  return get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_FAMILY_NAME)


@register_condition
@condition
def font_familyname(font_familynames):
  # This assumes that all familyname
  # name table entries are identical.
  # FIX-ME: Maybe we should have a check for that.
  #         Have we ever seen this kind of
  #         problem in the wild, though ?
  return font_familynames[0]


@register_check
@check(
    id = 'com.google.fonts/check/098'
  , conditions=['style',
                'font_metadata']
)
def com_google_fonts_check_098(style,
                              font_metadata,
                              font_familynames,
                              typographic_familynames):
  """METADATA.pb font.name field contains font name in right format ?"""
  from fontbakery.constants import RIBBI_STYLE_NAMES
  if style in RIBBI_STYLE_NAMES:
    familynames = font_familynames
  else:
    familynames = typographic_familynames

  for font_familyname in familynames:
    if font_familyname in font_metadata.name:
      yield PASS, ("METADATA.pb font.name field contains"
                   " font name in right format."
                   " ('{}' in '{}')").format(font_familyname,
                                             font_metadata.name)
    else:
      yield FAIL, ("METADATA.pb font.name field (\"{}\")"
                   " does not match correct font name format (\"{}\")."
                   "").format(font_metadata.name,
                              font_familyname)


@register_check
@check(
    id = 'com.google.fonts/check/099'
  , conditions=['style',
                'font_metadata']
)
def com_google_fonts_check_099(style,
                              font_metadata,
                              font_familynames,
                              typographic_familynames):
  """METADATA.pb font.full_name field contains font name in right format ?"""
  from fontbakery.constants import RIBBI_STYLE_NAMES
  if style in RIBBI_STYLE_NAMES:
    familynames = font_familynames
    if familynames == []:
      yield SKIP, "No FONT_FAMILYNAME"
  else:
    familynames = typographic_familynames
    if familynames == []:
      yield SKIP, "No TYPOGRAPHIC_FAMILYNAME"

  for font_familyname in familynames:
    if font_familyname in font_metadata.full_name:
      yield PASS, ("METADATA.pb font.full_name field contains"
                   " font name in right format."
                   " ('{}' in '{}')").format(font_familyname,
                                             font_metadata.full_name)
    else:
      yield FAIL, ("METADATA.pb font.full_name field (\"{}\")"
                   " does not match correct font name format (\"{}\")."
                   "").format(font_metadata.full_name,
                              font_familyname)


@register_check
@check(
    id = 'com.google.fonts/check/100'
  , conditions=['style', # This means the font filename (source of truth here) is good
                'font_metadata']
)
def com_google_fonts_check_100(ttFont,
                              font_metadata):
  """METADATA.pb font.filename field contains font name in right format ?"""
  expected = os.path.split(ttFont.reader.file.name)[1]
  if font_metadata.filename == expected:
    yield PASS, ("METADATA.pb filename field contains"
                 " font name in right format.")
  else:
    yield FAIL, ("METADATA.pb filename field (\"{}\") does not match"
                 " correct font name format (\"{}\")."
                 "").format(font_metadata.filename,
                            expected)


@register_check
@check(
    id = 'com.google.fonts/check/101'
  , conditions=['font_metadata',
                'font_familynames']
)
def com_google_fonts_check_101(font_metadata,
                              font_familynames):
  """METADATA.pb font.post_script_name field
     contains font name in right format ?"""
  for font_familyname in font_familynames:
    psname = "".join(str(font_familyname).split())
    if psname in "".join(font_metadata.post_script_name.split("-")):
      yield PASS, ("METADATA.pb postScriptName field"
                   " contains font name in right format.")
    else:
      yield FAIL, ("METADATA.pb postScriptName (\"{}\")"
                   " does not match correct font name format (\"{}\")."
                   "").format(font_metadata.post_script_name,
                              font_familyname)


@register_check
@check(
    id = 'com.google.fonts/check/102'
  , conditions=['font_metadata']
)
def com_google_fonts_check_102(font_metadata):
  """Copyright notice on METADATA.pb matches canonical pattern ?"""
  import re
  from unidecode import unidecode
  does_match = re.search(r'Copyright [0-9]{4} The .* Project Authors \([^\@]*\)',
                         font_metadata.copyright)
  if does_match:
    yield PASS, ("METADATA.pb copyright field '{}'"
                 " matches canonical pattern.").format(font_metadata.copyright)
  else:
    yield FAIL, ("METADATA.pb: Copyright notices should match"
                 " a pattern similar to:"
                 " 'Copyright 2017 The Familyname"
                 " Project Authors (git url)'\n"
                 "But instead we have got:"
                 " '{}'").format(unidecode(font_metadata.copyright))


@register_check
@check(
    id = 'com.google.fonts/check/103'
  , conditions=['font_metadata']
)
def com_google_fonts_check_103(font_metadata):
  """Copyright notice on METADATA.pb does not contain Reserved Font Name ?"""
  from unidecode import unidecode
  if "Reserved Font Name" in font_metadata.copyright:
    yield WARN, ("METADATA.pb: copyright field (\"{}\")"
                 " contains \"Reserved Font Name\"."
                 " This is an error except in a few specific"
                 " rare cases.").format(unidecode(font_metadata.copyright))
  else:
    yield PASS, ("METADATA.pb copyright field"
                 " does not contain \"Reserved Font Name\".")


@register_check
@check(
    id = 'com.google.fonts/check/104'
  , conditions=['font_metadata']
)
def com_google_fonts_check_104(font_metadata):
  """Copyright notice shouldn't exceed 500 chars."""
  if len(font_metadata.copyright) > 500:
    yield FAIL, ("METADATA.pb: Copyright notice exceeds"
                 " maximum allowed lengh of 500 characteres.")
  else:
    yield PASS, "Copyright notice string is shorter than 500 chars."


@register_condition
@condition
def canonical_filename(font_metadata):
  if not font_metadata:
    return
  style_names = {
    "normal": "",
    "italic": "Italic"
  }
  WEIGHT_VALUE_TO_NAME = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black"
  }
  familyname = font_metadata.name.replace(" ", "")
  style_weight = "{}{}".format(WEIGHT_VALUE_TO_NAME.get(font_metadata.weight),
                               style_names.get(font_metadata.style))
  if style_weight == "":
    style_weight = "Regular"
  return "{}-{}.ttf".format(familyname, style_weight)


@register_check
@check(
    id = 'com.google.fonts/check/105'
  , conditions=['font_metadata', 'canonical_filename']
)
def com_google_fonts_check_105(font_metadata, canonical_filename):
  """Filename is set canonically in METADATA.pb ?"""
  if canonical_filename != font_metadata.filename:
    yield FAIL, ("METADATA.pb: filename field (\"{}\")"
                 " does not match "
                 "canonical name \"{}\".".format(font_metadata.filename,
                                                 canonical_filename))
  else:
    yield PASS, "Filename in METADATA.pb is set canonically."


@register_check
@check(
    id = 'com.google.fonts/check/106'
  , conditions=['font_metadata']
)
def com_google_fonts_check_106(ttFont, font_metadata):
  """METADATA.pb font.style "italic" matches font internals ?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (NAMEID_FULL_FONT_NAME,
                                    MACSTYLE_ITALIC)
  if font_metadata.style != "italic":
    yield SKIP, "This check only applies to italic fonts."
  else:
    font_fullname = get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME)
    if len(font_fullname) == 0:
      yield SKIP, "Font lacks fullname entries in name table."
      # this fail scenario was already checked above
      # (passing those previous checks is a prerequisite for this one)
      # FIXME: Could we pack this into a condition ?
    else:
      # FIXME: here we only check the first name entry.
      #        Should we iterate over them all ? Or should we check
      #        if they're all the same?
      font_fullname = font_fullname[0]

      if not bool(ttFont["head"].macStyle & MACSTYLE_ITALIC):
        yield FAIL, Message("bad-macstyle",
                            "METADATA.pb style has been set to italic"
                            " but font macStyle is improperly set.")
      elif not font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL, Message("bad-fullfont-name",
                            ("Font macStyle Italic bit is set"
                             " but nameID {} (\"{}\") is not ended with"
                             " \"Italic\"").format(NAMEID_FULL_FONT_NAME,
                                                   font_fullname))
      else:
        yield PASS, ("OK: METADATA.pb font.style \"italic\""
                     " matches font internals.")


@register_check
@check(
    id = 'com.google.fonts/check/107'
  , conditions=['font_metadata']
)
def com_google_fonts_check_107(ttFont, font_metadata):
  """METADATA.pb font.style "normal" matches font internals ?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    MACSTYLE_ITALIC)
  if font_metadata.style != "normal":
    yield SKIP, "This check only applies to normal fonts."
    # FIXME: declare a common condition called "normal_style"
  else:
    font_familyname = get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)
    font_fullname = get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME)
    if len(font_familyname) == 0 or len(font_fullname) == 0:
      yield SKIP, ("Font lacks familyname and/or"
                   " fullname entries in name table.")
      # FIXME: This is the same SKIP condition as in check/106
      #        so we definitely need to address them with a common condition!
    else:
      font_familyname = font_familyname[0]
      font_fullname = font_fullname[0]

      if bool(ttFont["head"].macStyle & MACSTYLE_ITALIC):
        yield FAIL, Message("bad-macstyle",
                            ("METADATA.pb style has been set to normal"
                             " but font macStyle is improperly set."))
      elif font_familyname.split("-")[-1].endswith('Italic'):
        yield FAIL, Message("familyname-italic",
                            ("Font macStyle indicates a non-Italic font, but"
                             " nameID {} (FONT_FAMILY_NAME: \"{}\") ends with"
                             " \"Italic\".").format(NAMEID_FONT_FAMILY_NAME,
                                                    font_familyname))
      elif font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL, Message("fullfont-italic",
                            ("Font macStyle indicates a non-Italic font but"
                             " nameID {} (FULL_FONT_NAME: \"{}\") ends with"
                             " \"Italic\".").format(NAMEID_FULL_FONT_NAME,
                                                    font_fullname))
      else:
        yield PASS, ("METADATA.pb font.style \"normal\""
                     " matches font internals.")


@register_check
@check(
    id = 'com.google.fonts/check/108'
  , conditions=['font_metadata']
)
def com_google_fonts_check_108(ttFont, font_metadata):
  """METADATA.pb font.name and font.full_name fields match
     the values declared on the name table?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME)

  font_familyname = get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)[0]
  font_fullname = get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME)[0]
  # FIXME: common condition/name-id check as in the two previous checks.

  if font_fullname != font_metadata.full_name:
    yield FAIL, Message("fullname-mismatch",
                        ("METADATA.pb: Fullname (\"{}\")"
                         " does not match name table"
                         " entry \"{}\" !").format(font_metadata.full_name,
                                                   font_fullname))
  elif font_familyname != font_metadata.name:
    yield FAIL, Message("familyname-mismatch",
                        ("METADATA.pb Family name \"{}\")"
                         " does not match name table"
                         " entry \"{}\" !").format(font_metadata.name,
                                                   font_familyname))
  else:
    yield PASS, ("METADATA.pb familyname and fullName fields"
                 " match corresponding name table entries.")


# TODO: Design special case handling for whitelists/blacklists
# https://github.com/googlefonts/fontbakery/issues/1540
@register_condition
@condition
def whitelist_camelcased_familyname(font):
  familynames = [
    "BenchNine",
    "FakeFont",
    "McLaren",
    "MedievalSharp",
    "UnifrakturCook",
    "UnifrakturMaguntia"
  ]
  for familyname in familynames:
    if familyname in font:
      return True


@register_check
@check(
    id = 'com.google.fonts/check/109'
  , conditions=['font_metadata'
              , 'not whitelist_camelcased_familyname']
)
def com_google_fonts_check_109(font_metadata):
  """Check if fontname is not camel cased."""
  import re
  if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
    yield FAIL, ("METADATA.pb: '{}' is a CamelCased name."
                 " To solve this, simply use spaces"
                 " instead in the font name.").format(font_metadata.name)
  else:
    yield PASS, "Font name is not camel-cased."


@register_check
@check(
    id = 'com.google.fonts/check/110'
  , conditions=['metadata', # that's the family-wide metadata!
                'font_metadata'] # and this one's specific to a single file
)
def com_google_fonts_check_110(metadata, font_metadata):
  """Check font name is the same as family name."""
  if font_metadata.name != metadata.name:
    yield FAIL, ("METADATA.pb: {}: Family name \"{}\""
                 " does not match"
                 " font name: \"{}\"").format(font_metadata.filename,
                                              metadata.name,
                                              font_metadata.name)
  else:
    yield PASS, "Font name is the same as family name."


@register_check
@check(
    id = 'com.google.fonts/check/111'
  , conditions=['font_metadata']
)
def com_google_fonts_check_111(font_metadata):
  """Check that font weight has a canonical value."""
  first_digit = font_metadata.weight / 100
  if (font_metadata.weight % 100) != 0 or \
     (first_digit < 1 or first_digit > 9):
   yield FAIL, ("METADATA.pb: The weight is declared"
                " as {} which is not a "
                "multiple of 100"
                " between 100 and 900.").format(font_metadata.weight)
  else:
    yield PASS, "Font weight has a canonical value."


@register_check
@check(
    id = 'com.google.fonts/check/112'
  , conditions=['font_metadata']
)
def com_google_fonts_check_112(ttFont,
                              font_metadata):
  """Checking OS/2 usWeightClass matches weight specified at METADATA.pb"""
  # Weight name to value mapping:
  GF_API_WEIGHT_NAMES = {250: "Thin",
                         275: "ExtraLight",
                         300: "Light",
                         400: "Regular",
                         500: "Medium",
                         600: "SemiBold",
                         700: "Bold",
                         800: "ExtraBold",
                         900: "Black"}
  CSS_WEIGHT_NAMES = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black"
  }
  gf_weight = GF_API_WEIGHT_NAMES.get(ttFont["OS/2"].usWeightClass,
                                      "bad Google Fonts API weight value")
  css_weight = CSS_WEIGHT_NAMES.get(font_metadata.weight,
                                    "bad CSS weight value")
  if gf_weight != css_weight:
    yield FAIL, ("OS/2 usWeightClass ({}:\"{}\") does not match"
                 " weight specified at METADATA.pb ({}:\"{}\")."
                 "").format(ttFont["OS/2"].usWeightClass,
                            gf_weight,
                            font_metadata.weight,
                            css_weight)
  else:
    yield PASS, ("OS/2 usWeightClass matches"
                 " weight specified at METADATA.pb")


@register_check
@check(
    id = 'com.google.fonts/check/113'
  , conditions=['font_metadata']
)
def com_google_fonts_check_113(font_metadata):
  """Metadata weight matches postScriptName"""
  WEIGHTS = {
    "Thin": 100,
    "ThinItalic": 100,
    "ExtraLight": 200,
    "ExtraLightItalic": 200,
    "Light": 300,
    "LightItalic": 300,
    "Regular": 400,
    "Italic": 400,
    "Medium": 500,
    "MediumItalic": 500,
    "SemiBold": 600,
    "SemiBoldItalic": 600,
    "Bold": 700,
    "BoldItalic": 700,
    "ExtraBold": 800,
    "ExtraBoldItalic": 800,
    "Black": 900,
    "BlackItalic": 900
  }
  pair = []
  for k, weight in WEIGHTS.items():
    if weight == font_metadata.weight:
      pair.append((k, weight))

  if not pair:
    yield FAIL, ("METADATA.pb: Font weight"
                 " does not match postScriptName")
  elif not (font_metadata.post_script_name.endswith('-' + pair[0][0]) or
            font_metadata.post_script_name.endswith('-' + pair[1][0])):
    yield FAIL, ("METADATA.pb: postScriptName (\"{}\")"
                 " with weight {} must be"
                 " ended with \"{}\" or \"{}\""
                 "").format(font_metadata.post_script_name,
                            pair[0][1],
                            pair[0][0],
                            pair[1][0])
  else:
    yield PASS, "Weight value matches postScriptName."


# DEPRECATED: com.google.fonts/check/114
#
# == Rationale ==
# We need to assure coherence among the following pieces of info:
#
# (A) A given font canonical filename;
# (B) Its ttFont["OS/2"].usWeightClass;
# (C) The METADATA.pb font.weight field;
# (D) Its name table entries.
#
# - Canonical filenames (A) are treated as the source of truth.
# - com.google.fonts/check/001:  Makes sure (A) is good.
# - com.google.fonts/check/020:  (B) is tied to (A)
# - com.google.fonts/check/112:  (C) is tied to (B)
# - multiple name table checks are crafted to tie (D) to (A)
#
# The original implementation of com.google.fonts/check/114
# had a convoluted check linking together (B), (C) and (D).
# That was a complex and error-prone implementation.
#
# Given checks 001, 020 and 112 discussed above,
# it is clear that check/114 is redundant and thus
# can be safely deprecated.


@register_check
@check(
    id = 'com.google.fonts/check/115'
  , conditions=['font_metadata']
)
def com_google_fonts_check_115(ttFont, font_metadata):
  """Font styles are named canonically ?"""
  from fontbakery.constants import MACSTYLE_ITALIC

  def find_italic_in_name_table():
    for entry in ttFont["name"].names:
      if "italic" in entry.string.decode(entry.getEncoding()).lower():
        return True
    return False

  def is_italic():
    return (ttFont["head"].macStyle & MACSTYLE_ITALIC or
            ttFont["post"].italicAngle or
            find_italic_in_name_table())

  if font_metadata.style not in ["italic", "normal"]:
    yield SKIP, ("This check only applies to font styles declared"
                 " as \"italic\" or \"regular\" on METADATA.pb.")
  else:
    if is_italic() and font_metadata.style != "italic":
      yield FAIL, ("The font style is {}"
                   " but it should be italic").format(font_metadata.style)
    elif not is_italic() and font_metadata.style != "normal":
      yield FAIL, ("The font style is {}"
                   " but it should be normal").format(font_metadata.style)
    else:
      yield PASS, "Font styles are named canonically."


@register_check
@check(
    id = 'com.google.fonts/check/116'
)
def com_google_fonts_check_116(ttFont):
  """Is font em size (ideally) equal to 1000 ?"""
  upm_height = ttFont["head"].unitsPerEm
  if upm_height != 1000:
    yield WARN, ("Font em size ({}) is not"
                 " equal to 1000.").format(upm_height)
  else:
    yield PASS, "Font em size is equal to 1000."


@register_condition
@condition
def remote_styles(metadata):
  """Get a dictionary of TTFont objects of all font files of
     a given family as currently hosted at Google Fonts."""

  def download_family_from_Google_Fonts(family_name):
    """Return a zipfile containing a font family hosted on fonts.google.com"""
    from zipfile import ZipFile
    from fontbakery.utils import download_file
    url_prefix = 'https://fonts.google.com/download?family='
    url = '%s%s' % (url_prefix, family_name.replace(' ', '+'))
    return ZipFile(download_file(url))

  def fonts_from_zip(zipfile):
    '''return a list of fontTools TTFonts'''
    from fontTools.ttLib import TTFont
    fonts = []
    for file_name in zipfile.namelist():
      if file_name.endswith(".ttf"):
        fonts.append([file_name, TTFont(zipfile.open(file_name))])
    return fonts

  from zipfile import BadZipfile

  if (not listed_on_gfonts_api or
      not metadata):
    return None

  try:
    remote_fonts_zip = download_family_from_Google_Fonts(metadata.name)
    rstyles = {}

    for remote_filename, remote_font in fonts_from_zip(remote_fonts_zip):
      if '-' in remote_filename[:-4]:
        remote_style = remote_filename[:-4].split('-')[1]
      rstyles[remote_style] = remote_font
    return rstyles
  except IOError:
    return None
  except BadZipfile:
    return None

@register_condition
@condition
def gfonts_ttFont(style, remote_styles):
  """Get a TTFont object of a font downloaded from Google Fonts
     corresponding to the given TTFont object of
     a local font being checked."""
  if remote_styles and style in remote_styles:
    return remote_styles[style]

@register_check
@check(
    id = 'com.google.fonts/check/117'
  , conditions=['gfonts_ttFont']
)
def com_google_fonts_check_117(ttFont, gfonts_ttFont):
  """Version number has increased since previous release on Google Fonts?"""
  v_number = ttFont["head"].fontRevision
  gfonts_v_number = gfonts_ttFont["head"].fontRevision
  if v_number == gfonts_v_number:
    yield FAIL, ("Version number {} is equal to"
                 " version on Google Fonts.").format(v_number)
  elif v_number < gfonts_v_number:
    yield FAIL, ("Version number {} is less than"
                 " version on Google Fonts ({}).").format(v_number,
                                                          gfonts_v_number)
  else:
    yield PASS, ("Version number {} is greater than"
                 " version on Google Fonts ({}).").format(v_number,
                                                          gfonts_v_number)

@register_check
@check(
    id = 'com.google.fonts/check/118'
  , conditions=['gfonts_ttFont']
)
def com_google_fonts_check_118(ttFont, gfonts_ttFont):
  """Glyphs are similiar to Google Fonts version ?"""

  def glyphs_surface_area(ttFont):
    """Calculate the surface area of a glyph's ink"""
    from fontTools.pens.areaPen import AreaPen
    glyphs = {}
    glyph_set = ttFont.getGlyphSet()
    area_pen = AreaPen(glyph_set)

    for glyph in glyph_set.keys():
      glyph_set[glyph].draw(area_pen)

      area = area_pen.value
      area_pen.value = 0
      glyphs[glyph] = area
    return glyphs

  bad_glyphs = []
  these_glyphs = glyphs_surface_area(ttFont)
  gfonts_glyphs = glyphs_surface_area(gfonts_ttFont)

  shared_glyphs = set(these_glyphs) & set(gfonts_glyphs)

  this_upm = ttFont['head'].unitsPerEm
  gfonts_upm = gfonts_ttFont['head'].unitsPerEm

  for glyph in shared_glyphs:
    # Normalize area difference against comparison's upm
    this_glyph_area = (these_glyphs[glyph] / this_upm) * gfonts_upm
    gfont_glyph_area = (gfonts_glyphs[glyph] / gfonts_upm) * this_upm

    if abs(this_glyph_area - gfont_glyph_area) > 7000:
      bad_glyphs.append(glyph)

  if bad_glyphs:
    yield WARN, ("Following glyphs differ greatly from"
                 " Google Fonts version: [{}]").format(", ".join(bad_glyphs))
  else:
    yield PASS, ("Glyphs are similar in"
                 " comparison to the Google Fonts version.")


@register_check
@check(
    id = 'com.google.fonts/check/119'
  , conditions=['gfonts_ttFont']
)
def com_google_fonts_check_119(ttFont, gfonts_ttFont):
  """TTFAutohint x-height increase value is same as in
     previous release on Google Fonts ?"""

  def ttfauto_fpgm_xheight_rounding(fpgm_tbl, which):
    """Find the value from the fpgm table which controls ttfautohint's
    increase xheight parameter, '--increase-x-height'.
    This implementation is based on ttfautohint v1.6.

    This function has been tested on every font in the fonts/google repo
    which has an fpgm table. Results have been stored in a spreadsheet:
    http://tinyurl.com/jmlfmh3

    For more information regarding the fpgm table read:
    http://tinyurl.com/jzekfyx"""
    import re
    fpgm_tbl = '\n'.join(fpgm_tbl)
    xheight_pattern = r'(MPPEM\[ \].*\nPUSHW\[ \].*\n)([0-9]{1,5})'
    warning = None
    try:
      xheight_val = int(re.search(xheight_pattern, fpgm_tbl).group(2))
    except AttributeError:
      warning = ("No instruction for xheight rounding found"
                 " on the {} font").format(which)
      xheight_val = None
    return (warning, xheight_val)

  inc_xheight = None
  gf_inc_xheight = None

  if "fpgm" in ttFont:
    fpgm_tbl = ttFont["fpgm"].program.getAssembly()
    msg, inc_xheight = \
      ttfauto_fpgm_xheight_rounding(fpgm_tbl, "this fontfile")
    if msg: yield WARN, msg

  if 'fpgm' in gfonts_ttFont:
    gfonts_fpgm_tbl = gfonts_ttFont["fpgm"].program.getAssembly()
    warn, gf_inc_xheight = \
      ttfauto_fpgm_xheight_rounding(gfonts_fpgm_tbl, "GFonts release")
    if msg: yield WARN, msg

  if inc_xheight != gf_inc_xheight:
    yield FAIL, ("TTFAutohint --increase-x-height is {}. "
                 "It should match the previous"
                 " version's value ({}).").format(inc_xheight,
                                                  gf_inc_xheight)
  else:
    yield PASS, ("TTFAutohint --increase-x-height is the same as in"
                  " the previous Google Fonts release ({}).").format(inc_xheight)

# The following upstream font project checks have been DEPRECATED:
# com.google.fonts/check/120 "Each font in family project has matching glyph names ?"
# com.google.fonts/check/121 "Glyphs have same number of contours across family ?"
# com.google.fonts/check/122 "Glyphs have same number of points across family ?"
# com.google.fonts/check/123 "Does this font folder contain COPYRIGHT file ?"
# com.google.fonts/check/124 "Does this font folder contain a DESCRIPTION file ?"
# com.google.fonts/check/125 "Does this font folder contain licensing files ?"
# com.google.fonts/check/126 "Does font folder contain FONTLOG.txt ?"
# com.google.fonts/check/127 "Repository contains METADATA.pb file ?"
# com.google.fonts/check/128 "Copyright notice is consistent across all fonts in this family ?"

@register_check
@check(
    id = 'com.google.fonts/check/129'
  , conditions=['style']
)
def com_google_fonts_check_129(ttFont, style):
  """Checking OS/2 fsSelection value."""
  from fontbakery.utils import check_bit_entry
  from fontbakery.constants import (STYLE_NAMES,
                                    RIBBI_STYLE_NAMES,
                                    FSSEL_REGULAR,
                                    FSSEL_ITALIC,
                                    FSSEL_BOLD)

  # Checking fsSelection REGULAR bit:
  expected = "Regular" in style or \
             (style in STYLE_NAMES and
              style not in RIBBI_STYLE_NAMES and
              "Italic" not in style)
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FSSEL_REGULAR,
                        bitname="REGULAR")

  # Checking fsSelection ITALIC bit:
  expected = "Italic" in style
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FSSEL_ITALIC,
                        bitname="ITALIC")

  # Checking fsSelection BOLD bit:
  expected = style in ["Bold", "BoldItalic"]
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FSSEL_BOLD,
                        bitname="BOLD")


@register_check
@check(
    id = 'com.google.fonts/check/130'
  , conditions=['style']
)
def com_google_fonts_check_130(ttFont, style):
  """Checking post.italicAngle value."""
  failed = False
  value = ttFont["post"].italicAngle

  # Checking that italicAngle <= 0
  if value > 0:
    failed = True
    yield FAIL, ("The value of post.italicAngle must be"
                " changed from {} to {}.").format(value, -value)

  # Checking that italicAngle is less than 20 degrees:
  if abs(value) > 20:
    failed = True
    yield FAIL, ("The value of post.italicAngle must be"
                 " changed from {} to -20.").format(value)

  # Checking if italicAngle matches font style:
  if "Italic" in style:
    if ttFont['post'].italicAngle == 0:
      failed = True
      yield FAIL, ("Font is italic, so post.italicAngle"
                   " should be non-zero.")
  else:
    if ttFont["post"].italicAngle != 0:
      failed = True
      yield FAIL, ("Font is not italic, so post.italicAngle"
                   " should be equal to zero.")

  if not failed:
    yield PASS, "Value of post.italicAngle is {}.".format(value)


@register_check
@check(
    id = 'com.google.fonts/check/131'
  , conditions=['style']
)
def com_google_fonts_check_131(ttFont, style):
  """Checking head.macStyle value."""
  from fontbakery.utils import check_bit_entry
  from fontbakery.constants import (MACSTYLE_ITALIC,
                                    MACSTYLE_BOLD)
  # Checking macStyle ITALIC bit:
  expected = "Italic" in style
  yield check_bit_entry(ttFont, "head", "macStyle",
                        expected,
                        bitmask=MACSTYLE_ITALIC,
                        bitname="ITALIC")

  # Checking macStyle BOLD bit:
  expected = style in ["Bold", "BoldItalic"]
  yield check_bit_entry(ttFont, "head", "macStyle",
                        expected,
                        bitmask=MACSTYLE_BOLD,
                        bitname="BOLD")

# DEPRECATED CHECKS:
# com.google.fonts/check/132 - "Checking Cyrillic Historical glyph coverage."
# com.google.fonts/check/133 - "Checking Google Cyrillic Plus glyph coverage."
# com.google.fonts/check/134 - "Checking Google Cyrillic Plus (Localized Forms) glyph coverage."
# com.google.fonts/check/135 - "Checking Google Cyrillic Pro glyph coverage."
# com.google.fonts/check/136 - "Checking Google Greek Ancient Musical Symbols glyph coverage."
# com.google.fonts/check/137 - "Checking Google Greek Archaic glyph coverage."
# com.google.fonts/check/138 - "Checking Google Greek Coptic glyph coverage."
# com.google.fonts/check/139 - "Checking Google Greek Core glyph coverage."
# com.google.fonts/check/140 - "Checking Google Greek Expert glyph coverage."
# com.google.fonts/check/141 - "Checking Google Greek Plus glyph coverage."
# com.google.fonts/check/142 - "Checking Google Greek Pro glyph coverage."
# com.google.fonts/check/143 - "Checking Google Latin Core glyph coverage."
# com.google.fonts/check/144 - "Checking Google Latin Expert glyph coverage."
# com.google.fonts/check/145 - "Checking Google Latin Plus glyph coverage."
# com.google.fonts/check/146 - "Checking Google Latin Plus (Optional Glyphs) glyph coverage."
# com.google.fonts/check/147 - "Checking Google Latin Pro glyph coverage."
# com.google.fonts/check/148 - "Checking Google Latin Pro (Optional Glyphs) glyph coverage."
# com.google.fonts/check/149 - "Checking Google Arabic glyph coverage."
# com.google.fonts/check/150 - "Checking Google Vietnamese glyph coverage."
# com.google.fonts/check/151 - "Checking Google Extras glyph coverage."

@register_check
@check(
    id = 'com.google.fonts/check/152'
)
def com_google_fonts_check_152(ttFont):
  """Name table strings must not contain 'Reserved Font Name'."""
  failed = False
  for entry in ttFont["name"].names:
    string = entry.string.decode(entry.getEncoding())
    if "reserved font name" in string.lower():
      yield WARN, ("Name table entry (\"{}\")"
                   " contains \"Reserved Font Name\"."
                   " This is an error except in a few specific"
                   " rare cases.").format(string)
      failed = True
  if not failed:
    yield PASS, ("None of the name table strings"
                 " contain \"Reserved Font Name\".")


@register_check
@check(
    id = 'com.google.fonts/check/153'
  , rationale = """
      Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
      be constructured in a handful of ways. This means a glyph's contour count
      will only differ slightly amongst different fonts, e.g a 'g' could either
      be 2 or 3 contours, depending on whether its double story or single story.
      However, a quotedbl should have 2 contours, unless the font belongs to a
      display family.
    """
)
def com_google_fonts_check_153(ttFont):
  """Check if each glyph has the recommended amount of contours.

  This check is useful to assure glyphs aren't incorrectly constructed.

  The desired_glyph_data module contains the 'recommended' countour count
  for encoded glyphs. The contour counts are derived from fonts which were
  chosen for their quality and unique design decisions for particular glyphs.

  In the future, additional glyph data can be included. A good addition would
  be the 'recommended' anchor counts for each glyph.
  """
  from fontbakery.glyphdata import desired_glyph_data as glyph_data
  from fontbakery.utils import (get_font_glyph_data,
                                pretty_print_list)
  from fontbakery.constants import (PLATFORM_ID__WINDOWS,
                                    PLAT_ENC_ID__UCS2)
  # rearrange data structure:
  desired_glyph_data = {}
  for glyph in glyph_data:
    desired_glyph_data[glyph['unicode']] = glyph

  bad_glyphs = []
  desired_glyph_contours = {f: desired_glyph_data[f]['contours']
                            for f in desired_glyph_data}

  font_glyph_data = get_font_glyph_data(ttFont)

  if font_glyph_data is None:
      yield FAIL, "This font lacks cmap data."
  else:
    font_glyph_contours = {f['unicode']: list(f['contours'])[0]
                           for f in font_glyph_data}

    shared_glyphs = set(desired_glyph_contours) & set(font_glyph_contours)
    for glyph in shared_glyphs:
      if font_glyph_contours[glyph] not in desired_glyph_contours[glyph]:
        bad_glyphs.append([glyph,
                           font_glyph_contours[glyph],
                           desired_glyph_contours[glyph]])

    if len(bad_glyphs) > 0:
      cmap = ttFont['cmap'].getcmap(PLATFORM_ID__WINDOWS,
                                    PLAT_ENC_ID__UCS2).cmap
      bad_glyphs_name = [("Glyph name: {}\t"
                          "Counters detected: {}\t"
                          "Expected: {}").format(cmap[name],
                                                 count,
                                                 pretty_print_list(expected))
                         for name, count, expected in bad_glyphs]
      yield WARN, (("This check inspects the glyph outlines and detects the"
                    " total number of counters in each of them. The expected"
                    " values are infered from the typical ammounts of"
                    " counters observed in a large collection of reference"
                    " font families. The divergences listed below may simply"
                    " indicate a significantly different design on some of"
                    " your glyphs. On the other hand, some of these may flag"
                    " actual bugs in the font such as glyphs mapped to an"
                    " incorrect codepoint. Please consider reviewing"
                    " the design and codepoint assignment of these to make"
                    " sure they are correct.\n"
                    "\n"
                    "The following glyphs do not have the recommended"
                    " number of contours:\n"
                    "\n{}").format('\n'.join(bad_glyphs_name)))
    else:
      yield PASS, "All glyphs have the recommended amount of contours"


@register_check
@check(
    id = 'com.google.fonts/check/154'
  , conditions=['gfonts_ttFont']
)
def com_google_fonts_check_154(ttFont, gfonts_ttFont):
  """Check font has same encoded glyphs as version hosted on
  fonts.google.com"""
  cmap = ttFont['cmap'].getcmap(3, 1).cmap
  gf_cmap = gfonts_ttFont['cmap'].getcmap(3, 1).cmap
  missing_codepoints = set(gf_cmap.keys()) - set(cmap.keys())

  if missing_codepoints:
    hex_codepoints = ['0x' + hex(c).upper()[2:].zfill(4) for c
                      in missing_codepoints]
    yield FAIL, ("Font is missing the following glyphs"
                 " from the previous release"
                 " [{}]").format(', '.join(hex_codepoints))
  else:
    yield PASS, ('Font has all the glyphs from the previous release')


@register_check
@check(
    id = 'com.google.fonts/check/155'
  , conditions=['font_metadata']
)
def com_google_fonts_check_155(ttFont, font_metadata):
  """Copyright field for this font on METADATA.pb matches
     all copyright notice entries on the name table ?"""
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE
  from unidecode import unidecode
  failed = False
  for nameRecord in ttFont['name'].names:
    string = nameRecord.string.decode(nameRecord.getEncoding())
    if nameRecord.nameID == NAMEID_COPYRIGHT_NOTICE and\
       string != font_metadata.copyright:
        failed = True
        yield FAIL, ("Copyright field for this font on METADATA.pb ('{}')"
                     " differs from a copyright notice entry"
                     " on the name table:"
                     " '{}'").format(font_metadata.copyright,
                                     unidecode(string))
  if not failed:
    yield PASS, ("Copyright field for this font on METADATA.pb matches"
                 " copyright notice entries on the name table.")


@register_condition
@condition
def familyname(ttFont):
  filename = os.path.split(ttFont.reader.file.name)[1]
  filename_base = os.path.splitext(filename)[0]
  return filename_base.split('-')[0]


@register_condition
@condition
def familyname_with_spaces(ttFont):
  FAMILY_WITH_SPACES_EXCEPTIONS = {'VT323': 'VT323',
                                   'PressStart2P': 'Press Start 2P',
                                   'ABeeZee': 'ABeeZee'}
  fname = familyname(ttFont)
  if fname in FAMILY_WITH_SPACES_EXCEPTIONS.keys():
    return FAMILY_WITH_SPACES_EXCEPTIONS[fname]

  result = ''
  for c in fname:
    if c.isupper():
      result += " "
    result += c
  result = result.strip()

  if result[-3:] == "S C":
    return result[:-3] + "SC"
  else:
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


@register_check
@check(
    id = 'com.google.fonts/check/156'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_156(ttFont, style):
  """Font has all mandatory 'name' table entries ?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (RIBBI_STYLE_NAMES,
                                    NAMEID_STR,
                                    NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    NAMEID_FULL_FONT_NAME,
                                    NAMEID_POSTSCRIPT_NAME,
                                    NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                    NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
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
    if len(get_name_entry_strings(ttFont, nameId)) == 0:
      failed = True
      yield FAIL, ("Font lacks entry with"
                   " nameId={} ({})").format(nameId,
                                             NAMEID_STR[nameId])
  if not failed:
    yield PASS, "Font contains values for all mandatory name table entries."


@register_check
@check(
    id = 'com.google.fonts/check/157'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_157(ttFont, style, familyname_with_spaces):
  """ Check name table: FONT_FAMILY_NAME entries. """
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    PLATFORM_ID__MACINTOSH,
                                    PLATFORM_ID__WINDOWS)
  failed = False
  only_weight = get_only_weight(style)
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_FONT_FAMILY_NAME:

      if name.platformID == PLATFORM_ID__MACINTOSH:
        expected_value = familyname_with_spaces

      elif name.platformID == PLATFORM_ID__WINDOWS:
        if style in ['Regular',
                     'Italic',
                     'Bold',
                     'Bold Italic']:
          expected_value = familyname_with_spaces
        else:
          expected_value = " ".join([familyname_with_spaces,
                                     only_weight]).strip()
      else:
        failed = True
        yield FAIL, ("Font should not have a "
                     "{} entry!").format(name_entry_id(name))
        continue

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        yield FAIL, ("Entry {} on the 'name' table: "
                     "Expected '{}' "
                     "but got '{}'.").format(name_entry_id(name),
                                             expected_value,
                                             string)
  if not failed:
    yield PASS, "FONT_FAMILY_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/158'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_158(ttFont, style, familyname_with_spaces):
  """ Check name table: FONT_SUBFAMILY_NAME entries. """
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import (NAMEID_FONT_SUBFAMILY_NAME,
                                    PLATFORM_ID__MACINTOSH,
                                    PLATFORM_ID__WINDOWS,
                                    STYLE_NAMES)
  failed = False
  only_weight = get_only_weight(style)
  style_with_spaces = style.replace('Italic',
                                    ' Italic').strip()
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_FONT_SUBFAMILY_NAME:
      if style_with_spaces not in STYLE_NAMES:
        yield FAIL, ("Style name '{}' inferred from filename"
                     " is not canonical."
                     " Valid options are: {}").format(style_with_spaces,
                                                      STYLE_NAMES)
        failed = True
        continue

      if name.platformID == PLATFORM_ID__MACINTOSH:
        expected_value = style_with_spaces

      elif name.platformID == PLATFORM_ID__WINDOWS:
        if style_with_spaces in ["Bold", "Bold Italic"]:
          expected_value = style_with_spaces
        else:
          if "Italic" in style:
            expected_value = "Italic"
          else:
            expected_value = "Regular"
      else:
        yield FAIL, ("Font should not have a "
                     "{} entry!").format(name_entry_id(name))
        failed = True
        continue

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        yield FAIL, ("Entry {} on the 'name' table: "
                     "Expected '{}' "
                     "but got '{}'.").format(name_entry_id(name),
                                             expected_value,
                                             string)

  if not failed:
    yield PASS, "FONT_SUBFAMILY_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/159'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_159(ttFont, style, familyname_with_spaces):
  """ Check name table: FULL_FONT_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import NAMEID_FULL_FONT_NAME
  failed = False
  style_with_spaces = style.replace('Italic',
                                    ' Italic').strip()
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_FULL_FONT_NAME:
      expected_value = "{} {}".format(familyname_with_spaces,
                                      style_with_spaces)
      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        # special case
        # see https://github.com/googlefonts/fontbakery/issues/1436
        if style == "Regular" \
           and string == familyname_with_spaces:
          yield WARN, ("Entry {} on the 'name' table:"
                       " Got '{}' which lacks 'Regular',"
                       " but it is probably OK in this case."
                       "").format(name_entry_id(name),
                                  unidecode(string))
        else:
          yield FAIL, ("Entry {} on the 'name' table: "
                       "Expected '{}' "
                       "but got '{}'.").format(name_entry_id(name),
                                               expected_value,
                                               unidecode(string))
  if not failed:
    yield PASS, "FULL_FONT_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/160'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_160(ttFont, style, familyname):
  """ Check name table: POSTSCRIPT_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import NAMEID_POSTSCRIPT_NAME

  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_POSTSCRIPT_NAME:
      expected_value = "{}-{}".format(familyname, style)

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        yield FAIL, ("Entry {} on the 'name' table: "
                     "Expected '{}' "
                     "but got '{}'.").format(name_entry_id(name),
                                             expected_value,
                                             unidecode(string))
  if not failed:
    yield PASS, "POSTCRIPT_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/161'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_161(ttFont, style, familyname_with_spaces):
  """ Check name table: TYPOGRAPHIC_FAMILY_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import NAMEID_TYPOGRAPHIC_FAMILY_NAME

  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_TYPOGRAPHIC_FAMILY_NAME:
      if style in ['Regular',
                   'Italic',
                   'Bold',
                   'Bold Italic']:
        yield WARN, ("Font style is '{}' and, for that reason,"
                     " it is not expected to have a "
                     "{} entry!").format(style,
                                         name_entry_id(name))
      else:
        expected_value = familyname_with_spaces

        string = name.string.decode(name.getEncoding()).strip()
        if string != expected_value:
          failed = True
          yield FAIL, ("Entry {} on the 'name' table: "
                       "Expected '{}' "
                       "but got '{}'.").format(name_entry_id(name),
                                               expected_value,
                                               unidecode(string))
  if not failed:
    yield PASS, "TYPOGRAPHIC_FAMILY_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/162'
  , priority=IMPORTANT
  , conditions=['style']
)
def com_google_fonts_check_162(ttFont, style):
  """ Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME

  failed = False
  style_with_spaces = style.replace('Italic',
                                    ' Italic').strip()
  for name in ttFont['name'].names:
    if name.nameID == NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME:
      if style in ['Regular',
                   'Italic',
                   'Bold',
                   'Bold Italic']:
        yield WARN, ("Font style is '{}' and, for that reason,"
                     " it is not expected to have a "
                     "{} entry!").format(style,
                                         name_entry_id(name))
      else:
        expected_value = style_with_spaces

        string = name.string.decode(name.getEncoding()).strip()
        if string != expected_value:
          failed = True
          yield FAIL, ("Entry {} on the 'name' table: "
                       "Expected '{}' "
                       "but got '{}'.").format(name_entry_id(name),
                                               expected_value,
                                               unidecode(string))
  if not failed:
    yield PASS, "TYPOGRAPHIC_SUBFAMILY_NAME entries are all good."


@register_check
@check(
    id = 'com.google.fonts/check/163'
  , rationale = """
      According to a Glyphs tutorial (available at
      https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances),
      in order to make sure all versions of Windows recognize it as a valid
      font file, we must make sure that the concatenated length of the
      familyname (NAMEID_FONT_FAMILY_NAME) and style (NAMEID_FONT_SUBFAMILY_NAME)
      strings in the name table do not exceed 20 characters.
    """ # Somebody with access to Windows should make some experiments
        # and confirm that this is really the case.
  , affects = [('Windows', 'unspecified')]
  , request = 'https://github.com/googlefonts/fontbakery/issues/1488'
  , example_failures = None
)
def com_google_fonts_check_163(ttFont):
  """ Combined length of family and style must not exceed 20 characters. """
  from unidecode import unidecode
  from fontbakery.utils import (get_name_entries,
                                get_name_entry_strings)
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME,
                                    PLATID_STR)
  failed = False
  for familyname in get_name_entries(ttFont, NAMEID_FONT_FAMILY_NAME):
    # we'll only match family/style name entries with the same platform ID:
    plat = familyname.platformID
    familyname_str = familyname.string.decode(familyname.getEncoding())
    for stylename_str in get_name_entry_strings(ttFont,
                                                NAMEID_FONT_SUBFAMILY_NAME,
                                                platformID=plat):
      if len(familyname_str + stylename_str) > 20:
        failed = True
        yield WARN, ("The combined length of family and style"
                     " exceeds 20 chars in the following '{}' entries:"
                     " FONT_FAMILY_NAME = '{}' / SUBFAMILY_NAME = '{}'"
                     "").format(PLATID_STR[plat],
                                unidecode(familyname_str),
                                unidecode(stylename_str))
  if not failed:
    yield PASS, "All name entries are good."


@register_check
@check(
    id = 'com.google.fonts/check/164'
  , rationale = """
      This is an arbitrary max lentgh for the copyright notice field
      of the name table. We simply don't want such notices to be too long.
      Typically such notices are actually much shorter than this with
      a lenghth of roughtly 70 or 80 characters.
    """
  , request = 'https://github.com/googlefonts/fontbakery/issues/1603'
)
def com_google_fonts_check_164(ttFont):
  """ Length of copyright notice must not exceed 500 characters. """
  from unidecode import unidecode
  from fontbakery.utils import get_name_entries
  from fontbakery.constants import NAMEID_COPYRIGHT_NOTICE

  failed = False
  for notice in get_name_entries(ttFont, NAMEID_COPYRIGHT_NOTICE):
    notice_str = notice.string.decode(notice.getEncoding())
    if len(notice_str) > 500:
        failed = True
        yield FAIL, ("The length of the following copyright notice ({})"
                     " exceeds 500 chars: '{}'"
                     "").format(len(notice_str),
                                unidecode(notice_str))
  if not failed:
    yield PASS, ("All copyright notice name entries on the"
                 " 'name' table are shorter than 500 characters.")

FB_ISSUE_TRACKER = "https://github.com/googlefonts/fontbakery/issues"
@register_check
@check(
    id = 'com.google.fonts/check/165'
  , rationale = """
      We need to check names are not already used, and today the best
      place to check that is http://namecheck.fontdata.com
    """
  , request = 'https://github.com/googlefonts/fontbakery/issues/494'
  , conditions = ["familyname"]
)
def com_google_fonts_check_165(ttFont, familyname):
  """ Familyname must be unique according to namecheck.fontdata.com """
  import requests
  url = "http://namecheck.fontdata.com/?q={}".format(familyname)
  try:
    response = requests.get(url, timeout=10)
    data = response.content.decode("utf-8")
    if "fonts by that exact name" in data:
      yield INFO, ("The family name '{}' seem to be already in use.\n"
                   "Please visit {} for more info.").format(familyname, url)
    else:
      yield PASS, "Font familyname seems to be unique."
  except:
    yield ERROR, ("Failed to access: '{}'.\n"
                  "Please report this issue at:\n{}").format(url,
                                                             FB_ISSUE_TRACKER)


@register_check
@check(
    id = 'com.google.fonts/check/166'
  , rationale = """
      The git sha1 tagging and dev/release features of Source Foundry font-v
       tool are awesome and we would love to consider upstreaming the approach
       into fontmake someday. For now we only emit a WARN if a given font does
       not yet follow the experimental versionin style, but at some point we
       may start enforcing it.
    """
  , request = 'https://github.com/googlefonts/fontbakery/issues/1563'
)
def com_google_fonts_check_166(ttFont):
  """ Check for font-v versioning """
  from fontv.libfv import FontVersion

  fv = FontVersion(ttFont)
  if fv.version and (fv.is_development or fv.is_release):
    yield PASS, "Font version string looks GREAT!"
  else:
    yield INFO, ("Version string is: \"{}\"\n"
                 "The version string must ideally include a git commit hash"
                 " and eigther a 'dev' or a 'release' suffix such as in the"
                 " example below:\n"
                 "\"Version 1.3; git-0d08353-release\""
                 "").format(fv.get_version_string())


for section_name, section in specification._sections.items():
  print ("There is a total of {} checks on {}.".format(len(section._checks), section_name))
