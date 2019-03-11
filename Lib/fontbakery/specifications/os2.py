from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN, INFO
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('vmetrics', ))
]

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


@check(
  id = 'com.google.fonts/check/034',
  conditions = ['is_ttf']
)
def com_google_fonts_check_034(ttFont):
  """Check if OS/2 xAvgCharWidth is correct."""
  current_value = ttFont['OS/2'].xAvgCharWidth
  ACCEPTABLE_ERROR = 10  # Width deviation tolerance in font units

  # Since version 3, the average is computed using _all_ glyphs in a font.
  if ttFont['OS/2'].version >= 3:
    calculation_rule = "the average of the widths of all glyphs in the font"
    if not ttFont['hmtx'].metrics:  # May contain just '.notdef', which is valid.
      yield FAIL, Message("missing-glyphs",
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
      yield FAIL, Message("missing-glyphs",
                          "Font is missing the required latin lowercase "
                          "letters and/or space.")
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
                  " These are similar values, which"
                  " may be a symptom of the slightly different"
                  " calculation of the xAvgCharWidth value in"
                  " font editors. There's further discussion on"
                  " this at https://github.com/googlefonts/fontbakery"
                  "/issues/1622")
  else:
    yield WARN, (f"OS/2 xAvgCharWidth is {current_value} but it should be"
                 f" {expected_value} which corresponds to {calculation_rule}.")


@check(
  id = 'com.adobe.fonts/check/fsselection_matches_macstyle',
  rationale = """The bold and italic bits in OS/2.fsSelection must match the
  bold and italic bits in head.macStyle per the OpenType spec."""
)
def com_adobe_fonts_check_fsselection_matches_macstyle(ttFont):
  """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""
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
  id = 'com.adobe.fonts/check/bold_italic_unique_for_nameid1',
  rationale = """Per the OpenType spec: name ID 1 'is used in combination with
  Font Subfamily name (name ID 2), and should be shared among at most four
  fonts that differ only in weight or style ... This four-way distinction
  should also be reflected in the OS/2.fsSelection field, using bits 0 and 5.' 
  """
)
def com_adobe_fonts_check_bold_italic_unique_for_nameid1(ttFonts):
  """Check that OS/2.fsSelection bold & italic settings are unique
  for each NameID1"""
  from collections import Counter
  from fontbakery.utils import get_name_entry_strings
  from fontbakery.constants import NameID, FsSelection

  failed = False
  family_name_and_bold_italic = list()
  for ttFont in ttFonts:
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
