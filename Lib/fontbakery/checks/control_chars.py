from fontbakery.prelude import check, Message, FAIL


@check(
    id="control_chars",
    conditions=["are_ttf"],
    rationale="""
        Use of some unacceptable control characters in the U+0000 - U+001F range can
        lead to rendering issues on some platforms.

        Acceptable control characters are defined as .null (U+0000) and
        CR (U+000D) for this check.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2430",
)
def check_family_control_chars(ttFont):
    """Does font file include unacceptable control character glyphs?"""
    # list of unacceptable control character glyph names
    # definition includes the entire control character Unicode block except:
    #    - .null (U+0000)
    #    - CR (U+000D)
    UNACCEPTABLE_CC = {f"uni{n:04X}" for n in range(32) if n not in [0x00, 0x0D]}

    glyphset = set(ttFont["glyf"].glyphs.keys())
    bad_glyphs = glyphset.intersection(UNACCEPTABLE_CC)

    if bad_glyphs:
        bad = ", ".join(bad_glyphs)
        yield FAIL, Message(
            "unacceptable",
            f"The following unacceptable control characters were identified:\n{bad}",
        )
