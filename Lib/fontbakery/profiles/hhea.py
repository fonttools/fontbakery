from fontbakery.callable import check
from fontbakery.status import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('glyph_metrics_stats', 'is_ttf'))
]

def _get_missing_tables(req_tables_set, ttFont):
    """Returns a sorted list of table tags not supported by the font."""
    return sorted(req_tables_set - set(ttFont.keys()))


@check(
    id = 'com.google.fonts/check/linegaps',
    proposal = 'legacy:check/041'
)
def com_google_fonts_check_linegaps(ttFont):
    """Checking Vertical Metric Linegaps."""
    required_tables = {"hhea", "OS/2"}
    missing_tables = _get_missing_tables(required_tables, ttFont)
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

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
    id = 'com.google.fonts/check/maxadvancewidth',
    proposal = 'legacy:check/073'
)
def com_google_fonts_check_maxadvancewidth(ttFont):
    """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""
    required_tables = {"hhea", "hmtx"}
    missing_tables = _get_missing_tables(required_tables, ttFont)
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

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
