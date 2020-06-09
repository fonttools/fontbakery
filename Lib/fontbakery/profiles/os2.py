from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN, INFO
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('vmetrics', )),
    ('.googlefonts_conditions', ('RIBBI_ttFonts', ))
]

@check(
  id = 'com.google.fonts/check/family/panose_proportion'
)
def com_google_fonts_check_family_panose_proportion(ttFonts):
  """Fonts have consistent PANOSE proportion?"""
  passed = True
  proportion = None
  missing = False
  for ttFont in ttFonts:
    if "OS/2" not in ttFont:
      missing = True
      passed = False
      continue
    if proportion is None:
      proportion = ttFont['OS/2'].panose.bProportion
    if proportion != ttFont['OS/2'].panose.bProportion:
      passed = False

  if missing:
    yield FAIL,\
          Message("lacks-OS/2",
                  "One or more fonts lack the required OS/2 table.")

  if not passed:
    yield FAIL,\
          Message("inconsistency",
                  "PANOSE proportion is not the same across this family."
                  " In order to fix this, please make sure that"
                  " the panose.bProportion value is the same"
                  " in the OS/2 table of all of this family font files.")
  else:
    yield PASS, "Fonts have consistent PANOSE proportion."


@check(
  id = 'com.google.fonts/check/family/panose_familytype'
)
def com_google_fonts_check_family_panose_familytype(ttFonts):
  """Fonts have consistent PANOSE family type?"""
  passed = True
  familytype = None
  missing = False

  for ttfont in ttFonts:
    if "OS/2" not in ttfont:
      passed = False
      missing = True
      continue
    if familytype is None:
      familytype = ttfont['OS/2'].panose.bFamilyType
    if familytype != ttfont['OS/2'].panose.bFamilyType:
      passed = False

  if missing:
    yield FAIL,\
          Message("lacks-OS/2",
                  "One or more fonts lack the required OS/2 table.")

  if not passed:
    yield FAIL,\
          Message("inconsistency",
                  "PANOSE family type is not the same across this family."
                  " In order to fix this, please make sure that"
                  " the panose.bFamilyType value is the same"
                  " in the OS/2 table of all of this family font files.")
  else:
    yield PASS, "Fonts have consistent PANOSE family type."


@check(
  id = 'com.google.fonts/check/xavgcharwidth',
  conditions = ['is_ttf']
)
def com_google_fonts_check_xavgcharwidth(ttFont):
  """Check if OS/2 xAvgCharWidth is correct."""

  if "OS/2" not in ttFont:
    yield FAIL,\
          Message("lacks-OS/2",
                  "Required OS/2 table is missing.")
    return

  current_value = ttFont['OS/2'].xAvgCharWidth
  ACCEPTABLE_ERROR = 10  # Width deviation tolerance in font units

  # Since version 3, the average is computed using _all_ glyphs in a font.
  if ttFont['OS/2'].version >= 3:
    calculation_rule = "the average of the widths of all glyphs in the font"
    if not ttFont['hmtx'].metrics:  # May contain just '.notdef', which is valid.
      yield FAIL,\
            Message("missing-glyphs",
                    "CRITICAL: Found no glyph width data in the hmtx table!")
      return

    width_sum = 0
    count = 0
    for glyph_id in ttFont['glyf'].glyphs:  # At least .notdef must be present.
      width = ttFont['hmtx'].metrics[glyph_id][0]
      # The OpenType spec doesn't exclude negative widths, but only positive
      # widths seems to be the assumption in the wild?
      if width > 0:
        count += 1
        width_sum += width

    expected_value = int(round(width_sum / count))
  else:  # Version 2 and below only consider lowercase latin glyphs and space.
    calculation_rule = ("the weighted average of the widths of the latin"
                        " lowercase glyphs in the font")
    weightFactors = {
        'a': 64,
        'b': 14,
        'c': 27,
        'd': 35,
        'e': 100,
        'f': 20,
        'g': 14,
        'h': 42,
        'i': 63,
        'j': 3,
        'k': 6,
        'l': 35,
        'm': 20,
        'n': 56,
        'o': 56,
        'p': 17,
        'q': 4,
        'r': 49,
        's': 56,
        't': 71,
        'u': 31,
        'v': 10,
        'w': 18,
        'x': 3,
        'y': 18,
        'z': 2,
        'space': 166
    }
    glyph_order = ttFont.getGlyphOrder()
    if not all(character in glyph_order for character in weightFactors):
      yield FAIL,\
            Message("missing-glyphs",
                    "Font is missing the required"
                    " latin lowercase letters and/or space.")
      return

    width_sum = 0
    for glyph_id in weightFactors:
      width = ttFont['hmtx'].metrics[glyph_id][0]
      width_sum += (width * weightFactors[glyph_id])

    expected_value = int(width_sum / 1000.0 + 0.5)  # round to closest int

  difference = abs(current_value - expected_value)

  # We accept matches and off-by-ones due to rounding as correct.
  if current_value == expected_value or difference == 1:
    yield PASS, "OS/2 xAvgCharWidth value is correct."
  elif difference < ACCEPTABLE_ERROR:
    yield INFO, (f"OS/2 xAvgCharWidth is {current_value} but it should be"
                 f" {expected_value} which corresponds to {calculation_rule}."
                 f" These are similar values, which"
                 f" may be a symptom of the slightly different"
                 f" calculation of the xAvgCharWidth value in"
                 f" font editors. There's further discussion on"
                 f" this at https://github.com/googlefonts/fontbakery"
                 f"/issues/1622")
  else:
    yield WARN, (f"OS/2 xAvgCharWidth is {current_value} but it should be"
                 f" {expected_value} which corresponds to {calculation_rule}.")


@check(
  id = 'com.adobe.fonts/check/fsselection_matches_macstyle',
  rationale = """
    The bold and italic bits in OS/2.fsSelection must match the bold and italic bits in head.macStyle per the OpenType spec.
  """
)
def com_adobe_fonts_check_fsselection_matches_macstyle(ttFont):
  """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""

  # Check both OS/2 and head are present.
  missing_tables = False

  required = ["OS/2", "head"]
  for key in required:
      if key not in ttFont:
          missing_tables = True
          yield FAIL,\
                  Message(f'lacks-{key}',
                          f"The '{key}' table is missing.")
  if missing_tables:
    return

  from fontbakery.constants import FsSelection, MacStyle
  failed = False
  head_bold = (ttFont['head'].macStyle & MacStyle.BOLD) != 0
  os2_bold = (ttFont['OS/2'].fsSelection & FsSelection.BOLD) != 0
  if head_bold != os2_bold:
    failed = True
    yield FAIL, "The OS/2.fsSelection and head.macStyle " \
                "bold settings do not match."
  head_italic = (ttFont['head'].macStyle & MacStyle.ITALIC) != 0
  os2_italic = (ttFont['OS/2'].fsSelection & FsSelection.ITALIC) != 0
  if head_italic != os2_italic:
    failed = True
    yield FAIL, "The OS/2.fsSelection and head.macStyle " \
                "italic settings do not match."
  if not failed:
    yield PASS, "The OS/2.fsSelection and head.macStyle " \
                "bold and italic settings match."


@check(
  id = 'com.adobe.fonts/check/family/bold_italic_unique_for_nameid1',
  conditions=['RIBBI_ttFonts'],
  rationale = """
    Per the OpenType spec: name ID 1 'is used in combination with Font Subfamily name (name ID 2), and should be shared among at most four fonts that differ only in weight or style...

    This four-way distinction should also be reflected in the OS/2.fsSelection field, using bits 0 and 5.
  """
)
def com_adobe_fonts_check_family_bold_italic_unique_for_nameid1(RIBBI_ttFonts):
  """Check that OS/2.fsSelection bold & italic settings are unique
  for each NameID1"""
  from collections import Counter
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NameID, FsSelection

  failed = False
  family_name_and_bold_italic = list()
  for ttFont in RIBBI_ttFonts:
    names_list = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    # names_list will likely contain multiple entries, e.g. multiple copies
    # of the same name in the same language for different platforms, but
    # also different names in different languages, we use set() below
    # to remove the duplicates and only store the unique family name(s)
    # used for a given font
    names_set = set(names_list)

    bold = (ttFont['OS/2'].fsSelection & FsSelection.BOLD) != 0
    italic = (ttFont['OS/2'].fsSelection & FsSelection.ITALIC) != 0
    bold_italic = 'Bold=%r, Italic=%r' % (bold, italic)

    for name in names_set:
      family_name_and_bold_italic.append((name, bold_italic,))

  counter = Counter(family_name_and_bold_italic)

  for (family_name, bold_italic), count in counter.items():
    if count > 1:
      failed = True
      yield FAIL, ("Family '{}' has {} fonts (should be no more than 1) with "
                   "the same OS/2.fsSelection bold & italic settings: {}"
                   ).format(family_name, count, bold_italic)
  if not failed:
    yield PASS, ("The OS/2.fsSelection bold & italic settings were unique "
                 "within each compatible family group.")


@check(
  id = 'com.google.fonts/check/code_pages',
  rationale = """
    At least some programs (such as Word and Sublime Text) under Windows 7 do not recognize fonts unless code page bits are properly set on the ulCodePageRange1 (and/or ulCodePageRange2) fields of the OS/2 table.

    More specifically, the fonts are selectable in the font menu, but whichever Windows API these applications use considers them unsuitable for any character set, so anything set in these fonts is rendered with a fallback font of Arial.

    This check currently does not identify which code pages should be set. Auto-detecting coverage is not trivial since the OpenType specification leaves the interpretation of whether a given code page is "functional" or not open to the font developer to decide.

    So here we simply detect as a FAIL when a given font has no code page declared at all.
  """
)
def com_google_fonts_check_code_pages(ttFont):
  """Check code page character ranges"""

  if "OS/2" not in ttFont:
    yield FAIL, Message("lacks-OS/2", "The required OS/2 table is missing.")
    return

  if not hasattr(ttFont['OS/2'], "ulCodePageRange1") or \
     not hasattr(ttFont['OS/2'], "ulCodePageRange2") or \
     (ttFont['OS/2'].ulCodePageRange1 == 0 and \
      ttFont['OS/2'].ulCodePageRange2 == 0):
    yield FAIL, ("No code pages defined in the OS/2 table"
                 " ulCodePageRange1 and CodePageRange2 fields.")
  else:
    yield PASS, "At least one code page is defined."
