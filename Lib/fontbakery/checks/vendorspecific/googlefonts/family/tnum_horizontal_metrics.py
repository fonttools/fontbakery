from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/family/tnum_horizontal_metrics",
    conditions=["RIBBI_ttFonts"],
    rationale="""
        Tabular figures need to have the same metrics in all styles in order to allow
        tables to be set with proper typographic control, but to maintain the placement
        of decimals and numeric columns between rows.

        Here's a good explanation of this:
        https://www.typography.com/techniques/fonts-for-financials/#tabular-figs
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2278",
)
def check_family_tnum_horizontal_metrics(RIBBI_ttFonts):
    """All tabular figures must have the same width across the RIBBI-family."""
    tnum_widths = {}
    for ttFont in RIBBI_ttFonts:
        glyphs = ttFont.getGlyphSet()
        tnum_glyphs = [
            (glyph_id, glyphs[glyph_id])
            for glyph_id in glyphs.keys()
            if glyph_id.endswith(".tnum")
        ]
        for glyph_id, glyph in tnum_glyphs:
            if glyph.width not in tnum_widths:
                tnum_widths[glyph.width] = [glyph_id]
            else:
                tnum_widths[glyph.width].append(glyph_id)

    if len(tnum_widths.keys()) > 1:
        max_num = 0
        most_common_width = None
        for width, glyphs in tnum_widths.items():
            if len(glyphs) > max_num:
                max_num = len(glyphs)
                most_common_width = width

        del tnum_widths[most_common_width]
        yield FAIL, Message(
            "inconsistent-widths",
            f"The most common tabular glyph width is"
            f" {most_common_width}. But there are other"
            f" tabular glyphs with different widths"
            f" such as the following ones:\n"
            "\t{tnum_widths}.",
        )
