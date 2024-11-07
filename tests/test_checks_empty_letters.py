from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL, WARN


@check_id("empty_letters")
def test_check_empty_letters(check):
    """Validate that empty glyphs are found."""

    # this OT-CFF font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

    # this OT-CFF2 font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    assert_PASS(check(ttFont))

    # this TrueType font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Bold.ttf"))
    assert_PASS(check(ttFont))

    # Add 2 Korean hangul syllable characters to cmap table mapped to the 'space' glyph.
    # These characters are part of the set whose glyphs are allowed to be blank.
    # The check should only yield a WARN.
    for cmap_table in ttFont["cmap"].tables:
        if cmap_table.format != 4:
            cmap_table.cmap[0xB646] = "space"
            cmap_table.cmap[0xD7A0] = "space"
    msg = assert_results_contain(check(ttFont), WARN, "empty-hangul-letter")
    assert msg == "Found 2 empty hangul glyph(s)."

    # this font has empty glyphs for several letters,
    # the first of which is 'B' (U+0042)
    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "empty-letter")
    assert msg == "U+0042 should be visible, but its glyph ('B') is empty."
