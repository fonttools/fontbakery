from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    TEST_FILE,
    assert_PASS,
    assert_results_contain,
)
from fontbakery.status import WARN


@check_id("no_debugging_tables")
def test_check_no_debugging_tables(check):
    """Ensure fonts do not contain any preproduction tables."""

    ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "has-debugging-tables")

    del ttFont["FFTM"]
    assert_PASS(check(ttFont))
