from fontbakery.prelude import check, Message, FAIL


@check(
    id="family/control_chars",
    conditions=["are_ttf"],
    rationale="""
        Use of some unacceptable control characters in the U+0000 - U+001F range can
        lead to rendering issues on some platforms.

        Acceptable control characters are defined as .null (U+0000) and
        CR (U+000D) for this check.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2430",
)
def check_family_control_chars(ttFonts):
    """Does font file include unacceptable control character glyphs?"""
    # list of unacceptable control character glyph names
    # definition includes the entire control character Unicode block except:
    #    - .null (U+0000)
    #    - CR (U+000D)
    unacceptable_cc_list = [
        "uni0001",
        "uni0002",
        "uni0003",
        "uni0004",
        "uni0005",
        "uni0006",
        "uni0007",
        "uni0008",
        "uni0009",
        "uni000A",
        "uni000B",
        "uni000C",
        "uni000E",
        "uni000F",
        "uni0010",
        "uni0011",
        "uni0012",
        "uni0013",
        "uni0014",
        "uni0015",
        "uni0016",
        "uni0017",
        "uni0018",
        "uni0019",
        "uni001A",
        "uni001B",
        "uni001C",
        "uni001D",
        "uni001E",
        "uni001F",
    ]

    # A dict with 'key => value' pairs of
    # font path that did not pass the check => list of unacceptable glyph names
    bad_fonts = {}

    for ttFont in ttFonts:
        passed = True
        unacceptable_glyphs_in_set = []  # a list of unacceptable glyph names identified
        glyph_name_set = set(ttFont["glyf"].glyphs.keys())
        fontname = ttFont.reader.file.name

        for unacceptable_glyph_name in unacceptable_cc_list:
            if unacceptable_glyph_name in glyph_name_set:
                passed = False
                unacceptable_glyphs_in_set.append(unacceptable_glyph_name)

        if not passed:
            bad_fonts[fontname] = unacceptable_glyphs_in_set

    if len(bad_fonts) > 0:
        msg_unacceptable = (
            "The following unacceptable control characters were identified:\n"
        )
        for fnt in bad_fonts.keys():
            bad = ", ".join(bad_fonts[fnt])
            msg_unacceptable += f" {fnt}: {bad}\n"
        yield FAIL, Message("unacceptable", f"{msg_unacceptable}")
