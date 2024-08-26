from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.status import FAIL


def test_check_inconsistencies_between_fvar_stat():
    check = CheckTester("inconsistencies_between_fvar_stat")

    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont), "with a good varfont...")

    ttFont = TTFont(TEST_FILE("bad_fonts/fvar_stat_differences/AxisLocationVAR.ttf"))
    ttFont["name"].removeNames(nameID=277)
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-name-id",
        "fvar instance is missing in the name table",
    )

    # add name with wrong order of name parts
    ttFont["name"].setName("Medium Text", 277, 3, 1, 0x409)
    assert_results_contain(
        check(ttFont), FAIL, "missing-fvar-instance-axis-value", "missing in STAT table"
    )
