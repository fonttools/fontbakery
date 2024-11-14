from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)


@check_id("opentype/varfont/distinct_instance_records")
def test_check_varfont_distinct_instance_records(check):
    """All of the instance records in a font should have distinct coordinates
    and distinct subfamilyNameID and postScriptName ID values."""

    # All of the instance records in the reference varfont are unique
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    fvar_table = ttFont["fvar"]
    inst_1 = fvar_table.instances[0]
    inst_2 = fvar_table.instances[1]
    inst_3 = fvar_table.instances[2]
    inst_4 = fvar_table.instances[3]

    # Make instance 2 the same as instance 1
    inst_2.subfamilyNameID = inst_1.subfamilyNameID
    inst_2.coordinates["wght"] = inst_1.coordinates["wght"]
    msg = assert_results_contain(
        check(ttFont), WARN, "repeated-instance-record:Regular"
    )
    assert msg == "'Regular' is a repeated instance record."

    # Make instance 4 the same as instance 3
    inst_4.subfamilyNameID = inst_3.subfamilyNameID
    inst_4.coordinates["wght"] = inst_3.coordinates["wght"]
    msg = assert_results_contain(
        check(ttFont), WARN, "repeated-instance-record:SemiBold"
    )
    assert msg == "'SemiBold' is a repeated instance record."

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont["name"]
    assert_results_contain(check(ttFont), FAIL, "lacks-table")
