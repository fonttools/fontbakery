from fontbakery.message import Message
from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

import fontTools.ttLib

@check(
  id = 'com.google.fonts/check/069',
  conditions = ['is_ttf']
)
def com_google_fonts_check_069(ttFont):
  """Is there any unused data at the end of the glyf table?"""
  try:
    expected_glyphs = len(ttFont.getGlyphOrder())
    actual_glyphs = len(ttFont['glyf'].glyphs)
    diff = actual_glyphs - expected_glyphs

    if diff < 0:
      yield FAIL, Message("unreachable-data",
                          ("Glyf table has unreachable data at the end of "
                           " the table. Expected glyf table length {}"
                           " (from loca table), got length"
                           " {} (difference: {})").format(
                               expected_glyphs, actual_glyphs, diff))
    elif not diff:  # negative diff -> exception below
      yield PASS, "There is no unused data at the end of the glyf table."
    else:
      raise Exception("Bug: fontTools did not raise an expected exception.")
  except fontTools.ttLib.TTLibError as error:
    if "not enough 'glyf' table data" in format(error):
      yield FAIL, Message("missing-data",
                          ("Loca table references data beyond"
                           " the end of the glyf table."
                           " Expected glyf table length {}"
                           " (from loca table).").format(expected_glyphs))
    else:
      raise Exception("Bug: Unexpected fontTools exception.")


# This check was originally ported from
# Mekkablue Preflight Checks available at:
# https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Preflight%20Font.py
@check(
  id = 'com.google.fonts/check/075',
  conditions = ['is_ttf'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  })
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
