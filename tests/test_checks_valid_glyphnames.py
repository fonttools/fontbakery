import io

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN, FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
)


@check_id("valid_glyphnames")
def test_check_valid_glyphnames(check):
    """Glyph names are all valid?"""

    # We start with a good font file:
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # There used to be a 31 char max-length limit.
    # This was considered good:
    ttFont.glyphOrder[2] = "a" * 31
    assert_PASS(check(ttFont))

    # And this was considered bad:
    legacy_too_long = "a" * 32
    ttFont.glyphOrder[2] = legacy_too_long
    message = assert_results_contain(check(ttFont), WARN, "legacy-long-names")
    assert legacy_too_long in message

    # Nowadays, it seems most implementations can deal with
    # up to 63 char glyph names:
    good_name1 = "b" * 63
    # colr font may have a color layer in .notdef so allow these layers
    good_name2 = ".notdef.color0"
    bad_name1 = "a" * 64
    bad_name2 = "3cents"
    bad_name3 = ".threecents"
    ttFont.glyphOrder[2] = bad_name1
    ttFont.glyphOrder[3] = bad_name2
    ttFont.glyphOrder[4] = bad_name3
    ttFont.glyphOrder[5] = good_name1
    ttFont.glyphOrder[6] = good_name2
    message = assert_results_contain(check(ttFont), FAIL, "found-invalid-names")
    assert good_name1 not in message
    assert good_name2 not in message
    assert bad_name1 in message
    assert bad_name2 in message
    assert bad_name3 in message

    # TrueType fonts with a format 3 post table contain
    # no glyph names, so the check must be SKIP'd in that case.
    #
    # Upgrade to post format 3 and roundtrip data to update TTF object.
    ttf_skip_msg = "TrueType fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
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
