from fontTools.pens.boundsPen import BoundsPen

from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.iso15008.utils import (
    xheight_intersections,
    pair_kerning,
    DISCLAIMER,
)


@check(
    id="iso15008/interword_spacing",
    rationale="""
        According to ISO 15008, fonts used for in-car displays
        should not be too narrow or too wide.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the space character should have advance width
        between 250% and 300% of the space between the letters l and m.
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3253",
    ],
)
def check_iso15008_interword_spacing(font, ttFont):
    """Check if spacing between words is adequate for display use"""

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    from copy import deepcopy

    ttFont_copy = deepcopy(ttFont)

    l_intersections = xheight_intersections(ttFont_copy, "l")
    if len(l_intersections) < 2:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'l' glyph in the font, so the spacing could not be tested",
        )
        return

    l_advance = ttFont_copy["hmtx"]["l"][0]
    l_rsb = l_advance - l_intersections[-1].point.x

    glyphset = ttFont_copy.getGlyphSet()
    pen = BoundsPen(glyphset)
    glyphset["m"].draw(pen)
    (xMin, yMin, xMax, yMax) = pen.bounds
    m_advance = ttFont_copy["hmtx"]["m"][0]
    m_lsb = xMin
    m_rsb = m_advance - (m_lsb + xMax - xMin)

    n_lsb = ttFont_copy["hmtx"]["n"][1]

    l_m = l_rsb + pair_kerning(font, "l", "m") + m_lsb
    space_width = ttFont_copy["hmtx"]["space"][0]
    # Add spacing caused by normal sidebearings
    space_width += m_rsb + n_lsb

    if not 2.50 <= space_width / l_m <= 3.0:
        yield FAIL, Message(
            "bad-interword-spacing",
            f"The interword space ({space_width}) was"
            f" outside the recommended range ({l_m*2.5}-{l_m*3.0})",
        )
