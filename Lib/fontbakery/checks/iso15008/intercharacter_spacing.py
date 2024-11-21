from fontTools.pens.boundsPen import BoundsPen

from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.iso15008.utils import (
    xheight_intersections,
    stem_width,
    pair_kerning,
    DISCLAIMER,
)


@check(
    id="iso15008/intercharacter_spacing",
    rationale="""
        According to ISO 15008, fonts used for in-car displays should not
        be too narrow or too wide.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the spacing falls within the following values:

        * space between vertical strokes (e.g. "ll") should be 150%-240%
          of the stem width.

        * space between diagonals and verticals (e.g. "vl") should be
          at least 85% of the stem width.

        * diagonal characters should not touch (e.g. "vv").
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3252",
    ],
)
def check_iso15008_intercharacter_spacing(font, ttFont):
    """Check if spacing between characters is adequate for display use"""
    width = stem_width(ttFont)

    # Because an l can have a curly tail, we don't want the *glyph* sidebearings;
    # we want the sidebearings measured using a line at Y=x-height.
    l_intersections = xheight_intersections(ttFont, "l")
    if width is None or len(l_intersections) < 2:
        yield FAIL, Message("no-stem-width", "Could not determine stem width")
        return

    l_lsb = l_intersections[0].point.x
    l_advance = ttFont["hmtx"]["l"][0]
    l_rsb = l_advance - l_intersections[-1].point.x

    l_l = l_rsb + pair_kerning(font, "l", "l") + l_lsb
    if l_l is None:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'l' glyph in the font, so the spacing could not be tested",
        )
        return
    if not 1.5 <= (l_l / width) <= 2.4:
        yield FAIL, Message(
            "bad-vertical-vertical-spacing",
            f"The space between vertical strokes ({l_l})"
            f" does not conform to the expected"
            f" range of {width * 1.5}-{width * 2.4}",
        )

    # For v, however, a simple LSB/RSB is adequate.
    glyphset = ttFont.getGlyphSet()
    pen = BoundsPen(glyphset)
    glyphset["v"].draw(pen)
    (xMin, yMin, xMax, yMax) = pen.bounds
    v_advance = ttFont["hmtx"]["v"][0]

    v_lsb = xMin
    v_rsb = v_advance - (v_lsb + xMax - xMin)

    l_v = l_rsb + pair_kerning(font, "l", "v") + v_lsb

    if l_v is None:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'v' glyph in the font, so the spacing could not be tested",
        )
        return

    if (l_v / width) <= 0.85:
        yield FAIL, Message(
            "bad-vertical-diagonal-spacing",
            f"The space between vertical and diagonal strokes ({l_v})"
            f" was less than the expected"
            f" value of {width * 0.85}",
        )

    if v_rsb + pair_kerning(font, "v", "v") + v_lsb <= 0:
        yield FAIL, Message(
            "bad-diagonal-diagonal-spacing", "Diagonal strokes (vv) were touching"
        )
