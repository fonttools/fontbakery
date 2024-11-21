from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL, SKIP


@check_id("inconsistencies_between_fvar_STAT")
def test_check_inconsistencies_between_fvar_STAT(check):
    """Checking if STAT entries matches fvar and vice versa."""

    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont), "with a good varfont...")

    ttFont = TTFont(TEST_FILE("bad_fonts/fvar_STAT_differences/AxisLocationVAR.ttf"))
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


@check_id("STAT_in_statics")
def test_check_STAT_in_statics(check):
    """Checking STAT table on static fonts."""

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: has_STAT_table" in msg

    ttFont = TTFont(TEST_FILE("varfont/RobotoSerif[GRAD,opsz,wdth,wght].ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg

    # Remove fvar table to make FontBakery think it is dealing with a static font
    del ttFont["fvar"]

    # We know that our reference RobotoSerif varfont (which the check is induced
    # here to think it is a static font) has multiple records per design axis in its
    # STAT table:
    msg = assert_results_contain(check(ttFont), FAIL, "multiple-STAT-entries")
    assert "The STAT table has more than a single entry for the 'opsz' axis (5)" in msg

    # Remove all entries except the very first one:
    STAT_table = ttFont["STAT"].table
    STAT_table.AxisValueArray.AxisCount = 1
    STAT_table.AxisValueArray.AxisValue = [STAT_table.AxisValueArray.AxisValue[0]]

    # It should PASS now
    assert_PASS(check(ttFont))


@check_id("STAT_strings")
def test_check_STAT_strings(check):
    """Check correctness of STAT table strings"""

    good = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(good))

    bad = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Italic.ttf"))
    assert_results_contain(check(bad), FAIL, "bad-italic")
