from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, SKIP, WARN
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA

@check(id='com.google.fonts/check/069')
def com_google_fonts_check_069(ttFont):
  """Is there any unused data at the end of the glyf table?"""
  if 'CFF ' in ttFont:
    yield SKIP, "This check does not support CFF fonts."
  else:
    # -1 because https://www.microsoft.com/typography/otspec/loca.htm
    expected = len(ttFont['loca']) - 1
    actual = len(ttFont['glyf'])
    diff = actual - expected

    # allow up to 3 bytes of padding
    if diff > 3:
      yield FAIL, ("Glyf table has unreachable data at"
                   " the end of the table."
                   " Expected glyf table length {}"
                   " (from loca table), got length"
                   " {} (difference: {})").format(expected, actual, diff)
    elif diff < 0:
      yield FAIL, ("Loca table references data beyond"
                   " the end of the glyf table."
                   " Expected glyf table length {}"
                   " (from loca table), got length"
                   " {} (difference: {})").format(expected, actual, diff)
    else:
      yield PASS, "There is no unused data at the end of the glyf table."


@check(id='com.google.fonts/check/075')
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
