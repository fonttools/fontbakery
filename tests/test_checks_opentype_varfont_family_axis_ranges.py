from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, SKIP
from fontbakery.checks.opentype.slant_direction import REFERENCE
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/varfont/family_axis_ranges")
def test_check_varfont_family_axis_ranges(check):
    """Check that family axis ranges are indentical"""

    ttFonts = [
        TTFont("data/test/ubuntusansmono/UbuntuMono[wght].ttf"),
        TTFont("data/test/ubuntusansmono/UbuntuMono-Italic[wght].ttf"),
    ]
    assert_results_contain(check(ttFonts), FAIL, "axis-range-mismatch")

    ttFonts = [
        TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf"),
        TTFont("data/test/cabinvf/Cabin-Italic[wdth,wght].ttf"),
    ]
    assert_PASS(check(ttFonts), "with good varfont...")


@check_id("opentype/slant_direction")
def test_check_slant_direction(check):
    """Checking direction of slnt axis angles."""

    font = TEST_FILE("slant_direction/Cairo_correct_slnt_axis.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("slant_direction/Cairo_wrong_slnt_axis.ttf")
    assert_results_contain(check(font), FAIL, "positive-value-for-clockwise-lean")


@check_id("opentype/slant_direction")
def test_check_slant_direction_missing(check, tmp_path):
    """Check that the slant direction check handles the case where its reference
    codepoint is not present."""

    missing_codepoint = tmp_path / "MissingCodepoint.ttf"

    # Remove the reference codepoint from a TTF that would otherwise PASS.
    ttf = TTFont(TEST_FILE("slant_direction/Cairo_correct_slnt_axis.ttf"), lazy=False)
    for subtable in ttf["cmap"].tables:
        subtable.cmap.pop(ord(REFERENCE), None)
    ttf.save(missing_codepoint)

    assert_results_contain(check(str(missing_codepoint)), SKIP, "no-reference-glyph")
