import os
from fontbakery.prelude import check, Message, WARN, FAIL
from fontbakery.utils import bullet_list


@check(
    id="com.google.fonts/check/family/equal_codepoint_coverage",
    conditions=["are_ttf", "stylenames_are_canonical"],
    proposal="https://github.com/fonttools/fontbakery/issues/4180",
    rationale="""
        For a given family, all fonts must have the same codepoint coverage.
        This is because we want to avoid the situation where, for example,
        a character is present in a regular font but missing in the italic style;
        turning on italic would cause the character to be rendered either as a
        fake italic (auto-slanted) or to show tofu.
    """,
)
def com_google_fonts_check_family_equal_codepoint_coverage(fonts, config):
    """Fonts have equal codepoint coverage"""
    cmaps = {}
    for font in fonts:
        stylename = font.canonical_stylename
        cmaps[stylename] = font.font_codepoints
    cmap_list = list(cmaps.values())
    common_cps = cmap_list[0].intersection(*cmap_list[1:])
    problems = []

    for style, cmap in cmaps.items():
        residue = cmap - common_cps
        if residue:
            problems.append(
                f"* {style} contains encoded codepoints not found "
                "in other related fonts:"
                + bullet_list(config, ["U+%04x" % cp for cp in residue])
            )

    if problems:
        yield FAIL, Message("glyphset-diverges", "\n".join(problems))


@check(
    id="com.google.fonts/check/family/italics_have_roman_counterparts",
    rationale="""
        For each font family on Google Fonts, every Italic style must have
        a Roman sibling.

        This kind of problem was first observed at [1] where the Bold style was
        missing but BoldItalic was included.

        [1] https://github.com/google/fonts/pull/1482
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1733",
)
def com_google_fonts_check_family_italics_have_roman_counterparts(fonts, config):
    """Ensure Italic styles have Roman counterparts."""

    filenames = [f.file for f in fonts]
    italics = [f.file for f in fonts if "Italic" in f.file]
    missing_roman = []
    for italic in italics:
        if (
            "-" not in os.path.basename(italic)
            or len(os.path.basename(italic).split("-")[-1].split(".")) != 2
        ):
            yield WARN, Message(
                "bad-filename", f"Filename seems to be incorrect: '{italic}'"
            )

        style_from_filename = os.path.basename(italic).split("-")[-1].split(".")[0]
        is_varfont = "[" in style_from_filename

        # to remove the axes syntax used on variable-font filenames:
        if is_varfont:
            style_from_filename = style_from_filename.split("[")[0]

        if style_from_filename == "Italic":
            if is_varfont:
                # "Familyname-Italic[wght,wdth].ttf" => "Familyname[wght,wdth].ttf"
                roman_counterpart = italic.replace("-Italic", "")
            else:
                # "Familyname-Italic.ttf" => "Familyname-Regular.ttf"
                roman_counterpart = italic.replace("Italic", "Regular")
        else:
            # "Familyname-BoldItalic[wght,wdth].ttf" => "Familyname-Bold[wght,wdth].ttf"
            roman_counterpart = italic.replace("Italic", "")

        if roman_counterpart not in filenames:
            missing_roman.append(italic)

    if missing_roman:
        from fontbakery.utils import pretty_print_list

        missing_roman = pretty_print_list(config, missing_roman)
        yield FAIL, Message(
            "missing-roman", f"Italics missing a Roman counterpart: {missing_roman}"
        )


@check(
    id="com.google.fonts/check/family/tnum_horizontal_metrics",
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
def com_google_fonts_check_family_tnum_horizontal_metrics(RIBBI_ttFonts):
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
            f" such as the following ones:\n\t{tnum_widths}.",
        )
