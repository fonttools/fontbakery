from fontbakery.message import Message
from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

import fontTools.ttLib

@check(
  id = 'com.google.fonts/check/glyf_unused_data',
  conditions = ['is_ttf']
)
def com_google_fonts_check_glyf_unused_data(ttFont):
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
  id = 'com.google.fonts/check/points_out_of_bounds',
  conditions = ['is_ttf'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  })
def com_google_fonts_check_points_out_of_bounds(ttFont):
  """Check for points out of bounds."""
  from fontbakery.utils import pretty_print_list
  failed = False
  out_of_bounds = []
  for glyphName in ttFont['glyf'].keys():
    glyph = ttFont['glyf'][glyphName]
    coords = glyph.getCoordinates(ttFont['glyf'])[0]
    for x, y in coords:
      if round(x) < glyph.xMin or round(x) > glyph.xMax or \
         round(y) < glyph.yMin or round(y) > glyph.yMax or \
         abs(x) > 32766 or abs(y) > 32766:
        failed = True
        out_of_bounds.append((glyphName, x, y))

  if failed:
    yield WARN, ("The following glyphs have coordinates which are"
                 " out of bounds:\n\t* {}\nThis happens a lot when points"
                 " are not extremes, which is usually bad. However,"
                 " fixing this alert by adding points on extremes may"
                 " do more harm than good, especially with italics,"
                 " calligraphic-script, handwriting, rounded and"
                 " other fonts. So it is common to"
                 " ignore this message."
		 "".format(pretty_print_list(out_of_bounds,
                                             shorten=10,
                                             sep="\n\t* ")))
  else:
    yield PASS, "All glyph paths have coordinates within bounds!"
