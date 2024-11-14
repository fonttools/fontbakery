from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)


@check_id("opentype/varfont/same_size_instance_records")
def test_check_varfont_same_size_instance_records(check):
    """All of the instance records in a given font must have the same size,
    with all either including or omitting the postScriptNameID field. If the value
    is 0xFFFF it means that no PostScript name is provided for the instance."""

    # The value of postScriptNameID is 0xFFFF for all the instance records in the
    # reference varfont
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    fvar_table = ttFont["fvar"]
    inst_1 = fvar_table.instances[0]
    inst_2 = fvar_table.instances[1]
    inst_3 = fvar_table.instances[2]
    inst_4 = fvar_table.instances[3]

    # Change the postScriptNameID of one instance record
    inst_1.postscriptNameID = 256
    msg = assert_results_contain(check(ttFont), FAIL, "different-size-instance-records")
    assert msg == "Instance records don't all have the same size."

    # Change the postScriptNameID of the remaining instance records
    inst_2.postscriptNameID = 356
    inst_3.postscriptNameID = 456
    inst_4.postscriptNameID = 556
    assert_PASS(check(ttFont), "with a good varfont...")

    # Change the postScriptNameID of two instance records
    inst_1.postscriptNameID = 0xFFFF
    inst_3.postscriptNameID = 0xFFFF
    msg = assert_results_contain(check(ttFont), FAIL, "different-size-instance-records")
    assert msg == "Instance records don't all have the same size."

    fvar_table.instances = []
    msg = assert_results_contain(check(ttFont), SKIP, "no-instance-records")
    assert msg == "Font has no instance records."
