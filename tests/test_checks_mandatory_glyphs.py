from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN, FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("mandatory_glyphs")
def test_check_mandatory_glyphs(check):
    """Font contains the first few mandatory glyphs (.null or NULL, CR and space)?"""
    from fontTools import subset

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    options = subset.Options()
    options.glyph_names = True  # Preserve glyph names
    # By default, the subsetter keeps the '.notdef' glyph but removes its outlines
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="mn")  # Arbitrarily remove everything except 'm' and 'n'
    subsetter.subset(ttFont)
    message = assert_results_contain(check(ttFont), FAIL, "notdef-is-blank")
    assert message == "The '.notdef' glyph should contain a drawing, but it is blank."

    options.notdef_glyph = False  # Drop '.notdef' glyph
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="mn")
    subsetter.subset(ttFont)
    message = assert_results_contain(check(ttFont), WARN, "notdef-not-found")
    assert message == "Font should contain the '.notdef' glyph."

    # Change the glyph name from 'n' to '.notdef'
    # (Must reload the font here since we already decompiled the glyf table)
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.glyphOrder = ["m", ".notdef"]
    for subtable in ttFont["cmap"].tables:
        if subtable.isUnicode():
            subtable.cmap[110] = ".notdef"
            if 0 in subtable.cmap:
                del subtable.cmap[0]
    results = check(ttFont)
    message = assert_results_contain([results[0]], WARN, "notdef-not-first")
    assert message == "The '.notdef' should be the font's first glyph."

    message = assert_results_contain([results[1]], WARN, "notdef-has-codepoint")
    assert message == (
        "The '.notdef' glyph should not have a Unicode codepoint value assigned,"
        " but has 0x006E."
    )
