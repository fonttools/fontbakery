from fontTools.pens.boundsPen import BoundsPen

from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.iso15008.utils import (
    stem_width,
    DISCLAIMER,
)


@check(
    id="iso15008/interline_spacing",
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
def check_iso15008_interline_spacing(ttFont):
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
    elif linegap < width:
        yield FAIL, Message(
            "bad-interline-spacing",
            f"The interline space {linegap} should"
            f" be more than the stem width {width}",
        )
