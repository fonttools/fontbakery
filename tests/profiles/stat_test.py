from fontTools.ttLib import TTFont

from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles import opentype as opentype_profile


def test_check_varfont_stat_axis_record_for_each_axis():
    """Check the STAT table has an Axis Record for every axis in the font."""
    check = CheckTester(
        opentype_profile,
        "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    )

    # Our reference Cabin[wdth,wght].ttf variable font
    # has all necessary Axis Records
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # So the check must PASS
    msg = assert_PASS(check(ttFont))
    assert msg == "STAT table has all necessary Axis Records."

    # We then remove its first Axis Record (`wdth`):
    ttFont["STAT"].table.DesignAxisRecord.Axis.pop(0)

    # And now the problem should be detected::
    msg = assert_results_contain(check(ttFont), FAIL, "missing-axis-records")
    assert msg == (
        f"STAT table is missing Axis Records for the following axes:\n\n\t- wdth"
    )
