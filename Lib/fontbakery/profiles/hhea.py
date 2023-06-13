from fontbakery.callable import check
from fontbakery.status import FAIL, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import (  # NOQA pylint: disable=unused-import
    profile_factory,
)

profile_imports = [(".shared_conditions", ("glyph_metrics_stats", "is_ttf"))]


@check(id="com.google.fonts/check/maxadvancewidth", proposal="legacy:check/073")
def com_google_fonts_check_maxadvancewidth(ttFont):
    """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""

    required_tables = {"hhea", "hmtx"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    hhea_advance_width_max = ttFont["hhea"].advanceWidthMax
    hmtx_advance_width_max = None
    for g in ttFont["hmtx"].metrics.values():
        if hmtx_advance_width_max is None:
            hmtx_advance_width_max = max(0, g[0])
        else:
            hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

    if hmtx_advance_width_max != hhea_advance_width_max:
        yield FAIL, Message(
            "mismatch",
            f"AdvanceWidthMax mismatch:"
            f" expected {hmtx_advance_width_max} (from hmtx);"
            f" got {hhea_advance_width_max} (from hhea)",
        )
    else:
        yield PASS, (
            "MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables."
        )


@check(
    id="com.google.fonts/check/caret_slope",
    rationale="""
        Checks whether hhea.caretSlopeRise and hhea.caretSlopeRun
        match with post.italicAngle.

        For Upright fonts, you can set hhea.caretSlopeRise to 1
        and hhea.caretSlopeRun to 0.

        For Italic fonts, you can set hhea.caretSlopeRise to head.unitsPerEm
        and calculate hhea.caretSlopeRun like this:
        round(math.tan(math.radians(-1 * font["post"].italicAngle)) * font["head"].unitsPerEm)

        This check allows for a 0.1° rounding difference between the Italic angle
        as calculated by the caret slope and post.italicAngle
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3670",
)
def com_google_fonts_check_caret_slope(ttFont):
    """Check hhea.caretSlopeRise and hhea.caretSlopeRun"""

    import math

    postItalicAngle = ttFont["post"].italicAngle
    upm = ttFont["head"].unitsPerEm
    run = ttFont["hhea"].caretSlopeRun
    rise = ttFont["hhea"].caretSlopeRise
    if rise == 0:
        yield FAIL, Message(
            "zero-rise",
            "caretSlopeRise must not be zero. Set it to 1 for upright fonts.",
        )
        return
    hheaItalicAngle = math.degrees(math.atan(-run / rise))
    expectedCaretSlopeRun = round(math.tan(math.radians(-postItalicAngle)) * upm)
    if expectedCaretSlopeRun == 0:
        expectedCaretSlopeRise = 1
    else:
        expectedCaretSlopeRise = upm

    print(postItalicAngle, hheaItalicAngle)
    if abs(postItalicAngle - hheaItalicAngle) > 0.1:
        yield FAIL, Message(
            "caretslope-mismatch",
            f"hhea.caretSlopeRise and hhea.caretSlopeRun"
            f" do not match with post.italicAngle.\n"
            f"Got: caretSlopeRise {ttFont['hhea'].caretSlopeRise}"
            f" and caretSlopeRun {ttFont['hhea'].caretSlopeRun}\n"
            f"Expected: caretSlopeRise {expectedCaretSlopeRise}"
            f" and caretSlopeRun {expectedCaretSlopeRun}",
        )
    else:
        yield PASS, (
            "hhea.caretSlopeRise and hhea.caretSlopeRun match with post.italicAngle."
        )
