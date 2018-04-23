from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.message import Message
from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import


# This check was originally ported from
# Mekkablue Preflight Checks available at:
# https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Preflight%20Font.py
@check(
    id='com.google.fonts/check/075',
    conditions=['is_ttf'],
    request='https://github.com/googlefonts/fontbakery/issues/735')
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
