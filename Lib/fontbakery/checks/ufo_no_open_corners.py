from fontbakery.prelude import check, FAIL, Message
from fontbakery import utils


@check(
    id="ufo_no_open_corners",
    rationale="""
        This may be a requirement when creating a font that supports a roundness
        axis.
    """,
    conditions=["ufo_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/4808",
)
def check_ufo_no_open_corners(config, ufo):
    """Check the sources have no corners"""
    from glyphsLib.filters.eraseOpenCorners import EraseOpenCornersPen
    from fontTools.pens.basePen import NullPen

    font = ufo.ufo_font
    for layer in font.layers:
        offending_glyphs = []
        for glyph in layer:
            erase_open_corners = EraseOpenCornersPen(NullPen())
            for contour in glyph:
                contour.draw(erase_open_corners)
            if erase_open_corners.affected:
                offending_glyphs.append(glyph.name)

        if offending_glyphs:
            location_str = (
                "Default layer"
                if layer.name == font.layers.defaultLayer.name
                else layer.name
            )
            yield (
                FAIL,
                Message(
                    "open-corners-found",
                    f"{location_str} contains glyphs with open corners:\n\n"
                    f"{utils.bullet_list(config, offending_glyphs)}\n",
                ),
            )
