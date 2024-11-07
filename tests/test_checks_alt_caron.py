from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("alt_caron")
def test_check_alt_caron(check):
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""

    ttFont = TTFont(TEST_FILE("annie/AnnieUseYourTelescope-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "bad-mark")
    assert_results_contain(check(ttFont), FAIL, "wrong-mark")

    ttFont = TTFont(TEST_FILE("cousine/Cousine-Bold.ttf"))
    assert_results_contain(check(ttFont), WARN, "decomposed-outline")

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont))
