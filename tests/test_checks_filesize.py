from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.profiles import googlefonts
from fontbakery.status import FAIL, WARN


# This needs a profile to inject configuration data
@check_id("file_size", profile=googlefonts)
def test_check_file_size(check):
    """Ensure files are not too large."""

    assert_PASS(check(TEST_FILE("mada/Mada-Regular.ttf")))

    assert_results_contain(
        check(TEST_FILE("varfont/inter/Inter[slnt,wght].ttf")),
        WARN,
        "large-font",
        "with quite a big font...",
    )

    assert_results_contain(
        check(TEST_FILE("cjk/SourceHanSans-Regular.otf")),
        FAIL,
        "massive-font",
        "with a very big font...",
    )
