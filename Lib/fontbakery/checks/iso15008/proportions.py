from fontTools.pens.boundsPen import BoundsPen

from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.iso15008.utils import DISCLAIMER


@check(
    id="iso15008/proportions",
    rationale="""
        According to ISO 15008, fonts used for in-car displays should not be
        too narrow or too wide.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the ratio of H width to H height
        is between 0.65 and 0.80.
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3250",
    ],
)
def check_iso15008_proportions(ttFont):
    """Check if 0.65 => (H width / H height) => 0.80"""
    glyphset = ttFont.getGlyphSet()
    if "H" not in glyphset:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'H' glyph in the font,"
            " so the proportions could not be tested",
        )
        return

    pen = BoundsPen(glyphset)
    glyphset["H"].draw(pen)
    (xMin, yMin, xMax, yMax) = pen.bounds
    proportion = (xMax - xMin) / (yMax - yMin)
    if not 0.65 <= proportion <= 0.80:
        yield FAIL, Message(
            "invalid-proportion",
            f"The proportion of H width to H height ({proportion})"
            f"does not conform to the expected range of 0.65-0.80",
        )
