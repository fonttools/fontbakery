from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("transformed_components")
def test_check_transformed_components(check):
    """Ensure component transforms do not perform scaling or rotation."""

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    # DM Sans v1.100 had some transformed components
    # and it's hinted
    font = TEST_FILE("dm-sans-v1.100/DMSans-Regular.ttf")
    assert_results_contain(check(font), FAIL, "transformed-components")

    # Amiri is unhinted, but it contains four transformed components
    # that result in reversed outline direction
    font = TEST_FILE("amiri/AmiriQuranColored.ttf")
    assert_results_contain(check(font), FAIL, "transformed-components")
