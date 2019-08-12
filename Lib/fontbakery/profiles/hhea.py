from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, SKIP, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('glyph_metrics_stats', 'is_ttf'))
]

@check(
  id = 'com.google.fonts/check/linegaps'
)
def com_google_fonts_check_linegaps(ttFont):
  """Checking Vertical Metric Linegaps."""
  if ttFont["hhea"].lineGap != 0:
    yield WARN,\
          Message("hhea",
                  "hhea lineGap is not equal to 0.")
  elif ttFont["OS/2"].sTypoLineGap != 0:
    yield WARN,\
          Message("OS/2",
                  "OS/2 sTypoLineGap is not equal to 0.")
  else:
    yield PASS, "OS/2 sTypoLineGap and hhea lineGap are both 0."


@check(
  id = 'com.google.fonts/check/maxadvancewidth'
)
def com_google_fonts_check_maxadvancewidth(ttFont):
  """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""
  hhea_advance_width_max = ttFont['hhea'].advanceWidthMax
  hmtx_advance_width_max = None
  for g in ttFont['hmtx'].metrics.values():
    if hmtx_advance_width_max is None:
      hmtx_advance_width_max = max(0, g[0])
    else:
      hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

  if hmtx_advance_width_max != hhea_advance_width_max:
    yield FAIL,\
          Message("mismatch",
                  f"AdvanceWidthMax mismatch:"
                  f" expected {hmtx_advance_width_max} (from hmtx);"
                  f" got {hhea_advance_width_max} (from hhea)")
  else:
    yield PASS, ("MaxAdvanceWidth is consistent"
                 " with values in the Hmtx and Hhea tables.")


@check(
  id = 'com.google.fonts/check/monospace_max_advancewidth',
  conditions = ['glyph_metrics_stats']
)
def com_google_fonts_check_monospace_max_advancewidth(ttFont, glyph_metrics_stats):
  """Monospace font has hhea.advanceWidthMax equal to each glyph's
  advanceWidth?"""
  from fontbakery.utils import pretty_print_list

  seems_monospaced = glyph_metrics_stats["seems_monospaced"]
  if not seems_monospaced:
    yield SKIP, ("Font is not monospaced.")
    return

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
    yield WARN,\
          Message("should-be-monospaced",
                  "This seems to be a monospaced font,"
                  " so advanceWidth value should be the same"
                  " across all glyphs, but {}% of them"
                  " have a different value: {}"
                  "".format(round(100 * outliers_percentage, 2),
                            pretty_print_list(outliers)))
    if zero_or_double_width_outliers:
      yield WARN,\
            Message("variable-monospaced",
                    "Double-width and/or zero-width glyphs"
                    " were detected. These glyphs should be set"
                    " to the same width as all others"
                    " and then add GPOS single pos lookups"
                    " that zeros/doubles the widths as needed:"
                    " {}".format(pretty_print_list(
                                 zero_or_double_width_outliers)))
  else:
    yield PASS, ("hhea.advanceWidthMax is equal"
                 " to all glyphs' advanceWidth in this monospaced font.")
