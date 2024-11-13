from fontbakery.prelude import check, Message, WARN, FAIL


@check(
    id="opentype/caret_slope",
    rationale="""
        Checks whether hhea.caretSlopeRise and hhea.caretSlopeRun
        match with post.italicAngle.

        For Upright fonts, you can set hhea.caretSlopeRise to 1
        and hhea.caretSlopeRun to 0.

        For Italic fonts, you can set hhea.caretSlopeRise to head.unitsPerEm
        and calculate hhea.caretSlopeRun like this:
        round(math.tan(
          math.radians(-1 * font["post"].italicAngle)) * font["head"].unitsPerEm)

        This check allows for a 0.1° rounding difference between the Italic angle
        as calculated by the caret slope and post.italicAngle
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3670",
)
def check_caret_slope(ttFont):
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

    if abs(postItalicAngle - hheaItalicAngle) > 0.1:
        yield WARN, Message(
            "caretslope-mismatch",
            "hhea.caretSlopeRise and hhea.caretSlopeRun"
            " do not match with post.italicAngle.\n"
            f"Got: caretSlopeRise {ttFont['hhea'].caretSlopeRise}"
            f" and caretSlopeRun {ttFont['hhea'].caretSlopeRun}\n"
            f"Expected: caretSlopeRise {expectedCaretSlopeRise}"
            f" and caretSlopeRun {expectedCaretSlopeRun}",
        )
