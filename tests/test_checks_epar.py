from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import INFO


@check_id("epar")
def test_check_epar(check):
    """EPAR table present in font?"""

    # Our reference Mada Regular lacks an EPAR table:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must emit an INFO message inviting the designers
    # to learn more about it:
    assert_results_contain(
        check(ttFont), INFO, "lacks-EPAR", "with a font lacking an EPAR table..."
    )

    # add a fake EPAR table to validate the PASS code-path:
    ttFont["EPAR"] = "foo"
    assert_PASS(check(ttFont), "with a good font...")
