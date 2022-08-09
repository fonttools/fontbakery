from fontTools.ttLib import TTFont

from fontbakery.checkrunner import FAIL, SKIP
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

    # And now the problem should be detected:
    msg = assert_results_contain(check(ttFont), FAIL, "missing-axis-records")
    assert msg == (
        "STAT table is missing Axis Records for the following axes:\n\n\t- wdth"
    )

    # Now use a stactic font.
    # The check should be skipped due to an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Black.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: is_variable_font"


def test_check_stat_has_axis_value_tables():
    """Check the STAT table has at least one Axis Value table."""
    check = CheckTester(
        opentype_profile,
        "com.adobe.fonts/check/stat_has_axis_value_tables",
    )

    # Our reference Cabin[wdth,wght].ttf variable font has Axis Value tables.
    # So the check must PASS.
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "STAT table has Axis Value tables."

    # Remove the 4th Axis Value table (index 3), belonging to 'Medium' weight.
    # The check should FAIL.
    ttFont["STAT"].table.AxisValueArray.AxisValue.pop(3)
    msg = assert_results_contain(check(ttFont), FAIL, "missing-axis-value-table")
    assert msg == "STAT table is missing Axis Value for 'wght' value '500.0'"

    # Now remove all Axis Value tables by emptying the AxisValueArray.
    # The check should FAIL.
    ttFont["STAT"].table.AxisValueArray = None
    ttFont["STAT"].table.AxisValueCount = 0
    msg = assert_results_contain(check(ttFont), FAIL, "no-axis-value-tables")
    assert msg == "STAT table has no Axis Value tables."

    # Most of the Axis Value tables in Cabin[wdth,wght].ttf are format 1.
    # Now test with SourceSansVariable-Italic.ttf whose tables are mostly format 2.
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.ttf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "STAT table has Axis Value tables."

    # Remove the 2nd Axis Value table (index 1), belonging to 'Light' weight.
    # The check should FAIL.
    ttFont["STAT"].table.AxisValueArray.AxisValue.pop(1)
    msg = assert_results_contain(check(ttFont), FAIL, "missing-axis-value-table")
    assert msg == "STAT table is missing Axis Value for 'wght' value '300.0'"

    # Now use a font that has no STAT table.
    # The check should be skipped due to an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Black.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: has_STAT_table"
