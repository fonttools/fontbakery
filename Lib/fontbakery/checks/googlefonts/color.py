from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="com.google.fonts/check/colorfont_tables",
    rationale="""
        COLR v0 fonts are widely supported in most browsers so they do not require
        an SVG color table. However, some environments (e.g. Safari, Adobe apps)
        do not currently support COLR v1 so we need to add an SVG table to these fonts,
        except in the case of variable fonts, since SVG does not support
        OpenType Variations.

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
def com_google_fonts_check_colorfont_tables(font, ttFont):
    """Check font has the expected color font tables."""
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
        if font.is_variable_font:
            yield FAIL, Message(
                "variable-svg",
                "This is a variable font and SVG does not support"
                " OpenType Variations.\n"
                "Please remove the SVG table from this font.",
            )

        if "COLR" not in ttFont:
            yield FAIL, Message(
                "add-colr",
                "Font only has an SVG table."
                " Please add a COLR table as well.\n" + NANOEMOJI_ADVICE,
            )


@check(
    id="com.google.fonts/check/color_cpal_brightness",
    rationale="""
        Layers of a COLRv0 font should not be too dark or too bright. When layer colors
        are set explicitly, they can't be changed and they may turn out illegible
        against dark or bright backgrounds.

        While traditional color-less fonts can be colored in design apps or CSS, a
        black color definition in a COLRv0 font actually means that that layer will be
        rendered in black regardless of the background color. This leads to text
        becoming invisible against a dark background, for instance when using a dark
        theme in a web browser or operating system.

        This check ensures that layer colors are at least 10% bright and at most 90%
        bright, when not already set to the current color (0xFFFF).
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3908",
)
def com_google_fonts_check_color_cpal_brightness(config, ttFont):
    """Color layers should have a minimum brightness"""
    from fontbakery.utils import pretty_print_list

    def color_brightness(hex_value):
        """Generic color brightness formula"""
        return (hex_value[0] * 299 + hex_value[1] * 587 + hex_value[2] * 114) / 1000

    minimum_brightness = 256 * 0.1
    FOREGROUND_COLOR = 0xFFFF
    dark_glyphs = []
    if "COLR" in ttFont.keys() and ttFont["COLR"].version == 0:
        for key in ttFont["COLR"].ColorLayers:
            for layer in ttFont["COLR"].ColorLayers[key]:
                # 0xFFFF is the foreground color, ignore
                if layer.colorID != FOREGROUND_COLOR:
                    hex_value = ttFont["CPAL"].palettes[0][layer.colorID]
                    layer_brightness = color_brightness(hex_value)
                    if (
                        layer_brightness < minimum_brightness
                        or layer_brightness > 256 - minimum_brightness
                    ):
                        if key not in dark_glyphs:
                            dark_glyphs.append(key)
    if dark_glyphs:
        dark_glyphs = pretty_print_list(config, sorted(dark_glyphs))
        yield WARN, Message(
            "glyphs-too-dark-or-too-bright",
            f"The following glyphs have layers that are too bright or"
            f" too dark: {dark_glyphs}.\n"
            f"\n"
            f" To fix this, please either set the color definitions of all"
            f" layers in question to current color (0xFFFF), or alter"
            f" the brightness of these layers significantly.",
        )


@check(
    id="com.google.fonts/check/empty_glyph_on_gid1_for_colrv0",
    rationale="""
        A rendering bug in Windows 10 paints whichever glyph is on GID 1 on top of
        some glyphs, colored or not. This only occurs for COLR version 0 fonts.

        Having a glyph with no contours on GID 1 is a practical workaround for that.

        See https://github.com/googlefonts/gftools/issues/609
    """,
    proposal=[
        "https://github.com/googlefonts/gftools/issues/609",
        "https://github.com/fonttools/fontbakery/pull/3905",
    ],
)
def com_google_fonts_check_empty_glyph_on_gid1_for_colrv0(ttFont):
    """Put an empty glyph on GID 1 right after the .notdef glyph for COLRv0 fonts."""
    SUGGESTED_FIX = (
        "To fix this, please reorder the glyphs so that"
        " a glyph with no contours is on GID 1 right after the `.notdef` glyph."
        " This could be the space glyph."
    )
    from fontTools.pens.areaPen import AreaPen

    glyphOrder = ttFont.getGlyphOrder()
    glyphSet = ttFont.getGlyphSet()
    pen = AreaPen(glyphSet)
    gid1 = glyphSet[glyphOrder[1]]
    gid1.draw(pen)
    area = pen.value

    if "COLR" in ttFont.keys() and ttFont["COLR"].version == 0 and area != 0:
        yield FAIL, Message(
            "gid1-has-contours",
            "This is a COLR font. As a workaround for a rendering bug in"
            " Windows 10, it needs an empty glyph to be in GID 1. " + SUGGESTED_FIX,
        )
