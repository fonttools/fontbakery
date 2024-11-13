from fontbakery.prelude import check, Message, WARN, SKIP
from fontbakery.utils import get_mark_class_glyphnames, is_non_spacing_mark_char


@check(
    id="opentype/gdef_non_mark_chars",
    rationale="""
        Glyphs in the GDEF mark glyph class become non-spacing and may be repositioned
        if they have mark anchors.

        Only combining mark glyphs should be in that class. Any non-mark glyph
        must not be in that class, in particular spacing glyphs.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def check_gdef_non_mark_chars(ttFont, config):
    """Check GDEF mark glyph class doesn't have characters that are not marks."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        cmap = ttFont.getBestCmap()
        nonmark_chars = {
            charcode for charcode in cmap if is_non_spacing_mark_char(charcode) is False
        }
        nonmark_char_glyphnames = {cmap[c] for c in nonmark_chars}
        glyphname_to_char_mapping = {}
        for k, v in cmap.items():
            if v in glyphname_to_char_mapping:
                glyphname_to_char_mapping[v].add(k)
            else:
                glyphname_to_char_mapping[v] = {k}
        mark_class_glyphnames = get_mark_class_glyphnames(ttFont)
        nonmark_char_glyphnames_in_mark_class = (
            nonmark_char_glyphnames & mark_class_glyphnames
        )
        if nonmark_char_glyphnames_in_mark_class:
            nonmark_chars_in_mark_class = set()
            for glyphname in nonmark_char_glyphnames_in_mark_class:
                chars = glyphname_to_char_mapping[glyphname]
                for char in chars:
                    if char in nonmark_chars:
                        nonmark_chars_in_mark_class.add(char)
            formatted_nonmarks = "\t " + pretty_print_list(
                config,
                sorted("U+%04X" % c for c in nonmark_chars_in_mark_class),
                sep=", ",
            )
            yield WARN, Message(
                "non-mark-chars",
                f"The following non-mark characters should"
                f" not be in the GDEF mark glyph class:\n"
                f"{formatted_nonmarks}",
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )
