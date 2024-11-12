from fontTools.pens.boundsPen import BoundsPen
from fontbakery.prelude import check, Message, PASS, FAIL, WARN, SKIP


@check(
    id="typoascender_exceeds_Agrave",
    rationale="""
        MacOS uses OS/2.sTypoAscender/Descender values to determine the line height
        of a font. If the sTypoAscender value is smaller than the maximum height of
        the uppercase /Agrave, the font’s sTypoAscender value is ignored, and a very
        tall line height is used instead.

        This happens on a per-font, per-style basis, so it’s possible for a font to
        have a good sTypoAscender value in one style but not in another. This can
        lead to inconsistent line heights across a typeface family.

        So, it is important to ensure that the sTypoAscender value is greater than
        the maximum height of the uppercase /Agrave in all styles of a type family.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3170",
)
def check_typoascender_exceeds_Agrave(ttFont):
    """Checking that the typoAscender exceeds the yMax of the /Agrave."""

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    from copy import deepcopy

    ttFont_copy = deepcopy(ttFont)

    if "OS/2" not in ttFont_copy:
        yield FAIL, Message("lacks-OS/2", "Font file lacks OS/2 table")
        return

    glyphset = ttFont_copy.getGlyphSet()

    if "Agrave" not in glyphset and "uni00C0" not in glyphset:
        yield SKIP, Message(
            "lacks-Agrave",
            "Font file lacks the /Agrave, so it can’t be compared with typoAscender",
        )
        return

    pen = BoundsPen(glyphset)

    try:
        glyphset["Agrave"].draw(pen)
    except KeyError:
        glyphset["uni00C0"].draw(pen)

    yMax = pen.bounds[-1]

    typoAscender = ttFont_copy["OS/2"].sTypoAscender

    if typoAscender < yMax:
        yield WARN, Message(
            "typoAscender",
            f"OS/2.sTypoAscender value should be greater than {yMax},"
            f" but got {typoAscender} instead",
        )
    else:
        yield PASS, "OS/2.sTypoAscender value is greater than the yMax of /Agrave."
