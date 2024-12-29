from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/colorfont_tables",
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
