from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("sfnt_version")
def test_check_sfnt_version(check):
    """Ensure that the font has the proper sfntVersion value."""

    # Valid TrueType font; the check must PASS.
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    # Change the sfntVersion to an improper value for TrueType fonts.
    # The check should FAIL.
    ttFont.sfntVersion = "OTTO"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-ttf")
    assert msg == "Font with TrueType outlines has incorrect sfntVersion value: 'OTTO'"

    # Valid CFF font; the check must PASS.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    assert_PASS(check(ttFont))

    # Change the sfntVersion to an improper value for CFF fonts. The check should FAIL.
    ttFont.sfntVersion = "\x00\x01\x00\x00"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-cff")
    assert msg == (
        "Font with CFF data has incorrect sfntVersion value: '\x00\x01\x00\x00'"
    )

    # Valid CFF2 font; the check must PASS.
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    assert_PASS(check(ttFont))

    # Change the sfntVersion to an improper value for CFF fonts. The check should FAIL.
    ttFont.sfntVersion = "\x00\x01\x00\x00"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-cff")
    assert msg == (
        "Font with CFF data has incorrect sfntVersion value: '\x00\x01\x00\x00'"
    )
