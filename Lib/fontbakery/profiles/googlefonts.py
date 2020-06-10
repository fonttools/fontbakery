import os

from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.checkrunner import Section, INFO, WARN, ERROR, SKIP, PASS, FAIL
from fontbakery.callable import check, disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.constants import (PriorityLevel,
                                  NameID,
                                  PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID,
                                  MacintoshEncodingID,
                                  MacintoshLanguageID)


from .googlefonts_conditions import * # pylint: disable=wildcard-import,unused-wildcard-import
profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Google Fonts"))

METADATA_CHECKS = [
  'com.google.fonts/check/metadata/parses',
  'com.google.fonts/check/metadata/unknown_designer',
  'com.google.fonts/check/metadata/multiple_designers',
  'com.google.fonts/check/metadata/designer_values',
  'com.google.fonts/check/metadata/listed_on_gfonts',
  'com.google.fonts/check/metadata/unique_full_name_values',
  'com.google.fonts/check/metadata/unique_weight_style_pairs',
  'com.google.fonts/check/metadata/license',
  'com.google.fonts/check/metadata/menu_and_latin',
  'com.google.fonts/check/metadata/subsets_order',
  'com.google.fonts/check/metadata/copyright',
  'com.google.fonts/check/metadata/familyname',
  'com.google.fonts/check/metadata/has_regular',
  'com.google.fonts/check/metadata/regular_is_400',
  'com.google.fonts/check/metadata/nameid/family_name',
  'com.google.fonts/check/metadata/nameid/post_script_name',
  'com.google.fonts/check/metadata/nameid/full_name',
  'com.google.fonts/check/metadata/nameid/family_and_full_names', # FIXME! This seems redundant!
  'com.google.fonts/check/metadata/nameid/copyright',
  'com.google.fonts/check/metadata/nameid/font_name', # FIXME! This looks suspiciously similar to com.google.fonts/check/metadata/nameid/family_name
  'com.google.fonts/check/metadata/match_fullname_postscript',
  'com.google.fonts/check/metadata/match_filename_postscript',
  'com.google.fonts/check/metadata/match_weight_postscript',
  'com.google.fonts/check/metadata/valid_name_values',
  'com.google.fonts/check/metadata/valid_full_name_values',
  'com.google.fonts/check/metadata/valid_filename_values',
  'com.google.fonts/check/metadata/valid_post_script_name_values',
  'com.google.fonts/check/metadata/valid_copyright',
  'com.google.fonts/check/metadata/reserved_font_name',
  'com.google.fonts/check/metadata/copyright_max_length',
  'com.google.fonts/check/metadata/filenames',
  'com.google.fonts/check/metadata/italic_style',
  'com.google.fonts/check/metadata/normal_style',
  'com.google.fonts/check/metadata/fontname_not_camel_cased',
  'com.google.fonts/check/metadata/match_name_familyname',
  'com.google.fonts/check/metadata/canonical_weight_value',
  'com.google.fonts/check/metadata/os2_weightclass',
  'com.google.fonts/check/metadata/canonical_style_names',
  'com.google.fonts/check/metadata/broken_links',
  'com.google.fonts/check/metadata/undeclared_fonts'
]

DESCRIPTION_CHECKS = [
  'com.google.fonts/check/description/broken_links',
  'com.google.fonts/check/description/valid_html',
  'com.google.fonts/check/description/min_length',
  'com.google.fonts/check/description/max_length',
  'com.google.fonts/check/description/git_url',
  'com.google.fonts/check/description/eof_linebreak'
]

FAMILY_CHECKS = [
#  'com.google.fonts/check/family/equal_numbers_of_glyphs',
#  'com.google.fonts/check/family/equal_glyph_names',
  'com.google.fonts/check/family/has_license',
  'com.google.fonts/check/family/control_chars',
  'com.google.fonts/check/family/tnum_horizontal_metrics',
]

NAME_TABLE_CHECKS = [
  'com.google.fonts/check/name/unwanted_chars',
  'com.google.fonts/check/name/license',
  'com.google.fonts/check/name/license_url',
  'com.google.fonts/check/name/family_and_style_max_length',
  'com.google.fonts/check/name/line_breaks',
  'com.google.fonts/check/name/rfn',
]

REPO_CHECKS = [
  'com.google.fonts/check/repo/dirname_matches_nameid_1',
  'com.google.fonts/check/repo/vf_has_static_fonts',
  'com.google.fonts/check/repo/fb_report',
  'com.google.fonts/check/repo/zip_files',
  'com.google.fonts/check/license/OFL_copyright'
]

FONT_FILE_CHECKS = [
  'com.google.fonts/check/glyph_coverage',
  'com.google.fonts/check/canonical_filename',
  'com.google.fonts/check/usweightclass',
  'com.google.fonts/check/fstype',
  'com.google.fonts/check/vendor_id',
  'com.google.fonts/check/ligature_carets',
  'com.google.fonts/check/production_glyphs_similarity',
  'com.google.fonts/check/fontv',
#DISABLED:   'com.google.fonts/check/production_encoded_glyphs',
  'com.google.fonts/check/varfont/generate_static',
  'com.google.fonts/check/kerning_for_non_ligated_sequences',
  'com.google.fonts/check/name/description_max_length',
  'com.google.fonts/check/fvar_name_entries',
  'com.google.fonts/check/version_bump',
  'com.google.fonts/check/epar',
  'com.google.fonts/check/font_copyright',
  'com.google.fonts/check/italic_angle',
  'com.google.fonts/check/has_ttfautohint_params',
  'com.google.fonts/check/name/version_format',
  'com.google.fonts/check/name/familyname_first_char',
  'com.google.fonts/check/hinting_impact',
  'com.google.fonts/check/varfont/has_HVAR',
  'com.google.fonts/check/name/typographicfamilyname',
  'com.google.fonts/check/name/subfamilyname',
  'com.google.fonts/check/name/typographicsubfamilyname',
  'com.google.fonts/check/gasp',
  'com.google.fonts/check/name/familyname',
  'com.google.fonts/check/name/mandatory_entries',
  'com.google.fonts/check/name/copyright_length',
  'com.google.fonts/check/fontdata_namecheck',
  'com.google.fonts/check/name/ascii_only_entries',
  'com.google.fonts/check/varfont_has_instances',
  'com.google.fonts/check/varfont_weight_instances',
  'com.google.fonts/check/old_ttfautohint',
  'com.google.fonts/check/vttclean',
  'com.google.fonts/check/name/postscriptname',
  'com.google.fonts/check/aat',
  'com.google.fonts/check/name/fullfontname',
  'com.google.fonts/check/mac_style',
  'com.google.fonts/check/fsselection',
  'com.google.fonts/check/smart_dropout',
  'com.google.fonts/check/integer_ppem_if_hinted',
  'com.google.fonts/check/unitsperem_strict',
  'com.google.fonts/check/contour_count',
  'com.google.fonts/check/vertical_metrics_regressions',
  'com.google.fonts/check/cjk_vertical_metrics',
  'com.google.fonts/check/varfont_instance_coordinates',
  'com.google.fonts/check/varfont_instance_names',
  'com.google.fonts/check/varfont/consistent_axes',
  'com.google.fonts/check/varfont/unsupported_axes'
]

GOOGLEFONTS_PROFILE_CHECKS = \
  UNIVERSAL_PROFILE_CHECKS + \
  METADATA_CHECKS + \
  DESCRIPTION_CHECKS + \
  FAMILY_CHECKS + \
  NAME_TABLE_CHECKS + \
  REPO_CHECKS + \
  FONT_FILE_CHECKS


@check(
  id = 'com.google.fonts/check/canonical_filename',
  rationale = """
    A font's filename must be composed in the following manner:
    <familyname>-<stylename>.ttf

    - Nunito-Regular.ttf,
    - Oswald-BoldItalic.ttf

    Variable fonts must list the axis tags in alphabetical order in square brackets and separated by commas:
  
    - Roboto[wdth,wght].ttf
    - Familyname-Italic[wght].ttf
  """,
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_canonical_filename(font):
  """Checking file is named canonically."""
  from fontTools.ttLib import TTFont
  from .shared_conditions import is_variable_font
  from .googlefonts_conditions import canonical_stylename
  from fontbakery.utils import suffix
  from fontbakery.constants import (STATIC_STYLE_NAMES,
                                    MacStyle)

  def variable_font_filename(ttFont):
    from fontbakery.utils import get_name_entry_strings
    familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)[0]
    typo_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    familyname = typo_familynames[0] if typo_familynames else familyname
    familyname = "".join(familyname.split(' ')) #remove spaces
    if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
      familyname+="-Italic"

    tags = ttFont["fvar"].axes
    tags = list(map(lambda t: t.axisTag, tags))
    tags.sort()
    tags = "[{}]".format(",".join(tags))
    return f"{familyname}{tags}.ttf"

  failed = False
  if "_" in os.path.basename(font):
    failed = True
    yield FAIL,\
          Message("invalid-char",
                  f'font filename "{font}" is invalid.'
                  f' It must not contain underscore characters!')
    return

  ttFont = TTFont(font)
  if is_variable_font(ttFont):
    if suffix(font) in STATIC_STYLE_NAMES:
      failed = True
      yield FAIL,\
            Message("varfont-with-static-filename",
                    "This is a variable font, but it is using"
                    " a naming scheme typical of a static font.")

    expected = variable_font_filename(ttFont)
    font_filename = os.path.basename(font)
    if font_filename != expected:
      failed = True
      yield FAIL,\
            Message("bad-varfont-filename",
                    f"The file '{font_filename}' must be renamed"
                    f" to '{expected}' according to the"
                    f" Google Fonts naming policy for variable fonts.")

  else:
    if not canonical_stylename(font):
      failed = True
      style_names = '", "'.join(STATIC_STYLE_NAMES)
      yield FAIL,\
            Message("bad-static-filename",
                    f'Style name used in "{font}" is not canonical.'
                    f' You should rebuild the font using'
                    f' any of the following'
                    f' style names: "{style_names}".')

  if not failed:
    yield PASS, f"{font} is named canonically."


@check(
  id = 'com.google.fonts/check/description/broken_links',
  conditions = ['description'],
  rationale = """
    The snippet of HTML in the DESCRIPTION.en_us.html file is added to the font family webpage on the Google Fonts website. For that reason, all hyperlinks in it must be properly working. 
  """
)
def com_google_fonts_check_description_broken_links(description):
  """Does DESCRIPTION file contain broken links?"""
  import requests
  from lxml import etree
  doc = etree.fromstring("<html>" + description + "</html>")
  broken_links = []
  for a_href in doc.iterfind('.//a[@href]'):
    link = a_href.get("href")
    if link.startswith("mailto:") and \
       "@" in link and \
       "." in link.split("@")[1]:
      yield INFO,\
            Message("email",
                    f"Found an email address: {link}")
      continue

    try:
      response = requests.head(link, allow_redirects=True, timeout=10)
      code = response.status_code
      if code != requests.codes.ok:
        broken_links.append(f"{link} (status code: {code})")
    except requests.exceptions.Timeout:
      yield WARN,\
            Message("timeout",
                    f"Timedout while attempting to access: '{link}'."
                    f" Please verify if that's a broken link.")
    except requests.exceptions.RequestException:
      broken_links.append(link)

  if len(broken_links) > 0:
    broken_links_list = '\n\t'.join(broken_links)
    yield FAIL,\
          Message("broken-links",
                  f"The following links are broken"
                  f" in the DESCRIPTION file:\n\t"
                  f"{broken_links_list}")
  else:
    yield PASS, "All links in the DESCRIPTION file look good!"


@check(
  id = 'com.google.fonts/check/description/git_url',
  conditions = ['description'],
  rationale = """
    The contents of the DESCRIPTION.en-us.html file are displayed on the Google Fonts website in the about section of each font family specimen page.

    Since all of the Google Fonts collection is composed of libre-licensed fonts, this check enforces a policy that there must be a hypertext link in that page directing users to the repository where the font project files are made available.

    Such hosting is typically done on sites like Github, Gitlab, GNU Savannah or any other git-based version control service.
  """
)
def com_google_fonts_check_description_git_url(description):
  """Does DESCRIPTION file contain a upstream Git repo URL?"""
  from lxml import etree
  doc = etree.fromstring("<html>" + description + "</html>")
  git_urls = []
  for a_href in doc.iterfind('.//a[@href]'):
    link = a_href.get("href")
    if "://git" in link:
      git_urls.append(link)
      yield INFO,\
            Message("url-found",
                    f"Found a git repo URL: {link}")

  if len(git_urls) > 0:
    yield PASS, "Looks great!"
  else:
    yield FAIL,\
          Message("lacks-git-url",
                  "Please host your font project on a public Git repo"
                  " (such as GitHub or GitLab) and place a link"
                  " in the DESCRIPTION.en_us.html file.")


@check(
  id = 'com.google.fonts/check/description/valid_html',
  conditions = ['descfile'],
  rationale = """
    When packaging families for being pushed to the `google/fonts` git repo, if there is no DESCRIPTION.en_us.html file, some older versions of the `add_font.py` tool insert a dummy description file which contains invalid html.

    This file needs to either be replaced with an existing description file or edited by hand.
  """
)
def com_google_fonts_check_description_valid_html(descfile, description):
  """Is this a proper HTML snippet?"""
  if "<p>" not in description or "</p>" not in description:
    yield FAIL,\
          Message("bad-html",
                  f"{descfile} does not look like a propper HTML snippet.")
  else:
    yield PASS, f"{descfile} is a propper HTML file."


@check(
  id = 'com.google.fonts/check/description/min_length',
  conditions = ['description']
)
def com_google_fonts_check_description_min_length(description):
  """DESCRIPTION.en_us.html must have more than 200 bytes."""
  if len(description) <= 200:
    yield FAIL,\
          Message("too-short",
                  "DESCRIPTION.en_us.html must"
                  " have size larger than 200 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is larger than 200 bytes."


@check(
  id = 'com.google.fonts/check/description/max_length',
  conditions = ['description']
)
def com_google_fonts_check_description_max_length(description):
  """DESCRIPTION.en_us.html must have less than 1000 bytes."""
  if len(description) >= 1000:
    yield FAIL,\
          Message("too-long",
                  "DESCRIPTION.en_us.html must"
                  " have size smaller than 1000 bytes.")
  else:
    yield PASS, "DESCRIPTION.en_us.html is smaller than 1000 bytes."


@check(
  id = 'com.google.fonts/check/description/eof_linebreak',
  conditions = ['description'],
  rationale = """
    Some older text-handling tools sometimes misbehave if the last line of data in a text file is not terminated with a newline character (also known as '\\n').

    We know that this is a very small detail, but for the sake of keeping all DESCRIPTION.en_us.html files uniformly formatted throughout the GFonts collection, we chose to adopt the practice of placing this final linebreak char on them.
""",
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2879'
  }
)
def com_google_fonts_check_description_eof_linebreak(description):
  """DESCRIPTION.en_us.html should end in a linebreak."""
  if description[-1] != '\n':
    yield WARN,\
          Message("missing-eof-linebreak",
                  "The last characther on DESCRIPTION.en_us.html"
                  " is not a line-break. Please add it.")
  else:
    yield PASS, ":-)"


@check(
  id = 'com.google.fonts/check/metadata/parses',
  conditions = ['family_directory'],
  rationale = """
    The purpose of this check is to ensure that the METADATA.pb file is not malformed.
  """
)
def com_google_fonts_check_metadata_parses(family_directory):
  """Check METADATA.pb parse correctly."""
  from google.protobuf import text_format
  from fontbakery.utils import get_FamilyProto_Message
  try:
    pb_file = os.path.join(family_directory, "METADATA.pb")
    get_FamilyProto_Message(pb_file)
    yield PASS, "METADATA.pb parsed successfuly."
  except text_format.ParseError as e:
    yield FAIL,\
          Message("parsing-error",
                  f"Family metadata at {family_directory} failed to parse.\n"
                  f"TRACEBACK:\n{e}")
  except FileNotFoundError:
    yield SKIP, f"Font family at '{family_directory}' lacks a METADATA.pb file."


@check(
  id = 'com.google.fonts/check/metadata/unknown_designer',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_unknown_designer(family_metadata):
  """Font designer field in METADATA.pb must not be 'unknown'."""
  if family_metadata.designer.lower() == 'unknown':
    yield FAIL,\
          Message("unknown-designer",
                  f"Font designer field is '{family_metadata.designer}'.")
  else:
    yield PASS, "Font designer field is not 'unknown'."


@check(
  id = 'com.google.fonts/check/metadata/multiple_designers',
  conditions = ['family_metadata'],
  rationale = """
    For a while the string "Multiple designers" was used as a placeholder on METADATA.pb files. We should replace all those instances with actual designer names so that proper credits are displayed on the Google Fonts family specimen pages.

    If there's more than a single designer, the designer names must be separated by commas.
  """
)
def com_google_fonts_check_metadata_multiple_designers(family_metadata):
  """Font designer field in METADATA.pb must not contain 'Multiple designers'."""
  if 'multiple designer' in family_metadata.designer.lower():
    yield FAIL,\
          Message("multiple-designers",
                  f"Font designer field is '{family_metadata.designer}'."
                  f" Please add an explicit comma-separated list of designer names.")
  else:
    yield PASS, "Looks good."


@check(
  id = 'com.google.fonts/check/metadata/designer_values',
  conditions = ['family_metadata'],
  rationale = """
    We must use commas instead of forward slashes because the server-side code at the fonts.google.com directory will segment the string on the commas into a list of names and display the first item in the list as the "principal designer" while the remaining names are identified as "contributors".
   
    See eg https://fonts.google.com/specimen/Rubik
  """
)
def com_google_fonts_check_metadata_designer_values(family_metadata):
  """Multiple values in font designer field in
     METADATA.pb must be separated by commas."""

  if '/' in family_metadata.designer:
    yield FAIL,\
          Message("slash",
                  f"Font designer field contains a forward slash"
                  f" '{family_metadata.designer}'."
                  f" Please use commas to separate multiple names instead.")
  else:
    yield PASS, "Looks good."


@check(
  id = 'com.google.fonts/check/metadata/broken_links',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_broken_links(family_metadata):
  """Does METADATA.pb copyright field contain broken links?"""
  import requests
  broken_links = []
  for font_metadata in family_metadata.fonts:
    copyright = font_metadata.copyright
    if "mailto:" in copyright:
      yield INFO,\
            Message("email",
                    f"Found an email address: {copyright}")
      continue

    if "http" in copyright:
      link = "http" + copyright.split("http")[1]

      for endchar in [' ', ')']:
        if endchar in link:
          link = link.split(endchar)[0]

      try:
        response = requests.head(link, allow_redirects=True, timeout=10)
        code = response.status_code
        if code != requests.codes.ok:
          broken_links.append(("{} (status code: {})").format(link, code))
      except requests.exceptions.Timeout:
        yield WARN,\
              Message("timeout",
                      f"Timed out while attempting to access: '{link}'."
                      f" Please verify if that's a broken link.")
      except requests.exceptions.RequestException:
        broken_links.append(link)

  if len(broken_links) > 0:
    broken_links_list = '\n\t'.join(broken_links)
    yield FAIL,\
          Message("broken-links",
                  f"The following links are broken"
                  f" in the METADATA.pb file:\n\t"
                  f"{broken_links_list}")
  else:
    yield PASS, "All links in the METADATA.pb file look good!"


@check(
  id = 'com.google.fonts/check/metadata/undeclared_fonts',
  conditions = ['family_metadata'],
  rationale = """
    The set of font binaries available, except the ones on a "static" subdir, must match exactly those declared on the METADATA.pb file.

    Also, to avoid confusion, we expect that font files (other than statics) are not placed on subdirectories.
  """
)
def com_google_fonts_check_metadata_undeclared_fonts(family_metadata, family_directory):
  """Ensure METADATA.pb lists all font binaries."""

  pb_binaries = []
  for font_metadata in family_metadata.fonts:
    pb_binaries.append(font_metadata.filename)

  passed = True
  binaries = []
  for entry in os.listdir(family_directory):
    if entry != "static" and os.path.isdir(os.path.join(family_directory, entry)):
      for filename in os.listdir(os.path.join(family_directory, entry)):
        if filename[-4:] in [".ttf", ".otf"]:
          path = os.path.join(family_directory, entry, filename)
          passed = False
          yield WARN,\
                Message("font-on-subdir",
                        f'The file "{path}" is a font binary'
                        f' in a subdirectory.\n'
                        f'Please keep all font files (except VF statics) directly'
                        f' on the root directory side-by-side'
                        f' with its corresponding METADATA.pb file.')
    else:
      # Note: This does not include any font binaries placed in a "static" subdir!
      if entry[-4:] in [".ttf", ".otf"]:
        binaries.append(entry)


  for filename in set(pb_binaries) - set(binaries):
    passed = False
    yield FAIL,\
          Message("file-missing",
                  f'The file "{filename}" declared on METADATA.pb'
                  f' is not available in this directory.')


  for filename in set(binaries) - set(pb_binaries):
    passed = False
    yield FAIL,\
          Message("file-not-declared",
                  f'The file "{filename}" is not declared on METADATA.pb')

  if passed:
    yield PASS, "OK"



@disable # TODO: re-enable after addressing issue #1998
@check(
  id = 'com.google.fonts/check/family/equal_numbers_of_glyphs',
  conditions = ['are_ttf',
                'stylenames_are_canonical']
)
def com_google_fonts_check_family_equal_numbers_of_glyphs(ttFonts):
  """Fonts have equal numbers of glyphs?"""
  from .googlefonts_conditions import canonical_stylename

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

      yield FAIL,\
            Message("glyph-count-diverges",
                    f"{stylename} has {this_count} glyphs while"
                    f" {max_stylename} has {max_count} glyphs."
                    f" There are {diff_count} different glyphs"
                    f" among them: {diff}")
  if not failed:
    yield PASS, ("All font files in this family have"
                 " an equal total ammount of glyphs.")


@disable # TODO: re-enable after addressing issue #1998
@check(
  id = 'com.google.fonts/check/family/equal_glyph_names',
  conditions = ['are_ttf']
)
def com_google_fonts_check_family_equal_glyph_names(ttFonts):
  """Fonts have equal glyph names?"""
  from .googlefonts_conditions import style

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
    these_ones = set(ttFont["glyf"].glyphs.keys())
    for glyphname in all_glyphnames:
      if glyphname not in these_ones:
        failed = True
        missing[glyphname].append(fontname)
      else:
        available[glyphname].append(fontname)

  for gn in missing.keys():
    if missing[gn]:
      available_styles = [style(k) for k in available[gn]]
      missing_styles = [style(k) for k in missing[gn]]
      if None not in available_styles + missing_styles:
          # if possible, use stylenames in the log messages.
          avail = ', '.join(available_styles)
          miss = ', '.join(missing_styles)
      else:
          # otherwise, print filenames:
          avail = ', '.join(available[gn])
          miss = ', '.join(missing[gn])

      yield FAIL,\
            Message("missing-glyph",
                    f"Glyphname '{gn}' is defined on {avail}"
                    f" but is missing on {miss}.")

  if not failed:
    yield PASS, "All font files have identical glyph names."


@check(
  id = 'com.google.fonts/check/fstype',
  rationale = """
    The fsType in the OS/2 table is a legacy DRM-related field. Fonts in the Google Fonts collection must have it set to zero (also known as "Installable Embedding"). This setting indicates that the fonts can be embedded in documents and permanently installed by applications on remote systems.

    More detailed info is available at:
    https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
  """
)
def com_google_fonts_check_fstype(ttFont):
  """Checking OS/2 fsType does not impose restrictions."""
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

    yield FAIL,\
          Message("drm",
                  f"In this font fsType is set to {value} meaning that:\n"
                  f"{restrictions}\n"
                  f"\n"
                  f"No such DRM restrictions can be enabled on the"
                  f" Google Fonts collection, so the fsType field"
                  f" must be set to zero (Installable Embedding) instead.")
  else:
    yield PASS, "OS/2 fsType is properly set to zero."


@check(
  id = 'com.google.fonts/check/vendor_id',
  conditions = ['registered_vendor_ids'],
  rationale = """
    Microsoft keeps a list of font vendors and their respective contact info. This list is updated regularly and is indexed by a 4-char "Vendor ID" which is stored in the achVendID field of the OS/2 table.

    Registering your ID is not mandatory, but it is a good practice since some applications may display the type designer / type foundry contact info on some dialog and also because that info will be visible on Microsoft's website:

    https://docs.microsoft.com/en-us/typography/vendors/

    This check verifies whether or not a given font's vendor ID is registered in that list or if it has some of the default values used by the most common font editors.

    Each new FontBakery release includes a cached copy of that list of vendor IDs. If you registered recently, you're safe to ignore warnings emitted by this check, since your ID will soon be included in one of our upcoming releases.
  """
)
def com_google_fonts_check_vendor_id(ttFont, registered_vendor_ids):
  """Checking OS/2 achVendID."""

  SUGGEST_MICROSOFT_VENDORLIST_WEBSITE = (
    "If you registered it recently, then it's safe to ignore this warning message."
    " Otherwise, you should set it to your own unique 4 character code,"
    " and register it with Microsoft at"
    " https://www.microsoft.com/typography/links/vendorlist.aspx\n")

  vid = ttFont['OS/2'].achVendID
  bad_vids = ['UKWN', 'ukwn', 'PfEd']
  if vid is None:
    yield WARN,\
          Message("not set",
                  f"OS/2 VendorID is not set."
                  f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}")
  elif vid in bad_vids:
    yield WARN,\
          Message("bad",
                  f"OS/2 VendorID is '{vid}', a font editor default."
                  f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}")
  elif vid not in registered_vendor_ids.keys():
    yield WARN,\
          Message("unknown",
                  f"OS/2 VendorID value '{vid}' is not yet recognized."
                  f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}")
  else:
    yield PASS, f"OS/2 VendorID '{vid}' looks good!"


@check(
  id = 'com.google.fonts/check/glyph_coverage',
  rationale = """
    Google Fonts expects that fonts in its collection support at least the minimal set of characters defined in the `GF-latin-core` glyph-set.
  """
)
def com_google_fonts_check_glyph_coverage(ttFont):
  """Check `Google Fonts Latin Core` glyph coverage."""
  from fontbakery.utils import pretty_print_list
  from fontbakery.constants import GF_latin_core

  font_codepoints = set()
  for table in ttFont['cmap'].tables:
    if (table.platformID == PlatformID.WINDOWS and
        table.platEncID == WindowsEncodingID.UNICODE_BMP):
      font_codepoints.update(table.cmap.keys())

  required_codepoints = set(GF_latin_core.keys())
  diff = required_codepoints - font_codepoints
  if bool(diff):
    missing = ['0x%04X (%s)' % (c, GF_latin_core[c][1]) for c in sorted(diff)]
    yield FAIL,\
          Message("missing-codepoints",
                  f"Missing required codepoints:"
                  f" {pretty_print_list(missing, shorten=4)}")
    if len(missing) > 4:
      missing_list = "\n\t\t".join(missing)
      yield INFO,\
            Message("missing-codepoints-verbose",
                    f"Here's the full list of required codepoints"
                    f" still missing:\n\t\t{missing_list}")
  else:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/name/unwanted_chars'
)
def com_google_fonts_check_name_unwanted_chars(ttFont):
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
        yield FAIL,\
              Message("unwanted-chars",
                      f"NAMEID #{name.nameID} contains symbols that"
                      f" should be replaced by '{ascii_repl}'.")
        failed = True
  if not failed:
    yield PASS, ("No need to substitute copyright, registered and"
                 " trademark symbols in name table entries of this font.")


@check(
  id = 'com.google.fonts/check/usweightclass',
  conditions=['expected_style'],
  rationale = """
    Google Fonts expects variable fonts, static ttfs and static otfs to have differing OS/2 usWeightClass values.

    For Variable Fonts, Thin-Black must be 100-900
    For static ttfs, Thin-Black can be 100-900 or 250-900
    For static otfs, Thin-Black must be 250-900

    If static otfs are set lower than 250, text may appear blurry in legacy Windows applications.

    Glyphsapp users can change the usWeightClass value of an instance by adding a 'weightClass' customParameter.
  """
)
def com_google_fonts_check_usweightclass(ttFont, expected_style):
  """Checking OS/2 usWeightClass."""
  from fontbakery.profiles.shared_conditions import (
    is_ttf,
    is_cff,
    is_variable_font
  )

  failed = False
  expected_value = expected_style.usWeightClass
  weight_name = expected_style.name
  value = ttFont['OS/2'].usWeightClass
  has_expected_value = value == expected_value
  fail_message = \
    "OS/2 usWeightClass is '{}' when it should be '{}'."

  if is_variable_font(ttFont):
    if not has_expected_value:
      failed = True
      yield FAIL, Message(
        "bad-value",
        fail_message.format(value, expected_value)
      )
  # overrides for static Thin and ExtaLight fonts
  # for static ttfs, we don't mind if Thin is 250 and ExtraLight is 275.
  # However, if the values are incorrect we will recommend they set Thin
  # to 100 and ExtraLight to 250.
  # for static otfs, Thin must be 250 and ExtraLight must be 275
  elif "Thin" in weight_name:
    if is_ttf(ttFont) and value not in [100, 250]:
      failed = True
      yield FAIL, Message(
        "bad-value",
        fail_message.format(value, expected_value)
      )
    if is_cff(ttFont) and value != 250:
      failed = True
      yield FAIL, Message(
        "bad-value",
        fail_message.format(value, 250)
      )

  elif "ExtraLight" in weight_name:
    if is_ttf(ttFont) and value not in [200, 275]:
      failed = True
      yield FAIL, Message(
        "bad-value",
        fail_message.format(value, expected_value)
      )
    if is_cff(ttFont) and value != 275:
      failed = True
      yield FAIL, Message(
        "bad-value",
        fail_message.format(value, 275)
      )

  elif not has_expected_value:
    failed = True
    yield FAIL, Message(
      "bad-value",
      fail_message.format(value, expected_value)
    )

  if not failed:
    yield PASS, "OS/2 usWeightClass is good"


@check(
  id = 'com.google.fonts/check/family/has_license',
  conditions=['gfonts_repo_structure'],
)
def com_google_fonts_check_family_has_license(licenses):
  """Check font has a license."""
  from fontbakery.utils import pretty_print_list

  if len(licenses) > 1:
    filenames = [os.path.basename(f) for f in licenses]
    yield FAIL,\
          Message("multiple",
                  f"More than a single license file found:"
                  f" {pretty_print_list(filenames)}")
  elif not licenses:
    yield FAIL,\
          Message("no-license",
                  "No license file was found."
                  " Please add an OFL.txt or a LICENSE.txt file."
                  " If you are running fontbakery on a Google Fonts"
                  " upstream repo, which is fine, just make sure"
                  " there is a temporary license file in the same folder.")
  else:
    yield PASS, "Found license at '{}'".format(licenses[0])


@check(
  id = 'com.google.fonts/check/license/OFL_copyright',
  conditions = ['license_contents'],
  rationale = """
    An OFL.txt file's first line should be the font copyright e.g:
    "Copyright 2019 The Montserrat Project Authors (https://github.com/julietaula/montserrat)"
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2764'
  })
def com_google_fonts_check_license_OFL_copyright(license_contents):
  """Check license file has good copyright string."""
  import re
  string = license_contents.strip().split('\n')[0].lower()
  does_match = re.search(r'copyright [0-9]{4}(\-[0-9]{4})? the .* project authors \([^\@]*\)', string)
  if does_match:
    yield PASS, "looks good"
  else:
    yield FAIL, (f'First line in license file does not match expected format:'
                 f' "{string}"')


@check(
  id = 'com.google.fonts/check/name/license',
  conditions = ['license'],
  rationale = """
    A known licensing description must be provided in the NameID 14 (LICENSE DESCRIPTION) entries of the name table.

    The source of truth for this check (to determine which license is in use) is a file placed side-by-side to your font project including the licensing terms.

    Depending on the chosen license, one of the following string snippets is expected to be found on the NameID 13 (LICENSE DESCRIPTION) entries of the name table:
    - "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL"
    - "Licensed under the Apache License, Version 2.0"
    - "Licensed under the Ubuntu Font Licence 1.0."


    Currently accepted licenses are Apache or Open Font License.
    For a small set of legacy families the Ubuntu Font License may be acceptable as well.

    When in doubt, please choose OFL for new font projects.
  """,
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  })
def com_google_fonts_check_name_license(ttFont, license):
  """Check copyright namerecords match license file."""
  from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT
  failed = False
  http_warn = False
  placeholder = PLACEHOLDER_LICENSING_TEXT[license]
  entry_found = False
  for i, nameRecord in enumerate(ttFont["name"].names):
    if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
      entry_found = True
      value = nameRecord.toUnicode()
      if "http://" in value:
        yield WARN,\
              Message("http-in-description",
                      f'Please consider using HTTPS URLs at name table entry [plat={nameRecord.platformID}, enc={nameRecord.platEncID}, name={nameRecord.nameID}]')
        value = "https://".join(value.split("http://"))
        http_warn = True

      if value != placeholder:
        failed = True
        yield FAIL,\
              Message("wrong", \
                      f'License file {license} exists but'
                      f' NameID {NameID.LICENSE_DESCRIPTION}'
                      f' (LICENSE DESCRIPTION) value on platform'
                      f' {nameRecord.platformID}'
                      f' ({PlatformID(nameRecord.platformID).name})'
                      f' is not specified for that.'
                      f' Value was: "{value}"'
                      f' Must be changed to "{placeholder}"')
  if http_warn:
    yield WARN,\
          Message("http",
                  "For now we're still accepting http URLs,"
                  " but you should consider using https instead.\n")

  if not entry_found:
    yield FAIL,\
          Message("missing", \
                  f"Font lacks NameID {NameID.LICENSE_DESCRIPTION}"
                  f" (LICENSE DESCRIPTION). A proper licensing"
                  f" entry must be set.")
  elif not failed:
    yield PASS, "Licensing entry on name table is correctly set."


@check(
  id = 'com.google.fonts/check/name/license_url',
  rationale = """
    A known license URL must be provided in the NameID 14 (LICENSE INFO URL) entry of the name table.

    The source of truth for this check is the licensing text found on the NameID 13 entry (LICENSE DESCRIPTION).

    The string snippets used for detecting licensing terms are:
    - "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL"
    - "Licensed under the Apache License, Version 2.0"
    - "Licensed under the Ubuntu Font Licence 1.0."


    Currently accepted licenses are Apache or Open Font License.
    For a small set of legacy families the Ubuntu Font License may be acceptable as well.

    When in doubt, please choose OFL for new font projects.
  """,
  conditions = ['familyname'],
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_name_license_url(ttFont, familyname):
  """License URL matches License text on name table?"""
  from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT
  LEGACY_UFL_FAMILIES = ["Ubuntu", "UbuntuCondensed", "UbuntuMono"]
  LICENSE_URL = {
    'OFL.txt': 'https://scripts.sil.org/OFL',
    'LICENSE.txt': 'https://www.apache.org/licenses/LICENSE-2.0',
    'UFL.txt': 'https://www.ubuntu.com/legal/terms-and-policies/font-licence'
  }
  LICENSE_NAME = {
    'OFL.txt': 'Open Font',
    'LICENSE.txt': 'Apache',
    'UFL.txt': 'Ubuntu Font License'
  }
  detected_license = False
  http_warn = False
  for license in ['OFL.txt', 'LICENSE.txt', 'UFL.txt']:
    placeholder = PLACEHOLDER_LICENSING_TEXT[license]
    for nameRecord in ttFont['name'].names:
      string = nameRecord.string.decode(nameRecord.getEncoding())
      if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
        if "http://" in string:
          yield WARN,\
                Message("http-in-description",
                        f'Please consider using HTTPS URLs at name table entry [plat={nameRecord.platformID}, enc={nameRecord.platEncID}, name={nameRecord.nameID}]')
          string = "https://".join(string.split("http://"))
          http_warn = True

        if string == placeholder:
          detected_license = license
          break

  if detected_license == "UFL.txt" and familyname not in LEGACY_UFL_FAMILIES:
    yield FAIL,\
          Message("ufl",
                  "The Ubuntu Font License is only acceptable on"
                  " the Google Fonts collection for legacy font"
                  " families that already adopted such license."
                  " New Families should use eigther Apache or"
                  " Open Font License.")
  else:
    found_good_entry = False
    if not detected_license:
      yield SKIP, ("Could not infer the font license."
                   " Please ensure NameID 13 (LICENSE DESCRIPTION) is properly set.")
      return
    else:
      failed = False
      expected = LICENSE_URL[detected_license]
      for nameRecord in ttFont['name'].names:
        if nameRecord.nameID == NameID.LICENSE_INFO_URL:
          string = nameRecord.string.decode(nameRecord.getEncoding())
          if "http://" in string:
            yield WARN,\
                  Message("http-in-license-info",
                          f'Please consider using HTTPS URLs at name table entry [plat={nameRecord.platformID}, enc={nameRecord.platEncID}, name={nameRecord.nameID}]')
            string = "https://".join(string.split("http://"))
          if string == expected:
            found_good_entry = True
          else:
            failed = True
            yield FAIL,\
                  Message("licensing-inconsistency",
                          f"Licensing inconsistency in name table entries!"
                          f" NameID={NameID.LICENSE_DESCRIPTION}"
                          f" (LICENSE DESCRIPTION) indicates"
                          f" {LICENSE_NAME[detected_license]} licensing,"
                          f" but NameID={NameID.LICENSE_INFO_URL}"
                          f" (LICENSE URL) has '{string}'."
                          f" Expected: '{expected}'")
    if http_warn:
      yield WARN,\
            Message("http",
                    "For now we're still accepting http URLs,"
                    " but you should consider using https instead.\n")

    if not found_good_entry:
      yield FAIL,\
            Message("no-license-found",
                    f"A known license URL must be provided in"
                    f" the NameID {NameID.LICENSE_INFO_URL}"
                    f" (LICENSE INFO URL) entry."
                    f" Currently accepted licenses are"
                    f" Apache: '{LICENSE_URL['LICENSE.txt']}'"
                    f" or Open Font License: '{LICENSE_URL['OFL.txt']}'"
                    f"\n"
                    f"For a small set of legacy families the Ubuntu"
                    f" Font License '{LICENSE_URL['UFL.txt']}' may be"
                    f" acceptable as well."
                    f"\n"
                    f"When in doubt, please choose OFL for"
                    f" new font projects.")
    else:
      if failed:
        yield FAIL,\
              Message("bad-entries",
                      f"Even though a valid license URL was seen in the"
                      f" name table, there were also bad entries."
                      f" Please review NameIDs {NameID.LICENSE_DESCRIPTION}"
                      f" (LICENSE DESCRIPTION) and {NameID.LICENSE_INFO_URL}"
                      f" (LICENSE INFO URL).")
      else:
        yield PASS, "Font has a valid license URL in NAME table."


@check(
  id = 'com.google.fonts/check/name/description_max_length',
  rationale = """
    An old FontLab version had a bug which caused it to store copyright notices in nameID 10 entries.

    In order to detect those and distinguish them from actual legitimate usage of this name table entry, we expect that such strings do not exceed a reasonable length of 200 chars.

    Longer strings are likely instances of the FontLab bug.
  """
)
def com_google_fonts_check_name_description_max_length(ttFont):
  """Description strings in the name table must not exceed 200 characters."""
  failed = False
  for name in ttFont['name'].names:
    if (name.nameID == NameID.DESCRIPTION and
        len(name.string.decode(name.getEncoding())) > 200):
      failed = True
      break

  if failed:
    yield WARN,\
          Message("too-long",
                  f"A few name table entries with ID={NameID.DESCRIPTION}"
                  f" (NameID.DESCRIPTION) are longer than 200 characters."
                  f" Please check whether those entries are copyright"
                  f" notices mistakenly stored in the description"
                  f" string entries by a bug in an old FontLab version."
                  f" If that's the case, then such copyright notices"
                  f" must be removed from these entries.")
  else:
    yield PASS, "All description name records have reasonably small lengths."


@check(
  id = 'com.google.fonts/check/hinting_impact',
  conditions = ['hinting_stats'],
  rationale = """
    This check is merely informative, displaying and useful comparison of filesizes of hinted versus unhinted font files.
  """
)
def com_google_fonts_check_hinting_impact(font, hinting_stats):
  """Show hinting filesize impact."""
  hinted = hinting_stats["hinted_size"]
  dehinted = hinting_stats["dehinted_size"]
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

  yield INFO,\
        Message("size-impact",
                f"Hinting filesize impact:\n"
                f"\n"
                f"\t|  | {font} |\n"
                f"\t|:--- | ---:|\n"
                f"\t| Dehinted Size | {dehinted_size} |\n"
                f"\t| Hinted Size | {hinted_size} |\n"
                f"\t| Increase | {increase} |\n"
                f"\t| Change   | {change:.1f} % |\n")


@check(
  id = 'com.google.fonts/check/name/version_format'
)
def com_google_fonts_check_name_version_format(ttFont):
  """Version format is correct in 'name' table?"""
  from fontbakery.utils import get_name_entry_strings
  import re
  def is_valid_version_format(value):
    return re.match(r'Version\s0*[1-9][0-9]*\.\d+', value)

  failed = False
  version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    yield FAIL,\
          Message("no-version-string",
                  f"Font lacks a NameID.VERSION_STRING"
                  f" (nameID={NameID.VERSION_STRING}) entry")
  for ventry in version_entries:
    if not is_valid_version_format(ventry):
      failed = True
      yield FAIL,\
            Message("bad-version-strings",
                    f'The NameID.VERSION_STRING'
                    f' (nameID={NameID.VERSION_STRING}) value must'
                    f' follow the pattern "Version X.Y" with X.Y'
                    f' greater than or equal to 1.000.'
                    f' Current version string is: "{ventry}"')
  if not failed:
    yield PASS, "Version format in NAME table entries is correct."


@check(
  id = 'com.google.fonts/check/has_ttfautohint_params',
)
def com_google_fonts_check_has_ttfautohint_params(ttFont):
  """Font has ttfautohint params?"""
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
        yield PASS,\
              Message("ok",
                      f"Font has ttfautohint params ({params})")
        failed = False
    else:
      yield SKIP,\
            Message("not-hinted",
                    "Font appears to our heuristic as"
                    " not hinted using ttfautohint.")
      failed = False

  if failed:
    yield FAIL,\
          Message("lacks-ttfa-params",
                  "Font is lacking ttfautohint params on its"
                  " version strings on the name table.")


@check(
  id = 'com.google.fonts/check/old_ttfautohint',
  conditions = ['is_ttf'],
  rationale = """
    This check finds which version of ttfautohint was used, by inspecting name table entries and then finds which version of ttfautohint is currently installed in the system.
  """
)
def com_google_fonts_check_old_ttfautohint(ttFont, hinting_stats):
  """Font has old ttfautohint applied?"""
  from fontbakery.utils import get_name_entry_strings

  def ttfautohint_version(values):
    import re
    for value in values:
      results = re.search(r'ttfautohint \(v(.*)\)', value)
      if results:
        return results.group(1)

  def installed_version_is_newer(installed, used):
    # development versions may include a git commit hash
    # for now we will simply ignore it:
    installed = installed.split("-")[0]
    used = used.split("-")[0]

    installed = list(map(int, installed.split(".")))
    used = list(map(int, used.split(".")))
    return installed > used

  if not hinting_stats:
    yield ERROR,\
          Message("not-available",
                  "ttfautohint is not available.")
    return

  version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  ttfa_version = ttfautohint_version(version_strings)
  if len(version_strings) == 0:
    yield FAIL,\
          Message("lacks-version-strings",
                  "This font file lacks mandatory "
                  "version strings in its name table.")
  elif ttfa_version is None:
    yield INFO,\
          Message("version-not-detected",
                  f"Could not detect which version of"
                  f" ttfautohint was used in this font."
                  f" It is typically specified as a comment"
                  f" in the font version entries of the 'name' table."
                  f" Such font version strings are currently:"
                  f" {version_strings}")
  else:
    installed_ttfa = hinting_stats["version"]
    try:
      if installed_version_is_newer(installed_ttfa,
                                    ttfa_version):
        yield WARN,\
              Message("old-ttfa",
                      f"ttfautohint used in font = {ttfa_version};"
                      f" installed = {installed_ttfa};"
                      f" Need to re-run with the newer version!")
      else:
        yield PASS, (f"ttfautohint available in the system ({installed_ttfa})"
                     f" is older than the one used in the font"
                     f" ({ttfa_version}).")
    except ValueError:
      yield FAIL,\
            Message("parse-error",
                    f"Failed to parse ttfautohint version values:"
                    f" installed = '{installed_ttfa}';"
                    f" used_in_font = '{ttfa_version}'")


@check(
  id = 'com.google.fonts/check/epar',
  rationale = """
    The EPAR table is/was a way of expressing common licensing permissions and restrictions in metadata; while almost nothing supported it, Dave Crossland wonders that adding it to everything in Google Fonts could help make it more popular.

    More info is available at:
    https://davelab6.github.io/epar/
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/226'
  }
)
def com_google_fonts_check_epar(ttFont):
  """EPAR table present in font?"""

  if "EPAR" not in ttFont:
    yield INFO,\
          Message("lacks-EPAR",
                  "EPAR table not present in font. To learn more see"
                  " https://github.com/googlefonts/fontbakery/issues/818")
  else:
    yield PASS, "EPAR table present in font."


@check(
  id = 'com.google.fonts/check/gasp',
  conditions = ['is_ttf'],
  rationale = """
    Traditionally version 0 'gasp' tables were set so that font sizes below 8 ppem had no grid fitting but did have antialiasing. From 9-16 ppem, just grid fitting. And fonts above 17ppem had both antialiasing and grid fitting toggled on. The use of accelerated graphics cards and higher resolution screens make this approach obsolete. Microsoft's DirectWrite pushed this even further with much improved rendering built into the OS and apps.
   
    In this scenario it makes sense to simply toggle all 4 flags ON for all font sizes.
  """
)
def com_google_fonts_check_gasp(ttFont):
  """Is the Grid-fitting and Scan-conversion Procedure ('gasp') table
     set to optimize rendering?"""

  NON_HINTING_MESSAGE = ("If you are dealing with an unhinted font,"
                         " it can be fixed by running the fonts through"
                         " the command 'gftools fix-nonhinting'\n"
                         "GFTools is available at"
                         " https://pypi.org/project/gftools/")

  if "gasp" not in ttFont.keys():
    yield FAIL,\
          Message("lacks-gasp",
                  "Font is missing the 'gasp' table."
                  " Try exporting the font with autohinting enabled.\n" + \
                  NON_HINTING_MESSAGE)
  else:
    if not isinstance(ttFont["gasp"].gaspRange, dict):
      yield FAIL,\
            Message("empty",
                    "The 'gasp' table has no values.\n" + \
                    NON_HINTING_MESSAGE)
    else:
      failed = False
      if 0xFFFF not in ttFont["gasp"].gaspRange:
        yield WARN,\
              Message("lacks-ffff-range",
                      "The 'gasp' table does not have an entry"
                      " that applies for all font sizes."
                      " The gaspRange value for such entry should"
                      " be set to 0xFFFF.")
      else:
        gasp_meaning = {
          0x01: "- Use grid-fitting",
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
        yield INFO,\
              Message("ranges",
                      f"These are the ppm ranges declared on"
                      f" the gasp table:\n\n{table}\n")

        for key in ttFont["gasp"].gaspRange.keys():
          if key != 0xFFFF:
            yield WARN,\
                  Message("non-ffff-range",
                          f"The gasp table has a range of {key}"
                          f" that may be unneccessary.")
            failed = True
          else:
            value = ttFont["gasp"].gaspRange[0xFFFF]
            if value != 0x0F:
              failed = True
              yield WARN,\
                    Message("unset-flags",
                            f"The gasp range 0xFFFF value 0x{value:02X}"
                            f" should be set to 0x0F.")
        if not failed:
          yield PASS, ("The 'gasp' table is correctly set, with one "
                       "gaspRange:value of 0xFFFF:0x0F.")


@check(
  id = 'com.google.fonts/check/name/familyname_first_char',
  rationale = """
    Font family names which start with a numeral are often not discoverable in Windows applications.
  """
)
def com_google_fonts_check_name_familyname_first_char(ttFont):
  """Make sure family name does not begin with a digit."""
  from fontbakery.utils import get_name_entry_strings
  failed = False
  for familyname in get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME):
    digits = map(str, range(0, 10))
    if familyname[0] in digits:
      yield FAIL,\
            Message("begins-with-digit",
                    f"Font family name '{familyname}' begins with a digit!")
      failed = True
  if failed is False:
    yield PASS, "Font family name first character is not a digit."


@check(
  id = 'com.google.fonts/check/name/ascii_only_entries',
  rationale = """
    The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
   
    For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that string should be the same in CFF fonts which also have this requirement in the OpenType spec.

    Note:
    A common place where we find non-ASCII strings is on name table entries with NameID > 18, which are expressly for localising the ASCII-only IDs into Hindi / Arabic / etc.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1663'
  }
)
def com_google_fonts_check_name_ascii_only_entries(ttFont):
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
        badstring = string.encode("ascii",
                                  errors='xmlcharrefreplace')
        yield FAIL,\
              Message("bad-string",
                      (f"Bad string at"
                       f" [nameID {name.nameID}, '{name.getEncoding()}']:"
                       f" '{badstring}'"))
  if len(bad_entries) > 0:
    yield FAIL,\
          Message("non-ascii-strings",
                  (f"There are {len(bad_entries)} strings containing"
                    " non-ASCII characters in the ASCII-only"
                    " NAME table entries."))
  else:
    yield PASS, ("None of the ASCII-only NAME table entries"
                 " contain non-ASCII characteres.")


@check(
  id = 'com.google.fonts/check/metadata/listed_on_gfonts',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_listed_on_gfonts(listed_on_gfonts_api):
  """METADATA.pb: Fontfamily is listed on Google Fonts API?"""
  if not listed_on_gfonts_api:
    yield WARN,\
          Message("not-found",
                  "Family not found via Google Fonts API.")
  else:
    yield PASS, "Font is properly listed via Google Fonts API."


# Temporarily disabled as requested at
# https://github.com/googlefonts/fontbakery/issues/1728
@disable
@check(
  id = 'com.google.fonts/check/metadata/profiles_csv',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_profiles_csv(family_metadata):
  """METADATA.pb: Designer exists in Google Fonts profiles.csv?"""
  PROFILES_GIT_URL = ("https://github.com/google/"
                      "fonts/blob/master/designers/profiles.csv")
  PROFILES_RAW_URL = ("https://raw.githubusercontent.com/google/"
                      "fonts/master/designers/profiles.csv")
  if family_metadata.designer == "":
    yield FAIL,\
          Message("empty",
                  'METADATA.pb field "designer" MUST NOT be empty!')
  elif family_metadata.designer == "Multiple Designers":
    yield SKIP,\
          Message("multiple",
                  'Found "Multiple Designers" at METADATA.pb, which'
                  ' is OK, so we won\'t look for it at profiles.csv')
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
        yield WARN,\
              Message("not-listed",
                      f'METADATA.pb:'
                      f' Designer "{family_metadata.designer}" is'
                      f' not listed in CSV file at {PROFILES_GIT_URL}')
      else:
        yield PASS, ('Found designer "{family_metadata.designer}"'
                     ' at profiles.csv')
    except:
      yield WARN,\
            Message("csv-not-fetched",
                    f'Could not fetch "{PROFILES_RAW_URL}"')


@check(
  id = 'com.google.fonts/check/metadata/unique_full_name_values',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_unique_full_name_values(family_metadata):
  """METADATA.pb: check if fonts field only has
     unique "full_name" values.
  """
  fonts = {}
  for f in family_metadata.fonts:
    fonts[f.full_name] = f

  if len(set(fonts.keys())) != len(family_metadata.fonts):
    yield FAIL,\
          Message("duplicated",
                  'Found duplicated "full_name" values'
                  ' in METADATA.pb fonts field.')
  else:
    yield PASS, ('METADATA.pb "fonts" field only has'
                 ' unique "full_name" values.')


@check(
  id = 'com.google.fonts/check/metadata/unique_weight_style_pairs',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_unique_weight_style_pairs(family_metadata):
  """METADATA.pb: check if fonts field
     only contains unique style:weight pairs.
  """
  pairs = {}
  for f in family_metadata.fonts:
    styleweight = f"{f.style}:{f.weight}"
    pairs[styleweight] = 1
  if len(set(pairs.keys())) != len(family_metadata.fonts):
    yield FAIL,\
          Message("duplicated",
                  "Found duplicated style:weight pair"
                  " in METADATA.pb fonts field.")
  else:
    yield PASS, ("METADATA.pb \"fonts\" field only has"
                 " unique style:weight pairs.")


@check(
  id = 'com.google.fonts/check/metadata/license',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_license(family_metadata):
  """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
  expected_licenses = ["APACHE2", "OFL", "UFL"]
  if family_metadata.license in expected_licenses:
    yield PASS, (f'Font license is declared in METADATA.pb'
                 f' as "{family_metadata.license}"')
  else:
    yield FAIL,\
          Message("bad-license",
                  f'METADATA.pb license field ("{family_metadata.license}")'
                  f' must be one of the following: {expected_licenses}')


@check(
  id = 'com.google.fonts/check/metadata/menu_and_latin',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_menu_and_latin(family_metadata):
  """METADATA.pb should contain at least "menu" and "latin" subsets."""
  missing = []
  for s in ["menu", "latin"]:
    if s not in list(family_metadata.subsets):
      missing.append(s)

  if missing != []:
    if len(missing) == 2:
      missing = "both"
    else:
      missing = f'"{missing[0]}"'

    yield FAIL,\
          Message("missing",
                  f'Subsets "menu" and "latin" are mandatory,'
                  f' but METADATA.pb is missing {missing}.')
  else:
    yield PASS, 'METADATA.pb contains "menu" and "latin" subsets.'


@check(
  id = 'com.google.fonts/check/metadata/subsets_order',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_subsets_order(family_metadata):
  """METADATA.pb subsets should be alphabetically ordered."""
  expected = list(sorted(family_metadata.subsets))

  if list(family_metadata.subsets) != expected:
    yield FAIL,\
          Message("not-sorted",
                  ("METADATA.pb subsets are not sorted "
                   "in alphabetical order: Got ['{}']"
                   " and expected ['{}']"
                   "").format("', '".join(family_metadata.subsets),
                              "', '".join(expected)))
  else:
    yield PASS, "METADATA.pb subsets are sorted in alphabetical order."


@check(
  id = 'com.google.fonts/check/metadata/copyright',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_copyright(family_metadata):
  """METADATA.pb: Copyright notice is the same in all fonts?"""
  copyright = None
  fail = False
  for f in family_metadata.fonts:
    if copyright and f.copyright != copyright:
      fail = True
    copyright = f.copyright
  if fail:
    yield FAIL,\
          Message("inconsistency",
                  "METADATA.pb: Copyright field value"
                  " is inconsistent across family")
  else:
    yield PASS, "Copyright is consistent across family"


@check(
  id = 'com.google.fonts/check/metadata/familyname',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_familyname(family_metadata):
  """Check that METADATA.pb family values are all the same."""
  name = ""
  fail = False
  for f in family_metadata.fonts:
    if name and f.name != name:
      fail = True
    name = f.name
  if fail:
    yield FAIL,\
          Message("inconsistency",
                  'METADATA.pb: Family name is not the same'
                  ' in all metadata "fonts" items.')
  else:
    yield PASS, ('METADATA.pb: Family name is the same'
                 ' in all metadata "fonts" items.')


@check(
  id = 'com.google.fonts/check/metadata/has_regular',
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_has_regular(family_metadata):
  """METADATA.pb: According Google Fonts standards,
     families should have a Regular style.
  """
  from .googlefonts_conditions import has_regular_style

  if has_regular_style(family_metadata):
    yield PASS, "Family has a Regular style."
  else:
    yield FAIL,\
          Message("lacks-regular",
                  "This family lacks a Regular"
                  " (style: normal and weight: 400)"
                  " as required by Google Fonts standards.")


@check(
  id = 'com.google.fonts/check/metadata/regular_is_400',
  conditions = ['family_metadata',
                'has_regular_style']
)
def com_google_fonts_check_metadata_regular_is_400(family_metadata):
  """METADATA.pb: Regular should be 400."""
  badfonts = []
  for f in family_metadata.fonts:
    if f.full_name.endswith("Regular") and f.weight != 400:
      badfonts.append(f"{f.filename} (weight: {f.weight})")
  if len(badfonts) > 0:
    yield FAIL,\
          Message("not-400",
                  f'METADATA.pb: Regular font weight must be 400.'
                  f' Please fix these: {", ".join(badfonts)}')
  else:
    yield PASS, "Regular has weight = 400."


@check(
  id = 'com.google.fonts/check/metadata/nameid/family_name',
  conditions=['font_metadata']
)
def com_google_fonts_check_metadata_nameid_family_name(ttFont, font_metadata):
  """Checks METADATA.pb font.name field matches
     family name declared on the name table.
  """
  from fontbakery.utils import get_name_entry_strings

  familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
  if not familynames:
      familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
  if len(familynames) == 0:
    yield FAIL,\
          Message("missing",
                  (f"This font lacks a FONT_FAMILY_NAME entry"
                   f" (nameID = {NameID.FONT_FAMILY_NAME})"
                   f" in the name table."))
  else:
    if font_metadata.name not in familynames:
      yield FAIL,\
            Message("mismatch",
                    (f'Unmatched family name in font:'
                     f' TTF has "{familynames[0]}" while METADATA.pb'
                     f' has "{font_metadata.name}"'))
    else:
      yield PASS, (f'Family name "{font_metadata.name}" is identical'
                   f' in METADATA.pb and on the TTF file.')

@check(
  id = 'com.google.fonts/check/metadata/nameid/post_script_name',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_nameid_post_script_name(ttFont, font_metadata):
  """Checks METADATA.pb font.post_script_name matches
     postscript name declared on the name table.
  """
  failed = False
  from fontbakery.utils import get_name_entry_strings

  postscript_names = get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME)
  if len(postscript_names) == 0:
    failed = True
    yield FAIL,\
          Message("missing",
                  (f"This font lacks a POSTSCRIPT_NAME entry"
                   f" (nameID = {NameID.POSTSCRIPT_NAME})"
                   f" in the name table."))
  else:
    for psname in postscript_names:
      if psname != font_metadata.post_script_name:
        failed = True
        yield FAIL,\
              Message("mismatch",
                      (f'Unmatched postscript name in font:'
                       f' TTF has "{psname}" while METADATA.pb has'
                       f' "{font_metadata.post_script_name}".'))
  if not failed:
    yield PASS, (f'Postscript name "{font_metadata.post_script_name}"'
                 f' is identical in METADATA.pb and on the TTF file.')


@check(
  id = 'com.google.fonts/check/metadata/nameid/full_name',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_nameid_full_name(ttFont, font_metadata):
  """METADATA.pb font.full_name value matches
     fullname declared on the name table?
  """
  from fontbakery.utils import get_name_entry_strings

  full_fontnames = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
  if len(full_fontnames) == 0:
    yield FAIL,\
          Message("lacks-entry",
                  (f"This font lacks a FULL_FONT_NAME entry"
                   f" (nameID = {NameID.FULL_FONT_NAME})"
                   f" in the name table."))
  else:
    for full_fontname in full_fontnames:
      if full_fontname != font_metadata.full_name:
        yield FAIL,\
              Message("mismatch",
                      (f'Unmatched fullname in font:'
                       f' TTF has "{full_fontname}" while METADATA.pb'
                       f' has "{font_metadata.full_name}".'))
      else:
        yield PASS, (f'Font fullname "{full_fontname}" is identical'
                     f' in METADATA.pb and on the TTF file.')


@check(
  id = 'com.google.fonts/check/metadata/nameid/font_name',
  conditions=['font_metadata', 'style']
)
def com_google_fonts_check_metadata_nameid_font_name(ttFont, style, font_metadata):
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
    yield FAIL,\
          Message("lacks-entry",
                  (f"This font lacks a {NameID(nameid).name} entry"
                   f" (nameID = {nameid}) in the name table."))
  else:
    for font_familyname in font_familynames:
      if font_familyname != font_metadata.name:
        yield FAIL,\
              Message("mismatch",
                      (f'Unmatched familyname in font:'
                       f' TTF has familyname = "{font_familyname}" while'
                       f' METADATA.pb has font.name = "{font_metadata.name}".'))
      else:
        yield PASS, (f'OK: Family name "{font_metadata.name}" is identical'
                     f' in METADATA.pb and on the TTF file.')


@check(
  id = 'com.google.fonts/check/metadata/match_fullname_postscript',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_match_fullname_postscript(font_metadata):
  """METADATA.pb font.full_name and font.post_script_name
     fields have equivalent values ?
  """
  import re
  regex = re.compile(r"\W")
  post_script_name = regex.sub("", font_metadata.post_script_name)
  fullname = regex.sub("", font_metadata.full_name)
  if fullname != post_script_name:
    yield FAIL,\
          Message("mismatch",
                  f'METADATA.pb font full_name = "{font_metadata.full_name}"'
                  f' does not match'
                  f' post_script_name = "{font_metadata.post_script_name}"')
  else:
    yield PASS, ('METADATA.pb font fields "full_name" and'
                 ' "post_script_name" have equivalent values.')


@check(
  id = 'com.google.fonts/check/metadata/match_filename_postscript',
  conditions = ['font_metadata',
                'not is_variable_font']
  # FIXME: We'll want to review this once
  #        naming rules for varfonts are settled.
)
def com_google_fonts_check_metadata_match_filename_postscript(font_metadata):
  """METADATA.pb font.filename and font.post_script_name
     fields have equivalent values?
  """
  post_script_name = font_metadata.post_script_name
  filename = os.path.splitext(font_metadata.filename)[0]

  if filename != post_script_name:
    yield FAIL,\
          Message("mismatch",
                  f'METADATA.pb font filename = "{font_metadata.filename}"'
                  f' does not match'
                  f' post_script_name="{font_metadata.post_script_name}".')
  else:
    yield PASS, ('METADATA.pb font fields "filename" and'
                 ' "post_script_name" have equivalent values.')


@check(
  id = 'com.google.fonts/check/metadata/valid_name_values',
  conditions = ['style',
                'font_metadata']
)
def com_google_fonts_check_metadata_valid_name_values(style,
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
      yield FAIL,\
            Message("mismatch",
                    f'METADATA.pb font.name field ("{font_metadata.name}")'
                    f' does not match'
                    f' correct font name format ("{font_familyname}").')
  if not failed:
    yield PASS, ("METADATA.pb font.name field contains"
                 " font name in right format.")


@check(
  id = 'com.google.fonts/check/metadata/valid_full_name_values',
  conditions = ['style',
                'font_metadata']
)
def com_google_fonts_check_metadata_valid_full_name_values(style,
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
      yield PASS, (f'METADATA.pb font.full_name field contains'
                   f' font name in right format.'
                   f' ("{font_familyname}" in "{font_metadata.full_name}")')
    else:
      yield FAIL,\
            Message("mismatch",
                    f'METADATA.pb font.full_name field'
                    f' ("{font_metadata.full_name}")'
                    f' does not match correct font name format'
                    f' ("{font_familyname}").')


@check(
  id = 'com.google.fonts/check/metadata/valid_filename_values',
  conditions = ['style', # This means the font filename
                         # (source of truth here) is good
                'family_metadata']
)
def com_google_fonts_check_metadata_valid_filename_values(font,
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
    yield FAIL,\
          Message("bad-field",
                  f'None of the METADATA.pb filename fields match'
                  f' correct font name format ("{expected}").')


@check(
  id = 'com.google.fonts/check/metadata/valid_post_script_name_values',
  conditions = ['font_metadata',
                'font_familynames']
)
def com_google_fonts_check_metadata_valid_post_script_name_values(font_metadata,
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
      yield FAIL,\
            Message("mismatch",
                    f'METADATA.pb'
                    f' postScriptName ("{font_metadata.post_script_name}")'
                    f' does not match'
                    f' correct font name format ("{font_familyname}").')


@check(
  id = 'com.google.fonts/check/metadata/valid_copyright',
  conditions = ['font_metadata'],
  rationale = """
    The expected pattern for the copyright string adheres to the following rules:
    * It must say "Copyright" followed by a 4 digit year (optionally followed by a hyphen and another 4 digit year)
    * Then it must say "The <familyname> Project Authors"
    * And within parentheses, a URL for a git repository must be provided
    * The check is case insensitive and does not validate whether the familyname is correct, even though we'd expect it is (and we may soon update the check to validate that aspect as well!)

    Here is an example of a valid copyright string:
    "Copyright 2017 The Archivo Black Project Authors (https://github.com/Omnibus-Type/ArchivoBlack)"
  """
)
def com_google_fonts_check_metadata_valid_copyright(font_metadata):
  """Copyright notices match canonical pattern in METADATA.pb"""
  import re
  string = font_metadata.copyright.lower()
  does_match = re.search(r'copyright [0-9]{4}(\-[0-9]{4})? the .* project authors \([^\@]*\)',
                           string)
  if does_match:
    yield PASS, "METADATA.pb copyright string is good"
  else:
    yield FAIL,\
          Message("bad-notice-format",
                  f'METADATA.pb: Copyright notices should match'
                  f' a pattern similar to:\n'
                  f' "Copyright 2020 The Familyname Project Authors (git url)"'
                  f'\n'
                  f'But instead we have got:\n"{string}"')


@check(
  id = 'com.google.fonts/check/font_copyright',
)
def com_google_fonts_check_font_copyright(ttFont):
  """Copyright notices match canonical pattern in fonts"""
  import re
  from fontbakery.utils import get_name_entry_strings

  failed = False
  for string in get_name_entry_strings(ttFont, NameID.COPYRIGHT_NOTICE):
    does_match = re.search(r'Copyright [0-9]{4}(\-[0-9]{4})? The .* Project Authors \([^\@]*\)',
                           string)
    if does_match:
      yield PASS, ("Name Table entry: Copyright field '{}'"
                   " matches canonical pattern.").format(string)
    else:
      failed = True
      yield FAIL,\
            Message("bad-notice-format",
                    f'Name Table entry: Copyright notices should match'
                    f' a pattern similar to: "Copyright 2019'
                    f' The Familyname Project Authors (git url)"\n'
                    f'But instead we have got:\n"{string}"')
  if not failed:
    yield PASS, "Name table copyright entries are good"


@check(
  id = 'com.google.fonts/check/metadata/reserved_font_name',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_reserved_font_name(font_metadata):
  """Copyright notice on METADATA.pb should not contain 'Reserved Font Name'."""
  if "Reserved Font Name" in font_metadata.copyright:
    yield WARN,\
          Message("rfn",
                  f'METADATA.pb:'
                  f' copyright field ("{font_metadata.copyright}")'
                  f' contains "Reserved Font Name".'
                  f' This is an error except in a few specific rare cases.')
  else:
    yield PASS, ('METADATA.pb copyright field'
                 ' does not contain "Reserved Font Name".')


@check(
  id = 'com.google.fonts/check/metadata/copyright_max_length',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_copyright_max_length(font_metadata):
  """METADATA.pb: Copyright notice shouldn't exceed 500 chars."""
  if len(font_metadata.copyright) > 500:
    yield FAIL,\
          Message("max-length",
                  "METADATA.pb: Copyright notice exceeds"
                  " maximum allowed lengh of 500 characteres.")
  else:
    yield PASS, "Copyright notice string is shorter than 500 chars."


@check(
  id = 'com.google.fonts/check/metadata/filenames',
  rationale = """
    Note:
    This check only looks for files in the current directory.

    Font files in subdirectories are checked by these other two checks:
     - com.google.fonts/check/metadata/undeclared_fonts
     - com.google.fonts/check/repo/vf_has_static_fonts

    We may want to merge them all into a single check.
  """,
  conditions = ['family_metadata']
)
def com_google_fonts_check_metadata_filenames(fonts, family_directory, family_metadata):
  """METADATA.pb: Font filenames match font.filename entries?"""

  passed = True
  metadata_filenames = []
  font_filenames = [f for f in os.listdir(family_directory) if f[-4:] in [".ttf", ".otf"]]
  for font_metadata in family_metadata.fonts:
    if font_metadata.filename not in font_filenames:
      passed = False
      yield FAIL,\
            Message("file-not-found",
                    f'Filename "{font_metadata.filename}" is listed on'
                    f' METADATA.pb but an actual font file'
                    f' with that name was not found.')
    metadata_filenames.append(font_metadata.filename)

  for font in font_filenames:
    if font not in metadata_filenames:
      passed = False
      yield FAIL,\
            Message("file-not-declared",
                    f'Filename "{font}" is not declared'
                    f' on METADATA.pb as a font.filename entry.')
  if passed:
    yield PASS, "Filenames in METADATA.pb look good."


@check(
  id = 'com.google.fonts/check/metadata/italic_style',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_italic_style(ttFont, font_metadata):
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
        yield FAIL,\
              Message("bad-macstyle",
                      ("METADATA.pb style has been set to italic"
                       " but font macStyle is improperly set."))
      elif not font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL,\
              Message("bad-fullfont-name",
                      (f'Font macStyle Italic bit is set'
                       f' but nameID {NameID.FULL_FONT_NAME}'
                       f' ("{font_fullname}") is not'
                       f' ended with "Italic".'))
      else:
        yield PASS, ('OK: METADATA.pb font.style "italic"'
                     ' matches font internals.')


@check(
  id = 'com.google.fonts/check/metadata/normal_style',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_normal_style(ttFont, font_metadata):
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
      # FIXME: This is the same SKIP condition as in check/metadata/italic_style
      #        so we definitely need to address them with a common condition!
    else:
      font_familyname = font_familyname[0]
      font_fullname = font_fullname[0]

      if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
        yield FAIL,\
              Message("bad-macstyle",
                      ("METADATA.pb style has been set to normal"
                       " but font macStyle is improperly set."))
      elif font_familyname.split("-")[-1].endswith('Italic'):
        yield FAIL,\
              Message("familyname-italic",
                      (f'Font macStyle indicates a non-Italic font,'
                       f' but nameID {NameID.FONT_FAMILY_NAME}'
                       f' (FONT_FAMILY_NAME: "{font_familyname}")'
                       f' ends with "Italic".'))
      elif font_fullname.split("-")[-1].endswith("Italic"):
        yield FAIL,\
              Message("fullfont-italic",
                      (f'Font macStyle indicates a non-Italic font,'
                       f' but nameID {NameID.FULL_FONT_NAME}'
                       f' (FULL_FONT_NAME: "{font_fullname}")'
                       f' ends with "Italic".'))
      else:
        yield PASS, ('METADATA.pb font.style "normal"'
                     ' matches font internals.')


@check(
  id = 'com.google.fonts/check/metadata/nameid/family_and_full_names',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_nameid_family_and_full_names(ttFont, font_metadata):
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
    yield FAIL,\
          Message("fullname-mismatch",
                  (f'METADATA.pb: Fullname "{font_metadata.full_name}"'
                   f' does not match name table entry "{font_fullname}"!'))

  elif font_familyname != font_metadata.name:
    yield FAIL,\
          Message("familyname-mismatch",
                  (f'METADATA.pb Family name "{font_metadata.name}"'
                   f' does not match name table entry "{font_familyname}"!'))
  else:
    yield PASS, ("METADATA.pb familyname and fullName fields"
                 " match corresponding name table entries.")


@check(
  id = 'com.google.fonts/check/metadata/fontname_not_camel_cased',
  conditions = ['font_metadata',
                'not whitelist_camelcased_familyname']
)
def com_google_fonts_check_metadata_fontname_not_camel_cased(font_metadata):
  """METADATA.pb: Check if fontname is not camel cased."""
  import re
  if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
    yield FAIL,\
          Message("camelcase",
                  f'METADATA.pb: "{font_metadata.name}" is a CamelCased name.'
                  f' To solve this, simply use spaces'
                  f' instead in the font name.')
  else:
    yield PASS, "Font name is not camel-cased."


@check(
  id = 'com.google.fonts/check/metadata/match_name_familyname',
  conditions = ['family_metadata',      # that's the family-wide metadata!
                'font_metadata'] # and this one's specific to a single file
)
def com_google_fonts_check_metadata_match_name_familyname(family_metadata, font_metadata):
  """METADATA.pb: Check font name is the same as family name."""
  if font_metadata.name != family_metadata.name:
    yield FAIL,\
          Message("mismatch",
                  f'METADATA.pb: {font_metadata.filename}:\n'
                  f' Family name "{family_metadata.name}"'
                  f' does not match'
                  f' font name: "{font_metadata.name}"')
  else:
    yield PASS, "Font name is the same as family name."


@check(
  id = 'com.google.fonts/check/metadata/canonical_weight_value',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_canonical_weight_value(font_metadata):
  """METADATA.pb: Check that font weight has a canonical value."""
  first_digit = font_metadata.weight / 100
  if (font_metadata.weight % 100) != 0 or \
     (first_digit < 1 or first_digit > 9):
   yield FAIL,\
         Message("bad-weight",
                 f"METADATA.pb: The weight is declared"
                 f" as {font_metadata.weight} which is not a"
                 f" multiple of 100 between 100 and 900.")
  else:
    yield PASS, "Font weight has a canonical value."


@check(
  id = 'com.google.fonts/check/metadata/os2_weightclass',
  rationale =  """
    Check METADATA.pb font weights are correct.

    For static fonts, the metadata weight should be the same
    as the static font's OS/2 usWeightClass.

    For variable fonts, the weight value should be 400 if the
    font's wght axis range includes 400, otherwise it should be the
    value closest to 400.
  """,
  conditions = ['font_metadata'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2683'
  }
)
def com_google_fonts_check_metadata_os2_weightclass(ttFont,
                                                    font_metadata):
  """Check METADATA.pb font weights are correct."""
  from .shared_conditions import is_variable_font
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
  if is_variable_font(ttFont):
    axes = {f.axisTag: f for f in ttFont["fvar"].axes}
    # if there isn't a wght axis, use the OS/2.usWeightClass
    if 'wght' not in axes:
      font_weight = f['OS/2'].usWeightClass
    # if the wght range includes 400, use 400
    else:
      wght_includes_400 = axes['wght'].minValue <= 400 and axes['wght'].maxValue >= 400
      if wght_includes_400:
        font_weight = 400
      # if 400 isn't in the wght axis range, use the value closest to 400
      elif not wght_includes_400:
        if abs(axes['wght'].minValue - 400) < abs(axes['wght'].maxValue - 400):
          font_weight = axes['wght'].minValue
        else:
          font_weight = axes['wght'].maxValue
  else:
    font_weight = ttFont["OS/2"].usWeightClass

  gf_weight = GF_API_WEIGHT_NAMES.get(font_weight,
                                      "bad Google Fonts API weight value")
  css_weight = CSS_WEIGHT_NAMES.get(font_metadata.weight,
                                    "bad CSS weight value")
  if gf_weight != css_weight:
    yield FAIL,\
          Message("mismatch",
                  f'OS/2 usWeightClass'
                  f' ({ttFont["OS/2"].usWeightClass}:"{gf_weight}")'
                  f' does not match weight specified'
                  f' at METADATA.pb ({font_metadata.weight}:"{css_weight}").')
  else:
    yield PASS, ("OS/2 usWeightClass or wght axis value matches"
                 " weight specified at METADATA.pb")


@check(
  id = 'com.google.fonts/check/metadata/match_weight_postscript',
  conditions = ['font_metadata',
                'not is_variable_font']
)
def com_google_fonts_check_metadata_match_weight_postscript(font_metadata):
  """METADATA.pb weight matches postScriptName for static fonts."""
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
  id = 'com.google.fonts/check/metadata/canonical_style_names',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_canonical_style_names(ttFont, font_metadata):
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
    yield SKIP, ('This check only applies to font styles declared'
                 ' as "italic" or "normal" on METADATA.pb.')
  else:
    if is_italic() and font_metadata.style != "italic":
      yield FAIL,\
            Message("italic",
                    f'The font style is "{font_metadata.style}"'
                    f' but it should be "italic".')
    elif not is_italic() and font_metadata.style != "normal":
      yield FAIL,\
            Message("normal",
                    f'The font style is "{font_metadata.style}"'
                    f' but it should be "normal".')
    else:
      yield PASS, "Font styles are named canonically."


@check(
  id = 'com.google.fonts/check/unitsperem_strict',
  rationale = """
    Even though the OpenType spec allows unitsPerEm to be any value between 16 and 16384, the Google Fonts project aims at a narrower set of reasonable values.

    The spec suggests usage of powers of two in order to get some performance improvements on legacy renderers, so those values are acceptable.

    But value of 500 or 1000 are also acceptable, with the added benefit that it makes upm math easier for designers, while the performance hit of not using a power of two is most likely negligible nowadays.

    Another acceptable value is 2000. Since TT outlines are all integers (no floats), then instances in a VF suffer rounding compromises, and therefore a 1000 UPM is too small because it forces too many such compromises.
   
    Therefore 2000 is a good 'new VF standard', because 2000 is a simple 2x conversion from existing fonts drawn on a 1000 UPM, and anyone who knows what 10 units can do for 1000 UPM will know what 20 units does too.

    Additionally, values above 2048 would result in filesize increases with not much added benefit.
  """
)
def com_google_fonts_check_unitsperem_strict(ttFont):
  """ Stricter unitsPerEm criteria for Google Fonts. """
  upm_height = ttFont["head"].unitsPerEm
  ACCEPTABLE = [16, 32, 64, 128, 256, 500,
                512, 1000, 1024, 2000, 2048]
  if upm_height > 2048 and upm_height <= 4096:
    yield WARN,\
          Message("large-value",
                  f"Font em size (unitsPerEm) is {upm_height}"
                  f" which may be too large (causing filesize bloat),"
                  f" unless you are sure that the detail level"
                  f" in this font requires that much precision.")
  elif upm_height not in ACCEPTABLE:
    yield FAIL,\
          Message("bad-value",
                  f"Font em size (unitsPerEm) is {upm_height}."
                  f" If possible, please consider using 1000"
                  f" or even 2000 (which is ideal for"
                  f" Variable Fonts)."
                  f" Good values for unitsPerEm,"
                  f" though, are typically these: {ACCEPTABLE}.")
  elif upm_height < 2000:
    yield WARN,\
          Message("legacy-value",
                  f"Even though unitsPerEm ({upm_height}) in"
                  f" this font is reasonable. It is strongly"
                  f" advised to consider changing it to 2000,"
                  f" since it will likely improve the quality of"
                  f" Variable Fonts by avoiding excessive"
                  f" rounding of coordinates on interpolations.")
  else:
    yield PASS, f"Font em size is good (unitsPerEm = {upm_height})."


@check(
  id = 'com.google.fonts/check/version_bump',
  conditions = ['api_gfonts_ttFont',
                'github_gfonts_ttFont']
)
def com_google_fonts_check_version_bump(ttFont,
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
  id = 'com.google.fonts/check/production_glyphs_similarity',
  conditions = ['api_gfonts_ttFont']
)
def com_google_fonts_check_production_glyphs_similarity(ttFont, api_gfonts_ttFont):
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
  id = 'com.google.fonts/check/fsselection',
  conditions = ['style']
)
def com_google_fonts_check_fsselection(ttFont, style):
  """Checking OS/2 fsSelection value."""
  from fontbakery.utils import check_bit_entry
  from fontbakery.constants import (STATIC_STYLE_NAMES,
                                    RIBBI_STYLE_NAMES,
                                    FsSelection)

  # Checking fsSelection REGULAR bit:
  expected = "Regular" in style or \
             (style in STATIC_STYLE_NAMES and
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
  id = 'com.google.fonts/check/italic_angle',
  conditions = ['style'],
  rationale = """
    The 'post' table italicAngle property should be a reasonable amount, likely not more than -20°, never more than -30°, and never greater than 0°. Note that in the OpenType specification, the value is negative for a lean rightwards.

    https://docs.microsoft.com/en-us/typography/opentype/spec/post
  """
)
def com_google_fonts_check_italic_angle(ttFont, style):
  """Checking post.italicAngle value."""
  failed = False
  value = ttFont["post"].italicAngle

  # Checking that italicAngle <= 0
  if value > 0:
    failed = True
    yield FAIL,\
          Message("positive",
                  (f"The value of post.italicAngle is positive, which"
                   f" is likely a mistake and should become negative,"
                   f" from {value} to {-value}."))

  # Checking that italicAngle is less than 20° (not good) or 30° (bad)
  # Also note we invert the value to check it in a clear way
  if abs(value) > 30:
    failed = True
    yield FAIL,\
          Message("over-minus30-degrees",
                  (f"The value of post.italicAngle ({value}) is very high"
                   f" (over -30°!) and should be confirmed."))
  elif abs(value) > 20:
    failed = True
    yield WARN,\
          Message("over-minus20-degrees",
                  (f"The value of post.italicAngle ({value}) seems very high"
                   f" (over -20°!) and should be confirmed."))


  # Checking if italicAngle matches font style:
  if "Italic" in style:
    if ttFont['post'].italicAngle == 0:
      failed = True
      yield FAIL,\
            Message("zero-italic",
                    ("Font is italic, so post.italicAngle"
                     " should be non-zero."))
  else:
    if ttFont["post"].italicAngle != 0:
      failed = True
      yield FAIL,\
            Message("non-zero-normal",
                    ("Font is not italic, so post.italicAngle"
                     " should be equal to zero."))

  if not failed:
    yield PASS, (f'Value of post.italicAngle is {value}'
                 f' with style="{style}".')


@check(
  id = 'com.google.fonts/check/mac_style',
  conditions = ['style'],
  rationale = """
    The values of the flags on the macStyle entry on the 'head' OpenType table that describe whether a font is bold and/or italic must be coherent with the actual style of the font as inferred by its filename.
  """
)
def com_google_fonts_check_mac_style(ttFont, style):
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
  id = 'com.google.fonts/check/contour_count',
  conditions = ['is_ttf',
                'not is_variable_font'],
  rationale = """
    Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.

    However, a quotedbl should have 2 contours, unless the font belongs to a display family.

    This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.
  """
)
def com_google_fonts_check_contour_count(ttFont):
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

  def in_PUA_range(codepoint):
    """
      In Unicode, a Private Use Area (PUA) is a range of code points that,
      by definition, will not be assigned characters by the Unicode Consortium.
      Three private use areas are defined:
        one in the Basic Multilingual Plane (U+E000–U+F8FF),
        and one each in, and nearly covering, planes 15 and 16
        (U+F0000–U+FFFFD, U+100000–U+10FFFD).
    """
    return (codepoint >= 0xE000 and codepoint <= 0xF8FF) or \
           (codepoint >= 0xF0000 and codepoint <= 0xFFFFD) or \
           (codepoint >= 0x100000 and codepoint <= 0x10FFFD)

  # rearrange data structure:
  desired_glyph_data_by_codepoint = {}
  desired_glyph_data_by_glyphname = {}
  for glyph in glyph_data:
    desired_glyph_data_by_glyphname[glyph['name']] = glyph
    # since the glyph in PUA ranges have unspecified meaning,
    # it doesnt make sense for us to have an expected contour cont for them
    if not in_PUA_range(glyph['unicode']):
      desired_glyph_data_by_codepoint[glyph['unicode']] = glyph

  bad_glyphs = []
  desired_glyph_contours_by_codepoint = {f: desired_glyph_data_by_codepoint[f]['contours']
                                         for f in desired_glyph_data_by_codepoint}
  desired_glyph_contours_by_glyphname = {f: desired_glyph_data_by_glyphname[f]['contours']
                                         for f in desired_glyph_data_by_glyphname}

  font_glyph_data = get_font_glyph_data(ttFont)

  if font_glyph_data is None:
    yield FAIL,\
          Message("lacks-cmap",
                  "This font lacks cmap data.")
  else:
    font_glyph_contours_by_codepoint = {f['unicode']: list(f['contours'])[0]
                                        for f in font_glyph_data}
    font_glyph_contours_by_glyphname = {f['name']: list(f['contours'])[0]
                                        for f in font_glyph_data}

    shared_glyphs_by_codepoint = set(desired_glyph_contours_by_codepoint) & \
                                 set(font_glyph_contours_by_codepoint)
    for glyph in shared_glyphs_by_codepoint:
      if font_glyph_contours_by_codepoint[glyph] not in desired_glyph_contours_by_codepoint[glyph]:
        bad_glyphs.append([glyph,
                           font_glyph_contours_by_codepoint[glyph],
                           desired_glyph_contours_by_codepoint[glyph]])

    shared_glyphs_by_glyphname = set(desired_glyph_contours_by_glyphname) & \
                                 set(font_glyph_contours_by_glyphname)
    for glyph in shared_glyphs_by_glyphname:
      if font_glyph_contours_by_glyphname[glyph] not in desired_glyph_contours_by_glyphname[glyph]:
        bad_glyphs.append([glyph,
                           font_glyph_contours_by_glyphname[glyph],
                           desired_glyph_contours_by_glyphname[glyph]])

    if len(bad_glyphs) > 0:
      cmap = ttFont['cmap'].getcmap(PlatformID.WINDOWS,
                                    WindowsEncodingID.UNICODE_BMP).cmap

      def _glyph_name(cmap, name):
        if name in cmap:
          return cmap[name]
        else:
          return name

      bad_glyphs_name = [
        f"Glyph name: {_glyph_name(cmap, name)}\t"
        f"Contours detected: {count}\t"
        f"Expected: {pretty_print_list(expected, shorten=None, glue='or')}"
        for name, count, expected in bad_glyphs
      ]
      bad_glyphs_name = '\n'.join(bad_glyphs_name)
      yield WARN,\
            Message("contour-count",
                    f"This check inspects the glyph outlines and detects the"
                    f" total number of contours in each of them. The expected"
                    f" values are infered from the typical ammounts of"
                    f" contours observed in a large collection of reference"
                    f" font families. The divergences listed below may simply"
                    f" indicate a significantly different design on some of"
                    f" your glyphs. On the other hand, some of these may flag"
                    f" actual bugs in the font such as glyphs mapped to an"
                    f" incorrect codepoint. Please consider reviewing"
                    f" the design and codepoint assignment of these to make"
                    f" sure they are correct.\n"
                    f"\n"
                    f"The following glyphs do not have the recommended"
                    f" number of contours:\n"
                    f"\n"
                    f"{bad_glyphs_name}")
    else:
      yield PASS, "All glyphs have the recommended amount of contours"


# FIXME!
# Temporarily disabled since GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the check implementation below.
# More info at https://github.com/googlefonts/fontbakery/issues/2581
@disable
@check(
  id = 'com.google.fonts/check/production_encoded_glyphs',
  conditions = ['api_gfonts_ttFont']
)
def com_google_fonts_check_production_encoded_glyphs(ttFont, api_gfonts_ttFont):
  """Check font has same encoded glyphs as version hosted on
  fonts.google.com"""
  cmap = ttFont['cmap'].getcmap(3, 1).cmap
  gf_cmap = api_gfonts_ttFont['cmap'].getcmap(3, 1).cmap
  missing_codepoints = set(gf_cmap.keys()) - set(cmap.keys())

  if missing_codepoints:
    hex_codepoints = ['0x' + hex(c).upper()[2:].zfill(4) for c
                      in missing_codepoints]
    yield FAIL,\
          Message("lost-glyphs",
                  f"Font is missing the following glyphs"
                  f" from the previous release"
                  f" [{', '.join(hex_codepoints)}]")
  else:
    yield PASS, ('Font has all the glyphs from the previous release')


@check(
  id = 'com.google.fonts/check/metadata/nameid/copyright',
  conditions = ['font_metadata']
)
def com_google_fonts_check_metadata_nameid_copyright(ttFont, font_metadata):
  """Copyright field for this font on METADATA.pb matches
     all copyright notice entries on the name table ?"""
  failed = False
  for nameRecord in ttFont['name'].names:
    string = nameRecord.string.decode(nameRecord.getEncoding())
    if nameRecord.nameID == NameID.COPYRIGHT_NOTICE and\
       string != font_metadata.copyright:
      failed = True
      yield FAIL,\
            Message("mismatch",
                    f'Copyright field for this font on METADATA.pb'
                    f' ("{font_metadata.copyright}") differs from'
                    f' a copyright notice entry on the name table:'
                    f' "{string}"')
  if not failed:
    yield PASS, ("Copyright field for this font on METADATA.pb matches"
                 " copyright notice entries on the name table.")


@check(
  id = 'com.google.fonts/check/name/mandatory_entries',
  conditions = ['style'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_mandatory_entries(ttFont, style):
  """Font has all mandatory 'name' table entries?"""
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
      yield FAIL,\
            Message("missing-entry",
                    f"Font lacks entry with nameId={nameId}"
                    f" ({NameID(nameId).name})")
  if not failed:
    yield PASS, "Font contains values for all mandatory name table entries."


@check(
  id = 'com.google.fonts/check/name/familyname',
  conditions = ['style',
                'familyname_with_spaces'],
  rationale = """
    Checks that the family name infered from the font filename matches the string at nameID 1 (NAMEID_FONT_FAMILY_NAME) if it conforms to RIBBI and otherwise checks that nameID 1 is the family name + the style name.
  """,
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_familyname(ttFont, style, familyname_with_spaces):
  """Check name table: FONT_FAMILY_NAME entries."""
  from fontbakery.utils import name_entry_id

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
        yield FAIL,\
              Message("lacks-name",
                      f"Font should not have a "
                      f"{name_entry_id(name)} entry!")
        continue

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        yield FAIL,\
              Message("mismatch",
                      f'Entry {name_entry_id(name)} on the "name" table:'
                      f' Expected "{expected_value}"'
                      f' but got "{string}".')
  if not failed:
    yield PASS,\
          Message("ok",
                  "FONT_FAMILY_NAME entries are all good.")


@check(
  id = 'com.google.fonts/check/name/subfamilyname',
  conditions = ['expected_style'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_subfamilyname(ttFont, expected_style):
  """Check name table: FONT_SUBFAMILY_NAME entries."""
  failed = False
  nametable = ttFont['name']
  win_name = nametable.getName(NameID.FONT_SUBFAMILY_NAME,
                               PlatformID.WINDOWS,
                               WindowsEncodingID.UNICODE_BMP,
                               WindowsLanguageID.ENGLISH_USA)
  mac_name = nametable.getName(NameID.FONT_SUBFAMILY_NAME,
                               PlatformID.MACINTOSH,
                               MacintoshEncodingID.ROMAN,
                               MacintoshLanguageID.ENGLISH)

  if mac_name and mac_name.toUnicode() != expected_style.mac_style_name:
    failed = True
    yield FAIL,\
          Message("bad-familyname",
                  (f'SUBFAMILY_NAME for Mac "{mac_name.toUnicode()}"'
                   f' must be "{expected_style.mac_style_name}"'))
  if win_name.toUnicode() != expected_style.win_style_name:
    failed = True
    yield FAIL,\
          Message("bad-familyname",
                  f'SUBFAMILY_NAME for Win "{win_name.toUnicode()}"'
                  f' must be "{expected_style.win_style_name}"')
  if not failed:
    yield PASS, "FONT_SUBFAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/name/fullfontname',
  conditions = ['style_with_spaces',
                'familyname_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_fullfontname(ttFont,
                                             style_with_spaces,
                                             familyname_with_spaces):
  """Check name table: FULL_FONT_NAME entries."""
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
          yield WARN,\
                Message("lacks-regular",
                        f'Entry {name_entry_id(name)} on the "name" table:'
                        f' Got "{string}" which lacks "Regular",'
                        f' but it is probably OK in this case.')
        else:
          yield FAIL,\
                Message("bad-entry",
                        f'Entry {name_entry_id(name)} on the "name" table:'
                        f' Expected "{expected_value}" '
                        f' but got "{string}".')
  if not failed:
    yield PASS, "FULL_FONT_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/name/postscriptname',
  conditions = ['style',
                'familyname'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_postscriptname(ttFont, style, familyname):
  """Check name table: POSTSCRIPT_NAME entries."""
  from fontbakery.utils import name_entry_id

  failed = False
  for name in ttFont['name'].names:
    if name.nameID == NameID.POSTSCRIPT_NAME:
      expected_value = f"{familyname}-{style}"

      string = name.string.decode(name.getEncoding()).strip()
      if string != expected_value:
        failed = True
        yield FAIL,\
              Message("bad-entry",
                      f'Entry {name_entry_id(name)} on the "name" table:'
                      f' Expected "{expected_value}"'
                      f' but got "{string}".')
  if not failed:
    yield PASS, "POSTCRIPT_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/name/typographicfamilyname',
  conditions = ['style',
                'familyname_with_spaces'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_typographicfamilyname(ttFont, style, familyname_with_spaces):
  """Check name table: TYPOGRAPHIC_FAMILY_NAME entries."""
  from fontbakery.utils import name_entry_id

  failed = False
  if style in ['Regular',
               'Italic',
               'Bold',
               'BoldItalic']:
    for name in ttFont['name'].names:
      if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
        failed = True
        yield FAIL,\
              Message("ribbi",
                      (f'Font style is "{style}" and, for that reason,'
                       f' it is not expected to have a '
                       f'{name_entry_id(name)} entry!'))
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
          yield FAIL,\
                Message("non-ribbi-bad-value",
                        (f'Entry {name_entry_id(name)} on the "name" table:'
                         f' Expected "{expected_value}"'
                         f' but got "{string}".'))
    if not failed and not has_entry:
      failed = True
      yield FAIL,\
            Message("non-ribbi-lacks-entry",
                    ("Non-RIBBI fonts must have a TYPOGRAPHIC_FAMILY_NAME"
                     " entry on the name table."))
  if not failed:
    yield PASS, "TYPOGRAPHIC_FAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/name/typographicsubfamilyname',
  conditions=['expected_style'],
  misc_metadata = {
    'priority': PriorityLevel.IMPORTANT
  })
def com_google_fonts_check_name_typographicsubfamilyname(ttFont, expected_style):
  """Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries."""
  failed = False
  nametable = ttFont['name']
  win_name = nametable.getName(NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                               PlatformID.WINDOWS,
                               WindowsEncodingID.UNICODE_BMP,
                               WindowsLanguageID.ENGLISH_USA)
  mac_name = nametable.getName(NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                               PlatformID.MACINTOSH,
                               MacintoshEncodingID.ROMAN,
                               MacintoshLanguageID.ENGLISH)

  if all([win_name, mac_name]):
    if win_name.toUnicode() != mac_name.toUnicode():
      failed = True
      yield FAIL,\
            Message("mismatch",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME entry'
                    f' for Win "{win_name.toUnicode()}"'
                    f' and Mac "{mac_name.toUnicode()}" do not match.')

  if expected_style.is_ribbi:
    if win_name and win_name.toUnicode() != expected_style.win_style_name:
      failed = True
      yield FAIL,\
            Message("bad-win-name",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME entry'
                    f' for Win "{win_name.toUnicode()}"'
                    f' must be "{expected_style.win_style_name}".'
                    f' Please note, since the font style is RIBBI,'
                    f' this record can be safely deleted.')

    if mac_name and mac_name.toUnicode() != expected_style.mac_style_name:
      failed = True
      yield FAIL,\
            Message("bad-mac-name",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME entry'
                    f' for Mac "{mac_name.toUnicode()}"'
                    f' must be "{expected_style.mac_style_name}".'
                    f' Please note, since the font style is RIBBI,'
                    f' this record can be safely deleted.')

  if expected_style.typo_style_name:
    if not win_name:
      failed = True
      yield FAIL,\
            Message("missing-typo-win",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME for Win is missing.'
                    f' It must be "{expected_style.typo_style_name}".')

    elif win_name.toUnicode() != expected_style.typo_style_name:
      failed = True
      yield FAIL,\
            Message("bad-typo-win",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME for Win'
                    f' "{win_name.toUnicode()}" is incorrect.'
                    f' It must be "{expected_style.typo_style_name}".')

    if mac_name and mac_name.toUnicode() != expected_style.typo_style_name:
      failed = True
      yield FAIL,\
            Message("bad-typo-mac",
                    f'TYPOGRAPHIC_SUBFAMILY_NAME for Mac'
                    f' "{mac_name.toUnicode()}" is incorrect.'
                    f' It must be "{expected_style.typo_style_name}".'
                    f' Please note, this record can be safely deleted.')

  if not failed:
    yield PASS, "TYPOGRAPHIC_SUBFAMILY_NAME entries are all good."


@check(
  id = 'com.google.fonts/check/name/copyright_length',
  rationale = """
    This is an arbitrary max length for the copyright notice field of the name table. We simply don't want such notices to be too long. Typically such notices are actually much shorter than this with a length of roughly 70 or 80 characters.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1603'
  })
def com_google_fonts_check_name_copyright_length(ttFont):
  """Length of copyright notice must not exceed 500 characters."""
  from fontbakery.utils import get_name_entries

  failed = False
  for notice in get_name_entries(ttFont, NameID.COPYRIGHT_NOTICE):
    notice_str = notice.string.decode(notice.getEncoding())
    if len(notice_str) > 500:
      failed = True
      yield FAIL,\
            Message("too-long",
                    f'The length of the following copyright notice'
                    f' ({len(notice_str)}) exceeds 500 chars:'
                    f' "{notice_str}"')
  if not failed:
    yield PASS, ("All copyright notice name entries on the"
                 " 'name' table are shorter than 500 characters.")


@check(
  id = 'com.google.fonts/check/fontdata_namecheck',
  rationale = """
    We need to check names are not already used, and today the best place to check that is http://namecheck.fontdata.com
  """,
  conditions = ["familyname"],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/494'
  })
def com_google_fonts_check_fontdata_namecheck(ttFont, familyname):
  """Familyname must be unique according to namecheck.fontdata.com"""
  import requests
  FB_ISSUE_TRACKER = "https://github.com/googlefonts/fontbakery/issues"
  NAMECHECK_URL = "http://namecheck.fontdata.com"
  try:
    # Since October 2019, it seems that we need to fake our user-agent
    # in order to get correct query results
    FAKE = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
    response = requests.post(NAMECHECK_URL,
                             params={'q': familyname},
                             headers={'User-Agent': FAKE},
                             timeout=10)
    data = response.content.decode("utf-8")
    if "fonts by that exact name" in data:
      yield INFO,\
            Message("name-collision",
                    f'The family name "{familyname}" seems'
                    f' to be already in use.\n'
                    f'Please visit {NAMECHECK_URL} for more info.')
    else:
      yield PASS, "Font familyname seems to be unique."
  except:
    import sys
    yield ERROR,\
          Message("namecheck-service",
                  f"Failed to access: {NAMECHECK_URL}.\n"
                  f"\t\tThis check relies on the external service"
                  f" http://namecheck.fontdata.com via the internet."
                  f" While the service cannot be reached or does not"
                  f" respond this check is broken.\n"
                  f"\n"
                  f"\t\tYou can exclude this check with the command line"
                  f" option:\n"
                  f"\t\t-x com.google.fonts/check/fontdata_namecheck\n"
                  f"\n"
                  f"\t\tOr you can wait until the service is available again.\n"
                  f"\t\tIf the problem persists please report this issue"
                  f" at: {FB_ISSUE_TRACKER}\n"
                  f"\n"
                  f"\t\tOriginal error message:\n"
                  f"\t\t{sys.exc_info()[0]}")


@check(
  id = 'com.google.fonts/check/fontv',
  rationale = """
    The git sha1 tagging and dev/release features of Source Foundry `font-v` tool are awesome and we would love to consider upstreaming the approach into fontmake someday. For now we only emit a WARN if a given font does not yet follow the experimental versioning style, but at some point we may start enforcing it.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1563'
  })
def com_google_fonts_check_fontv(ttFont):
  """Check for font-v versioning."""
  from fontv.libfv import FontVersion

  fv = FontVersion(ttFont)
  if fv.version and (fv.is_development or fv.is_release):
    yield PASS, "Font version string looks GREAT!"
  else:
    yield INFO,\
          Message("bad-format",
                  f'Version string is: "{fv.get_name_id5_version_string()}"\n'
                  f'The version string must ideally include a git commit hash'
                  f' and either a "dev" or a "release" suffix such as in the'
                  f' example below:\n'
                  f'"Version 1.3; git-0d08353-release"')


# Disabling this check since the previous implementation was
# bogus due to the way fonttools encodes the data into the TTF
# files and the new attempt at targetting the real problem is
# still not quite right.
# FIXME: reimplement this addressing the actual root cause of the issue.
# See also ongoing discussion at:
# https://github.com/googlefonts/fontbakery/issues/1727
@disable
@check(
  id = 'com.google.fonts/check/negative_advance_width',
  rationale = """
    Advance width values in the Horizontal Metrics (htmx) table cannot be negative since they are encoded as unsigned 16-bit values. But some programs may infer and report a negative advance by looking up the x-coordinates of the glyphs directly on the glyf table.

    There are reports of broken versions of Glyphs.app causing this kind of problem as reported at
    https://github.com/googlefonts/fontbakery/issues/1720 and
    https://github.com/fonttools/fonttools/pull/1198

    This check detects and reports such malformed glyf table entries.
  """,
  conditions = ['is_ttf'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1720'
  })
def com_google_fonts_check_negative_advance_width(ttFont):
  """Check that advance widths cannot be inferred as negative."""
  failed = False
  for glyphName in ttFont["glyf"].glyphs:
    coords = ttFont["glyf"][glyphName].coordinates
    rightX = coords[-3][0]
    leftX = coords[-4][0]
    advwidth = rightX - leftX
    if advwidth < 0:
      failed = True
      yield FAIL,\
            Message("bad-coordinates",
                    f'Glyph "{glyphName}" has bad coordinates on the glyf'
                    f' table, which may lead to the advance width to be'
                    f' interpreted as a negative value ({advwidth}).')
  if not failed:
    yield PASS, "The x-coordinates of all glyphs look good."


@check(
  id = 'com.google.fonts/check/varfont/consistent_axes',
  rationale = """
    In order to facilitate the construction of intuitive and friendly user interfaces, all variable font files in a given family should have the same set of variation axes. Also, each axis must have a consistent setting of min/max value ranges accross all the files.
  """,
  conditions = ['VFs'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2810'
  })
def com_google_fonts_check_varfont_consistent_axes(VFs):
  """Ensure that all variable font files have the same set of axes and axis ranges."""
  ref_ranges = {}
  for vf in VFs:
    ref_ranges.update({k.axisTag: (k.minValue, k.maxValue)
                       for k in vf['fvar'].axes})

  passed = True
  for vf in VFs:
    for axis in ref_ranges:
      if axis not in map(lambda x: x.axisTag, vf['fvar'].axes):
        passed = False
        yield FAIL, \
              Message("missing-axis",
                      f"{os.path.basename(vf.reader.file.name)}: lacks a '{axis}' variation axis.")

  expected_ranges = {axis: {(vf['fvar'].axes[vf['fvar'].axes.index(axis)].minValue,
                             vf['fvar'].axes[vf['fvar'].axes.index(axis)].maxValue) for vf in VFs}
                     for axis in ref_ranges
                     if axis in vf['fvar'].axes}

  for axis, ranges in expected_ranges:
    if len(ranges) > 1:
      passed = False
      yield FAIL, \
            Message("inconsistent-axis-range",
                    "Axis 'axis' has diverging ranges accross the family: {ranges}.")

  if passed:
    yield PASS, "All looks good!"


@check(
  id = 'com.google.fonts/check/varfont/generate_static',
  rationale = """
    Google Fonts may serve static fonts which have been generated from variable fonts. This test will attempt to generate a static ttf using fontTool's varLib mutator.

    The target font will be the mean of each axis e.g:

    **VF font axes**

    - min weight, max weight = 400, 800
    - min width, max width = 50, 100

    **Target Instance**

    - weight = 600
    - width = 75
  """,
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1727'
  })
def com_google_fonts_check_varfont_generate_static(ttFont):
  """Check a static ttf can be generated from a variable font."""
  import tempfile
  from fontTools.varLib import mutator

  try:
    loc = {k.axisTag: float((k.maxValue + k.minValue) / 2)
           for k in ttFont['fvar'].axes}
    with tempfile.TemporaryFile() as instance:
      font = mutator.instantiateVariableFont(ttFont, loc)
      font.save(instance)
      yield PASS, ("fontTools.varLib.mutator"
                   " generated a static font instance")
  except Exception as e:
    yield FAIL,\
          Message("varlib-mutator",
                  f"fontTools.varLib.mutator failed"
                  f" to generated a static font instance\n"
                  f"{repr(e)}")


@check(
  id = 'com.google.fonts/check/varfont/has_HVAR',
  rationale = """
    Not having a HVAR table can lead to costly text-layout operations on some platforms, which we want to avoid.

    So, all variable fonts on the Google Fonts collection should have an HVAR with valid values.

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
  """Check that variable fonts have an HVAR table."""
  if "HVAR" in ttFont.keys():
    yield PASS, ("This variable font contains an HVAR table.")
  else:
    yield FAIL,\
          Message("lacks-HVAR",
                  "All variable fonts on the Google Fonts collection"
                  " must have a properly set HVAR table in order"
                  " to avoid costly text-layout operations on"
                  " certain platforms.")


# Temporarily disabled.
# See: https://github.com/googlefonts/fontbakery/issues/2118#issuecomment-432283698
@disable
@check(
  id = 'com.google.fonts/check/varfont/has_MVAR',
  rationale = """
    Per the OpenType spec, the MVAR tables contain variation data for metadata otherwise in tables such as OS/2 and hhea; if not present, then the default values in those tables will apply to all instances, which can effect text layout.

    Thus, MVAR tables should be present and correct in all variable fonts since text layout software depends on these values.
  """, # FIX-ME: Clarify this rationale text.
       #         See: https://github.com/googlefonts/fontbakery/issues/2118#issuecomment-432108560
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2118'
  })
def com_google_fonts_check_varfont_has_MVAR(ttFont):
  """Check that variable fonts have an MVAR table."""
  if "MVAR" in ttFont.keys():
    yield PASS, ("This variable font contains an MVAR table.")
  else:
    yield FAIL,\
          Message("lacks-MVAR",
                  "All variable fonts on the Google Fonts collection"
                  " must have a properly set MVAR table because"
                  " text-layout software depends on it.")


@check(
  id = 'com.google.fonts/check/smart_dropout',
  conditions = ['is_ttf',
                'not VTT_hinted'],
  rationale = """
    This setup is meant to ensure consistent rendering quality for fonts across all devices (with different rendering/hinting capabilities).

    Below is the snippet of instructions we expect to see in the fonts:
    B8 01 FF    PUSHW 0x01FF
    85          SCANCTRL (unconditinally turn on
                          dropout control mode)
    B0 04       PUSHB 0x04
    8D          SCANTYPE (enable smart dropout control)

    "Smart dropout control" means activating rules 1, 2 and 5:
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

    For more detailed info (such as other rules not enabled in this snippet), please refer to the TrueType Instruction Set documentation.
  """
)
def com_google_fonts_check_smart_dropout(ttFont):
  """Font enables smart dropout control in "prep" table instructions?"""
  INSTRUCTIONS = b"\xb8\x01\xff\x85\xb0\x04\x8d"

  if ("prep" in ttFont and
      INSTRUCTIONS in ttFont["prep"].program.getBytecode()):
    yield PASS, ("'prep' table contains instructions"
                  " enabling smart dropout control.")
  else:
    yield FAIL,\
          Message("lacks-smart-dropout",
                  "The 'prep' table does not contain TrueType"
                  " instructions enabling smart dropout control."
                  " To fix, export the font with autohinting enabled,"
                  " or run ttfautohint on the font, or run the"
                  " `gftools fix-nonhinting` script.")


@check(
  id = 'com.google.fonts/check/vttclean',
  rationale = """
    The goal here is to reduce filesizes and improve pageloading when dealing with webfonts.

    The VTT Talk sources are not necessary at runtime and endup being just dead weight when left embedded in the font binaries. The sources should be kept on the project files but stripped out when building release binaries.
  """
)
def com_google_fonts_check_vtt_clean(ttFont, vtt_talk_sources):
  """There must not be VTT Talk sources in the font."""

  if vtt_talk_sources:
    yield FAIL,\
          Message("has-vtt-sources",
                  f"Some tables containing VTT Talk (hinting) sources"
                  f" were found in the font and should be removed in order"
                  f" to reduce total filesize:"
                  f" {', '.join(vtt_talk_sources)}")
  else:
    yield PASS, "There are no tables with VTT Talk sources embedded in the font."


@check(
  id = 'com.google.fonts/check/aat',
  rationale = """
    Apple's TrueType reference manual [1] describes SFNT tables not in the Microsoft OpenType specification [2] and these can sometimes sneak into final release files, but Google Fonts should only have OpenType tables.

    [1] https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html
    [2] https://docs.microsoft.com/en-us/typography/opentype/spec/
  """
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
    yield FAIL,\
          Message("has-unwanted-tables",
                  f"Unwanted AAT tables were found"
                  f" in the font and should be removed, either by"
                  f" fonttools/ttx or by editing them using the tool"
                  f" they built with:"
                  f" {', '.join(unwanted_tables_found)}")
  else:
    yield PASS, "There are no unwanted AAT tables."


@check(
  id = 'com.google.fonts/check/fvar_name_entries',
  conditions = ['is_variable_font'],
  rationale = """
    The purpose of this check is to make sure that all name entries referenced by variable font instances do exist in the name table.
  """
)
def com_google_fonts_check_fvar_name_entries(ttFont):
  """All name entries referenced by fvar instances exist on the name table?"""

  failed = False
  for instance in ttFont["fvar"].instances:

    entries = [entry for entry in ttFont["name"].names
               if entry.nameID == instance.subfamilyNameID]
    if len(entries) == 0:
      failed = True
      yield FAIL,\
            Message("missing-name",
                    f"Named instance with coordinates {instance.coordinates}"
                    f" lacks an entry on the name table"
                    f" (nameID={instance.subfamilyNameID}).")

  if not failed:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/varfont_has_instances',
  conditions = ['is_variable_font'],
  rationale = """
    Named instances must be present in all variable fonts in order not to frustrate the users' typical expectations of a traditional static font workflow.
  """
)
def com_google_fonts_check_varfont_has_instances(ttFont):
  """A variable font must have named instances."""

  if len(ttFont["fvar"].instances):
    yield PASS, "OK"
  else:
    yield FAIL,\
          Message("lacks-named-instances",
                  "This variable font lacks"
                  " named instances on the fvar table.")


@check(
  id = 'com.google.fonts/check/varfont_weight_instances',
  conditions = ['is_variable_font'],
  rationale = """
    The named instances on the weight axis of a variable font must have coordinates that are multiples of 100 on the design space.
  """
)
def com_google_fonts_check_varfont_weight_instances(ttFont):
  """Variable font weight coordinates must be multiples of 100."""

  failed = False
  for instance in ttFont["fvar"].instances:
    if 'wght' in instance.coordinates and instance.coordinates['wght'] % 100 != 0:
      failed = True
      yield FAIL,\
            Message("bad-coordinate",
                    f"Found a variable font instance with"
                    f" 'wght'={instance.coordinates['wght']}."
                    f" This should instead be a multiple of 100.")

  if not failed:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/family/tnum_horizontal_metrics',
  conditions = ['RIBBI_ttFonts'],
  rationale = """
    Tabular figures need to have the same metrics in all styles in order to allow tables to be set with proper typographic control, but to maintain the placement of decimals and numeric columns between rows.

    Here's a good explanation of this:
    https://www.typography.com/techniques/fonts-for-financials/#tabular-figs
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2278'
  }
)
def com_google_fonts_check_family_tnum_horizontal_metrics(RIBBI_ttFonts):
  """All tabular figures must have the same width across the RIBBI-family."""
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
    yield FAIL,\
          Message("inconsistent-widths",
                  f"The most common tabular glyph width is"
                  f" {most_common_width}. But there are other"
                  f" tabular glyphs with different widths"
                  f" such as the following ones:\n\t{tnum_widths}.")
  else:
    yield PASS, "OK"


@check(
  id = 'com.google.fonts/check/integer_ppem_if_hinted',
  conditions = ['is_hinted'],
  rationale = """
    Hinted fonts must have head table flag bit 3 set.

    Per https://docs.microsoft.com/en-us/typography/opentype/spec/head, bit 3 of Head::flags decides whether PPEM should be rounded. This bit should always be set for hinted fonts.

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
    yield FAIL,\
          Message("bad-flags",
                  ("This is a hinted font, so it must have bit 3 set"
                   " on the flags of the head table, so that"
                   " PPEM values will be rounded into an integer"
                   " value.\n"
                   "\n"
                   "This can be accomplished by using the"
                   " 'gftools fix-hinting' command.\n"
                   "\n"
                   "# create virtualenv"
                   "python3 -m venv venv"
                   "\n"
                   "# activate virtualenv"
                   "source venv/bin/activate"
                   "\n"
                   "# install gftools"
                   "pip install git+https://www.github.com"
                   "/googlefonts/tools"))


@check(
  id = 'com.google.fonts/check/ligature_carets',
  conditions = ['ligature_glyphs'],
  rationale = """
    All ligatures in a font must have corresponding caret (text cursor) positions defined in the GDEF table, otherwhise, users may experience issues with caret rendering.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1225'
  }
)
def com_google_fonts_check_ligature_carets(ttFont, ligature_glyphs):
  """Are there caret positions declared for every ligature?"""
  if ligature_glyphs == -1:
    yield FAIL,\
          Message("malformed",
                  ("Failed to lookup ligatures."
                   " This font file seems to be malformed."
                   " For more info, read:"
                   " https://github.com/googlefonts/fontbakery/issues/1596"))
  elif "GDEF" not in ttFont:
    yield WARN,\
          Message("GDEF-missing",
                  ("GDEF table is missing, but it is mandatory"
                   " to declare it on fonts that provide ligature"
                   " glyphs because the caret (text cursor)"
                   " positioning for each ligature must be"
                   " provided in this table."))
  else:
    lig_caret_list = ttFont["GDEF"].table.LigCaretList
    if lig_caret_list is None:
      missing = set(ligature_glyphs)
    else:
      missing = set(ligature_glyphs) - set(lig_caret_list.Coverage.glyphs)

    if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
      yield WARN,\
            Message("lacks-caret-pos",
                    "This font lacks caret position values"
                    " for ligature glyphs on its GDEF table.")
    elif missing:
      missing = "\n\t- ".join(missing)
      yield WARN,\
            Message("incomplete-caret-pos-data",
                    f"This font lacks caret positioning"
                    f" values for these ligature glyphs:"
                    f"\n\t- {missing}\n\n  ")
    else:
      yield PASS, "Looks good!"


@check(
  id = 'com.google.fonts/check/kerning_for_non_ligated_sequences',
  conditions = ['ligatures',
                'has_kerning_info'],
  rationale = """
    Fonts with ligatures should have kerning on the corresponding non-ligated sequences for text where ligatures aren't used (eg https://github.com/impallari/Raleway/issues/14).
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1145'
  })
def com_google_fonts_check_kerning_for_non_ligated_sequences(ttFont, ligatures, has_kerning_info):
  """Is there kerning info for non-ligated sequences?"""

  def look_for_nonligated_kern_info(table):
    for pairpos in table.SubTable:
      for i, glyph in enumerate(pairpos.Coverage.glyphs):
        if not hasattr(pairpos, 'PairSet'):
          continue
        for pairvalue in pairpos.PairSet[i].PairValueRecord:
          kern_pair = (glyph, pairvalue.SecondGlyph)
          if kern_pair in ligature_pairs:
            ligature_pairs.remove(kern_pair)

  def ligatures_str(pairs):
    result = [f"\t- {first} + {second}" for first, second in pairs]
    return "\n".join(result)

  if ligatures == -1:
    yield FAIL,\
          Message("malformed",
                  "Failed to lookup ligatures."
                  " This font file seems to be malformed."
                  " For more info, read:"
                  " https://github.com/googlefonts/fontbakery/issues/1596")
  else:
    ligature_pairs = []
    for first, comp in ligatures.items():
      for components in comp:
        while components:
          pair = (first, components[0])
          if pair not in ligature_pairs:
            ligature_pairs.append(pair)
          first = components[0]
          components.pop(0)

    for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
      if record.FeatureTag == 'kern':
        for index in record.Feature.LookupListIndex:
          lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
          look_for_nonligated_kern_info(lookup)

    if ligature_pairs:
      yield WARN,\
            Message("lacks-kern-info",
                    f"GPOS table lacks kerning info for the following"
                    f" non-ligated sequences:\n"
                    f"{ligatures_str(ligature_pairs)}\n\n  ")
    else:
      yield PASS, ("GPOS table provides kerning info for "
                   "all non-ligated sequences.")


@check(
  id = 'com.google.fonts/check/name/family_and_style_max_length',
  rationale = """
    According to a GlyphsApp tutorial [1], in order to make sure all versions of Windows recognize it as a valid font file, we must make sure that the concatenated length of the familyname (NameID.FONT_FAMILY_NAME) and style (NameID.FONT_SUBFAMILY_NAME) strings in the name table do not exceed 20 characters.

    After discussing the problem in more detail at `FontBakery issue #2179 [2] we decided that allowing up to 27 chars would still be on the safe side, though.

    [1] https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances
    [2] https://github.com/googlefonts/fontbakery/issues/2179
  """,
  misc_metadata = {
    # Somebody with access to Windows should make some experiments
    # and confirm that this is really the case.
    'affects': [('Windows', 'unspecified')],
    'request': 'https://github.com/googlefonts/fontbakery/issues/1488',
  }
)
def com_google_fonts_check_name_family_and_style_max_length(ttFont):
  """Combined length of family and style must not exceed 27 characters."""
  from fontbakery.utils import (get_name_entries,
                                get_name_entry_strings)
  failed = False
  for familyname in get_name_entries(ttFont,
                                     NameID.FONT_FAMILY_NAME):
    # we'll only match family/style name entries with the same platform ID:
    plat = familyname.platformID
    familyname_str = familyname.string.decode(familyname.getEncoding())
    for stylename_str in get_name_entry_strings(ttFont,
                                                NameID.FONT_SUBFAMILY_NAME,
                                                platformID=plat):
      if len(familyname_str + stylename_str) > 27:
        failed = True
        yield WARN,\
              Message("too-long",
                      f"The combined length of family and style"
                      f" exceeds 27 chars in the following"
                      f" '{PlatformID(plat).name}' entries:\n"
                      f" FONT_FAMILY_NAME = '{familyname_str}' /"
                      f" SUBFAMILY_NAME = '{stylename_str}'\n"
                      f"\n"
                      f"Please take a look at the conversation at"
                      f" https://github.com/googlefonts/fontbakery/issues/2179"
                      f" in order to understand the reasoning behind these"
                      f" name table records max-length criteria.")
  if not failed:
    yield PASS, "All name entries are good."


@check(
  id = 'com.google.fonts/check/name/line_breaks',
  rationale = """
    There are some entries on the name table that may include more than one line of text. The Google Fonts team, though, prefers to keep the name table entries short and simple without line breaks.

    For instance, some designers like to include the full text of a font license in the "copyright notice" entry, but for the GFonts collection this entry should only mention year, author and other basic info in a manner enforced by com.google.fonts/check/font_copyright
  """
)
def com_google_fonts_check_name_line_breaks(ttFont):
  """Name table entries should not contain line-breaks."""
  failed = False
  for name in ttFont["name"].names:
    string = name.string.decode(name.getEncoding())
    if "\n" in string:
      failed = True
      yield FAIL,\
            Message("line-break",
                    f"Name entry {NameID(name.nameID).name}"
                    f" on platform {PlatformID(name.platformID).name}"
                    f" contains a line-break.")
  if not failed:
    yield PASS, ("Name table entries are all single-line"
                 " (no line-breaks found).")


@check(
  id = 'com.google.fonts/check/name/rfn',
  rationale = """
    Some designers adopt the "Reserved Font Name" clause of the OFL license. This means that the original author reserves the rights to the family name and other people can only distribute modified versions using a different family name.

    Google Fonts published updates to the fonts in the collection in order to fix issues and/or implement further improvements to the fonts. It is important to keep the family name so that users of the webfonts can benefit from the updates. Since it would forbid such usage scenario, all families in the GFonts collection are required to not adopt the RFN clause.

    This check ensures "Reserved Font Name" is not mentioned in the name table.
  """
)
def com_google_fonts_check_name_rfn(ttFont):
  """Name table strings must not contain the string 'Reserved Font Name'."""
  failed = False
  for entry in ttFont["name"].names:
    string = entry.toUnicode()
    if "reserved font name" in string.lower():
      yield FAIL,\
            Message("rfn",
                    f'Name table entry ("{string}")'
                    f' contains "Reserved Font Name".'
                    f' This is an error except in a few specific rare cases.')
      failed = True
  if not failed:
    yield PASS, 'None of the name table strings contain "Reserved Font Name".'


@check(
  id='com.google.fonts/check/family/control_chars',
  conditions=['are_ttf'],
  rationale="""
    Use of some unacceptable control characters in the U+0000 - U+001F range can lead to rendering issues on some platforms.
   
    Acceptable control characters are defined as .null (U+0000) and CR (U+000D) for this test.
  """
)
def com_google_fonts_check_family_control_chars(ttFonts):
  """Does font file include unacceptable control character glyphs?"""
  # list of unacceptable control character glyph names
  # definition includes the entire control character Unicode block except:
  #    - .null (U+0000)
  #    - CR (U+000D)
  unacceptable_cc_list = [
    "uni0001",
    "uni0002",
    "uni0003",
    "uni0004",
    "uni0005",
    "uni0006",
    "uni0007",
    "uni0008",
    "uni0009",
    "uni000A",
    "uni000B",
    "uni000C",
    "uni000E",
    "uni000F",
    "uni0010",
    "uni0011",
    "uni0012",
    "uni0013",
    "uni0014",
    "uni0015",
    "uni0016",
    "uni0017",
    "uni0018",
    "uni0019",
    "uni001A",
    "uni001B",
    "uni001C",
    "uni001D",
    "uni001E",
    "uni001F"
  ]

  # a dict with key:value of font path that failed check : list of unacceptable glyph names
  failed_font_dict = {}

  for ttFont in ttFonts:
    font_failed = False
    unacceptable_glyphs_in_set = []  # a list of unacceptable glyph names identified
    glyph_name_set = set(ttFont["glyf"].glyphs.keys())
    fontname = ttFont.reader.file.name

    for unacceptable_glyph_name in unacceptable_cc_list:
      if unacceptable_glyph_name in glyph_name_set:
        font_failed = True
        unacceptable_glyphs_in_set.append(unacceptable_glyph_name)

    if font_failed:
        failed_font_dict[fontname] = unacceptable_glyphs_in_set

  if len(failed_font_dict) > 0:
    msg_unacceptable = "The following unacceptable control characters were identified:\n"
    for fnt in failed_font_dict.keys():
      msg_unacceptable += f" {fnt}: {', '.join(failed_font_dict[fnt])}\n"
    yield FAIL,\
          Message("unacceptable",
                  f"{msg_unacceptable}")
  else:
    yield PASS, ("Unacceptable control characters were not identified.")


@check(
  id = 'com.google.fonts/check/repo/dirname_matches_nameid_1',
  conditions = ['gfonts_repo_structure',
                'not is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2302'
  }
)
def com_google_fonts_check_repo_dirname_match_nameid_1(fonts,
                                                       gfonts_repo_structure):
  """Directory name in GFonts repo structure must
     match NameID 1 of the regular."""
  from fontTools.ttLib import TTFont
  from fontbakery.utils import (get_name_entry_strings,
                                get_absolute_path,
                                get_regular)
  regular = get_regular(fonts)
  if not regular:
    yield FAIL,\
          Message("lacks-regular",
                  "The font seems to lack a regular.")
    return

  entry = get_name_entry_strings(TTFont(regular), NameID.FONT_FAMILY_NAME)[0]
  expected = entry.lower()
  expected = "".join(expected.split(' '))
  expected = "".join(expected.split('-'))

  license, familypath, filename = get_absolute_path(regular).split(os.path.sep)[-3:]
  if familypath == expected:
    yield PASS, "OK"
  else:
    yield FAIL,\
          Message("mismatch",
                  f"Family name on the name table ('{entry}') does not match"
                  f" directory name in the repo structure ('{familypath}')."
                  f" Expected '{expected}'.")


@check(
  id = 'com.google.fonts/check/repo/vf_has_static_fonts',
  conditions = ['family_directory',
                'gfonts_repo_structure',
                'is_variable_font'],
  rationale="""
    Variable font family directories kept in the google/fonts git repo must include a static/ subdir containing static fonts.
    These files are meant to be served for users that still lack support for variable fonts in their web browsers.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2654'
  }
)
def com_google_fonts_check_repo_vf_has_static_fonts(family_directory):
  """A static fonts directory with at least two fonts must accompany variable fonts"""
  static_dir = os.path.join(family_directory, 'static')
  if os.path.exists(static_dir):
    has_static_fonts = any([f for f in os.listdir(static_dir)
                            if f.endswith('.ttf')])
    if has_static_fonts:
      yield PASS, 'OK'
    else:
      yield FAIL, \
            Message("empty",
                    'Static dir is empty')
  else:
    yield FAIL, \
          Message("missing",
                  'Please create a subdirectory called "static/"'
                  ' and include in it static font files.')


@check(
  id = 'com.google.fonts/check/repo/fb_report',
  conditions = ['family_directory'],
  rationale="""
    A FontBakery report is ephemeral and so should be used for posting issues on a bug-tracker instead of being hosted in the font project repository.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2888'
  }
)
def com_google_fonts_check_repo_fb_report(family_directory):
  """A font repository should not include fontbakery report files"""
  from fontbakery.utils import filenames_ending_in

  has_report_files = any([f for f in filenames_ending_in(".json", family_directory)
                          if '"result"' in open(f).read()])
  if not has_report_files:
    yield PASS, 'OK'
  else:
    yield WARN, \
          Message("fb-report",
                  "There's no need to keep a copy of Font Bakery reports in the repository,"
                  " since they are ephemeral; FB has a 'github markdown' output mode"
                  " to make it easy to file reports as issues.")


@check(
  id = 'com.google.fonts/check/repo/zip_files',
  conditions = ['family_directory'],
  rationale="""
    Sometimes people check in ZIPs into their font project repositories. While we accept the practice of checking in binaries, we believe that a ZIP is a step too far ;)

    Note: a source purist position is that only source files and build scripts should be checked in. 
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2903'
  }
)
def com_google_fonts_check_repo_zip_files(family_directory):
  """A font repository should not include ZIP files"""
  from fontbakery.utils import (filenames_ending_in,
                                pretty_print_list)

  COMMON_ZIP_EXTENSIONS = [".zip", ".7z", ".rar"]
  zip_files = []
  for ext in COMMON_ZIP_EXTENSIONS:
    zip_files.extend(filenames_ending_in(ext, family_directory))

  if not zip_files:
    yield PASS, 'OK'
  else:
    files_list = pretty_print_list(zip_files,
                                   shorten=None,
                                   sep='\n\t* ')
    yield FAIL, \
          Message("zip-files",
                  f"Please do not host ZIP files on the project repository."
                  f" These files were detected:\n"
                  f"\t* {files_list}")


@check(
  id = 'com.google.fonts/check/vertical_metrics_regressions',
  conditions = ['remote_styles'],
  rationale="""
    If the family already exists on Google Fonts, we need to ensure that the checked family's vertical metrics are similar. This check will test the following schema which was outlined in Fontbakery issue #1162 [1]:

    - The family should visually have the same vertical metrics as the
      Regular style hosted on Google Fonts.
    - If the family on Google Fonts has differing hhea and typo metrics,
      the family being checked should use the typo metrics for both the
      hhea and typo entries.
    - If the family on Google Fonts has use typo metrics not enabled and the
      family being checked has it enabled, the hhea and typo metrics
      should use the family on Google Fonts winAscent and winDescent values.
    - If the upms differ, the values must be scaled so the visual appearance
      is the same.

    [1] https://github.com/googlefonts/fontbakery/issues/1162
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1162'
  }
)
def com_google_fonts_check_vertical_metrics_regressions(ttFonts, remote_styles):
  """Check if the vertical metrics of a family are similar to the same
  family hosted on Google Fonts."""
  import math
  from .shared_conditions import (is_variable_font,
                                  get_instance_axis_value,
                                  typo_metrics_enabled)


  failed = False
  ttFonts = list(ttFonts)
  if "Regular" in remote_styles:
    gf_font = remote_styles["Regular"]
  else:
    gf_font = None
    for style, font in remote_styles:
      if is_variable_font(font):
        if get_instance_axis_value(font, "Regular", "wght"):
          gf_font = font
  if not gf_font:
    gf_font = remote_styles[0][1]

  upm_scale = ttFonts[0]['head'].unitsPerEm / gf_font['head'].unitsPerEm

  gf_has_typo_metrics = typo_metrics_enabled(gf_font)
  fam_has_typo_metrics = typo_metrics_enabled(ttFonts[0])

  if (gf_has_typo_metrics and fam_has_typo_metrics) or \
  (not gf_has_typo_metrics and not fam_has_typo_metrics):
    expected_ascender = math.ceil(gf_font['OS/2'].sTypoAscender * upm_scale)
    expected_descender = math.ceil(gf_font['OS/2'].sTypoDescender * upm_scale)
  else:
    expected_ascender = math.ceil(gf_font["OS/2"].usWinAscent * upm_scale)
    expected_descender = -math.ceil(gf_font["OS/2"].usWinDescent * upm_scale)

  for ttFont in ttFonts:
    full_font_name = ttFont['name'].getName(4, 3, 1, 1033).toUnicode()
    typo_ascender = ttFont['OS/2'].sTypoAscender
    typo_descender = ttFont['OS/2'].sTypoDescender
    hhea_ascender = ttFont['hhea'].ascent
    hhea_descender = ttFont['hhea'].descent

    if typo_ascender != expected_ascender:
      failed = True
      yield FAIL,\
            Message("bad-typo-ascender",
                    f"{full_font_name}:"
                    f" OS/2 sTypoAscender is {typo_ascender}"
                    f" when it should be {expected_ascender}")

    if typo_descender != expected_descender:
      failed = True
      yield FAIL,\
            Message("bad-typo-descender",
                    f"{full_font_name}:"
                    f" OS/2 sTypoDescender is {typo_descender}"
                    f" when it should be {expected_descender}")

    if hhea_ascender != expected_ascender:
      failed = True
      yield FAIL,\
            Message("bad-hhea-ascender",
                    f"{full_font_name}:"
                    f" hhea Ascender is {hhea_ascender}"
                    f" when it should be {expected_ascender}")

    if hhea_descender != expected_descender:
      failed = True
      yield FAIL,\
            Message("bad-hhea-descender",
                    f"{full_font_name}:"
                    f" hhea Descender is {hhea_descender}"
                    f" when it should be {expected_descender}")
  if not failed:
    yield PASS, "Vertical metrics have not regressed."


@check(
  id = 'com.google.fonts/check/cjk_vertical_metrics',
  conditions = ['is_cjk_font',
                'not remote_styles'],
  rationale="""
    CJK fonts have different vertical metrics when compared to Latin fonts. We follow the schema developed by dr Ken Lunde for Source Han Sans and the Noto CJK fonts.

    Our documentation includes further information: https://github.com/googlefonts/gf-docs/tree/master/Spec#cjk-vertical-metrics
  """
)
def com_google_fonts_check_cjk_vertical_metrics(ttFont):
  """Check font follows the Google Fonts CJK vertical metric schema"""
  from .shared_conditions import is_cjk_font, typo_metrics_enabled
  filename = os.path.basename(ttFont.reader.file.name)

  # Check necessary tables are present.
  missing_tables = False
  required = ["OS/2", "hhea", "head"]
  for key in required:
    if key not in ttFont:
      missing_tables = True
      yield FAIL,\
            Message(f'lacks-{key}',
                    f"{filename} lacks a '{key}' table.")

  if missing_tables:
    return

  font_upm = ttFont['head'].unitsPerEm
  font_metrics = {
    'OS/2.sTypoAscender': ttFont['OS/2'].sTypoAscender,
    'OS/2.sTypoDescender': ttFont['OS/2'].sTypoDescender,
    'OS/2.sTypoLineGap': ttFont['OS/2'].sTypoLineGap,
    'hhea.ascent': ttFont['hhea'].ascent,
    'hhea.descent': ttFont['hhea'].descent,
    'hhea.lineGap': ttFont['hhea'].lineGap,
    'OS/2.usWinAscent': ttFont['OS/2'].usWinAscent,
    'OS/2.usWinDescent': ttFont['OS/2'].usWinDescent
  }
  expected_metrics = {
    'OS/2.sTypoAscender': font_upm * 0.88,
    'OS/2.sTypoDescender': font_upm * -0.12,
    'OS/2.sTypoLineGap': 0,
    'hhea.lineGap': 0,
  }

  failed = False
  warn = False

  # Check fsSelection bit 7 is not enabled
  if typo_metrics_enabled(ttFont):
    failed = True
    yield FAIL, \
          Message('bad-fselection-bit7',
                  'OS/2 fsSelection bit 7 must be disabled')

  # Check typo metrics and hhea lineGap match our expected values
  for k in expected_metrics:
    if font_metrics[k] != expected_metrics[k]:
      failed = True
      yield FAIL, \
            Message(f'bad-{k}',
                    f'{k} is "{font_metrics[k]}" it should be {expected_metrics[k]}')

  # Check hhea and win values match
  if font_metrics['hhea.ascent'] != font_metrics['OS/2.usWinAscent']:
      failed = True
      yield FAIL, \
            Message('ascent-mismatch',
                    'hhea.ascent must match OS/2.usWinAscent')

  if abs(font_metrics['hhea.descent']) != font_metrics['OS/2.usWinDescent']:
      failed = True
      yield FAIL, \
            Message('descent-mismatch',
                    'hhea.descent must match absolute value of OS/2.usWinDescent')

  # Check the sum of the hhea metrics is between 1.1-1.5x of the font's upm
  hhea_sum = (font_metrics['hhea.ascent'] +
              abs(font_metrics['hhea.descent']) +
              font_metrics['hhea.lineGap']) / font_upm
  if not failed and not 1.1 < hhea_sum <= 1.5:
    warn = True
    yield WARN, \
          Message('bad-hhea-range',
                  f"We recommend the absolute sum of the hhea metrics should be"
                  f" between 1.1-1.4x of the font's upm. This font has {hhea_sum}x")

  if not failed and not warn:
    yield PASS, 'Vertical metrics are good'


@check(
  id = 'com.google.fonts/check/varfont_instance_coordinates',
  conditions = ['is_variable_font'],
)
def com_google_fonts_check_varfont_instance_coordinates(ttFont):
  """Check variable font instances have correct coordinate values"""
  from fontbakery.parse import instance_parse
  from fontbakery.constants import SHOW_GF_DOCS_MSG
  failed = False
  for instance in ttFont['fvar'].instances:
    name = ttFont['name'].getName(
      instance.subfamilyNameID,
      PlatformID.WINDOWS,
      WindowsEncodingID.UNICODE_BMP,
      WindowsLanguageID.ENGLISH_USA
    ).toUnicode()
    expected_instance = instance_parse(name)
    for axis in instance.coordinates:
      if axis in expected_instance.coordinates and \
        instance.coordinates[axis] != expected_instance.coordinates[axis]:
        yield FAIL, \
          Message("bad-coordinate",
            f'Instance "{name}" {axis} value '
            f'is "{instance.coordinates[axis]}". '
            f'It should be "{expected_instance.coordinates[axis]}"')
        failed = True
  if failed:
    yield FAIL, SHOW_GF_DOCS_MSG
  else:
    yield PASS, "Instance coordinates are correct"


@check(
  id = 'com.google.fonts/check/varfont_instance_names',
  conditions = ['is_variable_font'],
)
def com_google_fonts_check_varfont_instance_names(ttFont):
  """Check variable font instances have correct names"""
  from fontbakery.parse import instance_parse
  from fontbakery.constants import SHOW_GF_DOCS_MSG
  show_docs, failed = False, False
  for instance in ttFont['fvar'].instances:
    name = ttFont['name'].getName(
      instance.subfamilyNameID,
      PlatformID.WINDOWS,
      WindowsEncodingID.UNICODE_BMP,
      WindowsLanguageID.ENGLISH_USA
    ).toUnicode()
    expected_instance = instance_parse(name)
    if expected_instance.unparsable_tokens:
      yield WARN, (
        f'Instance "{name}": contains the following unparsable tokens '
        f'"{expected_instance.unparsable_tokens}"'
      )
      show_docs = True
    # Check if name tokens are missing
    missing_tokens = set(expected_instance.expected_token_order) - \
                     set(expected_instance.raw_token_order)
    if missing_tokens:
      missing_tokens = ", ".join(missing_tokens)
      yield FAIL, (
        f'Instance "{name}": is missing the following name tokens '
        f'[{missing_tokens}]'
      )
      show_docs, failed = True, True
    # Check if name tokens are ordered correctly
    elif expected_instance.raw_token_order != expected_instance.expected_token_order:
      yield FAIL, (
        f'Instance "{name}": token ordering is incorrect '
        f'"{expected_instance.raw_token_order}". It should be '
        f'"{expected_instance.expected_token_order}"'
      )
      show_docs, failed = True, True
    # Check if name matches predicted name
    if not expected_instance.unparsable_tokens:
      if expected_instance.name != name:
        yield FAIL, \
          Message("bad-name",
            f'Instance name "{name}" is incorrect. '
            f'It should be "{expected_instance.name}"')
        show_docs, failed = True, True
    else:
      yield WARN, (
        f'Instance "{name}": cannot determine instance name due to '
        f'unparsable tokens'
      )
      show_docs = True

  if show_docs and failed:
    yield FAIL, Message("bad-instance-names", SHOW_GF_DOCS_MSG)
  elif show_docs and not failed:
    yield WARN, SHOW_GF_DOCS_MSG
  else:
    yield PASS, "Instance names are correct"


@check(
  id = 'com.google.fonts/check/varfont/unsupported_axes',
  rationale = """
    The 'ital' axis is not supported yet in Google Chrome. The 'opsz' axis also has patchy support.

    For the time being, we need to ensure that VFs do not contain either of these axes. Once browser support is better, we can deprecate this check.

    For more info regarding ital and opsz browser support, see:
    https://arrowtype.github.io/vf-slnt-test/
  """,
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2866'
  }
)
def com_google_fonts_check_varfont_unsupported_axes(ttFont):
  """ Ensure VFs do not contain opsz or ital axes. """
  from fontbakery.profiles.shared_conditions import opsz_axis, ital_axis
  if ital_axis(ttFont):
    yield FAIL,\
          Message("unsupported-ital",
                  'The "ital" axis is not yet well supported on Google Chrome.')
  elif opsz_axis(ttFont):
    yield FAIL,\
          Message("unsupported-opsz",
                  'The "opsz" axis is not yet well supported on Google Chrome.')
  else:
    yield PASS, "Looks good!"


###############################################################################

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


def check_skip_filter(checkid, font=None, **iterargs):
  if font and is_librebarcode(font) and checkid in (
    # See: https://github.com/graphicore/librebarcode/issues/3
    'com.google.fonts/check/monospace',
    'com.google.fonts/check/gpos_kerning_info',
    'com.google.fonts/check/currency_chars',
    'com.google.fonts/check/whitespace_ink'
  ):
    return False, ('LibreBarcode is blacklisted for this check, see '
                   'https://github.com/graphicore/librebarcode/issues/3')
  return True, None


profile.check_skip_filter = check_skip_filter
profile.auto_register(globals())
profile.test_expected_checks(GOOGLEFONTS_PROFILE_CHECKS, exclusive=True)
