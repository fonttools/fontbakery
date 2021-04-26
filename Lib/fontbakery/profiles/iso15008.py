"""
Checks for suitability for in-car displays (ISO 15008).
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontTools.pens.boundsPen import BoundsPen


profile = profile_factory(default_section=Section("Suitability for In-Car Display"))

DISCLAIMER = """
        (Note that PASSing this check does not guarantee compliance with ISO 15008.)
"""

CHECKS = ["com.google.fonts/check/iso15008_proportions"]


@check(
    id="com.google.fonts/check/iso15008_proportions",
    rationale="""
        According to ISO 15008, fonts used for in-car displays should not be too narrow or too wide.
        To ensure legibility of this font on in-car information systems, it is recommended that the ratio of H width to H height is between 0.65 and 0.80."""
    + DISCLAIMER,
)
def com_google_fonts_check_iso15008_proportions(ttFont):
    """Check if 0.65 => (H width / H height) => 0.80"""
    glyphset = ttFont.getGlyphSet()
    if "H" not in glyphset:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'H' glyph in the font, so the proportions could not be tested",
        )

    h_glyph = glyphset["H"]
    pen = BoundsPen(glyphset)
    h_glyph._glyph.draw(pen, ttFont.get("glyf"))
    (xMin, yMin, xMax, yMax) = pen.bounds
    proportion = (xMax - xMin) / (yMax - yMin)
    if 0.65 <= proportion <= 0.80:
        yield PASS, "the letter H is not too narrow or too wide"
    else:
        yield FAIL, Message(
            "invalid-proportion",
            f"The proportion of H width to H height ({proportion})"
            f"does not conform to the expected range of 0.65-0.80",
        )


profile.auto_register(globals())


profile.test_expected_checks(CHECKS, exclusive=True)
