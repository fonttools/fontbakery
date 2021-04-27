"""
Checks for suitability for in-car displays (ISO 15008).
"""

from fontbakery.callable import check, condition
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontTools.pens.boundsPen import BoundsPen
from beziers.path import BezierPath
from beziers.line import Line
from beziers.point import Point
import beziers


profile = profile_factory(default_section=Section("Suitability for In-Car Display"))

DISCLAIMER = """
        (Note that PASSing this check does not guarantee compliance with ISO 15008.)
"""

CHECKS = [
    "com.google.fonts/check/iso15008_proportions",
    "com.google.fonts/check/iso15008_stem_width",
]


@condition
def stem_width(ttFont):
    glyphset = ttFont.getGlyphSet()
    if "l" not in glyphset:
        return None
    paths = BezierPath.fromFonttoolsGlyph(ttFont, "l")
    if len(paths) != 1:
        return None
    path = paths[0]

    xheight = ttFont["OS/2"].sxHeight

    bounds = path.bounds()
    bounds.addMargin(10)
    ray = Line(Point(bounds.left, xheight), Point(bounds.right, xheight))
    intersections = []
    for seg in path.asSegments():
        intersections.extend(seg.intersections(ray))

    if len(intersections) != 2:
        return None
    (i1, i2) = intersections[0:2]
    return abs(i1.point.x - i2.point.x)


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


@check(
    id="com.google.fonts/check/iso15008_stem_width",
    rationale="""
        According to ISO 15008, fonts used for in-car displays should not be too light or too bold.
        To ensure legibility of this font on in-car information systems, it is recommended that the ratio of stem width to ascender height is between 0.10 and 0.20."""
    + DISCLAIMER,
)
def com_google_fonts_check_iso15008_stem_width(ttFont):
    """Check if 0.10 <= (stem width / ascender) <= 0.82"""
    width = stem_width(ttFont)
    print("Stem width", width)
    if width is None:
        yield FAIL, Message("no-stem-width", "Could not determine stem width")
        return
    ascender = ttFont["hhea"].ascender
    proportion = width / ascender
    if 0.10 <= proportion <= 0.20:
        yield PASS, "the stem width is not too light or too bold"
    else:
        yield FAIL, Message(
            "invalid-proportion",
            f"The proportion of stem width to ascender ({proportion})"
            f"does not conform to the expected range of 0.10-0.20",
        )


profile.auto_register(globals())


profile.test_expected_checks(CHECKS, exclusive=True)
