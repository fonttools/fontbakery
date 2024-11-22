from fontbakery.prelude import check, Message, PASS, WARN, INFO
from fontbakery.utils import (
    bullet_list,
    pretty_print_list,
)


@check(
    id="typenetwork/family/tnum_horizontal_metrics",
    rationale="""
        Tabular figures need to have the same metrics in all styles in order to allow
        tables to be set with proper typographic control, but to maintain the placement
        of decimals and numeric columns between rows.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_family_tnum_horizontal_metrics(ttFonts, config):
    """All tabular figures must have the same width across the family."""
    tnum_widths = {}
    half_width_glyphs = {}
    for ttFont in list(ttFonts):
        glyphs = ttFont.getGlyphSet()

        tabular_suffixes = (".tnum", ".tf", ".tosf", ".tsc", ".tab", ".tabular")
        tnum_glyphs = [
            (glyph_id, glyphs[glyph_id])
            for glyph_id in glyphs.keys()
            if any(suffix in glyph_id for suffix in tabular_suffixes)
        ]

        for glyph_id, glyph in tnum_glyphs:
            if glyph.width not in tnum_widths:
                tnum_widths[glyph.width] = [glyph_id]
            else:
                tnum_widths[glyph.width].append(glyph_id)

    max_num = 0
    most_common_width = None
    half_width = None

    # Get most common width
    for width, glyphs in tnum_widths.items():
        if len(glyphs) > max_num:
            max_num = len(glyphs)
            most_common_width = width
    if most_common_width:
        del tnum_widths[most_common_width]

    # Get Half width
    for width, glyphs in tnum_widths.items():
        if round(most_common_width / 2) == width:
            half_width = width
            half_width_glyphs = glyphs

    if half_width:
        del tnum_widths[half_width]

    if half_width:
        yield INFO, Message(
            "half-widths",
            f"The are other glyphs with half of the width ({half_width}) of the"
            f" most common width such as the following ones:\n\n"
            f"{bullet_list(config, half_width_glyphs)}.",
        )

    if len(tnum_widths.keys()):
        # prepare string to display
        tnumWidthsString = ""
        for width, glyphs in tnum_widths.items():
            tnumWidthsString += f"{width}: {pretty_print_list(config, glyphs)}\n\n"
        yield WARN, Message(
            "inconsistent-widths",
            f"The most common tabular glyph width is {most_common_width}."
            f" But there are other tabular glyphs with different widths"
            f" such as the following ones:\n\n{tnumWidthsString}.",
        )
    else:
        yield PASS, "OK"
