from fontbakery.prelude import check, WARN


@check(
    id="googlefonts/production_glyphs_similarity",
    conditions=["api_gfonts_ttFont"],
    rationale="""
        We check that the glyphs in the font are similar to the glyphs in the
        version hosted on fonts.google.com. We do not expect updated fonts to
        have exactly the same glyphs as the previous version, but we do expect
        the changes to be minimal.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_production_glyphs_similarity(ttFont, api_gfonts_ttFont, config):
    """Glyphs are similiar to Google Fonts version?"""

    # This check modifies the font file with `.draw(pen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    from copy import deepcopy

    ttFont_copy = deepcopy(ttFont)
    api_gfonts_ttFont_copy = deepcopy(api_gfonts_ttFont)

    from fontbakery.utils import pretty_print_list

    def glyphs_surface_area(a_ttFont):
        """Calculate the surface area of a glyph's ink"""
        from fontTools.pens.areaPen import AreaPen

        glyphs = {}
        glyph_set = a_ttFont.getGlyphSet()
        area_pen = AreaPen(glyph_set)

        for glyph in glyph_set.keys():
            glyph_set[glyph].draw(area_pen)

            area = area_pen.value
            area_pen.value = 0
            glyphs[glyph] = area
        return glyphs

    bad_glyphs = []
    these_glyphs = glyphs_surface_area(ttFont_copy)
    gfonts_glyphs = glyphs_surface_area(api_gfonts_ttFont_copy)

    shared_glyphs = set(these_glyphs) & set(gfonts_glyphs)

    this_upm = ttFont_copy["head"].unitsPerEm
    gfonts_upm = api_gfonts_ttFont_copy["head"].unitsPerEm

    for glyph in shared_glyphs:
        # Normalize area difference against comparison's upm
        this_glyph_area = (these_glyphs[glyph] / this_upm) * gfonts_upm
        gfont_glyph_area = (gfonts_glyphs[glyph] / gfonts_upm) * this_upm

        if abs(this_glyph_area - gfont_glyph_area) > 7000:
            bad_glyphs.append(glyph)

    if bad_glyphs:
        formatted_list = "\t* " + pretty_print_list(
            config, sorted(bad_glyphs), sep="\n\t* "
        )

        yield WARN, (
            "Following glyphs differ greatly from"
            f" Google Fonts version:\n{formatted_list}"
        )
