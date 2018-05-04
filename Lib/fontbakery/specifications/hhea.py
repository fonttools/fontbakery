from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('seems_monospaced', 'monospace_stats', 'is_ttf'))
]

@check(
  id = 'com.google.fonts/check/041'
)
def com_google_fonts_check_041(ttFont):
  """Checking Vertical Metric Linegaps."""
  if ttFont["hhea"].lineGap != 0:
    yield WARN, Message("hhea", "hhea lineGap is not equal to 0.")
  elif ttFont["OS/2"].sTypoLineGap != 0:
    yield WARN, Message("OS/2", "OS/2 sTypoLineGap is not equal to 0.")
  else:
    yield PASS, "OS/2 sTypoLineGap and hhea lineGap are both 0."


@check(
  id = 'com.google.fonts/check/073'
)
def com_google_fonts_check_073(ttFont):
  """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""
  hhea_advance_width_max = ttFont['hhea'].advanceWidthMax
  hmtx_advance_width_max = None
  for g in ttFont['hmtx'].metrics.values():
    if hmtx_advance_width_max is None:
      hmtx_advance_width_max = max(0, g[0])
    else:
      hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

  if hmtx_advance_width_max != hhea_advance_width_max:
    yield FAIL, ("AdvanceWidthMax mismatch: expected {} (from hmtx);"
                 " got {} (from hhea)").format(hmtx_advance_width_max,
                                               hhea_advance_width_max)
  else:
    yield PASS, ("MaxAdvanceWidth is consistent"
                 " with values in the Hmtx and Hhea tables.")


@check(
  id = 'com.google.fonts/check/079',
  conditions = ['seems_monospaced']
)
def com_google_fonts_check_079(ttFont):
  """Monospace font has hhea.advanceWidthMax equal to each glyph's
  advanceWidth?"""

  # hhea:advanceWidthMax is treated as source of truth here.
  max_advw = ttFont['hhea'].advanceWidthMax
  outliers = []
  zero_or_double_width_outliers = []
  glyphSet = ttFont.getGlyphSet().keys() # TODO: remove .keys() when fonttools is updated to 3.27
  glyphs = [
      g for g in glyphSet if g not in ['.notdef', '.null', 'NULL']
  ]
  for glyph_id in glyphs:
    width = ttFont['hmtx'].metrics[glyph_id][0]
    if width != max_advw:
      outliers.append(glyph_id)
    if width == 0 or width == 2 * max_advw:
      zero_or_double_width_outliers.append(glyph_id)

  if outliers:
    outliers_percentage = float(len(outliers)) / len(glyphSet)
    yield WARN, Message(
        "should-be-monospaced", "This seems to be a monospaced font,"
        " so advanceWidth value should be the same"
        " across all glyphs, but {}% of them"
        " have a different value: {}"
        "".format(round(100 * outliers_percentage, 2), ", ".join(outliers)))
    if zero_or_double_width_outliers:
      yield WARN, Message("variable-monospaced",
                          "Double-width and/or zero-width glyphs"
                          " were detected. These glyphs should be set"
                          " to the same width as all others"
                          " and then add GPOS single pos lookups"
                          " that zeros/doubles the widths as needed: {}".format(
                              ", ".join(zero_or_double_width_outliers)))
  else:
    yield PASS, ("hhea.advanceWidthMax is equal"
                 " to all glyphs' advanceWidth in this monospaced font.")
