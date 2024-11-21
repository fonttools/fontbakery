from fontbakery.prelude import check, Message, WARN, SKIP
from fontbakery.utils import get_mark_class_glyphnames


@check(
    id="opentype/gdef_spacing_marks",
    rationale="""
        Glyphs in the GDEF mark glyph class should be non-spacing.

        Spacing glyphs in the GDEF mark glyph class may have incorrect anchor
        positioning that was only intended for building composite glyphs during design.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def check_gdef_spacing_marks(ttFont, config):
    """Check glyphs in mark glyph class are non-spacing."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        spacing_glyphnames = {
            name for (name, (width, lsb)) in ttFont["hmtx"].metrics.items() if width > 0
        }
        mark_class_glyphnames = get_mark_class_glyphnames(ttFont)
        spacing_glyphnames_in_mark_glyph_class = (
            spacing_glyphnames & mark_class_glyphnames
        )
        if spacing_glyphnames_in_mark_glyph_class:
            cmap = ttFont["cmap"].getBestCmap()
            glyphs = [
                f"{glyphname} (U+{codepoint:04X})"
                for codepoint, glyphname in cmap.items()
                if glyphname in spacing_glyphnames_in_mark_glyph_class
            ]
            glyphs += [
                f"{glyphname} (unencoded)"
                for glyphname in spacing_glyphnames_in_mark_glyph_class
                if glyphname not in cmap.values()
            ]
            formatted_list = "\t " + pretty_print_list(config, sorted(glyphs), sep=", ")
            yield WARN, Message(
                "spacing-mark-glyphs",
                f"The following glyphs seem to be spacing (because they have width > 0"
                f" on the hmtx table) so they may be in the GDEF mark glyph class"
                f" by mistake, or they should have zero width instead:\n"
                f"{formatted_list}",
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )
