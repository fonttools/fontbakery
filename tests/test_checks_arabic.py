from fontTools.ttLib import TTFont

from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_allah_ligature():
    """Ensure correct formation of allah ligature in the presence of tashkeel marks."""
    check = CheckTester("allah_ligature")

    # font has no allah ligature
    ttFont = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_SKIP(check(ttFont))

    # allah ligature is present but generally unused
    ttFont = TTFont(TEST_FILE("fustat/Fustat[wght].ttf"))
    assert_PASS(check(ttFont))

    # classic mistake: tashkeel are placed on top of the allah ligature, colliding
    ttFont = TTFont(TEST_FILE("ibmplexsansarabic_v1_004/IBMPlexSansArabic-Regular.ttf"))
    assert_results_contain(check(ttFont), FAIL, "wrong-allah-with-tashkeel")

    # ligature is present and generally used, and correctly formed with tashkeel
    ttFont = TTFont(TEST_FILE("ibmplexsansarabic_v1_005/IBMPlexSansArabic-Regular.ttf"))
    assert_PASS(check(ttFont))
