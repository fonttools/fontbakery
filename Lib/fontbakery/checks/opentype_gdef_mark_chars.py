from fontbakery.prelude import check, Message, WARN, SKIP
from fontbakery.utils import get_mark_class_glyphnames, is_non_spacing_mark_char


@check(
    id="opentype/gdef_mark_chars",
    rationale="""
        Mark characters should be in the GDEF mark glyph class.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def check_gdef_mark_chars(ttFont, config):
    """Check mark characters are in GDEF mark glyph class."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        cmap = ttFont.getBestCmap()
        mark_class_glyphnames = get_mark_class_glyphnames(ttFont)
        mark_chars_not_in_mark_class = {
            charcode
            for charcode in cmap
            if is_non_spacing_mark_char(charcode) is True
            and cmap[charcode] not in mark_class_glyphnames
        }

        if mark_chars_not_in_mark_class:
            formatted_marks = "\t " + pretty_print_list(
                config,
                sorted(f"{cmap[c]} (U+{c:04X})" for c in mark_chars_not_in_mark_class),
                sep=", ",
            )
            yield WARN, Message(
                "mark-chars",
                f"The following mark characters could be"
                f" in the GDEF mark glyph class:\n"
                f"{formatted_marks}",
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )
