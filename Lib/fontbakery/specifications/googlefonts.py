# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from future import standard_library
standard_library.install_aliases()
from builtins import (str, map, hex, range)


from fontbakery.checkrunner import (
              INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , Section
            )
import os
from fontbakery.callable import condition, check, disable
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
from fontbakery.fonts_spec import spec_factory

spec_imports = (
    ('.', ('general', 'cmap', 'head', 'os2', 'post', 'name',
       'hhea', 'dsig', 'hmtx', 'gpos', 'gdef', 'kern', 'glyf',
       'prep', 'fvar', 'shared_conditions', 'loca')
    ),
)

# this is from the output of
# $ fontbakery check-specification  fontbakery.specifications.googlefonts -L
expected_check_ids = [
        'com.google.fonts/check/001' # Checking file is named canonically.
      , 'com.google.fonts/check/002' # Checking all files are in the same directory.
      , 'com.google.fonts/check/003' # Does DESCRIPTION file contain broken links?
      , 'com.google.fonts/check/004' # Is this a propper HTML snippet?
      , 'com.google.fonts/check/005' # DESCRIPTION.en_us.html must have more than 200 bytes.
      , 'com.google.fonts/check/006' # DESCRIPTION.en_us.html must have less than 1000 bytes.
      , 'com.google.fonts/check/007' # Font designer field in METADATA.pb must not be 'unknown'.
      , 'com.google.fonts/check/008' # Fonts have consistent underline thickness?
      , 'com.google.fonts/check/009' # Fonts have consistent PANOSE proportion?
      , 'com.google.fonts/check/010' # Fonts have consistent PANOSE family type?
      , 'com.google.fonts/check/011' # Fonts have equal numbers of glyphs?
      , 'com.google.fonts/check/012' # Fonts have equal glyph names?
      , 'com.google.fonts/check/013' # Fonts have equal unicode encodings?
      , 'com.google.fonts/check/014' # Make sure all font files have the same version value.
      , 'com.google.fonts/check/015' # Font has post table version 2?
      , 'com.google.fonts/check/016' # Checking OS/2 fsType.
      , 'com.google.fonts/check/018' # Checking OS/2 achVendID.
      , 'com.google.fonts/check/019' # Substitute copyright, registered and trademark symbols in name table entries.
      , 'com.google.fonts/check/020' # Checking OS/2 usWeightClass.
      , 'com.google.fonts/check/028' # Check font has a license.
      , 'com.google.fonts/check/029' # Check copyright namerecords match license file.
      , 'com.google.fonts/check/030' # "License URL matches License text on name table?
      , 'com.google.fonts/check/031' # Description strings in the name table must not contain copyright info.
      , 'com.google.fonts/check/032' # Description strings in the name table must not exceed 100 characters.
      , 'com.google.fonts/check/033' # Checking correctness of monospaced metadata.
      , 'com.google.fonts/check/034' # Check if OS/2 xAvgCharWidth is correct.
      , 'com.google.fonts/check/035' # Checking with ftxvalidator.
      , 'com.google.fonts/check/036' # Checking with ots-sanitize.
      , 'com.google.fonts/check/037' # Checking with Microsoft Font Validator.
      , 'com.google.fonts/check/038' # FontForge validation outputs error messages?
      , 'com.google.fonts/check/039' # FontForge checks.
      , 'com.google.fonts/check/040' # Checking OS/2 usWinAscent & usWinDescent.
      , 'com.google.fonts/check/041' # Checking Vertical Metric Linegaps.
      , 'com.google.fonts/check/042' # Checking OS/2 Metrics match hhea Metrics.
      , 'com.google.fonts/check/043' # Checking unitsPerEm value is reasonable.
      , 'com.google.fonts/check/044' # Checking font version fields.
      , 'com.google.fonts/check/045' # Does the font have a DSIG table?
      , 'com.google.fonts/check/046' # Font contains the first few mandatory glyphs (.null or NULL, CR and space)?
      , 'com.google.fonts/check/047' # Font contains glyphs for whitespace characters?
      , 'com.google.fonts/check/048' # Font has **proper** whitespace glyph names?
      , 'com.google.fonts/check/049' # Whitespace glyphs have ink?
      , 'com.google.fonts/check/050' # Whitespace glyphs have coherent widths?
      , 'com.google.fonts/check/052' # Font contains all required tables?
      , 'com.google.fonts/check/053' # Are there unwanted tables?
      , 'com.google.fonts/check/054' # Show hinting filesize impact.
      , 'com.google.fonts/check/055' # Version format is correct in 'name' table?
      , 'com.google.fonts/check/056' # Font has old ttfautohint applied?
      , 'com.google.fonts/check/057' # Name table entries should not contain line-breaks.
      , 'com.google.fonts/check/058' # Glyph names are all valid?
      , 'com.google.fonts/check/059' # Font contains unique glyph names?
      , 'com.google.fonts/check/061' # EPAR table present in font?
      , 'com.google.fonts/check/062' # Is 'gasp' table correctly set?
      , 'com.google.fonts/check/063' # Does GPOS table have kerning information?
      , 'com.google.fonts/check/064' # Is there a caret position declared for every ligature?
      , 'com.google.fonts/check/065' # Is there kerning info for non-ligated sequences?
      , 'com.google.fonts/check/066' # Is there a "kern" table declared in the font?
      , 'com.google.fonts/check/067' # Make sure family name does not begin with a digit.
      , 'com.google.fonts/check/068' # Does full font name begin with the font family name?
      , 'com.google.fonts/check/069' # Is there any unused data at the end of the glyf table?
      , 'com.google.fonts/check/070' # Font has all expected currency sign characters?
      , 'com.google.fonts/check/071' # Font follows the family naming recommendations?
      , 'com.google.fonts/check/072' # Font enables smart dropout control in "prep" table instructions?
      , 'com.google.fonts/check/073' # MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?
      , 'com.google.fonts/check/074' # Are there non-ASCII characters in ASCII-only NAME table entries?
      , 'com.google.fonts/check/075' # Check for points out of bounds.
      , 'com.google.fonts/check/076' # Check glyphs have unique unicode codepoints.
      , 'com.google.fonts/check/077' # Check all glyphs have codepoints assigned.
      #, 'com.google.fonts/check/078' # Check that glyph names do not exceed max length.
      , 'com.google.fonts/check/079' # Monospace font has hhea.advanceWidthMax equal to each glyph's advanceWidth?
      , 'com.google.fonts/check/080' # METADATA.pb: Ensure designer simple short name.
      , 'com.google.fonts/check/081' # METADATA.pb: Fontfamily is listed on Google Fonts API?
      , 'com.google.fonts/check/083' # METADATA.pb: check if fonts field only has unique "full_name" values.
      , 'com.google.fonts/check/084' # METADATA.pb: check if fonts field only contains unique style:weight pairs.
      , 'com.google.fonts/check/085' # METADATA.pb license is "APACHE2", "UFL" or "OFL"?
      , 'com.google.fonts/check/086' # METADATA.pb should contain at least "menu" and "latin" subsets.
      , 'com.google.fonts/check/087' # METADATA.pb subsets should be alphabetically ordered.
      , 'com.google.fonts/check/088' # Copyright notice is the same in all fonts?
      , 'com.google.fonts/check/089' # Check that METADATA family values are all the same.
      , 'com.google.fonts/check/090' # According Google Fonts standards, families should have a Regular style.
      , 'com.google.fonts/check/091' # Regular should be 400.
      , 'com.google.fonts/check/092' # Checks METADATA.pb font.name field matches family name declared on the name table.
      , 'com.google.fonts/check/093' # Checks METADATA.pb font.post_script_name matches postscript name declared on the name table.
      , 'com.google.fonts/check/094' # METADATA.pb font.fullname value matches fullname declared on the name table?
      , 'com.google.fonts/check/095' # METADATA.pb font.name value should be same as the family name declared on the name table.
      , 'com.google.fonts/check/096' # METADATA.pb family.full_name and family.post_script_name fields have equivalent values ?
      , 'com.google.fonts/check/097' # METADATA.pb family.filename and family.post_script_name fields have equivalent values?
      , 'com.google.fonts/check/098' # METADATA.pb font.name field contains font name in right format?
      , 'com.google.fonts/check/099' # METADATA.pb font.full_name field contains font name in right format?
      , 'com.google.fonts/check/100' # METADATA.pb font.filename field contains font name in right format?
      , 'com.google.fonts/check/101' # METADATA.pb font.post_script_name field contains font name in right format?
      , 'com.google.fonts/check/102' # Copyright notice on METADATA.pb matches canonical pattern?
      , 'com.google.fonts/check/103' # Copyright notice on METADATA.pb does not contain Reserved Font Name?
      , 'com.google.fonts/check/104' # Copyright notice shouldn't exceed 500 chars.
      , 'com.google.fonts/check/105' # Filename is set canonically in METADATA.pb?
      , 'com.google.fonts/check/106' # METADATA.pb font.style "italic" matches font internals?
      , 'com.google.fonts/check/107' # METADATA.pb font.style "normal" matches font internals?
      , 'com.google.fonts/check/108' # METADATA.pb font.name and font.full_name fields match the values declared on the name table?
      , 'com.google.fonts/check/109' # Check if fontname is not camel cased.
      , 'com.google.fonts/check/110' # Check font name is the same as family name.
      , 'com.google.fonts/check/111' # Check that font weight has a canonical value.
      , 'com.google.fonts/check/112' # Checking OS/2 usWeightClass matches weight specified at METADATA.pb.
      , 'com.google.fonts/check/113' # Metadata weight matches postScriptName.
      , 'com.google.fonts/check/115' # Font styles are named canonically?
      , 'com.google.fonts/check/116' # Is font em size (ideally) equal to 1000?
      , 'com.google.fonts/check/117' # Version number has increased since previous release on Google Fonts?
      , 'com.google.fonts/check/118' # Glyphs are similiar to Google Fonts version?
      , 'com.google.fonts/check/119' # TTFAutohint x-height increase value is same as in previous release on Google Fonts ?
      , 'com.google.fonts/check/129' # Checking OS/2 fsSelection value.
      , 'com.google.fonts/check/130' # Checking post.italicAngle value.
      , 'com.google.fonts/check/131' # Checking head.macStyle value.
      , 'com.google.fonts/check/152' # Name table strings must not contain 'Reserved Font Name'.
      , 'com.google.fonts/check/153' # Check if each glyph has the recommended amount of contours.
      , 'com.google.fonts/check/154' # Check font has same encoded glyphs as version hosted on fonts.google.com
      , 'com.google.fonts/check/155' # Copyright field for this font on METADATA.pb matches all copyright notice entries on the name table ?
      , 'com.google.fonts/check/156' # Font has all mandatory 'name' table entries ?
      , 'com.google.fonts/check/157' # Check name table: FONT_FAMILY_NAME entries.
      , 'com.google.fonts/check/158' # Check name table: FONT_SUBFAMILY_NAME entries.
      , 'com.google.fonts/check/159' # Check name table: FULL_FONT_NAME entries.
      , 'com.google.fonts/check/160' # Check name table: POSTSCRIPT_NAME entries.
      , 'com.google.fonts/check/161' # Check name table: TYPOGRAPHIC_FAMILY_NAME entries.
      , 'com.google.fonts/check/162' # Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries.
      , 'com.google.fonts/check/163' # Combined length of family and style must not exceed 20 characters.
      , 'com.google.fonts/check/164' # Length of copyright notice must not exceed 500 characters.
      , 'com.google.fonts/check/165' # Familyname must be unique according to namecheck.fontdata.com
      , 'com.google.fonts/check/166' # Check for font-v versioning
      , 'com.google.fonts/check/167' # The variable font 'wght' (Weight) axis coordinate must be 400 on the 'Regular' instance.
      , 'com.google.fonts/check/168' # The variable font 'wdth' (Width) axis coordinate must be 100 on the 'Regular' instance.
      , 'com.google.fonts/check/169' # The variable font 'slnt' (Slant) axis coordinate must be zero on the 'Regular' instance.
      , 'com.google.fonts/check/170' # The variable font 'ital' (Italic) axis coordinate must be zero on the 'Regular' instance.
      , 'com.google.fonts/check/171' # The variable font 'opsz' (Optical Size) axis coordinate should be between 9 and 13 on the 'Regular' instance.
      , 'com.google.fonts/check/172' # The variable font 'wght' (Weight) axis coordinate must be 700 on the 'Bold'
      , 'com.google.fonts/check/174' # Check a static ttf can be generated from a variable font.
      , 'com.google.fonts/check/180' # Does the number of glyphs in the loca table match the maxp table?
]

specification = spec_factory(default_section=Section("Google Fonts"))


# -------------------------------------------------------------------

@condition
def style(font):
  """Determine font style from canonical filename."""
  from fontbakery.constants import STYLE_NAMES
  filename = os.path.basename(font)
  if '-' in filename:
    stylename = os.path.splitext(filename)[0].split('-')[1]
    if stylename in [name.replace(' ', '') for name in STYLE_NAMES]:
      return stylename
  return None


@condition(force=True)
def expected_os2_weight(style):
  """The weight name and the expected OS/2 usWeightClass value inferred from
  the style part of the font name

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
  if not style:
    return None
  # Weight name to value mapping:
  GF_API_WEIGHTS = {
      "Thin": 250,
      "ExtraLight": 275,
      "Light": 300,
      "Regular": 400,
      "Medium": 500,
      "SemiBold": 600,
      "Bold": 700,
      "ExtraBold": 800,
      "Black": 900
  }
  if style == "Italic":
    weight_name = "Regular"
  elif style.endswith("Italic"):
    weight_name = style.replace("Italic", "")
  else:
    weight_name = style

  expected = GF_API_WEIGHTS[weight_name]
  return weight_name, expected


@condition(force=True)
def os2_weight_warn():
  return {"style": "ExtraLight",
          "value": 250,
          "message": ("A value of 250 for OS/2 usWeightClass is acceptable for TTFs"
                      " (but not for OTFs), because it won't auto-bold (and blur)"
                      " in Windows GDI apps. However, since OTFs will, and because"
                      " we'd like to have OTFs and TTFs be as consistent as possible,"
                      " we'd prefer ExtraLight to be 275 in both cases.")}


@check(
  id = 'com.google.fonts/check/001',
  misc_metadata = {
    'priority': CRITICAL
  }
)
def com_google_fonts_check_001(font):
  """Checking file is named canonically.

  A font's filename must be composed in the following manner:
  <familyname>-<stylename>.ttf

  e.g Nunito-Regular.ttf, Oswald-BoldItalic.ttf
  """
  from fontbakery.constants import STYLE_NAMES

  filename = os.path.basename(font)
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


@condition
def family_directory(fonts):
  """Get the path of font project directory."""
  if fonts:
    return os.path.dirname(fonts[0])


@condition
def descfile(family_directory):
  """Get the path of the DESCRIPTION file of a given font project."""
  if family_directory:
    descfilepath = os.path.join(family_directory, "DESCRIPTION.en_us.html")
    if os.path.exists(descfilepath):
      return descfilepath


@condition
def description(descfile):
  """Get the contents of the DESCRIPTION file of a font project."""
  if not descfile:
    return
  import io
  return io.open(descfile, "r", encoding="utf-8").read()


@check(
  id = 'com.google.fonts/check/003',
  conditions = ['description']
)
def com_google_fonts_check_003(description):
  """Does DESCRIPTION file contain broken links?"""
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


@check(
  id = 'com.google.fonts/check/004',
  conditions = ['descfile']
)
def com_google_fonts_check_004(descfile, description):
  """Is this a proper HTML snippet?

  When packaging families for google/fonts, if there is no
  DESCRIPTION.en_us.html file, the add_font.py metageneration tool will
  insert a dummy description file which contains invalid html.
  This file needs to either be replaced with an existing description file
  or edited by hand."""
  if "<p>" not in description or "</p>" not in description:
    yield FAIL, "{} does not look like a propper HTML snippet.".format(descfile)
  else:
    yield PASS, "{} is a propper HTML file.".format(descfile)


@check(
  id = 'com.google.fonts/check/005',
  conditions = ['description']
)
def com_google_fonts_check_005(description):
  """DESCRIPTION.en_us.html must have more than 200 bytes."""
  if len(description) <= 200:
    yield FAIL, ("DESCRIPTION.en_us.html must"
                 " have size larger than 200 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is larger than 200 bytes."


@check(
  id = 'com.google.fonts/check/006',
  conditions = ['description']
)
def com_google_fonts_check_006(description):
  """DESCRIPTION.en_us.html must have less than 1000 bytes."""
  if len(description) >= 1000:
    yield FAIL, ("DESCRIPTION.en_us.html must"
                 " have size smaller than 1000 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is smaller than 1000 bytes."


@condition
def metadata(family_directory):
  from fontbakery.utils import get_FamilyProto_Message

  if family_directory:
    pb_file = os.path.join(family_directory, "METADATA.pb")
    if os.path.exists(pb_file):
      return get_FamilyProto_Message(pb_file)


@check(
  id = 'com.google.fonts/check/007',
  conditions = ['metadata']
)
def com_google_fonts_check_007(metadata):
  """Font designer field in METADATA.pb must not be 'unknown'."""
  if metadata.designer.lower() == 'unknown':
    yield FAIL, "Font designer field is '{}'.".format(metadata.designer)
  else:
    yield PASS, "Font designer field is not 'unknown'."


@check(
  id = 'com.google.fonts/check/011',
  conditions = ['is_ttf']
)
def com_google_fonts_check_011(ttFonts):
  """Fonts have equal numbers of glyphs?"""
  fonts = list(ttFonts)
  failed = False
  max_style = None
  max_count = 0
  for ttFont in fonts:
    fontname = ttFont.reader.file.name
    stylename = style(fontname)
    this_count = len(ttFont['glyf'].glyphs)
    if this_count > max_count:
      max_count = this_count
      max_style = stylename

  for ttFont in fonts:
    fontname = ttFont.reader.file.name
    stylename = style(fontname)
    this_count = len(ttFont['glyf'].glyphs)
    if this_count != max_count:
      failed = True
      yield FAIL, ("{} has {} glyphs while"
                   " {} has {} glyphs.").format(stylename,
                                                this_count,
                                                max_style,
                                                max_count)
  if not failed:
    yield PASS, ("All font files in this family have"
                 " an equal total ammount of glyphs.")


@check(
  id = 'com.google.fonts/check/012',
  conditions = ['is_ttf']
)
def com_google_fonts_check_012(ttFonts):
  """Fonts have equal glyph names?"""
  fonts = list(ttFonts)

  all_glyphnames = set()
  for ttFont in fonts:
    all_glyphnames |= set(ttFont["glyf"].glyphs.keys())

  missing = {}
  available = {}
  for glyphname in all_glyphnames:
    missing[glyphname] = []
    available[glyphname] = []

  failed = False
  for ttFont in fonts:
    fontname = ttFont.reader.file.name
    stylename = style(fontname)
    these_ones = set(ttFont["glyf"].glyphs.keys())
    for glyphname in all_glyphnames:
      if glyphname not in these_ones:
        failed = True
        missing[glyphname].append(stylename)
      else:
        available[glyphname].append(stylename)

  for gn in missing.keys():
    if missing[gn]:
      yield FAIL, ("Glyphname '{}' is defined on {}"
                   " but is missing on"
                   " {}.").format(gn,
                                  ', '.join(missing[gn]),
                                  ', '.join(available[gn]))
  if not failed:
    yield PASS, "All font files have identical glyph names."


@check(
  id = 'com.google.fonts/check/016'
)
def com_google_fonts_check_016(ttFont):
  """Checking OS/2 fsType.

  Fonts must have their fsType bit set to 0. This setting is known as
  Installable Embedding,
  https://www.microsoft.com/typography/otspec/os2.htm#fst"""

  if ttFont['OS/2'].fsType != 0:
    yield FAIL, ("OS/2 fsType is a legacy DRM-related field from the 80's"
                 " and must be zero (disabled) in all fonts.")
  else:
    yield PASS, ("OS/2 fsType is properly set to zero "
                 "(80's DRM scheme is disabled).")


@condition
def registered_vendor_ids():
  """Get a list of vendor IDs from Microsoft's website."""
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


@check(
  id = 'com.google.fonts/check/018',
  conditions = ['registered_vendor_ids']
)
def com_google_fonts_check_018(ttFont, registered_vendor_ids):
  """Checking OS/2 achVendID."""

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
  elif vid not in registered_vendor_ids.keys():
    yield WARN, Message("unknown", ("OS/2 VendorID value '{}' is not"
                                    " a known registered id.").format(vid) +
                                    SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  else:
    yield PASS, "OS/2 VendorID '{}' looks good!".format(vid)


@check(
  id = 'com.google.fonts/check/019'
)
def com_google_fonts_check_019(ttFont):
  """Substitute copyright, registered and trademark
     symbols in name table entries."""
  failed = False
  replacement_map = [(u"\u00a9", '(c)'),
                     (u"\u00ae", '(r)'),
                     (u"\u2122", '(tm)')]
  for name in ttFont['name'].names:
    string = str(name.string, encoding=name.getEncoding())
    for mark, ascii_repl in replacement_map:
      new_string = string.replace(mark, ascii_repl)
      if string != new_string:
        yield FAIL, ("NAMEID #{} contains symbol that should be"
                     " replaced by '{}'.").format(name.nameID,
                                                  ascii_repl)
        failed = True
  if not failed:
    yield PASS, ("No need to substitute copyright, registered and"
                 " trademark symbols in name table entries of this font.")


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


@condition
def license_path(licenses):
  """Get license path."""
  # return license if there is exactly one license
  return licenses[0] if len(licenses) == 1 else None


@condition
def license(license_path):
  """Get license filename."""
  if license_path:
    return os.path.basename(license_path)


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


@check(
  id = 'com.google.fonts/check/029',
  conditions = ['license'],
  misc_metadata = {
    'priority': CRITICAL
  })
def com_google_fonts_check_029(ttFont, license):
  """Check copyright namerecords match license file."""
  from fontbakery.constants import (NAMEID_LICENSE_DESCRIPTION,
                                    # NAMEID_LICENSE_INFO_URL,
                                    PLACEHOLDER_LICENSING_TEXT,
                                    # NAMEID_STR,
                                    PLATID_STR)
  from unidecode import unidecode
  failed = False
  placeholder = PLACEHOLDER_LICENSING_TEXT[license]
  entry_found = False
  for i, nameRecord in enumerate(ttFont["name"].names):
    if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
      entry_found = True
      value = nameRecord.toUnicode()
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


@condition
def familyname(font):
  filename = os.path.basename(font)
  filename_base = os.path.splitext(filename)[0]
  return filename_base.split('-')[0]


@check(
  id = 'com.google.fonts/check/030',
  conditions = ['familyname'],
  misc_metadata = {
    'priority': CRITICAL
  }
)
def com_google_fonts_check_030(ttFont, familyname):
  """"License URL matches License text on name table?"""
  from fontbakery.constants import (NAMEID_LICENSE_DESCRIPTION,
                                    NAMEID_LICENSE_INFO_URL,
                                    PLACEHOLDER_LICENSING_TEXT)
  LEGACY_UFL_FAMILIES = ["Ubuntu", "UbuntuCondensed", "UbuntuMono"]
  LICENSE_URL = {
    'OFL.txt': u'http://scripts.sil.org/OFL',
    'LICENSE.txt': u'http://www.apache.org/licenses/LICENSE-2.0',
    'UFL.txt': u'https://www.ubuntu.com/legal/terms-and-policies/font-licence'
  }
  LICENSE_NAME = {
    'OFL.txt': u'Open Font',
    'LICENSE.txt': u'Apache',
    'UFL.txt': u'Ubuntu Font License'
  }
  detected_license = False
  for license in ['OFL.txt', 'LICENSE.txt', 'UFL.txt']:
    placeholder = PLACEHOLDER_LICENSING_TEXT[license]
    for nameRecord in ttFont['name'].names:
      string = nameRecord.string.decode(nameRecord.getEncoding())
      if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION and\
         string == placeholder:
        detected_license = license
        break

  if detected_license == "UFL.txt" and familyname not in LEGACY_UFL_FAMILIES:
    yield FAIL, Message("ufl",
                        ("The Ubuntu Font License is only acceptable on"
                         " the Google Fonts collection for legacy font"
                         " families that already adopted such license."
                         " New Families should use eigther Apache or"
                         " Open Font License."))
  else:
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
            yield FAIL, Message("licensing-inconsistency",
                                ("Licensing inconsistency in name table"
                                 " entries! NameID={} (LICENSE DESCRIPTION)"
                                 " indicates {} licensing, but NameID={}"
                                 " (LICENSE URL) has '{}'. Expected: '{}'"
                                 "").format(NAMEID_LICENSE_DESCRIPTION,
                                            LICENSE_NAME[detected_license],
                                            NAMEID_LICENSE_INFO_URL,
                                            string, expected))
    if not found_good_entry:
      yield FAIL, Message("no-license-found",
                          ("A known license URL must be provided in the"
                           " NameID {} (LICENSE INFO URL) entry."
                           " Currently accepted licenses are Apache or"
                           " Open Font License. For a small set of legacy"
                           " families the Ubuntu Font License may be"
                           " acceptable as well."
                           "").format(NAMEID_LICENSE_INFO_URL))
    else:
      if failed:
        yield FAIL, Message("bad-entries",
                            ("Even though a valid license URL was seen in"
                             " NAME table, there were also bad entries."
                             " Please review NameIDs {} (LICENSE DESCRIPTION)"
                             " and {} (LICENSE INFO URL)."
                             "").format(NAMEID_LICENSE_DESCRIPTION,
                                        NAMEID_LICENSE_INFO_URL))
      else:
        yield PASS, "Font has a valid license URL in NAME table."


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

@check(
  id = 'com.google.fonts/check/054',
  conditions = ['ttfautohint_stats']
)
def com_google_fonts_check_054(font, ttfautohint_stats):
  """Show hinting filesize impact.

     Current implementation simply logs useful info
     but there's no fail scenario for this checker."""

  if "missing" in ttfautohint_stats:
    yield WARN, Message("ttfa-missing",
                        TTFAUTOHINT_MISSING_MSG)
    return

  if ttfautohint_stats["dehinted_size"] == 0:
    yield WARN, Message("ttfa-bug",
                        ("ttfautohint --dehint reports that"
                         " \"This font has already been processed"
                         " with ttfautohint\"."
                         " This is a bug in an old version of ttfautohint."
                         " You'll need to upgrade it."
                         " See https://github.com/googlefonts/fontbakery/"
                         "issues/1043#issuecomment-249035069"))
    return

  hinted = ttfautohint_stats["hinted_size"]
  dehinted = ttfautohint_stats["dehinted_size"]
  increase = hinted - dehinted
  change = float(hinted)/dehinted - 1

  def filesize_formatting(s):
    if s < 1024:
      return "{} bytes".format(s)
    elif s < 1024*1024:
      return "{:.1f}kb".format(s/1024)
    else:
      return "{:.1f}Mb".format(s/(1024*1024))

  hinted_size = filesize_formatting(hinted)
  dehinted_size = filesize_formatting(dehinted)
  increase = filesize_formatting(increase)

  results_table = "Hinting filesize impact:\n\n"
  results_table += "|  | {} |\n".format(font)
  results_table += "|:--- | ---:|\n"
  results_table += "| Dehinted Size | {} |\n".format(dehinted_size)
  results_table += "| Hinted Size | {} |\n".format(hinted_size)
  results_table += "| Increase | {} |\n".format(increase)
  results_table += "| Change   | {:.1f} % |\n".format(change)
  yield INFO, results_table


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
                          ("The NAMEID_VERSION_STRING (nameID={}) value must"
                           " follow the pattern \"Version X.Y\" with X.Y"
                           " between 1.000 and 9.999."
                           " Current version string is:"
                           " \"{}\"").format(NAMEID_VERSION_STRING,
                                             ventry))
  if not failed:
    yield PASS, "Version format in NAME table entries is correct."


@check(
  id = 'com.google.fonts/check/056',
  conditions = ['ttfautohint_stats']
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


@check(
  id = 'com.google.fonts/check/061',
  rationale = """
    The EPAR table is/was a way of expressing common licensing permissions
    and restrictions in metadata; while almost nothing supported it,
    Dave Crossland wonders that adding it to everything in Google Fonts
    could help make it more popular.

    More info is available at:
    https://davelab6.github.io/epar/
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/226'
  }
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


@check(
  id = 'com.google.fonts/check/062'
)
def com_google_fonts_check_062(ttFont):
  """Is 'gasp' table set to optimize rendering?

  Traditionally version 0 'gasp' tables were set
  so that font sizes below 8 ppem had no grid
  fitting but did have antialiasing. From 9-16
  ppem, just grid fitting. And fonts above
  17ppem had both antialiasing and grid fitting
  toggled on. The use of accelerated graphics
  cards and higher resolution screens make this
  approach obsolete. Microsoft's DirectWrite
  pushed this even further with much improved
  rendering built into the OS and apps. In this
  scenario it makes sense to simply toggle all
  4 flags ON for all font sizes.
  """
  try:
    if not isinstance(ttFont["gasp"].gaspRange, dict):
      yield FAIL, "'gasp' table has no values."
    else:
      failed = False
      if 0xFFFF not in ttFont["gasp"].gaspRange:
        yield WARN, ("'gasp' table does not have a value for all"
                     " sizes (gaspRange 0xFFFF). It should be set to 1.")
      else:
        for key in ttFont["gasp"].gaspRange.keys():
          if key != 0xFFFF:
            yield WARN, ("'gasp' table has a gaspRange of {} that"
                         " may be unneccessary.").format(hex(key))
            failed = True
          else:
            value = ttFont["gasp"].gaspRange[key]
            if value != 0x0F:
              failed = True
              yield WARN, ("gaspRange {} value {} should be set"
                           " to 0x0F.").format(hex(key), value)
        if not failed:
          yield PASS, ("'gasp' table is correctly set, with one "
                       "gaspRange:value of 0xFFFF:0x0F.")
  except KeyError:
    yield FAIL, ("Font is missing the 'gasp' table."
                 " Try exporting the font with autohinting enabled.")


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


# TODO: extend this to check for availability of all required currency symbols.
@check(
  id = 'com.google.fonts/check/070'
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


@check(
  id = 'com.google.fonts/check/074',
  rationale = """
    The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
    For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that
    string should be the same in CFF fonts which also have this
    requirement in the OpenType spec.

    Note:
    A common place where we find non-ASCII strings is on name table
    entries with NameID > 18, which are expressly for localising
    the ASCII-only IDs into Hindi / Arabic / etc.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1663'
  }
)
def com_google_fonts_check_074(ttFont):
  """Are there non-ASCII characters in ASCII-only NAME table entries?"""
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


@check(
  id = 'com.google.fonts/check/080',
  conditions = ['metadata']
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

@condition
def listed_on_gfonts_api(metadata):
  if not metadata:
    return False
  import requests
  url = ('http://fonts.googleapis.com'
         '/css?family={}').format(metadata.name.replace(' ', '+'))
  r = requests.get(url)
  return r.status_code == 200


@check(
  id = 'com.google.fonts/check/081',
  conditions = ['metadata']
)
def com_google_fonts_check_081(listed_on_gfonts_api):
  """METADATA.pb: Fontfamily is listed on Google Fonts API?"""
  if not listed_on_gfonts_api:
    yield WARN, "Family not found via Google Fonts API."
  else:
    yield PASS, "Font is properly listed via Google Fonts API."


# Temporarily disabled as requested at
# https://github.com/googlefonts/fontbakery/issues/1728
@disable
@check(
  id = 'com.google.fonts/check/082',
  conditions = ['metadata']
)
def com_google_fonts_check_082(metadata):
  """METADATA.pb: Designer exists in Google Fonts profiles.csv?"""
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
    from urllib import request
    import csv
    try:
      handle = request.urlopen(PROFILES_RAW_URL)
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


@check(
  id = 'com.google.fonts/check/083',
  conditions = ['metadata']
)
def com_google_fonts_check_083(metadata):
  """METADATA.pb: check if fonts field only has
     unique "full_name" values.
  """
  fonts = {}
  for f in metadata.fonts:
    fonts[f.full_name] = f

  if len(set(fonts.keys())) != len(metadata.fonts):
    yield FAIL, ("Found duplicated \"full_name\" values"
                 " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique \"full_name\" values.")


@check(
  id = 'com.google.fonts/check/084',
  conditions = ['metadata']
)
def com_google_fonts_check_084(metadata):
  """METADATA.pb: check if fonts field
     only contains unique style:weight pairs.
  """
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


@check(
  id = 'com.google.fonts/check/085',
  conditions = ['metadata']
)
def com_google_fonts_check_085(metadata):
  """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
  licenses = ["APACHE2", "OFL", "UFL"]
  if metadata.license in licenses:
    yield PASS, ("Font license is declared"
                 " in METADATA.pb as \"{}\"").format(metadata.license)
  else:
    yield FAIL, ("METADATA.pb license field (\"{}\")"
                 " must be one of the following:"
                 " {}").format(metadata.license,
                               licenses)


@check(
  id = 'com.google.fonts/check/086',
  conditions = ['metadata']
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


@check(
  id = 'com.google.fonts/check/087',
  conditions = ['metadata']
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


@check(
  id = 'com.google.fonts/check/088',
  conditions = ['metadata']
)
def com_google_fonts_check_088(metadata):
  """Copyright notice is the same in all fonts?"""
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


@check(
  id = 'com.google.fonts/check/089',
  conditions = ['metadata']
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


@condition
def has_regular_style(metadata):
  fonts = metadata.fonts if metadata else []
  for f in fonts:
    if f.weight == 400 and f.style == "normal":
      return True
  return False


@check(
  id = 'com.google.fonts/check/090',
  conditions = ['metadata']
)
def com_google_fonts_check_090(has_regular_style):
  """According Google Fonts standards,
     families should have a Regular style.
  """
  if has_regular_style:
    yield PASS, "Family has a Regular style."
  else:
    yield FAIL, ("This family lacks a Regular"
                 " (style: normal and weight: 400)"
                 " as required by Google Fonts standards.")


@check(
  id = 'com.google.fonts/check/091',
  conditions = ['metadata',
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


@condition
def font_metadata(metadata, font):
  if not metadata:
    return
  for f in metadata.fonts:
    if font.endswith(f.filename):
      return f


@check(
  id = 'com.google.fonts/check/092',
  conditions=['font_metadata']
)
def com_google_fonts_check_092(ttFont, font_metadata):
  """Checks METADATA.pb font.name field matches
     family name declared on the name table.
  """
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

@check(
  id = 'com.google.fonts/check/093',
  conditions = ['font_metadata']
)
def com_google_fonts_check_093(ttFont, font_metadata):
  """Checks METADATA.pb font.post_script_name matches
     postscript name declared on the name table.
  """
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


@check(
  id = 'com.google.fonts/check/094',
  conditions = ['font_metadata']
)
def com_google_fonts_check_094(ttFont, font_metadata):
  """METADATA.pb font.fullname value matches
     fullname declared on the name table?
  """
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


@check(
  id = 'com.google.fonts/check/095',
  conditions=['font_metadata', 'style']
)
def com_google_fonts_check_095(ttFont, style, font_metadata):
  """METADATA.pb font.name value should be same as
     the family name declared on the name table.
  """
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


@check(
  id = 'com.google.fonts/check/096',
  conditions = ['font_metadata']
)
def com_google_fonts_check_096(font_metadata):
  """METADATA.pb family.full_name and family.post_script_name
     fields have equivalent values ?
  """
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


@check(
  id = 'com.google.fonts/check/097',
  conditions = ['font_metadata']
)
def com_google_fonts_check_097(font_metadata):
  """METADATA.pb family.filename and family.post_script_name
     fields have equivalent values?
  """
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


@condition
def font_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_FONT_FAMILY_NAME
  return get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME)


@condition
def typographic_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NAMEID_TYPOGRAPHIC_FAMILY_NAME
  return get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_FAMILY_NAME)


@condition
def font_familyname(font_familynames):
  # This assumes that all familyname
  # name table entries are identical.
  # FIX-ME: Maybe we should have a check for that.
  #         Have we ever seen this kind of
  #         problem in the wild, though ?
  return font_familynames[0]


@check(
  id = 'com.google.fonts/check/098',
  conditions = ['style',
                'font_metadata']
)
def com_google_fonts_check_098(style,
                               font_metadata,
                               font_familynames,
                               typographic_familynames):
  """METADATA.pb font.name field contains font name in right format?"""
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


@check(
  id = 'com.google.fonts/check/099',
  conditions = ['style',
                'font_metadata']
)
def com_google_fonts_check_099(style,
                               font_metadata,
                               font_familynames,
                               typographic_familynames):
  """METADATA.pb font.full_name field contains font name in right format?"""
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


@check(
  id = 'com.google.fonts/check/100',
  conditions = ['style', # This means the font filename
                         # (source of truth here) is good
                'font_metadata']
)
def com_google_fonts_check_100(font,
                               font_metadata):
  """METADATA.pb font.filename field contains font name in right format?"""
  expected = os.path.basename(font)
  if font_metadata.filename == expected:
    yield PASS, ("METADATA.pb filename field contains"
                 " font name in right format.")
  else:
    yield FAIL, ("METADATA.pb filename field (\"{}\") does not match"
                 " correct font name format (\"{}\")."
                 "").format(font_metadata.filename,
                            expected)


@check(
  id = 'com.google.fonts/check/101',
  conditions = ['font_metadata',
                'font_familynames']
)
def com_google_fonts_check_101(font_metadata,
                              font_familynames):
  """METADATA.pb font.post_script_name field
     contains font name in right format?
  """
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


@check(
  id = 'com.google.fonts/check/102',
  conditions = ['font_metadata']
)
def com_google_fonts_check_102(font_metadata):
  """Copyright notice on METADATA.pb matches canonical pattern?"""
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


@check(
  id = 'com.google.fonts/check/103',
  conditions = ['font_metadata']
)
def com_google_fonts_check_103(font_metadata):
  """Copyright notice on METADATA.pb does not contain Reserved Font Name?"""
  from unidecode import unidecode
  if "Reserved Font Name" in font_metadata.copyright:
    yield WARN, ("METADATA.pb: copyright field (\"{}\")"
                 " contains \"Reserved Font Name\"."
                 " This is an error except in a few specific"
                 " rare cases.").format(unidecode(font_metadata.copyright))
  else:
    yield PASS, ("METADATA.pb copyright field"
                 " does not contain \"Reserved Font Name\".")


@check(
  id = 'com.google.fonts/check/104',
  conditions = ['font_metadata']
)
def com_google_fonts_check_104(font_metadata):
  """Copyright notice shouldn't exceed 500 chars."""
  if len(font_metadata.copyright) > 500:
    yield FAIL, ("METADATA.pb: Copyright notice exceeds"
                 " maximum allowed lengh of 500 characteres.")
  else:
    yield PASS, "Copyright notice string is shorter than 500 chars."


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


@check(
  id = 'com.google.fonts/check/105',
  conditions = ['font_metadata',
                'canonical_filename']
)
def com_google_fonts_check_105(font_metadata, canonical_filename):
  """Filename is set canonically in METADATA.pb?"""
  if canonical_filename != font_metadata.filename:
    yield FAIL, ("METADATA.pb: filename field (\"{}\")"
                 " does not match "
                 "canonical name \"{}\".".format(font_metadata.filename,
                                                 canonical_filename))
  else:
    yield PASS, "Filename in METADATA.pb is set canonically."


@check(
  id = 'com.google.fonts/check/106',
  conditions = ['font_metadata']
)
def com_google_fonts_check_106(ttFont, font_metadata):
  """METADATA.pb font.style "italic" matches font internals?"""
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


@check(
  id = 'com.google.fonts/check/107',
  conditions = ['font_metadata']
)
def com_google_fonts_check_107(ttFont, font_metadata):
  """METADATA.pb font.style "normal" matches font internals?"""
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


@check(
  id = 'com.google.fonts/check/108',
  conditions = ['font_metadata']
)
def com_google_fonts_check_108(ttFont, font_metadata):
  """METADATA.pb font.name and font.full_name fields match
     the values declared on the name table?
  """
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


@check(
  id = 'com.google.fonts/check/109',
  conditions = ['font_metadata',
                'not whitelist_camelcased_familyname']
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


@check(
  id = 'com.google.fonts/check/110',
  conditions = ['metadata',      # that's the family-wide metadata!
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


@check(
  id = 'com.google.fonts/check/111',
  conditions = ['font_metadata']
)
def com_google_fonts_check_111(font_metadata):
  """Check that font weight has a canonical value."""
  first_digit = font_metadata.weight / 100
  if (font_metadata.weight % 100) != 0 or \
     (first_digit < 1 or first_digit > 9):
   yield FAIL, ("METADATA.pb: The weight is declared"
                " as {} which is not a"
                " multiple of 100"
                " between 100 and 900.").format(font_metadata.weight)
  else:
    yield PASS, "Font weight has a canonical value."


@check(
  id = 'com.google.fonts/check/112',
  conditions = ['font_metadata']
)
def com_google_fonts_check_112(ttFont,
                              font_metadata):
  """Checking OS/2 usWeightClass matches weight specified at METADATA.pb."""
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


@check(
  id = 'com.google.fonts/check/113',
  conditions = ['font_metadata']
)
def com_google_fonts_check_113(font_metadata):
  """Metadata weight matches postScriptName."""
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
    yield FAIL, ("METADATA.pb: Font weight value ({})"
                 " is invalid.").format(font_metadata.weight)
  elif not (font_metadata.post_script_name.endswith('-' + pair[0][0]) or
            font_metadata.post_script_name.endswith('-' + pair[1][0])):
    yield FAIL, ("METADATA.pb: Mismatch between postScriptName (\"{}\")"
                 " and weight value ({}). The name must be"
                 " ended with \"{}\" or \"{}\"."
                 "").format(font_metadata.post_script_name,
                            pair[0][1],
                            pair[0][0],
                            pair[1][0])
  else:
    yield PASS, "Weight value matches postScriptName."


@check(
  id = 'com.google.fonts/check/115',
  conditions = ['font_metadata']
)
def com_google_fonts_check_115(ttFont, font_metadata):
  """Font styles are named canonically?"""
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


@check(
  id = 'com.google.fonts/check/116'
)
def com_google_fonts_check_116(ttFont):
  """Is font em size (ideally) equal to 1000?"""
  upm_height = ttFont["head"].unitsPerEm
  if upm_height != 1000:
    yield WARN, ("Font em size ({}) is not"
                 " equal to 1000.").format(upm_height)
  else:
    yield PASS, "Font em size is equal to 1000."


@condition
def remote_styles(metadata):
  """Get a dictionary of TTFont objects of all font files of
     a given family as currently hosted at Google Fonts.
  """

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
      if file_name.lower().endswith(".ttf"):
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


@condition
def api_gfonts_ttFont(style, remote_styles):
  """Get a TTFont object of a font downloaded from Google Fonts
     corresponding to the given TTFont object of
     a local font being checked.
  """
  if remote_styles and style in remote_styles:
    return remote_styles[style]


@condition
def github_gfonts_ttFont(ttFont, license):
  """Get a TTFont object of a font downloaded
     from Google Fonts git repository.
  """
  if not license:
    return

  from fontbakery.utils import download_file
  from fontTools.ttLib import TTFont
  LICENSE_DIRECTORY = {
    "OFL.txt": "ofl",
    "UFL.txt": "ufl",
    "APACHE.txt": "apache"
  }
  filename = os.path.basename(ttFont.reader.file.name)
  fontname = filename.split('-')[0].lower()
  url = ("https://github.com/google/fonts/raw/master"
         "/{}/{}/{}").format(LICENSE_DIRECTORY[license],
                             fontname,
                             filename)
  return TTFont(download_file(url))


@check(
  id = 'com.google.fonts/check/117',
  conditions = ['api_gfonts_ttFont',
                'github_gfonts_ttFont']
)
def com_google_fonts_check_117(ttFont,
                               api_gfonts_ttFont,
                               github_gfonts_ttFont):
  """Version number has increased since previous release on Google Fonts?"""
  v_number = ttFont["head"].fontRevision
  api_gfonts_v_number = api_gfonts_ttFont["head"].fontRevision
  github_gfonts_v_number = github_gfonts_ttFont["head"].fontRevision
  failed = False

  if v_number == api_gfonts_v_number:
    failed = True
    yield FAIL, ("Version number {} is equal to"
                 " version on Google Fonts.").format(v_number)

  if v_number < api_gfonts_v_number:
    failed = True
    yield FAIL, ("Version number {} is less than"
                 " version on Google Fonts ({})."
                 "").format(v_number,
                            api_gfonts_v_number)

  if v_number == github_gfonts_v_number:
    failed = True
    yield FAIL, ("Version number {} is equal to"
                 " version on Google Fonts GitHub repo."
                 "").format(v_number)

  if v_number < github_gfonts_v_number:
    failed = True
    yield FAIL, ("Version number {} is less than"
                 " version on Google Fonts GitHub repo ({})."
                 "").format(v_number,
                            github_gfonts_v_number)

  if not failed:
    yield PASS, ("Version number {} is greater than"
                 " version on Google Fonts GitHub ({})"
                 " and production servers ({})."
                 "").format(v_number,
                            github_gfonts_v_number,
                            api_gfonts_v_number)


@check(
  id = 'com.google.fonts/check/118',
  conditions = ['api_gfonts_ttFont']
)
def com_google_fonts_check_118(ttFont, api_gfonts_ttFont):
  """Glyphs are similiar to Google Fonts version?"""

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
  gfonts_glyphs = glyphs_surface_area(api_gfonts_ttFont)

  shared_glyphs = set(these_glyphs) & set(gfonts_glyphs)

  this_upm = ttFont['head'].unitsPerEm
  gfonts_upm = api_gfonts_ttFont['head'].unitsPerEm

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


@check(
  id = 'com.google.fonts/check/119',
  conditions = ['api_gfonts_ttFont']
)
def com_google_fonts_check_119(ttFont, api_gfonts_ttFont):
  """TTFAutohint x-height increase value is same as in
     previous release on Google Fonts?"""

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

  if 'fpgm' in api_gfonts_ttFont:
    gfonts_fpgm_tbl = api_gfonts_ttFont["fpgm"].program.getAssembly()
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


@check(
  id = 'com.google.fonts/check/129',
  conditions = ['style']
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


@check(
  id = 'com.google.fonts/check/130',
  conditions = ['style']
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


@check(
  id = 'com.google.fonts/check/131',
  conditions = ['style']
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


@check(
  id = 'com.google.fonts/check/153',
  rationale = """
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


@check(
  id = 'com.google.fonts/check/154',
  conditions = ['api_gfonts_ttFont']
)
def com_google_fonts_check_154(ttFont, api_gfonts_ttFont):
  """Check font has same encoded glyphs as version hosted on
  fonts.google.com"""
  cmap = ttFont['cmap'].getcmap(3, 1).cmap
  gf_cmap = api_gfonts_ttFont['cmap'].getcmap(3, 1).cmap
  missing_codepoints = set(gf_cmap.keys()) - set(cmap.keys())

  if missing_codepoints:
    hex_codepoints = ['0x' + hex(c).upper()[2:].zfill(4) for c
                      in missing_codepoints]
    yield FAIL, ("Font is missing the following glyphs"
                 " from the previous release"
                 " [{}]").format(', '.join(hex_codepoints))
  else:
    yield PASS, ('Font has all the glyphs from the previous release')


@check(
  id = 'com.google.fonts/check/155',
  conditions = ['font_metadata']
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


@condition
def familyname_with_spaces(familyname):
  FAMILY_WITH_SPACES_EXCEPTIONS = {'VT323': 'VT323',
                                   'PressStart2P': 'Press Start 2P',
                                   'ABeeZee': 'ABeeZee',
                                   'IBMPlexMono': 'IBM Plex Mono',
                                   'IBMPlexSans': 'IBM Plex Sans',
                                   'IBMPlexSerif': 'IBM Plex Serif'}
  if familyname in FAMILY_WITH_SPACES_EXCEPTIONS.keys():
    return FAMILY_WITH_SPACES_EXCEPTIONS[familyname]

  result = []
  for c in familyname:
    if c.isupper():
      result.append(" ")
    result.append(c)
  result = ''.join(result).strip()

  def of_special_case(s):
    """Special case for family names such as
       MountainsofChristmas which would need to
       have the "of" split apart from "Mountains".

       See also: https://github.com/googlefonts/fontbakery/issues/1489
       "Failure to handle font family with 3 words in it"
    """
    if s[-2:] == "of":
      return s[:-2] + " of"
    else:
      return s

  result = " ".join(map(of_special_case, result.split(" ")))

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


@check(
  id = 'com.google.fonts/check/156',
  conditions = ['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/157',
  conditions = ['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/158',
  conditions = ['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
def com_google_fonts_check_158(ttFont, style, familyname_with_spaces):
  """ Check name table: FONT_SUBFAMILY_NAME entries. """
  from fontbakery.utils import name_entry_id
  from fontbakery.constants import (NAMEID_FONT_SUBFAMILY_NAME,
                                    PLATFORM_ID__MACINTOSH,
                                    PLATFORM_ID__WINDOWS,
                                    STYLE_NAMES)
  failed = False
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


@check(
  id = 'com.google.fonts/check/159',
  conditions = ['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/160',
  conditions = ['style'],
  misc_metadata = {
   'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/161',
  conditions = ['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/162',
  conditions=['style'],
  misc_metadata = {
    'priority': IMPORTANT
  })
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


@check(
  id = 'com.google.fonts/check/164',
  rationale = """
    This is an arbitrary max lentgh for the copyright notice field
    of the name table. We simply don't want such notices to be too long.
    Typically such notices are actually much shorter than this with
    a lenghth of roughtly 70 or 80 characters.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1603'
  })
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


@check(
  id = 'com.google.fonts/check/165',
  rationale = """
      We need to check names are not already used, and today the best
      place to check that is http://namecheck.fontdata.com
  """,
  conditions = ["familyname"],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/494'
  })
def com_google_fonts_check_165(ttFont, familyname):
  """ Familyname must be unique according to namecheck.fontdata.com """
  FB_ISSUE_TRACKER = "https://github.com/googlefonts/fontbakery/issues"
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

@check(
  id = 'com.google.fonts/check/166',
  rationale = """
    The git sha1 tagging and dev/release features of Source Foundry font-v
     tool are awesome and we would love to consider upstreaming the approach
     into fontmake someday. For now we only emit a WARN if a given font does
     not yet follow the experimental versioning style, but at some point we
     may start enforcing it.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1563'
  })
def com_google_fonts_check_166(ttFont):
  """ Check for font-v versioning """
  from fontv.libfv import FontVersion

  fv = FontVersion(ttFont)
  if fv.version and (fv.is_development or fv.is_release):
    yield PASS, "Font version string looks GREAT!"
  else:
    yield INFO, ("Version string is: \"{}\"\n"
                 "The version string must ideally include a git commit hash"
                 " and either a 'dev' or a 'release' suffix such as in the"
                 " example below:\n"
                 "\"Version 1.3; git-0d08353-release\""
                 "").format(fv.get_name_id5_version_string())


# Disabling this check since the previous implementation was
# bogus due to the way fonttools encodes the data into the TTF
# files and the new attempt at targetting the real problem is
# still not quite right.
# FIXME: reimplement this addressing the actual root cause of the issue.
# See also ongoing discussion at:
# https://github.com/googlefonts/fontbakery/issues/1727
@disable
@check(
  id = 'com.google.fonts/check/173',
  rationale = """
    Advance width values in the Horizontal Metrics (htmx)
    table cannot be negative since they are encoded as unsigned
    16-bit values. But some programs may infer and report
    a negative advance by looking up the x-coordinates of
    the glyphs directly on the glyf table.

    There are reports of broken versions of Glyphs.app causing
    this kind of problem as reported at
    https://github.com/googlefonts/fontbakery/issues/1720 and
    https://github.com/fonttools/fonttools/pull/1198

    This check detects and reports such malformed
    glyf table entries.
  """,
  conditions = ['is_ttf'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1720'
  })
def com_google_fonts_check_173(ttFont):
  """ Check that advance widths cannot be inferred as negative. """
  failed = False
  for glyphName in ttFont["glyf"].glyphs:
    coords = ttFont["glyf"][glyphName].coordinates
    rightX = coords[-3][0]
    leftX = coords[-4][0]
    advwidth = rightX - leftX
    if advwidth < 0:
      failed = True
      yield FAIL, ("glyph '{}' has bad coordinates on the glyf table,"
                   " which may lead to the advance width to be"
                   " interpreted as a negative"
                   " value ({}).").format(glyphName,
                                          advwidth)
  if not failed:
    yield PASS, "The x-coordinates of all glyphs look good."


@check(
  id = 'com.google.fonts/check/174',
  rationale = """
  Google Fonts may serve static fonts which have been generated
  from variable fonts.

  This test will attempt to generate a static ttf using fontTool's
  varLib mutator.

  The target font will be the mean of each axis e.g:

  VF font axes:
  min weight, max weight = 400, 800
  min width, max width = 50, 100

  Target Instance:
  weight = 600,
  width = 75
  """,
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1727'
  })
def com_google_fonts_check_174(ttFont):
  """ Check a static ttf can be generated from a variable font. """
  import tempfile
  from fontTools.varLib import mutator

  try:
    loc = {k.axisTag: float((k.maxValue + k.minValue) / 2)
           for k in ttFont['fvar'].axes}
    with tempfile.TemporaryFile() as instance:
      font = mutator.instantiateVariableFont(ttFont, loc)
      font.save(instance)
      yield PASS, ("fontTools.varLib.mutator generated a static font "
                   "instance")
  except Exception as e:
    yield FAIL, ("fontTools.varLib.mutator failed to generated a static font "
                 "instance\n{}".format(repr(e)))

def is_librebarcode(font):
  font_filenames = [
    "LibreBarcode39-Regular.ttf",
    "LibreBarcode39Text-Regular.ttf",
    "LibreBarcode128-Regular.ttf",
    "LibreBarcode128Text-Regular.ttf",
    "LibreBarcode39Extended-Regular.ttf",
    "LibreBarcode39ExtendedText-Regular.ttf"
  ]
  for font_filename in font_filenames:
    if font_filename in font:
      return True

@condition(force=True)
def fontforge_skip_checks(font):
  """Skip by fontforge reported issues for google fonts specific fonts."""
  if is_librebarcode(font):
    # see https://github.com/graphicore/librebarcode/issues/3
    # 0x20: Glyphs have points at extremas
    # 0x200: Font doesn't have invalid glyph names
    return 0x20 + 0x200
  return None

def check_skip_filter(checkid, font=None, **iterargs):
  if font and is_librebarcode(font) and checkid in (
        # See: https://github.com/graphicore/librebarcode/issues/3
        'com.google.fonts/check/033' # Checking correctness of monospaced metadata.
      , 'com.google.fonts/check/063' # Does GPOS table have kerning information?
      , 'com.google.fonts/check/070' # Font has all expected currency sign characters?
      , 'com.google.fonts/check/049' # Whitespace glyphs have ink?
  ):
    return False, ('LibreBarcode is blacklisted for this check, see '
                  'https://github.com/graphicore/librebarcode/issues/3')
  return True, None

specification.check_skip_filter = check_skip_filter

specification.auto_register(globals())

specification.test_expected_checks(expected_check_ids, exclusive=True)

# FIXME: use logging.info or remove?
for section_name, section in specification._sections.items():
  print ("{} checks on {}".format(len(section._checks), section_name))

