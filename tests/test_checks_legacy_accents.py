from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("legacy_accents")
def test_check_legacy_accents(check):
    """Check that legacy accents aren't used in composite glyphs."""

    test_font = TTFont(TEST_FILE("montserrat/Montserrat-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_results_contain(
        check(test_font),
        FAIL,
        "legacy-accents-gdef",
        "for legacy accents being defined in GDEF as marks.",
    )

    test_font = TTFont(TEST_FILE("lugrasimo/Lugrasimo-Regular.ttf"))
    assert_results_contain(
        check(test_font),
        FAIL,
        "legacy-accents-width",
        "for legacy accents having zero width.",
    )
