from fontbakery.callable import check
from fontbakery.status import PASS, WARN, SKIP
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # noqa:F401 pylint:disable=W0611


def _is_non_spacing_mark_char(charcode):
    from fontTools import unicodedata

    category = unicodedata.category(chr(charcode))
    if category.startswith("C"):
        # skip control characters
        return None
    else:
        # Non spacing marks either have the Unicode General_category:
        # Mn, Nonspacing_Mark
        # Me, Enclosing_Mark
        # Characters with the category Mc, Spacing_Mark should not be considered
        # as non spacing marks.
        return category in ("Mn", "Me")


def _get_mark_class_glyphnames(ttFont):
    from fontbakery.constants import GlyphClass

    class_defs = ttFont["GDEF"].table.GlyphClassDef.classDefs.items()
    return {name for (name, value) in class_defs if value == GlyphClass.MARK}


@check(
    id="com.google.fonts/check/gdef_spacing_marks",
    rationale="""
        Glyphs in the GDEF mark glyph class should be non-spacing.

        Spacing glyphs in the GDEF mark glyph class may have incorrect anchor
        positioning that was only intended for building composite glyphs during design.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def com_google_fonts_check_gdef_spacing_marks(ttFont, config):
    """Check glyphs in mark glyph class are non-spacing."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        spacing_glyphnames = {
            name for (name, (width, lsb)) in ttFont["hmtx"].metrics.items() if width > 0
        }
        mark_class_glyphnames = _get_mark_class_glyphnames(ttFont)
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
                f"The following spacing glyphs may be in"
                f" the GDEF mark glyph class by mistake:\n"
                f"{formatted_list}",
            )
        else:
            yield PASS, (
                "Font does not has spacing glyphs in the GDEF mark glyph class."
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )


@check(
    id="com.google.fonts/check/gdef_mark_chars",
    rationale="""
        Mark characters should be in the GDEF mark glyph class.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def com_google_fonts_check_gdef_mark_chars(ttFont, config):
    """Check mark characters are in GDEF mark glyph class."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        cmap = ttFont.getBestCmap()
        mark_class_glyphnames = _get_mark_class_glyphnames(ttFont)
        mark_chars_not_in_mark_class = {
            charcode
            for charcode in cmap
            if _is_non_spacing_mark_char(charcode) is True
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
            yield PASS, (
                "Font does not have mark characters"
                " not in the GDEF mark glyph class."
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )


@check(
    id="com.google.fonts/check/gdef_non_mark_chars",
    rationale="""
        Glyphs in the GDEF mark glyph class become non-spacing and may be repositioned
        if they have mark anchors.

        Only combining mark glyphs should be in that class. Any non-mark glyph
        must not be in that class, in particular spacing glyphs.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2877",
)
def com_google_fonts_check_gdef_non_mark_chars(ttFont, config):
    """Check GDEF mark glyph class doesn't have characters that are not marks."""
    from fontbakery.utils import pretty_print_list

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        cmap = ttFont.getBestCmap()
        nonmark_chars = {
            charcode
            for charcode in cmap
            if _is_non_spacing_mark_char(charcode) is False
        }
        nonmark_char_glyphnames = {cmap[c] for c in nonmark_chars}
        glyphname_to_char_mapping = {}
        for k, v in cmap.items():
            if v in glyphname_to_char_mapping:
                glyphname_to_char_mapping[v].add(k)
            else:
                glyphname_to_char_mapping[v] = {k}
        mark_class_glyphnames = _get_mark_class_glyphnames(ttFont)
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
            yield PASS, (
                "Font does not have non-mark characters"
                " in the GDEF mark glyph class."
            )
    else:
        yield SKIP, (
            'Font does not declare an optional "GDEF" table'
            " or has any GDEF glyph class definition."
        )
