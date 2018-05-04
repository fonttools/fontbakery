from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN, INFO
from fontbakery.constants import CRITICAL
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('seems_monospaced', 'monospace_stats'))
]

@check(
  id = 'com.google.fonts/check/031',
  misc_metadata = {
    'priority': CRITICAL
  }
)
def com_google_fonts_check_031(ttFont):
  """Description strings in the name table must not contain copyright info."""
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


@check(
  id = 'com.google.fonts/check/032'
)
def com_google_fonts_check_032(ttFont):
  """Description strings in the name table must not exceed 100 characters."""
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


@check(
  id = 'com.google.fonts/check/033',
  conditions = ['monospace_stats',
                'is_ttf']
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
                                    PANOSE_PROPORTION__MONOSPACED)
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
                         "").format(width_max, ttFont['hhea'].advanceWidthMax))
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
        if g not in ['.notdef', '.null', 'NULL'] and
        ttFont['hmtx'].metrics[g][0] != most_common_width
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
                               100.0 * outliers_ratio, unusually_spaced_glyphs))
    if not failed:
      yield PASS, Message("mono-good", ("Font is monospaced and all"
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
      yield PASS, Message("good", ("Font is not monospaced and"
                                   " all related metadata look good."))


@check(
  id = 'com.google.fonts/check/057'
)
def com_google_fonts_check_057(ttFont):
  """Name table entries should not contain line-breaks."""
  from fontbakery.constants import (NAMEID_STR, PLATID_STR)
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
      yield FAIL, Message(
          "does-not", (" On the 'name' table, the full font name"
                       " (NameID {} - FULL_FONT_NAME: '{}')"
                       " does not begin with font family name"
                       " (NameID {} - FONT_FAMILY_NAME:"
                       " '{}')".format(NAMEID_FULL_FONT_NAME, familyname,
                                       NAMEID_FONT_FAMILY_NAME, fullfontname)))
    else:
      yield PASS, "Full font name begins with the font family name."


@check(
  id = 'com.google.fonts/check/071'
)
def com_google_fonts_check_071(ttFont):
  """Font follows the family naming recommendations?"""
  # See http://forum.fontlab.com/index.php?topic=313.0
  import re
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import (
      NAMEID_POSTSCRIPT_NAME, NAMEID_FULL_FONT_NAME, NAMEID_FONT_FAMILY_NAME,
      NAMEID_FONT_SUBFAMILY_NAME, NAMEID_TYPOGRAPHIC_FAMILY_NAME,
      NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
  bad_entries = []

  # <Postscript name> may contain only a-zA-Z0-9
  # and one hyphen
  bad_psname = re.compile("[^A-Za-z0-9-]")
  for string in get_name_entry_strings(ttFont, NAMEID_POSTSCRIPT_NAME):
    if bad_psname.search(string):
      bad_entries.append({
          'field':
          'PostScript Name',
          'value':
          string,
          'rec':
          'May contain only a-zA-Z0-9'
          ' characters and an hyphen.'
      })
    if string.count('-') > 1:
      bad_entries.append({
          'field': 'Postscript Name',
          'value': string,
          'rec': 'May contain not more'
          ' than a single hyphen'
      })

  for string in get_name_entry_strings(ttFont, NAMEID_FULL_FONT_NAME):
    if len(string) >= 64:
      bad_entries.append({
          'field': 'Full Font Name',
          'value': string,
          'rec': 'exceeds max length (63)'
      })

  for string in get_name_entry_strings(ttFont, NAMEID_POSTSCRIPT_NAME):
    if len(string) >= 30:
      bad_entries.append({
          'field': 'PostScript Name',
          'value': string,
          'rec': 'exceeds max length (29)'
      })

  for string in get_name_entry_strings(ttFont, NAMEID_FONT_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'Family Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont, NAMEID_FONT_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'Style Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont, NAMEID_TYPOGRAPHIC_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'OT Family Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'OT Style Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })
  weight_value = None
  if "OS/2" in ttFont:
    field = "OS/2 usWeightClass"
    weight_value = ttFont["OS/2"].usWeightClass

  if weight_value is not None:
    # <Weight> value >= 250 and <= 900 in steps of 50
    if weight_value % 50 != 0:
      bad_entries.append({
          "field": field,
          'value': weight_value,
          "rec": "Value should ideally be a multiple of 50."
      })
    full_info = " "
    " 'Having a weightclass of 100 or 200 can result in a \"smear bold\" or"
    " (unintentionally) returning the style-linked bold. Because of this,"
    " you may wish to manually override the weightclass setting for all"
    " extra light, ultra light or thin fonts'"
    " - http://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html"
    if weight_value < 250:
      bad_entries.append({
          "field":
          field,
          'value':
          weight_value,
          "rec":
          "Value should ideally be 250 or more." + full_info
      })
    if weight_value > 900:
      bad_entries.append({
          "field": field,
          'value': weight_value,
          "rec": "Value should ideally be 900 or less."
      })
  if len(bad_entries) > 0:
    table = "| Field | Value | Recommendation |\n"
    table += "|:----- |:----- |:-------------- |\n"
    for bad in bad_entries:
      table += "| {} | {} | {} |\n".format(bad["field"], bad["value"],
                                           bad["rec"])
    yield INFO, ("Font does not follow "
                 "some family naming recommendations:\n\n"
                 "{}").format(table)
  else:
    yield PASS, "Font follows the family naming recommendations."


@check(
  id = 'com.google.fonts/check/152'
)
def com_google_fonts_check_152(ttFont):
  """Name table strings must not contain the string 'Reserved Font Name'."""
  failed = False
  for entry in ttFont["name"].names:
    string = entry.toUnicode()
    if "reserved font name" in string.lower():
      yield WARN, ("Name table entry (\"{}\")"
                   " contains \"Reserved Font Name\"."
                   " This is an error except in a few specific"
                   " rare cases.").format(string)
      failed = True
  if not failed:
    yield PASS, ("None of the name table strings"
                 " contain \"Reserved Font Name\".")


@check(
  id = 'com.google.fonts/check/163',
  rationale = """
    According to a Glyphs tutorial (available at
    https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances),
    in order to make sure all versions of Windows recognize it as a valid
    font file, we must make sure that the concatenated length of the
    familyname (NAMEID_FONT_FAMILY_NAME) and style
    (NAMEID_FONT_SUBFAMILY_NAME)
    strings in the name table do not exceed 20 characters.
    """,
  misc_metadata = {
    # Somebody with access to Windows should make some experiments
    # and confirm that this is really the case.
    'affects': [('Windows', 'unspecified')],
    'request': 'https://github.com/googlefonts/fontbakery/issues/1488',
  }
)
def com_google_fonts_check_163(ttFont):
  """Combined length of family and style must not exceed 20 characters."""
  from unidecode import unidecode
  from fontbakery.utils import (get_name_entries, get_name_entry_strings)
  from fontbakery.constants import (NAMEID_FONT_FAMILY_NAME,
                                    NAMEID_FONT_SUBFAMILY_NAME, PLATID_STR)
  failed = False
  for familyname in get_name_entries(ttFont, NAMEID_FONT_FAMILY_NAME):
    # we'll only match family/style name entries with the same platform ID:
    plat = familyname.platformID
    familyname_str = familyname.string.decode(familyname.getEncoding())
    for stylename_str in get_name_entry_strings(
        ttFont, NAMEID_FONT_SUBFAMILY_NAME, platformID=plat):
      if len(familyname_str + stylename_str) > 20:
        failed = True
        yield WARN, ("The combined length of family and style"
                     " exceeds 20 chars in the following '{}' entries:"
                     " FONT_FAMILY_NAME = '{}' / SUBFAMILY_NAME = '{}'"
                     "").format(PLATID_STR[plat], unidecode(familyname_str),
                                unidecode(stylename_str))
  if not failed:
    yield PASS, "All name entries are good."
