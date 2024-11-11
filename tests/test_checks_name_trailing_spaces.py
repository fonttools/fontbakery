from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("name/trailing_spaces")
def test_check_name_trailing_spaces(check):
    """Name table entries must not have trailing spaces."""

    # Our reference Cabin Regular is known to be good:
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    for i, entry in enumerate(ttFont["name"].names):
        good_string = ttFont["name"].names[i].toUnicode()
        bad_string = good_string + " "
        ttFont["name"].names[i].string = bad_string.encode(entry.getEncoding())
        assert_results_contain(
            check(ttFont),
            FAIL,
            "trailing-space",
            f'with a bad name table entry ({i}: "{bad_string}")...',
        )

        # restore good entry before moving to the next one:
        ttFont["name"].names[i].string = good_string.encode(entry.getEncoding())
