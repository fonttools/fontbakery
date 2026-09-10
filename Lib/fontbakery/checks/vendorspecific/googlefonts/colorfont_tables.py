from fontTools.misc.psCharStrings import calcSubrBias

from fontbakery.prelude import FAIL, Message, check


def _svg_color_glyph_names(ttFont):
    """Return the names of the glyphs covered by the font's SVG documents."""
    glyph_order = ttFont.getGlyphOrder()
    names = set()
    for doc in getattr(ttFont["SVG "], "docList", None) or []:
        try:
            start_glyph_id, end_glyph_id = doc.startGlyphID, doc.endGlyphID
        except AttributeError:
            # Support old-style docList entries: [doc, startGlyphID, endGlyphID]
            start_glyph_id, end_glyph_id = doc[1], doc[2]
        for glyph_id in range(start_glyph_id, end_glyph_id + 1):
            if 0 <= glyph_id < len(glyph_order):
                names.add(glyph_order[glyph_id])
    return names


def _cff2_charstring_uses_blend(charstring, _seen=None):
    """Whether a CFF2 charstring uses the blend operator, directly or
    through any of the subroutines it calls."""
    if _seen is None:
        _seen = set()
    if id(charstring) in _seen:
        return False
    _seen.add(id(charstring))

    charstring.decompile()
    subr_number = None
    for token in charstring.program:
        if isinstance(token, (int, float)):
            subr_number = token
        elif token == "blend":
            return True
        elif token == "callsubr" and subr_number is not None:
            subrs = getattr(charstring.private, "Subrs", None)
            if subrs:
                index = int(subr_number) + calcSubrBias(subrs)
                if 0 <= index < len(subrs) and _cff2_charstring_uses_blend(
                    subrs[index], _seen
                ):
                    return True
        elif token == "callgsubr" and subr_number is not None:
            global_subrs = charstring.globalSubrs
            if global_subrs:
                index = int(subr_number) + calcSubrBias(global_subrs)
                if 0 <= index < len(global_subrs) and _cff2_charstring_uses_blend(
                    global_subrs[index], _seen
                ):
                    return True
    return False


def _svg_color_glyphs_have_variations(ttFont):
    """Whether any of the glyphs described by the SVG table has variation data.

    SVG does not support OpenType Variations, so an SVG table is only a
    problem on a variable font when the color glyphs it describes actually
    vary (via 'gvar' or 'CFF2').
    """
    svg_glyph_names = _svg_color_glyph_names(ttFont)
    if not svg_glyph_names:
        # An SVG table without any glyph coverage is degenerate;
        # stay conservative and flag it as before.
        return True

    if "gvar" in ttFont:
        variations = ttFont["gvar"].variations
        return any(variations.get(name) for name in svg_glyph_names)

    if "CFF2" in ttFont:
        cff = ttFont["CFF2"].cff
        charstrings = cff[cff.fontNames[0]].CharStrings
        return any(
            _cff2_charstring_uses_blend(charstrings[name])
            for name in svg_glyph_names
            if name in charstrings
        )

    # Unexpected outline format for a variable font: stay conservative.
    return True


@check(
    id="googlefonts/colorfont_tables",
    rationale="""
        COLR v0 fonts are widely supported in most browsers so they do not require
        an SVG color table. However, some environments (e.g. Safari, Adobe apps)
        do not currently support COLR v1 so we need to add an SVG table to these fonts,
        except in the case of variable fonts whose color glyphs have variations,
        since SVG does not support OpenType Variations.

        A variable font whose SVG color glyphs do not have any variation data
        (in 'gvar' or 'CFF2') is fine, though, since those glyphs render the
        same at every point in the design space.

        To automatically generate compatible SVG/COLR tables,
        run the maximum_color tool in nanoemoji:
        https://github.com/googlefonts/nanoemoji
    """,
    proposal=[
        "https://googlefonts.github.io/gf-guide/color.html",
        "https://github.com/fonttools/fontbakery/issues/3886",
        "https://github.com/fonttools/fontbakery/issues/3888",
        "https://github.com/fonttools/fontbakery/pull/3889",
        "https://github.com/fonttools/fontbakery/issues/4131",
    ],
)
def check_colorfont_tables(font, ttFont):
    """Ensure font has the expected color font tables."""
    NANOEMOJI_ADVICE = (
        "You can do it by using the maximum_color tool provided by"
        " the nanoemoji project:\n"
        "https://github.com/googlefonts/nanoemoji"
    )

    if "COLR" in ttFont:
        if ttFont["COLR"].version == 0 and "SVG " in ttFont:
            yield FAIL, Message(
                "drop-svg",
                "Font has a COLR v0 table, which is already widely supported,"
                " so the SVG table isn't needed.",
            )

        elif (
            ttFont["COLR"].version == 1
            and "SVG " not in ttFont
            and not font.is_variable_font
        ):
            yield FAIL, Message(
                "add-svg",
                "Font has COLRv1 but no SVG table; for CORLv1, we require"
                " that an SVG table is present to support environments where"
                " the former is not supported yet.\n" + NANOEMOJI_ADVICE,
            )

    if "SVG " in ttFont:
        if font.is_variable_font and _svg_color_glyphs_have_variations(ttFont):
            yield FAIL, Message(
                "variable-svg",
                "This is a variable font and at least one of its SVG color"
                " glyphs has variation data, which SVG does not support.\n"
                "Please remove the SVG table from this font.",
            )

        if "COLR" not in ttFont:
            yield FAIL, Message(
                "add-colr",
                "Font only has an SVG table."
                " Please add a COLR table as well.\n" + NANOEMOJI_ADVICE,
            )
