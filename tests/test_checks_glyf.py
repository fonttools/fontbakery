from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL


@check_id("nested_components")
def test_check_nested_components(check):
    """Ensure glyphs do not have components which are themselves components."""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # We need to create a nested component. "second" has components, so setting
    # one of "quotedbl"'s components to "second" should do it.
    ttFont["glyf"]["quotedbl"].components[0].glyphName = "second"

    assert_results_contain(check(ttFont), FAIL, "found-nested-components")
