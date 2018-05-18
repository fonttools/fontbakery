from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, WARN
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

@condition
def expected_os2_weight():
  """Return a tuple of weight name and expected OS/2 usWeightClass or None.

  use: @condition(force=True) in your spec to override this condition.
  """
  return None

@condition
def os2_weight_warn():
  """ This can be used to specify special cases in which we want to
      just warn the user about a mismatching os2 weight value
      instead of failing the check.

  use: @condition(force=True) in your spec to override this condition.
  """
  return None


@check(
  id = 'com.google.fonts/check/020',
  conditions = ['expected_os2_weight']
)
def com_google_fonts_check_020(ttFont,
                               expected_os2_weight,
                               os2_weight_warn):
  """Checking OS/2 usWeightClass."""
  weight_name, expected_value = expected_os2_weight
  value = ttFont['OS/2'].usWeightClass
  if value != expected_value:
    if os2_weight_warn and \
       weight_name == os2_weight_warn["style"] and \
       value == os2_weight_warn["value"]:
      yield WARN, os2_weight_warn["message"]
    else:
      yield FAIL, ("OS/2 usWeightClass expected value for"
                   " '{}' is {} but this font has"
                   " {}.").format(weight_name, expected_value, value)
  else:
    yield PASS, "OS/2 usWeightClass value looks good!"


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
    yield WARN, ("OS/2 xAvgCharWidth is {} but should be"
                  " {} which corresponds to the weighted"
                  " average of the widths of the latin"
                  " lowercase glyphs in the font."
                  " These are similar values, which"
                  " may be a symptom of the slightly different"
                  " calculation of the xAvgCharWidth value in"
                  " font editors. There's further discussion on"
                  " this at https://github.com/googlefonts/fontbakery"
                  "/issues/1622").format(current_value, expected_value)
  else:
    yield FAIL, ("OS/2 xAvgCharWidth is {} but it should be "
                  "{} which corresponds to the weighted "
                  "average of the widths of the latin "
                  "lowercase glyphs in "
                  "the font").format(current_value, expected_value)


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
  id = 'com.google.fonts/check/042'
)
def com_google_fonts_check_042(ttFont):
  """Checking OS/2 Metrics match hhea Metrics.

  OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, Linux and Windows.

  Mac OS X uses the hhea values
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
    yield PASS, ("OS/2.sTypoAscender/Descender" " match hhea.ascent/descent.")
