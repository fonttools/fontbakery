"""
Checks for suitability for in-car displays (ISO 15008).
"""
from beziers.line import Line
from beziers.path import BezierPath
from beziers.point import Point
from fontTools.pens.boundsPen import BoundsPen

from fontbakery.callable import check
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.utils import exit_with_install_instructions

try:
    import uharfbuzz as hb
except ImportError:
    exit_with_install_instructions()

profile_imports = ((".", ("shared_conditions",)),)
profile = profile_factory(default_section=Section("Suitability for In-Car Display"))

DISCLAIMER = """
        (Note that passing this check does not guarantee compliance with ISO-15008.)
"""

CHECKS = [
    "com.google.fonts/check/iso15008_proportions",
    "com.google.fonts/check/iso15008_stem_width",
    "com.google.fonts/check/iso15008_intercharacter_spacing",
    "com.google.fonts/check/iso15008_interword_spacing",
    "com.google.fonts/check/iso15008_interline_spacing",
]


def xheight_intersections(ttFont, glyph):
    glyphset = ttFont.getGlyphSet()
    if glyph not in glyphset:
        return []

    paths = BezierPath.fromFonttoolsGlyph(ttFont, glyph)
    if len(paths) != 1:
        return []
    path = paths[0]

    xheight = ttFont["OS/2"].sxHeight

    bounds = path.bounds()
    bounds.addMargin(10)
    ray = Line(Point(bounds.left, xheight), Point(bounds.right, xheight))
    intersections = []
    for seg in path.asSegments():
        intersections.extend(seg.intersections(ray))
    return sorted(intersections, key=lambda i: i.point.x)


def stem_width(ttFont):
    glyphset = ttFont.getGlyphSet()
    if "l" not in glyphset:
        return None

    intersections = xheight_intersections(ttFont, "l")
    if len(intersections) != 2:
        return None
    (i1, i2) = intersections[0:2]
    return abs(i1.point.x - i2.point.x)


def pair_kerning(font, left, right):
    """The kerning between two glyphs (specified by name), in font units."""
    with open(font, "rb") as fontfile:
        fontdata = fontfile.read()
    face = hb.Face(fontdata)
    font = hb.Font(face)
    scale = face.upem
    font.scale = (scale, scale)
    buf = hb.Buffer()
    buf.add_str(left + right)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    pos = buf.glyph_positions[0].x_advance
    buf = hb.Buffer()
    buf.add_str(left + right)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": False})
    pos2 = buf.glyph_positions[0].x_advance
    return pos - pos2


@check(
    id="com.google.fonts/check/iso15008_proportions",
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
def com_google_fonts_check_iso15008_proportions(ttFont):
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
        According to ISO 15008, fonts used for in-car displays should
        not be too light or too bold.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the ratio of stem width to ascender height
        is between 0.10 and 0.20.
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3251",
    ],
)
def com_google_fonts_check_iso15008_stem_width(ttFont):
    """Check if 0.10 <= (stem width / ascender) <= 0.82"""
    width = stem_width(ttFont)
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


@check(
    id="com.google.fonts/check/iso15008_intercharacter_spacing",
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
def com_google_fonts_check_iso15008_intercharacter_spacing(font, ttFont):
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
    if 1.5 <= (l_l / width) <= 2.4:
        yield PASS, "Distance between vertical strokes was adequate"
    else:
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

    if (l_v / width) > 0.85:
        yield PASS, "Distance between vertical and diagonal strokes was adequate"
    else:
        yield FAIL, Message(
            "bad-vertical-diagonal-spacing",
            f"The space between vertical and diagonal strokes ({l_v})"
            f" was less than the expected"
            f" value of {width * 0.85}",
        )

    v_v = v_rsb + pair_kerning(font, "v", "v") + v_lsb
    if v_v > 0:
        yield PASS, "Distance between diagonal strokes was adequate"
    else:
        yield FAIL, Message(
            "bad-diagonal-diagonal-spacing", "Diagonal strokes (vv) were touching"
        )


@check(
    id="com.google.fonts/check/iso15008_interword_spacing",
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
def com_google_fonts_check_iso15008_interword_spacing(font, ttFont):
    """Check if spacing between words is adequate for display use"""
    l_intersections = xheight_intersections(ttFont, "l")
    if len(l_intersections) < 2:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'l' glyph in the font, so the spacing could not be tested",
        )
        return

    l_advance = ttFont["hmtx"]["l"][0]
    l_rsb = l_advance - l_intersections[-1].point.x

    glyphset = ttFont.getGlyphSet()
    pen = BoundsPen(glyphset)
    glyphset["m"].draw(pen)
    (xMin, yMin, xMax, yMax) = pen.bounds
    m_advance = ttFont["hmtx"]["m"][0]
    m_lsb = xMin
    m_rsb = m_advance - (m_lsb + xMax - xMin)

    n_lsb = ttFont["hmtx"]["n"][1]

    l_m = l_rsb + pair_kerning(font, "l", "m") + m_lsb
    space_width = ttFont["hmtx"]["space"][0]
    # Add spacing caused by normal sidebearings
    space_width += m_rsb + n_lsb

    if 2.50 <= space_width / l_m <= 3.0:
        yield PASS, "Advance width of interword space was adequate"
    else:
        yield FAIL, Message(
            "bad-interword-spacing",
            f"The interword space ({space_width}) was"
            f" outside the recommended range ({l_m*2.5}-{l_m*3.0})",
        )


@check(
    id="com.google.fonts/check/iso15008_interline_spacing",
    rationale="""
        According to ISO 15008, fonts used for in-car displays
        should not be too narrow or too wide.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the vertical metrics be set to a minimum
        at least one stem width between the bottom of the descender
        and the top of the ascender.
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3254",
    ],
)
def com_google_fonts_check_iso15008_interline_spacing(ttFont):
    """Check if spacing between lines is adequate for display use"""
    glyphset = ttFont.getGlyphSet()
    if "h" not in glyphset or "g" not in glyphset:
        yield FAIL, Message(
            "glyph-not-present",
            "There was no 'g'/'h' glyph in the font,"
            " so the spacing could not be tested",
        )
        return

    pen = BoundsPen(glyphset)
    glyphset["h"].draw(pen)
    (_, _, _, h_yMax) = pen.bounds

    pen = BoundsPen(glyphset)
    glyphset["g"].draw(pen)
    (_, g_yMin, _, _) = pen.bounds

    linegap = (
        (g_yMin - ttFont["OS/2"].sTypoDescender)
        + ttFont["OS/2"].sTypoLineGap
        + (ttFont["OS/2"].sTypoAscender - h_yMax)
    )
    width = stem_width(ttFont)
    if width is None:
        yield FAIL, Message("no-stem-width", "Could not determine stem width")
        return
    if linegap < width:
        yield FAIL, Message(
            "bad-interline-spacing",
            f"The interline space {linegap} should"
            f" be more than the stem width {width}",
        )
        return
    yield PASS, "Amount of interline space was adequate"


profile.auto_register(globals())


profile.test_expected_checks(CHECKS, exclusive=True)
