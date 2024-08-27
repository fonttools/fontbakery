from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.status import FAIL


def test_check_glyf_nested_components():
    """Ensure glyphs do not have components which are themselves components."""
    check = CheckTester("glyf_nested_components")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # We need to create a nested component. "second" has components, so setting
    # one of "quotedbl"'s components to "second" should do it.
    ttFont["glyf"]["quotedbl"].components[0].glyphName = "second"

    assert_results_contain(check(ttFont), FAIL, "found-nested-components")
