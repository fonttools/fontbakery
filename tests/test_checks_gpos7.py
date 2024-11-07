from conftest import check_id
from fontbakery.status import WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("gpos7")
def test_check_gpos7(check):
    """Check if font contains any GPOS 7 lookups which are not widely supported."""

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("notosanskhudawadi/NotoSansKhudawadi-Regular.ttf")
    assert_results_contain(check(font), WARN, "has-gpos7")
