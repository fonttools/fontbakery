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
# from .shared_conditions import is_variable_font
from fontbakery.callable import condition, check, disable
from fontbakery.message import Message
from fontbakery.constants import(PriorityLevel,
                                 NameID,
                                 PlatformID,
                                 WindowsEncodingID)
from fontbakery.fonts_spec import spec_factory

spec_imports = (
    ('.', ('general', 'cmap', 'head', 'os2', 'post', 'name',
       'hhea', 'dsig', 'hmtx', 'gpos', 'gdef', 'kern', 'glyf',
       'fvar', 'shared_conditions', 'loca')
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
      , 'com.google.fonts/check/032' # Description strings in the name table must not exceed 200 characters.
      , 'com.google.fonts/check/033' # Checking correctness of monospaced metadata.
      , 'com.google.fonts/check/034' # Check if OS/2 xAvgCharWidth is correct.
      , 'com.adobe.fonts/check/fsselection_matches_macstyle' # Check if OS/2 fsSelection matches head macStyle bold and italic bits.
      , 'com.adobe.fonts/check/bold_italic_unique_for_nameid1' # Check that OS/2.fsSelection bold & italic settings are unique for each NameID1
      , 'com.google.fonts/check/035' # Checking with ftxvalidator.
      , 'com.google.fonts/check/036' # Checking with ots-sanitize.
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
      , 'com.google.fonts/check/077' # Check all glyphs have codepoints assigned.
      #, 'com.google.fonts/check/078' # Check that glyph names do not exceed max length.
      , 'com.google.fonts/check/079' # Monospace font has hhea.advanceWidthMax equal to each glyph's advanceWidth?
      , 'com.google.fonts/check/081' # METADATA.pb: Fontfamily is listed on Google Fonts API?
      , 'com.google.fonts/check/083' # METADATA.pb: check if fonts field only has unique "full_name" values.
      , 'com.google.fonts/check/084' # METADATA.pb: check if fonts field only contains unique style:weight pairs.
      , 'com.google.fonts/check/085' # METADATA.pb license is "APACHE2", "UFL" or "OFL"?
      , 'com.google.fonts/check/086' # METADATA.pb should contain at least "menu" and "latin" subsets.
      , 'com.google.fonts/check/087' # METADATA.pb subsets should be alphabetically ordered.
      , 'com.google.fonts/check/088' # METADATA.pb: Copyright notice is the same in all fonts?
      , 'com.google.fonts/check/089' # Check that METADATA.pb family values are all the same.
      , 'com.google.fonts/check/090' # METADATA.pb: According Google Fonts standards, families should have a Regular style.
      , 'com.google.fonts/check/091' # METADATA.pb: Regular should be 400.
      , 'com.google.fonts/check/092' # Checks METADATA.pb font.name field matches family name declared on the name table.
      , 'com.google.fonts/check/093' # Checks METADATA.pb font.post_script_name matches postscript name declared on the name table.
      , 'com.google.fonts/check/094' # METADATA.pb font.full_name value matches fullname declared on the name table?
      , 'com.google.fonts/check/095' # METADATA.pb font.name value should be same as the family name declared on the name table.
      , 'com.google.fonts/check/096' # METADATA.pb font.full_name and font.post_script_name fields have equivalent values ?
      , 'com.google.fonts/check/097' # METADATA.pb font.filename and font.post_script_name fields have equivalent values?
      , 'com.google.fonts/check/098' # METADATA.pb font.name field contains font name in right format?
      , 'com.google.fonts/check/099' # METADATA.pb font.full_name field contains font name in right format?
      , 'com.google.fonts/check/100' # METADATA.pb font.filename field contains font name in right format?
      , 'com.google.fonts/check/101' # METADATA.pb font.post_script_name field contains font name in right format?
      , 'com.google.fonts/check/102' # Copyright notice on METADATA.pb matches canonical pattern?
      , 'com.google.fonts/check/103' # Copyright notice on METADATA.pb does not contain Reserved Font Name?
      , 'com.google.fonts/check/104' # METADATA.pb: Copyright notice shouldn't exceed 500 chars.
      , 'com.google.fonts/check/105' # Filename is set canonically in METADATA.pb?
      , 'com.google.fonts/check/106' # METADATA.pb font.style "italic" matches font internals?
      , 'com.google.fonts/check/107' # METADATA.pb font.style "normal" matches font internals?
      , 'com.google.fonts/check/108' # METADATA.pb font.name and font.full_name fields match the values declared on the name table?
      , 'com.google.fonts/check/109' # METADATA.pb: Check if fontname is not camel cased.
      , 'com.google.fonts/check/110' # METADATA.pb: Check font name is the same as family name.
      , 'com.google.fonts/check/111' # METADATA.pb: Check that font weight has a canonical value.
      , 'com.google.fonts/check/112' # Checking OS/2 usWeightClass matches weight specified at METADATA.pb.
      , 'com.google.fonts/check/113' # METADATA.pb weight matches postScriptName.
      , 'com.google.fonts/check/115' # METADATA.pb: Font styles are named canonically?
      , 'com.google.fonts/check/116' # Stricter unitsPerEm criteria for Google Fonts.
      , 'com.google.fonts/check/117' # Version number has increased since previous release on Google Fonts?
      , 'com.google.fonts/check/118' # Glyphs are similiar to Google Fonts version?
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
      , 'com.google.fonts/check/ttx-roundtrip' # Checking with fontTools.ttx
      , 'com.google.fonts/check/has_ttfautohint_params' # Font has ttfautohint params
      , 'com.google.fonts/check/vttclean' # There must not be VTT Talk sources in the font.
      , 'com.google.fonts/check/varfont/has_HVAR' # Check that variable fonts have an HVAR table.
#      , 'com.google.fonts/check/varfont/has_MVAR' # Check that variable fonts have an MVAR table.
      , 'com.google.fonts/check/fontbakery_version' # Do we have the latest version of FontBakery installed?
      , 'com.google.fonts/check/aat' # Are there unwanted Apple tables?
      , 'com.google.fonts/check/ftxvalidator_is_available' # Is the command "ftxvalidator" (Apple Font Tool Suite) available?
      , 'com.adobe.fonts/check/postscript_name_cff_vs_name' # CFF table FontName must match name table ID 6 (PostScript name).
      , 'com.adobe.fonts/check/postscript_name_consistency' # Name table ID 6 (PostScript name) must be consistent across platforms.
      , 'com.adobe.fonts/check/max_4_fonts_per_family_name' # Verify that each group of fonts with the same nameID 1 has maximum of 4 fonts
      , 'com.google.fonts/check/metadata/parses' # Check METADATA.pb parses correctly.
      , 'com.google.fonts/check/fvar_name_entries' # All name entries referenced by fvar instances exist on the name table?
      , 'com.google.fonts/check/varfont_has_instances' # A variable font must have named instances.
      , 'com.google.fonts/check/varfont_weight_instances' # Variable font weight coordinates must be multiples of 100.
      , 'com.google.fonts/check/wght_valid_range' # Weight axis coordinate must be within spec range of 1 to 1000 on all instances.
      , 'com.google.fonts/check/tnum_horizontal_metrics' # All tabular figures must have the same width across the whole family.
      , 'com.google.fonts/check/integer_ppem_if_hinted' # PPEM must be an integer on hinted fonts.
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


@condition
def style_with_spaces(font):
  """Stylename with spaces (derived from a canonical filename)."""
  if style(font):
    return style(font).replace('Italic',
                               ' Italic').strip()


@condition
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


@condition
def stylenames_are_canonical(fonts):
  """ Are all font files named canonically ? """
  for font in fonts:
    if not canonical_stylename(font):
      return False
  # otherwise:
  return True


@condition
def canonical_stylename(font):
  """ Returns the canonical stylename of a given font. """
  from fontbakery.constants import STYLE_NAMES
  from fontbakery.specifications.shared_conditions import is_variable_font
  from fontTools.ttLib import TTFont

  filename = os.path.basename(font)
  basename = os.path.splitext(filename)[0]
  # remove spaces in style names
  valid_style_suffixes = [name.replace(' ', '') for name in STYLE_NAMES]
  valid_varfont_suffixes = ["VF",
                            "Italic",
                            "Italic-VF",
                            "Roman",
                            "Roman-VF"]

  suffix = basename.split('-')
  suffix.pop(0)
  suffix = '-'.join(suffix)

  varfont = os.path.exists(font) and is_variable_font(TTFont(font))
  if ('-' in basename and
      (suffix in valid_varfont_suffixes and varfont)
      or (suffix in valid_style_suffixes and not varfont)):
    return suffix


@check(
  id = 'com.google.fonts/check/001',
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_001(font):
  """Checking file is named canonically.

  A font's filename must be composed in the following manner:
  <familyname>-<stylename>.ttf

  e.g. Nunito-Regular.ttf,
       Oswald-BoldItalic.ttf

  Variable fonts must use the "-VF", "Roman" or "Italic" suffixes:

  e.g. Roboto-VF.ttf,
       Barlow-VF.ttf,
       Example-Roman-VF.ttf,
       Familyname-Italic-VF.ttf
       Orbitron-Roman.ttf,
       Somethingelse-Italic.ttf
  """
  from fontbakery.constants import STYLE_NAMES

  if canonical_stylename(font):
    yield PASS, f"{font} is named canonically."
  else:
    style_names = '", "'.join(STYLE_NAMES)
    yield FAIL, (f'Style name used in "{font}" is not canonical.'
                  ' You should rebuild the font using'
                  ' any of the following'
                 f' style names: "{style_names}".')


@condition
def family_directory(fonts):
  """Get the path of font project directory."""
  if fonts:
    dirname = os.path.dirname(fonts[0])
    if dirname == '':
      dirname = '.'
    return dirname


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
      yield INFO, (f"Found an email address: {link}")
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
    yield FAIL, f"{descfile} does not look like a propper HTML snippet."
  else:
    yield PASS, f"{descfile} is a propper HTML file."


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
def family_metadata(family_directory):
  from google.protobuf import text_format
  from fontbakery.utils import get_FamilyProto_Message

  if family_directory:
    try:
      pb_file = os.path.join(family_directory, "METADATA.pb")
      if os.path.exists(pb_file):
        return get_FamilyProto_Message(pb_file)
    except text_format.ParseError:
      return None


@check(
  id = 'com.google.fonts/check/metadata/parses',
  conditions = ['family_directory'],
  rationale = """
  The purpose of this check is to ensure that
  the METADATA.pb file is not malformed.
  """
)
def com_google_fonts_check_metadata_parses(family_directory):
  """ Check METADATA.pb parse correctly. """
  from google.protobuf import text_format
  from fontbakery.utils import get_FamilyProto_Message
  try:
    pb_file = os.path.join(family_directory, "METADATA.pb")
    get_FamilyProto_Message(pb_file)
    yield PASS, "METADATA.pb parsed successfuly."
  except text_format.ParseError as e:
    yield FAIL, (f"Family metadata at {family_directory} failed to parse.\n"
                 f"TRACEBACK:\n{e}")
  except FileNotFoundError:
    yield SKIP, f"Font family at '{family_directory}' lacks a METADATA.pb file."


@check(
  id = 'com.google.fonts/check/007',
  conditions = ['family_metadata']
)
def com_google_fonts_check_007(family_metadata):
  """Font designer field in METADATA.pb must not be 'unknown'."""
  if family_metadata.designer.lower() == 'unknown':
    yield FAIL, f"Font designer field is '{family_metadata.designer}'."
  else:
    yield PASS, "Font designer field is not 'unknown'."


@check(
  id = 'com.google.fonts/check/011',
  conditions = ['are_ttf',
                'stylenames_are_canonical']
)
def com_google_fonts_check_011(ttFonts):
  """Fonts have equal numbers of glyphs?"""
  # ttFonts is an iterator, so here we make a list from it
  # because we'll have to iterate twice in this check implementation:
  the_ttFonts = list(ttFonts)

  failed = False
  max_stylename = None
  max_count = 0
  max_glyphs = None
  for ttFont in the_ttFonts:
    fontname = ttFont.reader.file.name
    stylename = canonical_stylename(fontname)
    this_count = len(ttFont['glyf'].glyphs)
    if this_count > max_count:
      max_count = this_count
      max_stylename = stylename
      max_glyphs = set(ttFont['glyf'].glyphs)

  for ttFont in the_ttFonts:
    fontname = ttFont.reader.file.name
    stylename = canonical_stylename(fontname)
    these_glyphs = set(ttFont['glyf'].glyphs)
    this_count = len(these_glyphs)
    if this_count != max_count:
      failed = True
      all_glyphs = max_glyphs.union(these_glyphs)
      common_glyphs = max_glyphs.intersection(these_glyphs)
      diff = all_glyphs - common_glyphs
      diff_count = len(diff)
      if diff_count < 10:
        diff = ", ".join(diff)
      else:
        diff = ", ".join(list(diff)[:10]) + " (and more)"

      yield FAIL, (f"{stylename} has {this_count} glyphs while"
                   f" {max_stylename} has {max_count} glyphs."
                   f" There are {diff_count} different glyphs"
                   f" among them: {diff}")
  if not failed:
    yield PASS, ("All font files in this family have"
                 " an equal total ammount of glyphs.")


@check(
  id = 'com.google.fonts/check/012',
  conditions = ['are_ttf']
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
                                  ', '.join(available[gn]),
                                  ', '.join(missing[gn]))
  if not failed:
    yield PASS, "All font files have identical glyph names."


@check(
  id = 'com.google.fonts/check/016'
)
def com_google_fonts_check_016(ttFont):
  """Checking OS/2 fsType.

  Fonts must have their fsType field set to zero.
  This setting is known as Installable Embedding, meaning
  that none of the DRM restrictions are enabled on the fonts.

  More info available at:
  https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
  """
  value = ttFont['OS/2'].fsType
  if value != 0:
    FSTYPE_RESTRICTIONS = {
      0x0002: ("* The font must not be modified, embedded or exchanged in"
               " any manner without first obtaining permission of"
               " the legal owner."),
      0x0004: ("The font may be embedded, and temporarily loaded on the"
               " remote system, but documents that use it must"
               " not be editable."),
      0x0008: ("The font may be embedded but must only be installed"
               " temporarily on other systems."),
      0x0100: ("The font may not be subsetted prior to embedding."),
      0x0200: ("Only bitmaps contained in the font may be embedded."
               " No outline data may be embedded.")
    }
    restrictions = ""
    for bit_mask in FSTYPE_RESTRICTIONS.keys():
      if value & bit_mask:
        restrictions += FSTYPE_RESTRICTIONS[bit_mask]

    if value & 0b1111110011110001:
      restrictions += ("* There are reserved bits set,"
                       " which indicates an invalid setting.")

    yield FAIL, ("OS/2 fsType is a legacy DRM-related field.\n"
                 "In this font it is set to {} meaning that:\n"
                 "{}\n"
                 "No such DRM restrictions can be enabled on the"
                 " Google Fonts collection, so the fsType field"
                 " must be set to zero (Installable Embedding) instead.\n"
                 "Fonts with this setting indicate that they may be embedded"
                 " and permanently installed on the remote system"
                 " by an application.\n\n"
                 " More detailed info is available at:\n"
                 " https://docs.microsoft.com/en-us"
                 "/typography/opentype/spec/os2#fstype"
                 "").format(value, restrictions)
  else:
    yield PASS, ("OS/2 fsType is properly set to zero.")


@condition
def registered_vendor_ids():
  """Get a list of vendor IDs from Microsoft's website."""
  from bs4 import BeautifulSoup
  from pkg_resources import resource_filename

  registered_vendor_ids = {}
  CACHED = resource_filename('fontbakery',
                             'data/fontbakery-microsoft-vendorlist.cache')
  content = open(CACHED, encoding='utf-8').read()
  soup = BeautifulSoup(content, 'html.parser')

  IDs = [chr(c + ord('a')) for c in range(ord('z') - ord('a') + 1)]
  IDs.append("0-9-")

  for section_id in IDs:
    section = soup.find('h2', {'id': section_id})
    table = section.find_next_sibling('table')
    if not table: continue

    #print ("table: '{}'".format(table))
    for row in table.findAll('tr'):
      #print("ROW: '{}'".format(row))
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
    yield WARN, Message("not set", "OS/2 VendorID is not set." +
                                   SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif vid in bad_vids:
    yield WARN, Message("bad", ("OS/2 VendorID is '{}',"
                                " a font editor default.").format(vid) +
                                SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  elif vid not in registered_vendor_ids.keys():
    yield WARN, Message("unknown", ("OS/2 VendorID value '{}' is not"
                                    " a known registered id.").format(vid) +
                                    SUGGEST_MICROSOFT_VENDORLIST_WEBSITE)
  else:
    yield PASS, f"OS/2 VendorID '{vid}' looks good!"


@check(
  id = 'com.google.fonts/check/019'
)
def com_google_fonts_check_019(ttFont):
  """Substitute copyright, registered and trademark
     symbols in name table entries."""
  failed = False
  replacement_map = [("\u00a9", '(c)'),
                     ("\u00ae", '(r)'),
                     ("\u2122", '(tm)')]
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


@check(
  id = 'com.google.fonts/check/020',
  conditions=['style']
)
def com_google_fonts_check_020(font, ttFont, style):
  """Checking OS/2 usWeightClass."""
  from fontbakery.specifications.shared_conditions import is_ttf

  weight_name, expected_value = expected_os2_weight(style)
  value = ttFont['OS/2'].usWeightClass

  if value != expected_value:

    if is_ttf(ttFont) and \
       (weight_name == 'Thin' and value == 100) or \
       (weight_name == 'ExtraLight' and value == 200):
      yield WARN, ("{}:{} is OK on TTFs, but OTF files with those values"
                   " will cause bluring on Windows."
                   " GlyphsApp users must set a Instance Custom Parameter"
                   " for the Thin and ExtraLight styles to 250 and 275,"
                   " so that if OTFs are exported then it will not"
                   " blur on Windows.")
    else:
      yield FAIL, ("OS/2 usWeightClass expected value for"
                   " '{}' is {} but this font has"
                   " {}.").format(weight_name, expected_value, value)
  else:
    yield PASS, "OS/2 usWeightClass value looks good!"


def git_rootdir(family_dir):
  if not family_dir:
    return None

  original_dir = os.getcwd()
  root_dir = None
  try:
    import subprocess
    os.chdir(family_dir)
    git_cmd = [
        "git", "rev-parse", "--show-toplevel"
    ]
    git_output = subprocess.check_output(git_cmd, stderr=subprocess.STDOUT)
    root_dir = git_output.decode("utf-8").strip()

  except (OSError, IOError, subprocess.CalledProcessError):
    pass # Not a git repo, or git is not installed.

  os.chdir(original_dir)
  return root_dir


@condition
def licenses(family_directory):
  """Get a list of paths for every license
     file found in a font project."""
  found = []
  search_paths = [family_directory]
  gitroot = git_rootdir(family_directory)
  if gitroot and gitroot not in search_paths:
    search_paths.append(gitroot)

  for directory in search_paths:
    if directory:
      for license in ['OFL.txt', 'LICENSE.txt']:
        license_path = os.path.join(directory, license)
        if os.path.exists(license_path):
          found.append(license_path)
  return found


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
    yield FAIL, Message("no-license",
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
    'priority': PriorityLevel.CRITICAL
  })
def com_google_fonts_check_029(ttFont, license):
  """Check copyright namerecords match license file."""
  from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT
  from unidecode import unidecode
  failed = False
  placeholder = PLACEHOLDER_LICENSING_TEXT[license]
  entry_found = False
  for i, nameRecord in enumerate(ttFont["name"].names):
    if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
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
                                        NameID.LICENSE_DESCRIPTION,
                                        nameRecord.platformID,
                                        PlatformID(nameRecord.platformID).name,
                                        unidecode(value),
                                        unidecode(placeholder)))
  if not entry_found:
    yield FAIL, Message("missing", \
                        ("Font lacks NameID {} "
                         "(LICENSE DESCRIPTION). A proper licensing entry"
                         " must be set.").format(NameID.LICENSE_DESCRIPTION))
  elif not failed:
    yield PASS, "Licensing entry on name table is correctly set."


@condition
def familyname(font):
  filename = os.path.basename(font)
  filename_base = os.path.splitext(filename)[0]
  if '-' in filename_base:
    return filename_base.split('-')[0]


@check(
  id = 'com.google.fonts/check/030',
  conditions = ['familyname'],
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_030(ttFont, familyname):
  """"License URL matches License text on name table?"""
  from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT
  LEGACY_UFL_FAMILIES = ["Ubuntu", "UbuntuCondensed", "UbuntuMono"]
  LICENSE_URL = {
    'OFL.txt': 'http://scripts.sil.org/OFL',
    'LICENSE.txt': 'http://www.apache.org/licenses/LICENSE-2.0',
    'UFL.txt': 'https://www.ubuntu.com/legal/terms-and-policies/font-licence'
  }
  LICENSE_NAME = {
    'OFL.txt': 'Open Font',
    'LICENSE.txt': 'Apache',
    'UFL.txt': 'Ubuntu Font License'
  }
  detected_license = False
  for license in ['OFL.txt', 'LICENSE.txt', 'UFL.txt']:
    placeholder = PLACEHOLDER_LICENSING_TEXT[license]
    for nameRecord in ttFont['name'].names:
      string = nameRecord.string.decode(nameRecord.getEncoding())
      if nameRecord.nameID == NameID.LICENSE_DESCRIPTION and\
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
        if nameRecord.nameID == NameID.LICENSE_INFO_URL:
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
                                 "").format(NameID.LICENSE_DESCRIPTION,
                                            LICENSE_NAME[detected_license],
                                            NameID.LICENSE_INFO_URL,
                                            string, expected))
    if not found_good_entry:
      yield FAIL, Message("no-license-found",
                          ("A known license URL must be provided in the"
                           " NameID {} (LICENSE INFO URL) entry."
                           " Currently accepted licenses are Apache or"
                           " Open Font License. For a small set of legacy"
                           " families the Ubuntu Font License may be"
                           " acceptable as well."
                           "").format(NameID.LICENSE_INFO_URL))
    else:
      if failed:
        yield FAIL, Message("bad-entries",
                            ("Even though a valid license URL was seen in"
                             " NAME table, there were also bad entries."
                             " Please review NameIDs {} (LICENSE DESCRIPTION)"
                             " and {} (LICENSE INFO URL)."
                             "").format(NameID.LICENSE_DESCRIPTION,
                                        NameID.LICENSE_INFO_URL))
      else:
        yield PASS, "Font has a valid license URL in NAME table."


@check(
  id = 'com.google.fonts/check/032',
  rationale = """
  An old FontLab version had a bug which caused it to store
  copyright notices in nameID 10 entries.

  In order to detect those and distinguish them from actual
  legitimate usage of this name table entry, we expect that
  such strings do not exceed a reasonable length of 200 chars.

  Longer strings are likely instances of the FontLab bug.
  """
)
def com_google_fonts_check_032(ttFont):
  """Description strings in the name table must not exceed 200 characters."""
  failed = False
  for name in ttFont['name'].names:
    if (name.nameID == NameID.DESCRIPTION and
        len(name.string.decode(name.getEncoding())) > 200):
      failed = True
      break

  if failed:
    yield WARN, ("A few name table entries with ID={} (NameID.DESCRIPTION)"
                 " are longer than 200 characters."
                 " Please check whether those entries are copyright notices"
                 " mistakenly stored in the description string entries by"
                 " a bug in an old FontLab version."
                 " If that's the case, then such copyright notices must be"
                 " removed from these entries."
                 "").format(NameID.DESCRIPTION)
  else:
    yield PASS, "All description name records have reasonably small lengths."


@condition
def ttfautohint_stats(font):
  from ttfautohint import ttfautohint, libttfautohint
  from io import BytesIO
  from fontTools.ttLib import TTFont
  from fontbakery.specifications.shared_conditions import is_ttf

  if not is_ttf(TTFont(font)):
    return None

  original_buffer = BytesIO()
  TTFont(font).save(original_buffer)
  dehinted_buffer = ttfautohint(in_buffer=original_buffer.getvalue(),
                                dehint=True)
  return {
    "dehinted_size": len(dehinted_buffer),
    "hinted_size": os.stat(font).st_size,
    "version": libttfautohint.version_string
  }

@check(
  id = 'com.google.fonts/check/054',
  conditions = ['is_ttf',
                'ttfautohint_stats']
)
def com_google_fonts_check_054(font, ttfautohint_stats):
  """Show hinting filesize impact.

     Current implementation simply logs useful info
     but there's no fail scenario for this checker."""

  hinted = ttfautohint_stats["hinted_size"]
  dehinted = ttfautohint_stats["dehinted_size"]
  increase = hinted - dehinted
  change = (float(hinted)/dehinted - 1) * 100

  def filesize_formatting(s):
    if s < 1024:
      return f"{s} bytes"
    elif s < 1024*1024:
      return "{:.1f}kb".format(s/1024)
    else:
      return "{:.1f}Mb".format(s/(1024*1024))

  hinted_size = filesize_formatting(hinted)
  dehinted_size = filesize_formatting(dehinted)
  increase = filesize_formatting(increase)

  results_table = "Hinting filesize impact:\n\n"
  results_table += f"|  | {font} |\n"
  results_table += "|:--- | ---:|\n"
  results_table += f"| Dehinted Size | {dehinted_size} |\n"
  results_table += f"| Hinted Size | {hinted_size} |\n"
  results_table += f"| Increase | {increase} |\n"
  results_table += f"| Change   | {change:.1f} % |\n"
  yield INFO, results_table


@check(
  id = 'com.google.fonts/check/055'
)
def com_google_fonts_check_055(ttFont):
  """Version format is correct in 'name' table?"""
  from fontbakery.utils import get_name_entry_strings
  import re
  def is_valid_version_format(value):
    return re.match(r'Version\s0*[1-9]+\.\d+', value)

  failed = False
  version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    yield FAIL, Message("no-version-string",
                        ("Font lacks a NameID.VERSION_STRING (nameID={})"
                         " entry").format(NameID.VERSION_STRING))
  for ventry in version_entries:
    if not is_valid_version_format(ventry):
      failed = True
      yield FAIL, Message("bad-version-strings",
                          ("The NameID.VERSION_STRING (nameID={}) value must"
                           " follow the pattern \"Version X.Y\" with X.Y"
                           " between 1.000 and 9.999."
                           " Current version string is:"
                           " \"{}\"").format(NameID.VERSION_STRING,
                                             ventry))
  if not failed:
    yield PASS, "Version format in NAME table entries is correct."


@check(
  id = 'com.google.fonts/check/has_ttfautohint_params',
)
def com_google_fonts_check_has_ttfautohint_params(ttFont):
  """ Font has ttfautohint params? """
  from fontbakery.utils import get_name_entry_strings

  def ttfautohint_version(value):
    # example string:
    #'Version 1.000; ttfautohint (v0.93) -l 8 -r 50 -G 200 -x 14 -w "G"
    import re
    results = re.search(r'ttfautohint \(v(.*)\) ([^;]*)', value)
    if results:
      return results.group(1), results.group(2)

  version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  failed = True
  for vstring in version_strings:
    values = ttfautohint_version(vstring)
    if values:
      ttfa_version, params = values
      if params:
        yield PASS, f"Font has ttfautohint params ({params})"
        failed = False
    else:
        yield SKIP, "Font appears to our heuristic as not hinted using ttfautohint."
        failed = False

  if failed:
    yield FAIL, "Font is lacking ttfautohint params on its version strings on the name table."


@check(
  id = 'com.google.fonts/check/056',
  conditions = ['is_ttf']
)
def com_google_fonts_check_056(ttFont, ttfautohint_stats):
  """Font has old ttfautohint applied?

     1. find which version was used, by inspecting name table entries

     2. find which version of ttfautohint is installed
  """
  from fontbakery.utils import get_name_entry_strings

  def ttfautohint_version(values):
    import re
    for value in values:
      results = re.search(r'ttfautohint \(v(.*)\)', value)
      if results:
        return results.group(1)

  def installed_version_is_newer(installed, used):
    installed = list(map(int, installed.split(".")))
    used = list(map(int, used.split(".")))
    return installed > used

  if not ttfautohint_stats:
    yield ERROR, "ttfautohint is not available."
    return

  version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
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
        yield PASS, (f"ttfautohint available in the system ({installed_ttfa}) is older"
                     f" than the one used in the font ({ttfa_version}).")
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
#  import ipdb; ipdb.set_trace()
  if "EPAR" not in ttFont:
    yield INFO, ("EPAR table not present in font."
                 " To learn more see"
                 " https://github.com/googlefonts/"
                 "fontbakery/issues/818")
  else:
    yield PASS, "EPAR table present in font."


@check(
  id = 'com.google.fonts/check/062',
  conditions = ['is_ttf'],
  rationale = """
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
)
def com_google_fonts_check_062(ttFont):
  """Is 'gasp' table set to optimize rendering?"""

  if "gasp" not in ttFont.keys():
    yield FAIL, ("Font is missing the 'gasp' table."
                 " Try exporting the font with autohinting enabled.")
  else:
    if not isinstance(ttFont["gasp"].gaspRange, dict):
      yield FAIL, "'gasp' table has no values."
    else:
      failed = False
      if 0xFFFF not in ttFont["gasp"].gaspRange:
        yield WARN, ("'gasp' table does not have an entry for all"
                     " font sizes (gaspRange 0xFFFF).")
      else:
        gasp_meaning = {
          0x01: "- Use gridfitting",
          0x02: "- Use grayscale rendering",
          0x04: "- Use gridfitting with ClearType symmetric smoothing",
          0x08: "- Use smoothing along multiple axes with ClearType®"
        }
        table = []
        for key in ttFont["gasp"].gaspRange.keys():
          value = ttFont["gasp"].gaspRange[key]
          meaning = []
          for flag, info in gasp_meaning.items():
            if value & flag:
              meaning.append(info)

          meaning = "\n\t".join(meaning)
          table.append(f"PPM <= {key}:\n\tflag = 0x{value:02X}\n\t{meaning}")

        table = "\n".join(table)
        yield INFO, ("These are the ppm ranges declared on the"
                    f" gasp table:\n\n{table}\n")

        for key in ttFont["gasp"].gaspRange.keys():
          if key != 0xFFFF:
            yield WARN, ("'gasp' table has a gaspRange of {} that"
                         " may be unneccessary.").format(key)
            failed = True
          else:
            value = ttFont["gasp"].gaspRange[0xFFFF]
            if value != 0x0F:
              failed = True
              yield WARN, (f"gaspRange 0xFFFF value 0x{value:02X}"
                            " should be set to 0x0F.")
        if not failed:
          yield PASS, ("'gasp' table is correctly set, with one "
                       "gaspRange:value of 0xFFFF:0x0F.")


@check(
  id = 'com.google.fonts/check/067'
)
def com_google_fonts_check_067(ttFont):
  """Make sure family name does not begin with a digit.

     Font family names which start with a numeral are often not
     discoverable in Windows applications.
  """
  from fontbakery.utils import get_name_entry_strings
  failed = False
  for familyname in get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME):
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
      yield WARN, f"Font lacks \"{charname}\" character (unicode: 0x{codepoint:04X})"

  for codepoint, charname in MANDATORY.items():
    if not font_has_char(ttFont, codepoint):
      failed = True
      yield FAIL, f"Font lacks \"{charname}\" character (unicode: 0x{codepoint:04X})"

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
  bad_entries = []
  for name in ttFont["name"].names:
    if name.nameID == NameID.COPYRIGHT_NOTICE or \
       name.nameID == NameID.POSTSCRIPT_NAME:
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


@condition
def listed_on_gfonts_api(family_metadata):
  if not family_metadata:
    return False

  import requests
  url = ('http://fonts.googleapis.com'
         '/css?family={}').format(family_metadata.name.replace(' ', '+'))
  r = requests.get(url)
  return r.status_code == 200


@check(
  id = 'com.google.fonts/check/081',
  conditions = ['family_metadata']
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
  conditions = ['family_metadata']
)
def com_google_fonts_check_082(family_metadata):
  """METADATA.pb: Designer exists in Google Fonts profiles.csv?"""
  PROFILES_GIT_URL = ("https://github.com/google/"
                      "fonts/blob/master/designers/profiles.csv")
  PROFILES_RAW_URL = ("https://raw.githubusercontent.com/google/"
                      "fonts/master/designers/profiles.csv")
  if family_metadata.designer == "":
    yield FAIL, ("METADATA.pb field \"designer\" MUST NOT be empty!")
  elif family_metadata.designer == "Multiple Designers":
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
      if family_metadata.designer not in designers:
        yield WARN, ("METADATA.pb: Designer \"{}\" is not listed"
                     " in profiles.csv"
                     " (at \"{}\")").format(family_metadata.designer,
                                            PROFILES_GIT_URL)
      else:
        yield PASS, ("Found designer \"{}\""
                     " at profiles.csv").format(family_metadata.designer)
    except:
      yield WARN, f"Failed to fetch \"{PROFILES_RAW_URL}\""


@check(
  id = 'com.google.fonts/check/083',
  conditions = ['family_metadata']
)
def com_google_fonts_check_083(family_metadata):
  """METADATA.pb: check if fonts field only has
     unique "full_name" values.
  """
  fonts = {}
  for f in family_metadata.fonts:
    fonts[f.full_name] = f

  if len(set(fonts.keys())) != len(family_metadata.fonts):
    yield FAIL, ("Found duplicated \"full_name\" values"
                 " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique \"full_name\" values.")


@check(
  id = 'com.google.fonts/check/084',
  conditions = ['family_metadata']
)
def com_google_fonts_check_084(family_metadata):
  """METADATA.pb: check if fonts field
     only contains unique style:weight pairs.
  """
  pairs = {}
  for f in family_metadata.fonts:
    styleweight = f"{f.style}:{f.weight}"
    pairs[styleweight] = 1
  if len(set(pairs.keys())) != len(family_metadata.fonts):
    yield FAIL, ("Found duplicated style:weight pair"
                 " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique style:weight pairs.")


@check(
  id = 'com.google.fonts/check/085',
  conditions = ['family_metadata']
)
def com_google_fonts_check_085(family_metadata):
  """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
  licenses = ["APACHE2", "OFL", "UFL"]
  if family_metadata.license in licenses:
    yield PASS, ("Font license is declared"
                 " in METADATA.pb as \"{}\"").format(family_metadata.license)
  else:
    yield FAIL, ("METADATA.pb license field (\"{}\")"
                 " must be one of the following:"
                 " {}").format(family_metadata.license,
                               licenses)


@check(
  id = 'com.google.fonts/check/086',
  conditions = ['family_metadata']
)
def com_google_fonts_check_086(family_metadata):
  """METADATA.pb should contain at least "menu" and "latin" subsets."""
  missing = []
  for s in ["menu", "latin"]:
    if s not in list(family_metadata.subsets):
      missing.append(s)

  if missing != []:
    yield FAIL, ("Subsets \"menu\" and \"latin\" are mandatory,"
                 " but METADATA.pb is missing"
                 " \"{}\"").format(" and ".join(missing))
  else:
    yield PASS, "METADATA.pb contains \"menu\" and \"latin\" subsets."


@check(
  id = 'com.google.fonts/check/087',
  conditions = ['family_metadata']
)
def com_google_fonts_check_087(family_metadata):
  """METADATA.pb subsets should be alphabetically ordered."""
  expected = list(sorted(family_metadata.subsets))

  if list(family_metadata.subsets) != expected:
    yield FAIL, ("METADATA.pb subsets are not sorted "
                 "in alphabetical order: Got ['{}']"
                 " and expected ['{}']").format("', '".join(family_metadata.subsets),
                                                "', '".join(expected))
  else:
    yield PASS, "METADATA.pb subsets are sorted in alphabetical order."


@check(
  id = 'com.google.fonts/check/088',
  conditions = ['family_metadata']
)
def com_google_fonts_check_088(family_metadata):
  """METADATA.pb: Copyright notice is the same in all fonts?"""
  copyright = None
  fail = False
  for f in family_metadata.fonts:
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
  conditions = ['family_metadata']
)
def com_google_fonts_check_089(family_metadata):
  """Check that METADATA.pb family values are all the same."""
  name = ""
  fail = False
  for f in family_metadata.fonts:
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
def has_regular_style(family_metadata):
  fonts = family_metadata.fonts if family_metadata else []
  for f in fonts:
    if f.weight == 400 and f.style == "normal":
      return True
  return False


@check(
  id = 'com.google.fonts/check/090',
  conditions = ['family_metadata']
)
def com_google_fonts_check_090(family_metadata):
  """METADATA.pb: According Google Fonts standards,
     families should have a Regular style.
  """
  if has_regular_style(family_metadata):
    yield PASS, "Family has a Regular style."
  else:
    yield FAIL, ("This family lacks a Regular"
                 " (style: normal and weight: 400)"
                 " as required by Google Fonts standards.")


@check(
  id = 'com.google.fonts/check/091',
  conditions = ['family_metadata',
                'has_regular_style']
)
def com_google_fonts_check_091(family_metadata):
  """METADATA.pb: Regular should be 400."""
  badfonts = []
  for f in family_metadata.fonts:
    if f.full_name.endswith("Regular") and f.weight != 400:
      badfonts.append(f"{f.filename} (weight: {f.weight})")
  if len(badfonts) > 0:
    yield FAIL, ("METADATA.pb: Regular font weight must be 400."
                 " Please fix these: {}").format(", ".join(badfonts))
  else:
    yield PASS, "Regular has weight = 400."


@condition
def font_metadata(family_metadata, font):
  if not family_metadata:
    return

  for f in family_metadata.fonts:
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

  familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
  if not familynames:
      familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
  if len(familynames) == 0:
    yield FAIL, Message("missing",
                        ("This font lacks a FONT_FAMILY_NAME entry"
                         " (nameID={}) in the name"
                         " table.").format(NameID.FONT_FAMILY_NAME))
  else:
    if font_metadata.name not in familynames:
      yield FAIL, Message("mismatch",
                          ("Unmatched family name in font:"
                           " TTF has \"{}\" while METADATA.pb"
                           " has \"{}\"").format(familynames[0],
                                                 font_metadata.name))
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

  postscript_names = get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME)
  if len(postscript_names) == 0:
    failed = True
    yield FAIL, Message("missing",
                        ("This font lacks a POSTSCRIPT_NAME"
                         " entry (nameID={}) in the "
                         "name table.").format(NameID.POSTSCRIPT_NAME))
  else:
    for psname in postscript_names:
      if psname != font_metadata.post_script_name:
        failed = True
        yield FAIL, Message("mismatch",
                            ("Unmatched postscript name in font:"
                             " TTF has \"{}\" while METADATA.pb"
                             " has \"{}\"."
                             "").format(psname,
                                        font_metadata.post_script_name))
  if not failed:
    yield PASS, ("Postscript name \"{}\" is identical"
                 " in METADATA.pb and on the"
                 " TTF file.").format(font_metadata.post_script_name)


@check(
  id = 'com.google.fonts/check/094',
  conditions = ['font_metadata']
)
def com_google_fonts_check_094(ttFont, font_metadata):
  """METADATA.pb font.full_name value matches
     fullname declared on the name table?
  """
  from fontbakery.utils import get_name_entry_strings

  full_fontnames = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
  if len(full_fontnames) == 0:
    yield FAIL, Message("lacks-entry",
                        ("This font lacks a FULL_FONT_NAME"
                         " entry (nameID={}) in the"
                         " name table.").format(NameID.FULL_FONT_NAME))
  else:
    for full_fontname in full_fontnames:
      if full_fontname != font_metadata.full_name:
        yield FAIL, Message("mismatch",
                            ("Unmatched fullname in font:"
                             " TTF has \"{}\" while METADATA.pb"
                             " has \"{}\".").format(full_fontname,
                                                    font_metadata.full_name))
      else:
        yield PASS, ("Font fullname \"{}\" is identical"
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
  from fontbakery.constants import RIBBI_STYLE_NAMES

  if style in RIBBI_STYLE_NAMES:
    font_familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    nameid = NameID.FONT_FAMILY_NAME
  else:
    font_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    nameid = NameID.TYPOGRAPHIC_FAMILY_NAME

  if len(font_familynames) == 0:
    yield FAIL, Message("lacks-entry",
                        (f"This font lacks a {NameID(nameid).name} entry"
                         f" (nameID={nameid}) in the name table."))
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
  """METADATA.pb font.full_name and font.post_script_name
     fields have equivalent values ?
  """
  import re
  regex = re.compile(r"\W")
  post_script_name = regex.sub("", font_metadata.post_script_name)
  fullname = regex.sub("", font_metadata.full_name)
  if fullname != post_script_name:
    yield FAIL, ("METADATA.pb font full_name=\"{}\""
                 " does not match post_script_name ="
                 " \"{}\"").format(font_metadata.full_name,
                                   font_metadata.post_script_name)
  else:
    yield PASS, ("METADATA.pb font fields \"full_name\" and"
                 " \"post_script_name\" have equivalent values.")


@check(
  id = 'com.google.fonts/check/097',
  conditions = ['font_metadata']
)
def com_google_fonts_check_097(font_metadata, is_variable_font):
  """METADATA.pb font.filename and font.post_script_name
     fields have equivalent values?
  """
  post_script_name = font_metadata.post_script_name
  filename = os.path.splitext(font_metadata.filename)[0]

  if is_variable_font:
    valid_varfont_suffixes = [
      ("-VF", "Regular"),
      ("Roman", "Regular"),
      ("Roman-VF", "Regular"),
      ("Italic", "Italic"),
      ("Italic-VF", "Italic"),
    ]
    for valid_suffix, style in valid_varfont_suffixes:
      if valid_suffix in filename:
        filename = style.join(filename.split(valid_suffix))

  if filename != post_script_name:
    yield FAIL, ("METADATA.pb font filename=\"{}\" does not match"
                 " post_script_name=\"{}\"."
                 "").format(font_metadata.filename,
                            font_metadata.post_script_name)
  else:
    yield PASS, ("METADATA.pb font fields \"filename\" and"
                 " \"post_script_name\" have equivalent values.")


@condition
def font_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  return get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)


@condition
def typographic_familynames(ttFont):
  from fontbakery.utils import get_name_entry_strings
  return get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)


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

  failed = False
  for font_familyname in familynames:
    if font_familyname not in font_metadata.name:
      failed = True
      yield FAIL, ("METADATA.pb font.name field (\"{}\")"
                   " does not match correct font name format (\"{}\")."
                   "").format(font_metadata.name,
                              font_familyname)
  if not failed:
    yield PASS, ("METADATA.pb font.name field contains"
                 " font name in right format.")


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
                'family_metadata']
)
def com_google_fonts_check_100(font,
                               family_metadata):
  """METADATA.pb font.filename field contains font name in right format?"""
  expected = os.path.basename(font)
  failed = True
  for font_metadata in family_metadata.fonts:
    if font_metadata.filename == expected:
      failed = False
      yield PASS, ("METADATA.pb filename field contains"
                   " font name in right format.")
      break
  if failed:
    yield FAIL, ("None of the METADATA.pb filename fields match"
                f" correct font name format (\"{expected}\").")


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
def com_google_fonts_check_102(ttFont, font_metadata):
  """Copyright notices match canonical pattern?"""
  import re
  from fontbakery.utils import get_name_entry_strings

  testcases = [('METADATA.pb', font_metadata.copyright)]
  for entry in get_name_entry_strings(ttFont, NameID.COPYRIGHT_NOTICE):
    testcases.append(('Name table entry', entry))

  failed = False
  for case, value in testcases:
    does_match = re.search(r'Copyright [0-9]{4} The .* Project Authors \([^\@]*\)',
                           value)
    if does_match:
      yield PASS, ("{}: Copyright field '{}'"
                   " matches canonical pattern.").format(case, value)
    else:
      failed = True
      yield FAIL, ("{}: Copyright notices should match"
                   " a pattern similar to:"
                   " 'Copyright 2017 The Familyname"
                   " Project Authors (git url)'\n"
                   "But instead we have got:"
                   " '{}'").format(case, value)

  if not failed:
    yield PASS, "All copyright notice strings are good."


@check(
  id = 'com.google.fonts/check/103',
  conditions = ['font_metadata']
)
def com_google_fonts_check_103(font_metadata):
  """Copyright notice on METADATA.pb should not contain 'Reserved Font Name'."""
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
  """METADATA.pb: Copyright notice shouldn't exceed 500 chars."""
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
  return f"{familyname}-{style_weight}.ttf"


@check(
  id = 'com.google.fonts/check/105',
  conditions = ['font_metadata',
                'canonical_filename']
)
def com_google_fonts_check_105(font_metadata,
                               canonical_filename,
                               is_variable_font):
  """METADATA.pb: Filename is set canonically?"""

  if is_variable_font:
    valid_varfont_suffixes = [
      ("-VF", "Regular"),
      ("Roman", "Regular"),
      ("Roman-VF", "Regular"),
      ("Italic", "Italic"),
      ("Italic-VF", "Italic"),
    ]
    for valid_suffix, style in valid_varfont_suffixes:
      if valid_suffix in canonical_filename:
        canonical_filename = style.join(canonical_filename.split(valid_suffix))

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
  from fontbakery.constants import MacStyle

  if font_metadata.style != "italic":
    yield SKIP, "This check only applies to italic fonts."
  else:
    font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
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

      if not bool(ttFont["head"].macStyle & MacStyle.ITALIC):
        yield FAIL, Message("bad-macstyle",
                            "METADATA.pb style has been set to italic"
                            " but font macStyle is improperly set.")
      elif not font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL, Message("bad-fullfont-name",
                            ("Font macStyle Italic bit is set"
                             " but nameID {} (\"{}\") is not ended with"
                             " \"Italic\"").format(NameID.FULL_FONT_NAME,
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
  from fontbakery.constants import MacStyle

  if font_metadata.style != "normal":
    yield SKIP, "This check only applies to normal fonts."
    # FIXME: declare a common condition called "normal_style"
  else:
    font_familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
    if len(font_familyname) == 0 or len(font_fullname) == 0:
      yield SKIP, ("Font lacks familyname and/or"
                   " fullname entries in name table.")
      # FIXME: This is the same SKIP condition as in check/106
      #        so we definitely need to address them with a common condition!
    else:
      font_familyname = font_familyname[0]
      font_fullname = font_fullname[0]

      if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
        yield FAIL, Message("bad-macstyle",
                            ("METADATA.pb style has been set to normal"
                             " but font macStyle is improperly set."))
      elif font_familyname.split("-")[-1].endswith('Italic'):
        yield FAIL, Message("familyname-italic",
                            ("Font macStyle indicates a non-Italic font, but"
                             " nameID {} (FONT_FAMILY_NAME: \"{}\") ends with"
                             " \"Italic\".").format(NameID.FONT_FAMILY_NAME,
                                                    font_familyname))
      elif font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL, Message("fullfont-italic",
                            ("Font macStyle indicates a non-Italic font but"
                             " nameID {} (FULL_FONT_NAME: \"{}\") ends with"
                             " \"Italic\".").format(NameID.FULL_FONT_NAME,
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

  font_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
  if font_familynames:
      font_familyname = font_familynames[0]
  else:
      font_familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)[0]
  font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)[0]
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
  """METADATA.pb: Check if fontname is not camel cased."""
  import re
  if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
    yield FAIL, ("METADATA.pb: '{}' is a CamelCased name."
                 " To solve this, simply use spaces"
                 " instead in the font name.").format(font_metadata.name)
  else:
    yield PASS, "Font name is not camel-cased."


@check(
  id = 'com.google.fonts/check/110',
  conditions = ['family_metadata',      # that's the family-wide metadata!
                'font_metadata'] # and this one's specific to a single file
)
def com_google_fonts_check_110(family_metadata, font_metadata):
  """METADATA.pb: Check font name is the same as family name."""
  if font_metadata.name != family_metadata.name:
    yield FAIL, ("METADATA.pb: {}: Family name \"{}\""
                 " does not match"
                 " font name: \"{}\"").format(font_metadata.filename,
                                              family_metadata.name,
                                              font_metadata.name)
  else:
    yield PASS, "Font name is the same as family name."


@check(
  id = 'com.google.fonts/check/111',
  conditions = ['font_metadata']
)
def com_google_fonts_check_111(font_metadata):
  """METADATA.pb: Check that font weight has a canonical value."""
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
  """METADATA.pb weight matches postScriptName."""
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
  """METADATA.pb: Font styles are named canonically?"""
  from fontbakery.constants import MacStyle

  def find_italic_in_name_table():
    for entry in ttFont["name"].names:
      if entry.nameID < 256 and "italic" in entry.string.decode(entry.getEncoding()).lower():
        return True
    return False

  def is_italic():
    return (ttFont["head"].macStyle & MacStyle.ITALIC or
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
  id = 'com.google.fonts/check/116',
  rationale = """
  Even though the OpenType spec allows unitsPerEm to
  be any value between 16 and 16384, the Google Fonts
  project aims at a narrower set of reasonable values.

  The spec suggests usage of powers of two in order
  to get some performance improvements on legacy
  renderers, so those values are acceptable.

  But value of 500 or 1000 are also acceptable, with
  the added benefit that it makes upm math easier for
  designers, while the performance hit of not using
  a power of two is most likely negligible nowadays.

  Another acceptable value is 2000.
  Since TT outlines are all integers (no floats),
  then instances in a VF suffer rounding compromises,
  and therefore a 1000 UPM is to small because it
  forces too many such compromises.
  Therefore 2000 is a good 'new VF standard',
  because 2000 is a simple 2x conversion from existing
  fonts drawn on a 1000 UPM, and anyone who knows
  what 10 units can do for 1000 UPM will know what
  20 units does too.

  Additionally, values above 2048 would
  result in filesize increases with not much
  added benefit.
  """
)
def com_google_fonts_check_116(ttFont):
  """ Stricter unitsPerEm criteria for Google Fonts. """
  upm_height = ttFont["head"].unitsPerEm
  ACCEPTABLE = [16, 32, 64, 128, 256, 500,
                512, 1000, 1024, 2000, 2048]
  if upm_height not in ACCEPTABLE:
    yield FAIL, (f"Font em size (unitsPerEm) is {upm_height}."
                  " If possible, please consider using 1000"
                  " or even 2000 (which is ideal for"
                  " Variable Fonts)."
                  " The acceptable values for unitsPerEm,"
                 f" though, are: {ACCEPTABLE}.")
  elif upm_height != 2000:
    yield WARN, (f"Even though unitsPerEm ({upm_height}) in"
                  " this font is reasonable. It is strongly"
                  " advised to consider changing it to 2000,"
                  " since it will likely improve the quality of"
                  " Variable Fonts by avoiding excessive"
                  " rounding of coordinates on interpolations.")
  else:
    yield PASS, "Font em size is good (unitsPerEm = 2000)."


@condition
def remote_styles(family_metadata):
  """Get a dictionary of TTFont objects of all font files of
     a given family as currently hosted at Google Fonts.
  """

  def download_family_from_Google_Fonts(family_name):
    """Return a zipfile containing a font family hosted on fonts.google.com"""
    from zipfile import ZipFile
    from fontbakery.utils import download_file
    url_prefix = 'https://fonts.google.com/download?family='
    url = '{}{}'.format(url_prefix, family_name.replace(' ', '+'))
    return ZipFile(download_file(url))


  def fonts_from_zip(zipfile):
    '''return a list of fontTools TTFonts'''
    from fontTools.ttLib import TTFont
    from io import BytesIO
    fonts = []
    for file_name in zipfile.namelist():
      if file_name.lower().endswith(".ttf"):
        file_obj = BytesIO(zipfile.open(file_name).read())
        fonts.append([file_name, TTFont(file_obj)])
    return fonts

  if (not listed_on_gfonts_api(family_metadata) or
      not family_metadata):
    return None

  remote_fonts_zip = download_family_from_Google_Fonts(family_metadata.name)
  rstyles = {}

  for remote_filename, remote_font in fonts_from_zip(remote_fonts_zip):
    remote_style = os.path.splitext(remote_filename)[0]
    if '-' in remote_style:
      remote_style = remote_style.split('-')[1]
    rstyles[remote_style] = remote_font
  return rstyles


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
  from urllib.request import HTTPError
  LICENSE_DIRECTORY = {
    "OFL.txt": "ofl",
    "UFL.txt": "ufl",
    "LICENSE.txt": "apache"
  }
  filename = os.path.basename(ttFont.reader.file.name)
  fontname = filename.split('-')[0].lower()
  url = ("https://github.com/google/fonts/raw/master"
         "/{}/{}/{}").format(LICENSE_DIRECTORY[license],
                             fontname,
                             filename)
  try:
    fontfile = download_file(url)
    return TTFont(fontfile)
  except HTTPError:
    return None


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
  id = 'com.google.fonts/check/129',
  conditions = ['style']
)
def com_google_fonts_check_129(ttFont, style):
  """Checking OS/2 fsSelection value."""
  from fontbakery.utils import check_bit_entry
  from fontbakery.constants import (STYLE_NAMES,
                                    RIBBI_STYLE_NAMES,
                                    FsSelection)

  # Checking fsSelection REGULAR bit:
  expected = "Regular" in style or \
             (style in STYLE_NAMES and
              style not in RIBBI_STYLE_NAMES and
              "Italic" not in style)
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FsSelection.REGULAR,
                        bitname="REGULAR")

  # Checking fsSelection ITALIC bit:
  expected = "Italic" in style
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FsSelection.ITALIC,
                        bitname="ITALIC")

  # Checking fsSelection BOLD bit:
  expected = style in ["Bold", "BoldItalic"]
  yield check_bit_entry(ttFont, "OS/2", "fsSelection",
                        expected,
                        bitmask=FsSelection.BOLD,
                        bitname="BOLD")


@check(
  id = 'com.google.fonts/check/130',
  conditions = ['style'],
  rationale = """The 'post' table italicAngle property should be a
  reasonable amount, likely not more than -20°, never more than -30°,
  and never greater than 0°. Note that in the OpenType specification,
  the value is negative for a lean rightwards.
  https://docs.microsoft.com/en-us/typography/opentype/spec/post"""
)
def com_google_fonts_check_130(ttFont, style):
  """Checking post.italicAngle value."""
  failed = False
  value = ttFont["post"].italicAngle

  # Checking that italicAngle <= 0
  if value > 0:
    failed = True
    yield FAIL, Message("positive",
                        ("The value of post.italicAngle is positive, which"
                         " is likely a mistake and should become negative,"
                         " from {} to {}.").format(value, -value))

  # Checking that italicAngle is less than 20° (not good) or 30° (bad)
  # Also note we invert the value to check it in a clear way
  if abs(value) > 30:
    failed = True
    yield FAIL, Message("over -30 degrees",
                        ("The value of post.italicAngle ({}) is very"
                         " high (over -30°!) and should be"
                         " confirmed.").format(value))
  elif abs(value) > 20:
    failed = True
    yield WARN, Message("over -20 degrees",
                        ("The value of post.italicAngle ({}) seems very"
                         " high (over -20°!) and should be"
                         " confirmed.").format(value))


  # Checking if italicAngle matches font style:
  if "Italic" in style:
    if ttFont['post'].italicAngle == 0:
      failed = True
      yield FAIL, Message("zero-italic",
                          ("Font is italic, so post.italicAngle"
                           " should be non-zero."))
  else:
    if ttFont["post"].italicAngle != 0:
      failed = True
      yield FAIL, Message("non-zero-normal",
                          ("Font is not italic, so post.italicAngle"
                           " should be equal to zero."))

  if not failed:
    yield PASS, ("Value of post.italicAngle is {}"
                 " with style='{}'.").format(value, style)


@check(
  id = 'com.google.fonts/check/131',
  conditions = ['style'],
  rationale = """
  The values of the flags on the macStyle entry on the 'head' OpenType
  table that describe whether a font is bold and/or italic
  must be coherent with the actual style of the font as inferred
  by its filename.
  """
)
def com_google_fonts_check_131(ttFont, style):
  """Checking head.macStyle value."""
  from fontbakery.utils import check_bit_entry
  from fontbakery.constants import MacStyle

  # Checking macStyle ITALIC bit:
  expected = "Italic" in style
  yield check_bit_entry(ttFont, "head", "macStyle",
                        expected,
                        bitmask=MacStyle.ITALIC,
                        bitname="ITALIC")

  # Checking macStyle BOLD bit:
  expected = style in ["Bold", "BoldItalic"]
  yield check_bit_entry(ttFont, "head", "macStyle",
                        expected,
                        bitmask=MacStyle.BOLD,
                        bitname="BOLD")


@check(
  id = 'com.google.fonts/check/153',
  conditions = ['is_ttf',
                'not is_variable_font'],
  rationale = """
    Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
    be constructured in a handful of ways. This means a glyph's contour count
    will only differ slightly amongst different fonts, e.g a 'g' could either
    be 2 or 3 contours, depending on whether its double story or single story.
    However, a quotedbl should have 2 contours, unless the font belongs to a
    display family.

    This check currently does not cover variable fonts because there's plenty
    of alternative ways of constructing glyphs with multiple outlines for each
    feature in a VarFont. The expected contour count data for this check is
    currently optimized for the typical construction of glyphs in static fonts.
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
      cmap = ttFont['cmap'].getcmap(PlatformID.WINDOWS,
                                    WindowsEncodingID.UNICODE_BMP).cmap
      bad_glyphs_name = [("Glyph name: {}\t"
                          "Contours detected: {}\t"
                          "Expected: {}").format(cmap[name],
                                                 count,
                                                 pretty_print_list(expected))
                         for name, count, expected in bad_glyphs]
      yield WARN, (("This check inspects the glyph outlines and detects the"
                    " total number of contours in each of them. The expected"
                    " values are infered from the typical ammounts of"
                    " contours observed in a large collection of reference"
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
  from unidecode import unidecode
  failed = False
  for nameRecord in ttFont['name'].names:
    string = nameRecord.string.decode(nameRecord.getEncoding())
    if nameRecord.nameID == NameID.COPYRIGHT_NOTICE and\
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
                                   'K2D': 'K2D',
                                   'PressStart2P': 'Press Start 2P',
                                   'ABeeZee': 'ABeeZee',
                                   'IBMPlexMono': 'IBM Plex Mono',
                                   'IBMPlexSans': 'IBM Plex Sans',
                                   'IBMPlexSerif': 'IBM Plex Serif'}
  if not familyname:
    return None

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


@check(
  id = 'com.google.fonts/check/156',
  conditions = ['style'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_156(ttFont, style):
  """Font has all mandatory 'name' table entries ?"""
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import RIBBI_STYLE_NAMES

  required_nameIDs = [NameID.FONT_FAMILY_NAME,
                      NameID.FONT_SUBFAMILY_NAME,
                      NameID.FULL_FONT_NAME,
                      NameID.POSTSCRIPT_NAME]
  if style not in RIBBI_STYLE_NAMES:
    required_nameIDs += [NameID.TYPOGRAPHIC_FAMILY_NAME,
                         NameID.TYPOGRAPHIC_SUBFAMILY_NAME]
  failed = False
  # The font must have at least these name IDs:
  for nameId in required_nameIDs:
    if len(get_name_entry_strings(ttFont, nameId)) == 0:
      failed = True
      yield FAIL, (f"Font lacks entry with nameId={nameId}"
                   f" ({NameID(nameId).name})")
  if not failed:
    yield PASS, "Font contains values for all mandatory name table entries."


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
  return onlyWeight.get(value, value)


@check(
  id = 'com.google.fonts/check/157',
  conditions = ['style',
                'familyname_with_spaces'],
  rationale = """
    Checks that the family name infered from the font filename
    matches the string at nameID 1 (NAMEID_FONT_FAMILY_NAME)
    if it conforms to RIBBI and otherwise checks that nameID 1
    is the family name + the style name.
  """,
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_157(ttFont, style, familyname_with_spaces):
  """ Check name table: FONT_FAMILY_NAME entries. """
  from fontbakery.utils import name_entry_id
  failed = False
  only_weight = get_only_weight(style)
  for name in ttFont['name'].names:
    if name.nameID == NameID.FONT_FAMILY_NAME:

      if name.platformID == PlatformID.MACINTOSH:
        expected_value = familyname_with_spaces

      elif name.platformID == PlatformID.WINDOWS:
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
        failed = True
        yield FAIL, ("Entry {} on the 'name' table: "
                     "Expected '{}' "
                     "but got '{}'.").format(name_entry_id(name),
                                             expected_value,
                                             string)
  if not failed:
    yield PASS, "FONT_FAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/158',
  conditions = ['style_with_spaces',
                'familyname_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_158(ttFont,
                               style_with_spaces,
                               familyname_with_spaces):
  """ Check name table: FONT_SUBFAMILY_NAME entries. """
  from fontbakery.utils import name_entry_id

  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NameID.FONT_SUBFAMILY_NAME:
      if name.platformID == PlatformID.MACINTOSH:
        expected_value = style_with_spaces

      elif name.platformID == PlatformID.WINDOWS:
        if style_with_spaces in ["Bold", "Bold Italic"]:
          expected_value = style_with_spaces
        else:
          if "Italic" in style_with_spaces:
            expected_value = "Italic"
          else:
            expected_value = "Regular"
      else:
        yield FAIL, Message("invalid-entry",
                            ("Font should not have a "
                             "{} entry!").format(name_entry_id(name)))
        failed = True
        continue

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        yield FAIL, Message("bad-familyname",
                            ("Entry {} on the 'name' table: "
                             "Expected '{}' "
                             "but got '{}'.").format(name_entry_id(name),
                                                     expected_value,
                                                     string))

  if not failed:
    yield PASS, "FONT_SUBFAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/159',
  conditions = ['style_with_spaces',
                'familyname_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_159(ttFont,
                               style_with_spaces,
                               familyname_with_spaces):
  """ Check name table: FULL_FONT_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id
  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NameID.FULL_FONT_NAME:
      expected_value = "{} {}".format(familyname_with_spaces,
                                      style_with_spaces)
      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        # special case
        # see https://github.com/googlefonts/fontbakery/issues/1436
        if style_with_spaces == "Regular" \
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
  conditions = ['style',
                'familyname'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_160(ttFont, style, familyname):
  """ Check name table: POSTSCRIPT_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id

  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NameID.POSTSCRIPT_NAME:
      expected_value = f"{familyname}-{style}"

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
  conditions = ['style',
                'familyname_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_161(ttFont, style, familyname_with_spaces):
  """ Check name table: TYPOGRAPHIC_FAMILY_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id

  failed = False
  if style in ['Regular',
               'Italic',
               'Bold',
               'BoldItalic']:
    for name in ttFont['name'].names:
      if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
        failed = True
        yield FAIL, Message("ribbi",
                            ("Font style is '{}' and, for that reason,"
                             " it is not expected to have a "
                             "{} entry!").format(style,
                                                 name_entry_id(name)))
  else:
    expected_value = familyname_with_spaces
    has_entry = False
    for name in ttFont['name'].names:
      if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
        string = name.string.decode(name.getEncoding()).strip()
        if string == expected_value:
          has_entry = True
        else:
          failed = True
          yield FAIL, Message("non-ribbi-bad-value",
                              ("Entry {} on the 'name' table: "
                               "Expected '{}' "
                               "but got '{}'.").format(name_entry_id(name),
                                                       expected_value,
                                                       unidecode(string)))
    if not failed and not has_entry:
      failed = True
      yield FAIL, Message("non-ribbi-lacks-entry",
                          ("non-RIBBI fonts must have a"
                           " TYPOGRAPHIC_FAMILY_NAME entry"
                           " on the name table."))
  if not failed:
    yield PASS, "TYPOGRAPHIC_FAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/162',
  conditions=['style_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_162(ttFont, style_with_spaces):
  """ Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries. """
  from unidecode import unidecode
  from fontbakery.utils import name_entry_id

  failed = False
  if style_with_spaces in ['Regular',
                           'Italic',
                           'Bold',
                           'Bold Italic']:
    for name in ttFont['name'].names:
      if name.nameID == NameID.TYPOGRAPHIC_SUBFAMILY_NAME:
        failed = True
        yield FAIL, Message("ribbi",
                            ("Font style is '{}' and, for that reason,"
                             " it is not expected to have a "
                             "{} entry!").format(style_with_spaces,
                                                 name_entry_id(name)))
  else:
    expected_value = style_with_spaces
    has_entry = False
    for name in ttFont['name'].names:
      if name.nameID == NameID.TYPOGRAPHIC_SUBFAMILY_NAME:
        string = name.string.decode(name.getEncoding()).strip()
        if string == expected_value:
          has_entry = True
        else:
          failed = True
          yield FAIL, Message("non-ribbi-bad-value",
                              ("Entry {} on the 'name' table: "
                               "Expected '{}' "
                               "but got '{}'.").format(name_entry_id(name),
                                                       expected_value,
                                                       unidecode(string)))
    if not failed and not has_entry:
      failed = True
      yield FAIL, Message("non-ribbi-lacks-entry",
                          ("non-RIBBI fonts must have a"
                           " TYPOGRAPHIC_SUBFAMILY_NAME entry"
                           " on the name table."))
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

  failed = False
  for notice in get_name_entries(ttFont, NameID.COPYRIGHT_NOTICE):
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
  url = f"http://namecheck.fontdata.com/?q={familyname}"
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


@check(
  id = 'com.google.fonts/check/varfont/has_HVAR',
  rationale = """
  Not having a HVAR table can lead to costly
  text-layout operations on some platforms,
  which we want to avoid.

  So, all variable fonts on the Google Fonts
  collection should have an HVAR with valid values.

  More info on the HVAR table can be found at:
  https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements
  """, # FIX-ME: We should clarify which are these
       #         platforms in which there can be issues
       #         with costly text-layout operations
       #         when an HVAR table is missing!
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2119'
  })
def com_google_fonts_check_varfont_has_HVAR(ttFont):
  """ Check that variable fonts have an HVAR table. """
  if "HVAR" in ttFont.keys():
    yield PASS, ("This variable font contains an HVAR table.")
  else:
    yield FAIL, ("All variable fonts on the Google Fonts collection"
                 " must have a properly set HVAR table in order"
                 " to avoid costly text-layout operations on"
                 " certain platforms.")


# Temporarily disabled.
# See: https://github.com/googlefonts/fontbakery/issues/2118#issuecomment-432283698
@disable
@check(
  id = 'com.google.fonts/check/varfont/has_MVAR',
  rationale = """
  Per the OpenType spec, the MVAR tables contain
  variation data for metadata otherwise in tables
  such as OS/2 and hhea; if not present, then
  the default values in those tables will apply
  to all instances, which can effect text layout.

  Thus, MVAR tables should be present and correct
  in all variable fonts since text layout software
  depends on these values.
  """, # FIX-ME: Clarify this rationale text.
       #         See: https://github.com/googlefonts/fontbakery/issues/2118#issuecomment-432108560
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2118'
  })
def com_google_fonts_check_varfont_has_MVAR(ttFont):
  """ Check that variable fonts have an MVAR table. """
  if "MVAR" in ttFont.keys():
    yield PASS, ("This variable font contains an MVAR table.")
  else:
    yield FAIL, ("All variable fonts on the Google Fonts collection"
                 " must have a properly set MVAR table because"
                 " text-layout software depends on it.")


@check(
  id = 'com.google.fonts/check/040',
  conditions = ['vmetrics']
)
def com_google_fonts_check_040(ttFont, vmetrics):
  """Checking OS/2 usWinAscent & usWinDescent.

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
  the win values to values greater than the yMax and abs(yMin).
  """
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
    yield FAIL, Message(
        "descent", ("OS/2.usWinDescent value"
                    " should be equal or greater than {}, but got"
                    " {} instead").format(
                        abs(vmetrics['ymin']), ttFont['OS/2'].usWinDescent))
  if not failed:
    yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"


@check(
  id = 'com.google.fonts/check/042',
  rationale = """When OS/2 and hhea vertical metrics match, the same
  linespacing results on macOS, GNU+Linux and Windows. Unfortunately as of 2018,
  Google Fonts has released many fonts with vertical metrics that don't match
  in this way. When we fix this issue in these existing families, we will
  create a visible change in line/paragraph layout for either Windows or macOS
  users, which will upset some of them.

  But we have a duty to fix broken stuff, and inconsistent paragraph layout is
  unacceptably broken when it is possible to avoid it.

  If users complain and prefer the old broken version, they are libre to take
  care of their own situation."""
)
def com_google_fonts_check_042(ttFont):
  """Checking OS/2 Metrics match hhea Metrics.

  OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, GNU+Linux and Windows.

  Mac OS X uses the hhea values.
  Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.
  """
  # OS/2 sTypoAscender and sTypoDescender match hhea ascent and descent
  if ttFont["OS/2"].sTypoAscender != ttFont["hhea"].ascent:
    yield FAIL, Message("ascender",
                        "OS/2 sTypoAscender and hhea ascent must be equal.")
  elif ttFont["OS/2"].sTypoDescender != ttFont["hhea"].descent:
    yield FAIL, Message("descender",
                        "OS/2 sTypoDescender and hhea descent must be equal.")
  else:
    yield PASS, ("OS/2.sTypoAscender/Descender values"
                 " match hhea.ascent/descent.")


@condition
def VTT_hinted(ttFont):
  # it seems that VTT is the only program that generates a TSI5 table
  return 'TSI5' in ttFont


@check(
  id = 'com.google.fonts/check/072',
  conditions = ['is_ttf',
                'not VTT_hinted']
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
  INSTRUCTIONS = b"\xb8\x01\xff\x85\xb0\x04\x8d"

  if ("prep" in ttFont and
      INSTRUCTIONS in ttFont["prep"].program.getBytecode()):
    yield PASS, ("'prep' table contains instructions"
                  " enabling smart dropout control.")
  else:
    yield FAIL, ("'prep' table does not contain TrueType "
                  " instructions enabling smart dropout control."
                  " To fix, export the font with autohinting enabled,"
                  " or run ttfautohint on the font, or run the "
                  " `gftools fix-nonhinting` script.")


@check(
  id = 'com.google.fonts/check/vttclean'
)
def com_google_fonts_check_vtt_clean(ttFont, vtt_talk_sources):
  """There must not be VTT Talk sources in the font."""

  if vtt_talk_sources:
    yield FAIL, ("Some tables containing VTT Talk (hinting) sources"
                 " were found in the font and should be removed in order"
                 " to reduce total filesize:"
                 " {}").format(", ".join(vtt_talk_sources))
  else:
    yield PASS, "There are no tables with VTT Talk sources embedded in the font."


@check(
  id = 'com.google.fonts/check/aat',
  rationale = """Apple's TrueType reference manual
  (https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  describes SFNT tables not in the Microsoft OpenType specification
  (https://docs.microsoft.com/en-us/typography/opentype/spec/)
  and these can sometimes sneak into final release files,
  but Google Fonts should only have OpenType tables."""
)
def com_google_fonts_check_aat(ttFont):
  """Are there unwanted Apple tables?"""
  UNWANTED_TABLES = {
    'EBSC', 'Zaph', 'acnt', 'ankr', 'bdat', 'bhed', 'bloc',
    'bmap', 'bsln', 'fdsc', 'feat', 'fond', 'gcid', 'just',
    'kerx', 'lcar', 'ltag', 'mort', 'morx', 'opbd', 'prop',
    'trak', 'xref'
  }
  unwanted_tables_found = []
  for table in ttFont.keys():
    if table in UNWANTED_TABLES:
      unwanted_tables_found.append(table)

  if len(unwanted_tables_found) > 0:
    yield FAIL, ("Unwanted AAT tables were found"
                 " in the font and should be removed, either by"
                 " fonttools/ttx or by editing them using the tool"
                 " they built with:"
                 " {}").format(", ".join(unwanted_tables_found))
  else:
    yield PASS, "There are no unwanted AAT tables."


@check(
  id = 'com.google.fonts/check/fvar_name_entries',
  conditions = ['is_variable_font'],
  rationale = """
  The purpose of this check is to make sure that all
  name entries referenced by variable font instances
  do exist in the name table.
  """
)
def com_google_fonts_check_fvar_name_entries(ttFont):
  """All name entries referenced by fvar instances exist on the name table?"""

  failed = False
  for instance in ttFont["fvar"].instances:

    entries = [entry for entry in ttFont["name"].names if entry.nameID == instance.subfamilyNameID]
    if len(entries) == 0:
      failed = True
      yield FAIL, (f"Named instance with coordinates {instance.coordinates}"
                   f" lacks an entry on the name table (nameID={instance.subfamilyNameID}).")

  if not failed:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/varfont_has_instances',
  conditions = ['is_variable_font'],
  rationale = """
  Named instances must be present in all variable fonts.
  """
)
def com_google_fonts_check_varfont_has_instances(ttFont):
  """A variable font must have named instances."""

  if len(ttFont["fvar"].instances):
    yield PASS, "OK"
  else:
    yield FAIL, "This variable font lacks named instances on the fvar table."


@check(
  id = 'com.google.fonts/check/varfont_weight_instances',
  conditions = ['is_variable_font'],
  rationale = """
  The named instances on the weight axis of a variable font
  must have coordinates that are multiples of 100 on the design space.
  """
)
def com_google_fonts_check_varfont_weight_instances(ttFont):
  """Variable font weight coordinates must be multiples of 100."""

  failed = False
  for instance in ttFont["fvar"].instances:
    if 'wght' in instance.coordinates and instance.coordinates['wght'] % 100 != 0:
      failed = True
      yield FAIL, ("Found an variable font instance with"
                  f" 'wght'={instance.coordinates['wght']}."
                   " This should instead be a multiple of 100.")

  if not failed:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/tnum_horizontal_metrics',
  rationale = """
    Tabular figures need to have the same metrics in all styles
    in order to allow tables to be set with proper
    typographic control, but to maintain the placement of
    decimals and numeric columns between rows.

    Here's a good explanation of this:
    https://www.typography.com/techniques/fonts-for-financials/#tabular-figs
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2278'
  }
)
def com_google_fonts_check_tnum_horizontal_metrics(fonts):
  """All tabular figures must have the same width across the RIBBI-family."""
  from fontbakery.constants import RIBBI_STYLE_NAMES
  from fontTools.ttLib import TTFont
  RIBBI_ttFonts = [TTFont(f)
                   for f in fonts
                   if style(f) in RIBBI_STYLE_NAMES]
  tnum_widths = {}
  for ttFont in RIBBI_ttFonts:
    glyphs = ttFont.getGlyphSet()
    tnum_glyphs = [(glyph_id, glyphs[glyph_id])
                   for glyph_id in glyphs.keys()
                   if glyph_id.endswith(".tnum")]
    for glyph_id, glyph in tnum_glyphs:
      if glyph.width not in tnum_widths:
        tnum_widths[glyph.width] = [glyph_id]
      else:
        tnum_widths[glyph.width].append(glyph_id)

  if len(tnum_widths.keys()) > 1:
    max_num = 0
    most_common_width = None
    for width, glyphs in tnum_widths.items():
      if len(glyphs) > max_num:
        max_num = len(glyphs)
        most_common_width = width

    del tnum_widths[most_common_width]
    yield FAIL, (f"The most common tabular glyph width is {most_common_width}."
                  " But there are other tabular glyphs with different widths"
                 f" such as the following ones:\n\t{tnum_widths}.")
  else:
    yield PASS, "OK"


@condition
def is_hinted(ttFont):
  return "fpgm" in ttFont


@check(
  id = 'com.google.fonts/check/integer_ppem_if_hinted',
  conditions = ['is_hinted'],
  rationale = """
    Hinted fonts must have head table flag bit 3 set.

    Per https://docs.microsoft.com/en-us/typography/opentype/spec/head,
    bit 3 of Head::flags decides whether PPEM should be rounded.
    This bit should always be set for hinted fonts.

    Note:
    Bit 3 = Force ppem to integer values for all internal scaler math;
            May use fractional ppem sizes if this bit is clear;
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2338'
  }
)
def com_google_fonts_check_integer_ppem_if_hinted(ttFont):
  """PPEM must be an integer on hinted fonts."""

  if ttFont["head"].flags & (1 << 3):
    yield PASS, "OK"
  else:
    yield FAIL, ("This is a hinted font, so it must have bit 3 set"
                 " on the flags of the head table, so that PPEM values"
                 " will be rounded into and integer value.")


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
