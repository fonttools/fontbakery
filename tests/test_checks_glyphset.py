from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    portable_path,
    TEST_FILE,
)
from fontbakery.status import FAIL
from fontbakery.utils import can_shape, remove_cmap_entry


def test_can_shape():
    font = TTFont(
        portable_path("data/test/source-sans-pro/OTF/SourceSansPro-Regular.otf")
    )
    assert can_shape(font, "ABC")
    assert not can_shape(font, "こんにちは")


@check_id("control_chars")
def test_check_family_control_chars(check):
    """Are any unacceptable control characters present in font files?"""

    good_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCGood-Regular.ttf"
    )
    bad_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCOneBad-Regular.ttf"
    )

    # No unacceptable control characters should pass
    assert_PASS(check(good_font), "with a good font...")

    # Unacceptable control chars should fail
    assert_results_contain(
        check(bad_font),
        FAIL,
        "unacceptable",
        "with a bad font that has one bad char...",
    )


@check_id("whitespace_glyphs")
def test_check_whitespace_glyphs(check):
    """Font contains glyphs for whitespace characters?"""

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # We remove the nbsp char (0x00A0)
    remove_cmap_entry(ttFont, 0x00A0)

    # And make sure the problem is detected:
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x00A0",
        "with a font lacking a nbsp (0x00A0)...",
    )

    # restore original Mada Regular font:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # And finally do the same with the space character (0x0020):
    remove_cmap_entry(ttFont, 0x0020)
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x0020",
        "with a font lacking a space (0x0020)...",
    )
