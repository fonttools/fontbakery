from beziers.line import Line
from beziers.path import BezierPath
from beziers.point import Point

from fontbakery.utils import exit_with_install_instructions


DISCLAIMER = """
        (Note that passing this check does not guarantee compliance with ISO-15008.)
"""


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

    try:
        import uharfbuzz as hb
    except ImportError:
        exit_with_install_instructions("iso15008")

    with open(font.file, "rb") as fontfile:
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
