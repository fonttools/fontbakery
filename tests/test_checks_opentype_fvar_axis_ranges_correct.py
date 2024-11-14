from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)


@check_id("opentype/fvar/axis_ranges_correct")
def test_check_varfont_wght_valid_range(check):
    """The variable font 'wght' (Weight) axis coordinate
    must be within spec range of 1 to 1000 on all instances."""
    # Our reference varfont CabinVFBeta.ttf
    # has all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    # We then introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 0
    assert_results_contain(check(ttFont), FAIL, "wght-out-of-range", "with wght=0...")

    # And yet another bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 1001
    assert_results_contain(
        check(ttFont), FAIL, "wght-out-of-range", "with wght=1001..."
    )


@check_id("opentype/fvar/axis_ranges_correct")
def test_check_varfont_wdth_valid_range(check):
    """The variable font 'wdth' (Width) axis coordinate
    must be strictly greater than zero, per the spec."""
    # Our reference varfont CabinVFBeta.ttf
    # has all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    # We then introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0
    assert_results_contain(check(ttFont), FAIL, "wdth-out-of-range", "with wght=0...")

    # A valid but unusual value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 1001
    assert_results_contain(
        check(ttFont), WARN, "wdth-greater-than-1000", "with wght=1001..."
    )


@check_id("opentype/fvar/axis_ranges_correct")
def test_check_varfont_slnt_range(check):
    """The variable font 'slnt' (Slant) axis coordinate
    specifies positive values in its range?"""
    # Our reference Inter varfont has a bad slnt range
    ttFont = TTFont("data/test/varfont/inter/Inter[slnt,wght].ttf")
    assert_results_contain(
        check(ttFont),
        WARN,
        "unusual-slnt-range",
        'with a varfont that has an unusual "slnt" range.',
    )

    # We then fix the font-bug by flipping the slnt axis range:
    for i, axis in enumerate(ttFont["fvar"].axes):
        if axis.axisTag == "slnt":
            minValue, maxValue = axis.minValue, axis.maxValue
            ttFont["fvar"].axes[i].minValue = -maxValue
            ttFont["fvar"].axes[i].maxValue = -minValue

    # And it must now be good ;-)
    assert_PASS(check(ttFont))
