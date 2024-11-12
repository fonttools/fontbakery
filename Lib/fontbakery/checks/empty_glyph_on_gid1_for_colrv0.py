from fontbakery.prelude import check, Message, FAIL


@check(
    id="empty_glyph_on_gid1_for_colrv0",
    rationale="""
        A rendering bug in Windows 10 paints whichever glyph is on GID 1 on top of
        some glyphs, colored or not. This only occurs for COLR version 0 fonts.

        Having a glyph with no contours on GID 1 is a practical workaround for that.

        See https://github.com/googlefonts/gftools/issues/609
    """,
    proposal=[
        "https://github.com/googlefonts/gftools/issues/609",
        "https://github.com/fonttools/fontbakery/pull/3905",
    ],
)
def check_empty_glyph_on_gid1_for_colrv0(ttFont):
    """Put an empty glyph on GID 1 right after the .notdef glyph for COLRv0 fonts."""
    SUGGESTED_FIX = (
        "To fix this, please reorder the glyphs so that"
        " a glyph with no contours is on GID 1 right after the `.notdef` glyph."
        " This could be the space glyph."
    )
    from fontTools.pens.areaPen import AreaPen

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    from copy import deepcopy

    ttFont_copy = deepcopy(ttFont)

    glyphOrder = ttFont_copy.getGlyphOrder()
    glyphSet = ttFont_copy.getGlyphSet()
    pen = AreaPen(glyphSet)
    gid1 = glyphSet[glyphOrder[1]]
    gid1.draw(pen)
    area = pen.value

    if "COLR" in ttFont_copy.keys() and ttFont_copy["COLR"].version == 0 and area != 0:
        yield FAIL, Message(
            "gid1-has-contours",
            "This is a COLR font. As a workaround for a rendering bug in"
            " Windows 10, it needs an empty glyph to be in GID 1. " + SUGGESTED_FIX,
        )
