from fontbakery.prelude import check, Message, WARN


@check(
    id="cjk_not_enough_glyphs",
    conditions=["is_claiming_to_be_cjk_font"],
    rationale="""
        Kana has 150 characters and it's the smallest CJK writing system.

        If a font contains less CJK glyphs than this writing system, we inform the
        user that some glyphs may be encoded incorrectly.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3214",
)
def check_cjk_not_enough_glyphs(font):
    """Any CJK font should contain at least a minimal set of 150 CJK characters."""

    cjk_glyphs = font.get_cjk_glyphs
    cjk_glyph_count = len(cjk_glyphs)
    if cjk_glyph_count > 0 and cjk_glyph_count < 150:
        if cjk_glyph_count == 1:
            num_CJK_glyphs = "There is only one CJK glyph"
        else:
            num_CJK_glyphs = f"There are only {cjk_glyph_count} CJK glyphs"

        yield WARN, Message(
            "cjk-not-enough-glyphs",
            f"{num_CJK_glyphs} when there needs to be at least 150"
            f" in order to support the smallest CJK writing system, Kana.\n"
            f"The following CJK glyphs were found:\n"
            f"{cjk_glyphs}\n"
            f"Please check that these glyphs have the correct unicodes.",
        )
