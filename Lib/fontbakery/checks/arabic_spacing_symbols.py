from fontbakery.prelude import FAIL, Message, check


@check(
    id="arabic_spacing_symbols",
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4295",
    ],
    rationale="""
        Unicode has a few spacing symbols representing Arabic dots and other marks,
        but they are purposefully not classified as marks.

        Many fonts mistakenly classify them as marks, making them unsuitable
        for their original purpose as stand-alone symbols to used in pedagogical
        contexts discussing Arabic consonantal marks.
    """,
    severity=4,
)
def check_arabic_spacing_symbols(ttFont):
    """Check that Arabic spacing symbols U+FBB2–FBC1 aren't classified as marks."""

    # code-points
    ARABIC_SPACING_SYMBOLS = {
        0xFBB2,  # Dot Above
        0xFBB3,  # Dot Below
        0xFBB4,  # Two Dots Above
        0xFBB5,  # Two Dots Below
        0xFBB6,  # Three Dots Above
        0xFBB7,  # Three Dots Below
        0xFBB8,  # Three Dots Pointing Downwards Above
        0xFBB9,  # Three Dots Pointing Downwards Below
        0xFBBA,  # Four Dots Above
        0xFBBB,  # Four Dots Below
        0xFBBC,  # Double Vertical Bar Below
        0xFBBD,  # Two Dots Vertically Above
        0xFBBE,  # Two Dots Vertically Below
        0xFBBF,  # Ring
        0xFBC0,  # Small Tah Above
        0xFBC1,  # Small Tah Below
        0xFBC2,  # Wasla Above
    }

    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
        reverseCmap = ttFont["cmap"].buildReversed()
        for name in reverseCmap:
            if reverseCmap[name].intersection(ARABIC_SPACING_SYMBOLS):
                if name in class_def and class_def[name] == 3:
                    yield FAIL, Message(
                        "mark-in-gdef",
                        f'"{name}" is defined in GDEF as a mark (class 3).',
                    )
