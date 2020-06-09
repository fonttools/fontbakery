from fontbakery.callable import check
from fontbakery.checkrunner import ERROR, FAIL, PASS, WARN, INFO
from fontbakery.message import Message
from fontbakery.constants import (PriorityLevel,
                                  NameID,
                                  PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID)
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('glyph_metrics_stats', ))
]


@check(
  id = 'com.adobe.fonts/check/name/empty_records',
  rationale = """
    Check the name table for empty records, as this can cause problems in Adobe apps.
  """
)
def com_adobe_fonts_check_name_empty_records(ttFont):
    """Check name table for empty records."""
    failed = False
    for name_record in ttFont['name'].names:
        name_string = name_record.toUnicode().strip()
        if len(name_string) == 0:
            failed = True
            name_key = tuple([name_record.platformID, name_record.platEncID,
                             name_record.langID, name_record.nameID])
            yield FAIL,\
                  Message("empty-record",
                          f'"name" table record with key={name_key} is'
                          f' empty and should be removed.')
    if not failed:
        yield PASS, ("No empty name table records found.")


@check(
  id = 'com.google.fonts/check/name/no_copyright_on_description',
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_name_no_copyright_on_description(ttFont):
  """Description strings in the name table must not contain copyright info."""
  failed = False
  for name in ttFont['name'].names:
    if 'opyright' in name.string.decode(name.getEncoding())\
       and name.nameID == NameID.DESCRIPTION:
      failed = True

  if failed:
    yield FAIL,\
          Message("copyright-on-description",
                  f"Some namerecords with"
                  f" ID={NameID.DESCRIPTION} (NameID.DESCRIPTION)"
                  f" containing copyright info should be removed"
                  f" (perhaps these were added by a longstanding"
                  f" FontLab Studio 5.x bug that copied"
                  f" copyright notices to them.)")
  else:
    yield PASS, ("Description strings in the name table"
                 " do not contain any copyright string.")


@check(
  id = 'com.google.fonts/check/monospace',
  conditions = ['glyph_metrics_stats',
                'is_ttf'],
  rationale = """
    There are various metadata in the OpenType spec to specify if a font is monospaced or not. If the font is not truly monospaced, then no monospaced metadata should be set (as sometimes they mistakenly are...)

    Requirements for monospace fonts:

    * post.isFixedPitch - "Set to 0 if the font is proportionally spaced, non-zero if the font is not proportionally spaced (monospaced)"
      www.microsoft.com/typography/otspec/post.htm

    * hhea.advanceWidthMax must be correct, meaning no glyph's width value is greater.
      www.microsoft.com/typography/otspec/hhea.htm

    * OS/2.panose.bProportion must be set to 9 (monospace). Spec says: "The PANOSE definition contains ten digits each of which currently describes up to sixteen variations. Windows uses bFamilyType, bSerifStyle and bProportion in the font mapper to determine family type. It also uses bProportion to determine if the font is monospaced."
      www.microsoft.com/typography/otspec/os2.htm#pan
      monotypecom-test.monotype.de/services/pan2

    * OS/2.xAvgCharWidth must be set accurately.
      "OS/2.xAvgCharWidth is used when rendering monospaced fonts, at least by Windows GDI"
      http://typedrawers.com/discussion/comment/15397/#Comment_15397

    Also we should report an error for glyphs not of average width.

    Please also note:
    Thomas Phinney told us that a few years ago (as of December 2019), if you gave a font a monospace flag in Panose, Microsoft Word would ignore the actual advance widths and treat it as monospaced. Source: https://typedrawers.com/discussion/comment/45140/#Comment_45140
  """
)
def com_google_fonts_check_monospace(ttFont, glyph_metrics_stats):
  """Checking correctness of monospaced metadata."""
  from fontbakery.constants import (IsFixedWidth,
                                    PANOSE_Proportion)
  failed = False
  # Note: These values are read from the dict here only to
  # reduce the max line length in the check implementation below:
  seems_monospaced = glyph_metrics_stats["seems_monospaced"]
  most_common_width = glyph_metrics_stats["most_common_width"]
  width_max = glyph_metrics_stats['width_max']

  # Check for missing tables before indexing them
  missing_tables = False
  required = ["glyf", "hhea", "hmtx", "OS/2", "post"]
  for key in required:
    if key not in ttFont:
      missing_tables = True
      yield FAIL,\
            Message(f'lacks-{key}',
                    f"Font file lacks a '{key}' table.")

  if missing_tables:
    return

  if ttFont['hhea'].advanceWidthMax != width_max:
    failed = True
    yield FAIL,\
          Message("bad-advanceWidthMax",
                  f"Value of hhea.advanceWidthMax"
                  f" should be set to {width_max}"
                  f" but got {ttFont['hhea'].advanceWidthMax} instead.")
  if seems_monospaced:
    if ttFont['post'].isFixedPitch == IsFixedWidth.NOT_MONOSPACED:
      failed = True
      yield FAIL,\
            Message("mono-bad-post-isFixedPitch",
                    f"On monospaced fonts, the value of post.isFixedPitch"
                    f" must be set to a non-zero value"
                    f" (meaning 'fixed width monospaced'),"
                    f" but got {ttFont['post'].isFixedPitch} instead.")

    if ttFont['OS/2'].panose.bProportion != PANOSE_Proportion.MONOSPACED:
      failed = True
      yield FAIL,\
            Message("mono-bad-panose-proportion",
                    f"On monospaced fonts, the value of"
                    f" OS/2.panose.bProportion"
                    f" must be set to {PANOSE_Proportion.MONOSPACED}"
                    f" (proportion: monospaced),"
                    f" but got {ttFont['OS/2'].panose.bProportion} instead.")

    num_glyphs = len(ttFont['glyf'].glyphs)
    unusually_spaced_glyphs = [
        g for g in ttFont['glyf'].glyphs
        if g not in ['.notdef', '.null', 'NULL'] and
        ttFont['hmtx'].metrics[g][0] != most_common_width
    ]
    outliers_ratio = float(len(unusually_spaced_glyphs)) / num_glyphs
    if outliers_ratio > 0:
      failed = True
      yield WARN,\
            Message("mono-outliers",
                    f"Font is monospaced"
                    f" but {len(unusually_spaced_glyphs)} glyphs"
                    f" ({100.0 * outliers_ratio}%)"
                    f" have a different width."
                    f" You should check the widths of:"
                    f" {unusually_spaced_glyphs}")
    if not failed:
      yield PASS,\
            Message("mono-good",
                    "Font is monospaced and all related metadata look good.")
  else:
    # it is a non-monospaced font, so lets make sure
    # that all monospace-related metadata is properly unset.

    if ttFont['post'].isFixedPitch != IsFixedWidth.NOT_MONOSPACED:
      failed = True
      yield FAIL,\
            Message("bad-post-isFixedPitch",
                    f"On non-monospaced fonts,"
                    f" the post.isFixedPitch value must be set to"
                    f" {IsFixedWidth.NOT_MONOSPACED} (not monospaced),"
                    f" but got {ttFont['post'].isFixedPitch} instead.")

    if ttFont['OS/2'].panose.bProportion == PANOSE_Proportion.MONOSPACED:
      failed = True
      yield FAIL,\
            Message("bad-panose-proportion",
                    "On non-monospaced fonts,"
                    " the OS/2.panose.bProportion value can be set to"
                    " any value except 9 (proportion: monospaced)"
                    " which is the bad value we got in this font.")
    if not failed:
      yield PASS,\
            Message("good",
                    "Font is not monospaced and"
                    " all related metadata look good.")


@check(
  id = 'com.google.fonts/check/name/match_familyname_fullfont'
)
def com_google_fonts_check_name_match_familyname_fullfont(ttFont):
  """Does full font name begin with the font family name?"""
  from fontbakery.utils import get_name_entry_strings
  familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
  fullfontname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)

  if len(familyname) == 0:
    yield FAIL,\
          Message("no-font-family-name",
                  "Font lacks a NameID.FONT_FAMILY_NAME"
                  " entry in the 'name' table.")
  elif len(fullfontname) == 0:
    yield FAIL,\
          Message("no-full-font-name",
                  "Font lacks a NameID.FULL_FONT_NAME"
                  " entry in the 'name' table.")
  else:
    # we probably should check all found values are equivalent.
    # and, in that case, then performing the rest of the check
    # with only the first occurences of the name entries
    # will suffice:
    fullfontname = fullfontname[0]
    familyname = familyname[0]

    if not fullfontname.startswith(familyname):
      yield FAIL,\
            Message("does-not",
                    f"On the 'name' table, the full font name"
                    f" (NameID {NameID.FULL_FONT_NAME}"
                    f" - FULL_FONT_NAME: '{familyname}')"
                    f" does not begin with font family name"
                    f" (NameID {NameID.FONT_FAMILY_NAME}"
                    f" - FONT_FAMILY_NAME: '{fullfontname}')")
    else:
      yield PASS, "Full font name begins with the font family name."


@check(
  id = 'com.google.fonts/check/family_naming_recommendations'
)
def com_google_fonts_check_family_naming_recommendations(ttFont):
  """Font follows the family naming recommendations?"""
  # See http://forum.fontlab.com/index.php?topic=313.0
  import re
  from fontbakery.utils import get_name_entry_strings
  bad_entries = []

  # <Postscript name> may contain only a-zA-Z0-9
  # and one hyphen
  bad_psname = re.compile("[^A-Za-z0-9-]")
  for string in get_name_entry_strings(ttFont,
                                       NameID.POSTSCRIPT_NAME):
    if bad_psname.search(string):
      bad_entries.append({
          'field':
          'PostScript Name',
          'value':
          string,
          'rec': ('May contain only a-zA-Z0-9'
                  ' characters and an hyphen.')
      })
    if string.count('-') > 1:
      bad_entries.append({
          'field': 'Postscript Name',
          'value': string,
          'rec': ('May contain not more'
                  ' than a single hyphen')
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.FULL_FONT_NAME):
    if len(string) >= 64:
      bad_entries.append({
          'field': 'Full Font Name',
          'value': string,
          'rec': 'exceeds max length (63)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.POSTSCRIPT_NAME):
    if len(string) >= 64:
      bad_entries.append({
          'field': 'PostScript Name',
          'value': string,
          'rec': 'exceeds max length (63)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.FONT_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'Family Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.FONT_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'Style Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.TYPOGRAPHIC_FAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'OT Family Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  for string in get_name_entry_strings(ttFont,
                                       NameID.TYPOGRAPHIC_SUBFAMILY_NAME):
    if len(string) >= 32:
      bad_entries.append({
          'field': 'OT Style Name',
          'value': string,
          'rec': 'exceeds max length (31)'
      })

  if len(bad_entries) > 0:
    table = "| Field | Value | Recommendation |\n"
    table += "|:----- |:----- |:-------------- |\n"
    for bad in bad_entries:
      table += "| {} | {} | {} |\n".format(bad["field"],
                                           bad["value"],
                                           bad["rec"])
    yield INFO,\
          Message("bad-entries",
                  f"Font does not follow "
                  f"some family naming recommendations:\n"
                  f"\n"
                  f"{table}")
  else:
    yield PASS, "Font follows the family naming recommendations."


@check(
  id = 'com.adobe.fonts/check/name/postscript_vs_cff',
  conditions = ['is_cff'],
  rationale = """
    The PostScript name entries in the font's 'name' table should match the FontName string in the 'CFF ' table.

    The 'CFF ' table has a lot of information that is duplicated in other tables. This information should be consistent across tables, because there's no guarantee which table an app will get the data from.
  """,
)
def com_adobe_fonts_check_name_postscript_vs_cff(ttFont):
  """CFF table FontName must match name table ID 6 (PostScript name)."""
  cff_names = ttFont['CFF '].cff.fontNames
  if len(cff_names) != 1:
    yield ERROR, ("Unexpected number of font names in CFF table.")
    return

  passed = True
  cff_name = cff_names[0]
  for entry in ttFont['name'].names:
    if entry.nameID == NameID.POSTSCRIPT_NAME:
      postscript_name = entry.toUnicode()
      if postscript_name != cff_name:
        passed = False
        yield FAIL,\
              Message("mismatch",
                      f"Name table PostScript name '{postscript_name}' "
                      f"does not match CFF table FontName '{cff_name}'.")

  if passed:
    yield PASS, ("Name table PostScript name matches CFF table FontName.")


@check(
  id = 'com.adobe.fonts/check/name/postscript_name_consistency',
  conditions = ['not is_cff'],  # e.g. TTF or CFF2
  rationale = """
    The PostScript name entries in the font's 'name' table should be consistent across platforms.

    This is the TTF/CFF2 equivalent of the CFF 'postscript_name_cff_vs_name' check.
  """,
)
def com_adobe_fonts_check_name_postscript_name_consistency(ttFont):
  """Name table ID 6 (PostScript name) must be consistent across platforms."""
  postscript_names = set()
  for entry in ttFont['name'].names:
    if entry.nameID == NameID.POSTSCRIPT_NAME:
      postscript_name = entry.toUnicode()
      postscript_names.add(postscript_name)

  if len(postscript_names) > 1:
    yield FAIL,\
          Message("inconsistency",
                  f'Entries in the "name" table for ID 6'
                  f' (PostScript name) are not consistent.'
                  f' Names found: {sorted(postscript_names)}.')
  else:
    yield PASS, ('Entries in the "name" table for ID 6 '
                 '(PostScript name) are consistent.')


@check(
  id = 'com.adobe.fonts/check/family/max_4_fonts_per_family_name',
  rationale = """
    Per the OpenType spec:
    'The Font Family name ... should be shared among at most four fonts that differ only in weight or style ...'
  """,
)
def com_adobe_fonts_check_family_max_4_fonts_per_family_name(ttFonts):
  """Verify that each group of fonts with the same nameID 1
  has maximum of 4 fonts"""
  from collections import Counter
  from fontbakery.utils import get_name_entry_strings

  family_names = list()
  for ttFont in ttFonts:
    names_list = get_name_entry_strings(ttFont,
                                        NameID.FONT_FAMILY_NAME,
                                        PlatformID.WINDOWS,
                                        WindowsEncodingID.UNICODE_BMP,
                                        WindowsLanguageID.ENGLISH_USA)
    # names_list may contain multiple entries.
    # We use set() below to remove the duplicates and only store
    # the unique family name(s) used for a given font
    names_set = set(names_list)
    family_names.extend(names_set)

  passed = True
  counter = Counter(family_names)
  for family_name, count in counter.items():
    if count > 4:
      passed = False
      yield FAIL,\
            Message("too-many",
                    f"Family '{family_name}' has {count} fonts"
                    f" (should be 4 or fewer).")
  if passed:
    yield PASS, ("There were no more than 4 fonts per family name.")
