from conftest import check_id

#  from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    #    assert_results_contain,
    TEST_FILE,
)


@check_id("ttx_roundtrip")
def test_check_ttx_roundtrip(check):
    """Checking with fontTools.ttx"""

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font))

    # TODO: Can anyone show us a font file that fails ttx roundtripping?!
    #
    # font = TEST_FILE("...")
    # assert_results_contain(check(font),
    #                        FAIL, None) # FIXME: This needs a message keyword
