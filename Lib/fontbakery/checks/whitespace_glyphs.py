from fontbakery.prelude import check, Message, FAIL, PASS


@check(
    id="whitespace_glyphs",
    rationale="""
        The OpenType specification recommends that fonts should contain
        glyphs for the following whitespace characters:

        - U+0020 SPACE
        - U+00A0 NO-BREAK SPACE

        The space character is required for text processing, and the no-break
        space is useful to prevent line breaks at its position. It is also
        recommended to have a glyph for the tab character (U+0009) and the
        soft hyphen (U+00AD), but these are not mandatory.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_whitespace_glyphs(ttFont, missing_whitespace_chars):
    """Font contains glyphs for whitespace characters?"""
    failed = False
    for wsc in missing_whitespace_chars:
        failed = True
        yield FAIL, Message(
            f"missing-whitespace-glyph-{wsc}",
            f"Whitespace glyph missing for codepoint {wsc}.",
        )

    if not failed:
        yield PASS, "Font contains glyphs for whitespace characters."
