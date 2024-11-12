from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import glyph_has_ink


@check(
    id="mandatory_glyphs",
    rationale="""
        The OpenType specification v1.8.2 recommends that the first glyph is the
        '.notdef' glyph without a codepoint assigned and with a drawing:

        The .notdef glyph is very important for providing the user feedback
        that a glyph is not found in the font. This glyph should not be left
        without an outline as the user will only see what looks like a space
        if a glyph is missing and not be aware of the active font’s limitation.

        https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph

        Pre-v1.8, it was recommended that fonts should also contain 'space', 'CR'
        and '.null' glyphs. This might have been relevant for MacOS 9 applications.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_mandatory_glyphs(ttFont):
    """Font contains '.notdef' as its first glyph?"""
    NOTDEF = ".notdef"
    glyph_order = ttFont.getGlyphOrder()

    if NOTDEF not in glyph_order or len(glyph_order) == 0:
        yield WARN, Message(
            "notdef-not-found", f"Font should contain the {NOTDEF!r} glyph."
        )
        # The font doesn't even have the notdef. There's no point in testing further.
        return

    if glyph_order[0] != NOTDEF:
        yield WARN, Message(
            "notdef-not-first", f"The {NOTDEF!r} should be the font's first glyph."
        )

    cmap = ttFont.getBestCmap()  # e.g. {65: 'A', 66: 'B', 67: 'C'} or None
    if cmap and NOTDEF in cmap.values():
        rev_cmap = {name: val for val, name in reversed(sorted(cmap.items()))}
        yield WARN, Message(
            "notdef-has-codepoint",
            f"The {NOTDEF!r} glyph should not have a Unicode codepoint value assigned,"
            f" but has 0x{rev_cmap[NOTDEF]:04X}.",
        )

    if not glyph_has_ink(ttFont, NOTDEF):
        yield FAIL, Message(
            "notdef-is-blank",
            f"The {NOTDEF!r} glyph should contain a drawing, but it is blank.",
        )
