from fontbakery.prelude import check, Message, FAIL, INFO, PASS, WARN, FATAL


@check(
    id="opentype/xavgcharwidth",
    rationale="""
        The OS/2.xAvgCharWidth field is used to calculate the width of a string of
        characters. It is the average width of all non-zero width glyphs in the font.

        This check ensures that the value is correct. A failure here may indicate
        a bug in the font compiler, rather than something that the designer can
        do anything about.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_xavgcharwidth(ttFont):
    """Check if OS/2 xAvgCharWidth is correct."""

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "Required OS/2 table is missing.")
        return

    current_value = ttFont["OS/2"].xAvgCharWidth
    ACCEPTABLE_ERROR = 10  # Width deviation tolerance in font units

    # Since version 3, the average is computed using _all_ glyphs in a font.
    if ttFont["OS/2"].version >= 3:
        calculation_rule = "the average of the widths of all glyphs in the font"
        if not ttFont["hmtx"].metrics:  # May contain just '.notdef', which is valid.
            yield FATAL, Message(
                "missing-glyphs",
                "Found no glyph width data in the hmtx table!",
            )
            return

        width_sum = 0
        count = 0
        for width, _ in ttFont[
            "hmtx"
        ].metrics.values():  # At least .notdef must be present.
            # The OpenType spec excludes negative widths (the
            # relevant field in `hmtx` tables is unsigned);
            # other formats (UFO) may allow signed, and
            # therefore negative, widths.
            # For extra reassurance, here we only count strictly
            # positive widths.
            if width > 0:
                count += 1
                width_sum += width

        expected_value = int(round(width_sum / count))
    else:  # Version 2 and below only consider lowercase latin glyphs and space.
        calculation_rule = (
            "the weighted average of the widths of the latin"
            " lowercase glyphs in the font"
        )
        weightFactors = {
            "a": 64,
            "b": 14,
            "c": 27,
            "d": 35,
            "e": 100,
            "f": 20,
            "g": 14,
            "h": 42,
            "i": 63,
            "j": 3,
            "k": 6,
            "l": 35,
            "m": 20,
            "n": 56,
            "o": 56,
            "p": 17,
            "q": 4,
            "r": 49,
            "s": 56,
            "t": 71,
            "u": 31,
            "v": 10,
            "w": 18,
            "x": 3,
            "y": 18,
            "z": 2,
            "space": 166,
        }
        glyph_order = ttFont.getGlyphOrder()
        if not all(character in glyph_order for character in weightFactors):
            yield FATAL, Message(
                "missing-glyphs",
                "Font is missing the required latin lowercase letters and/or space.",
            )
            return

        width_sum = 0
        for glyph_id in weightFactors:
            width = ttFont["hmtx"].metrics[glyph_id][0]
            width_sum += width * weightFactors[glyph_id]

        expected_value = int(width_sum / 1000.0 + 0.5)  # round to closest int

    difference = abs(current_value - expected_value)

    # We accept matches and off-by-ones due to rounding as correct.
    if current_value == expected_value or difference == 1:
        yield PASS, "OS/2 xAvgCharWidth value is correct."
    elif difference < ACCEPTABLE_ERROR:
        yield INFO, Message(
            "xAvgCharWidth-close",
            f"OS/2 xAvgCharWidth is {current_value} but it should be"
            f" {expected_value} which corresponds to {calculation_rule}."
            f" These are similar values, which"
            f" may be a symptom of the slightly different"
            f" calculation of the xAvgCharWidth value in"
            f" font editors. There's further discussion on"
            f" this at https://github.com/fonttools/fontbakery"
            f"/issues/1622",
        )
    else:
        yield WARN, Message(
            "xAvgCharWidth-wrong",
            f"OS/2 xAvgCharWidth is {current_value} but it should be"
            f" {expected_value} which corresponds to {calculation_rule}.",
        )
