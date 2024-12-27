from conftest import check_id
from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)
from fontbakery.status import FAIL, SKIP


@check_id("varfont/bold_wght_coord")
def test_check_varfont_bold_wght_coord(check):
    """The variable font 'wght' (Weight) axis coordinate
    must be 700 on the 'Bold' instance."""

    # Our reference varfont CabinVFBeta.ttf
    # has a good Bold:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont), "with a good Bold:wght coordinate...")

    # We then change the value to ensure the problem is properly detected by the check:
    ttFont["fvar"].instances[3].coordinates["wght"] = 600
    assert_results_contain(
        check(ttFont), FAIL, "wght-not-700", "with a bad Bold:wght coordinage (600)..."
    )

    # Check we skip when we don't have a 700 weight.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    del ttFont["fvar"].instances[3]
    ttFont["fvar"].axes[0].maxValue = 600
    assert_results_contain(check(ttFont), SKIP, "no-bold-weight")
