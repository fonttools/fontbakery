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
