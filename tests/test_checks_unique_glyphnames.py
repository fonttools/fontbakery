import io

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
)


@check_id("unique_glyphnames")
def test_check_unique_glyphnames(check):
    """Font contains unique glyph names?"""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # Fonttools renames duplicate glyphs with #1, #2, ... on load.
    # Code snippet from https://github.com/fonttools/fonttools/issues/149
    glyph_names = ttFont.getGlyphOrder()
    glyph_names[2] = glyph_names[3]

    # Load again, we changed the font directly.
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    # Just access the data to make fonttools generate it.
    ttFont["post"]  # pylint:disable=pointless-statement
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_results_contain(check(ttFont), FAIL, "duplicated-glyph-names")
    assert "space" in message

    # Upgrade to post format 3 and roundtrip data to update TTF object.
    ttf_skip_msg = "TrueType fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    ttFont["post"].formatType = 3
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_SKIP(check(ttFont))
    assert ttf_skip_msg in message

    # Also test with CFF...
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

    # ... and CFF2 fonts
    cff2_skip_msg = "OpenType-CFF2 fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    message = assert_SKIP(check(ttFont))
    assert cff2_skip_msg in message
