from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)


@check_id("opentype/varfont/foundry_defined_tag_name")
def test_check_varfont_foundry_defined_tag_name(check):
    "Validate foundry-defined design-variation axis tag names."

    # Our reference varfont CabinVFBeta.ttf has registered tags.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    ttFont["fvar"].axes[0].axisTag = "GOOD"
    assert_PASS(check(ttFont), "with a good all uppercase axis tag...")

    ttFont["fvar"].axes[0].axisTag = "G009"
    assert_PASS(check(ttFont), "with all uppercase + digits...")

    ttFont["fvar"].axes[0].axisTag = "ITAL"
    assert_results_contain(
        check(ttFont),
        WARN,
        "foundry-defined-similar-registered-name",
        "with an uppercase version of registered tag...",
    )

    ttFont["fvar"].axes[0].axisTag = "nope"
    assert_results_contain(
        check(ttFont),
        FAIL,
        "invalid-foundry-defined-tag-first-letter",
        "when first letter of axis tag is not uppercase...",
    )

    ttFont["fvar"].axes[0].axisTag = "N0pe"
    assert_results_contain(
        check(ttFont),
        FAIL,
        "invalid-foundry-defined-tag-chars",
        "when characters not all uppercase-letters or digits...",
    )
