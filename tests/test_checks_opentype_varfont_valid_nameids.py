from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
)


@check_id("opentype/varfont/valid_nameids")
def test_check_varfont_valid_nameids(check):
    ####
    # The value of axisNameID used by each VariationAxisRecord must
    # be greater than 255 and less than 32768.

    # The axisNameID values in the reference varfont are all valid
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    fvar_table = ttFont["fvar"]
    wght_axis = fvar_table.axes[0]
    wdth_axis = fvar_table.axes[1]

    # Change the axes' axisNameID to the maximum and minimum allowed values
    wght_axis.axisNameID = 32767
    wdth_axis.axisNameID = 256
    assert_PASS(check(ttFont), "with a good varfont...")

    # Change the axes' axisNameID to invalid values
    # (32768 is greater than the maximum, and 255 is less than the minimum)
    wght_axis.axisNameID = 32768
    assert_results_contain(check(ttFont), FAIL, "invalid-axis-nameid:32768")

    wdth_axis.axisNameID = 255
    assert_results_contain(check(ttFont), FAIL, "invalid-axis-nameid:255")

    # Another set of invalid values
    wght_axis.axisNameID = 128
    assert_results_contain(check(ttFont), FAIL, "invalid-axis-nameid:128")

    wdth_axis.axisNameID = 36000
    assert_results_contain(check(ttFont), FAIL, "invalid-axis-nameid:36000")

    ####
    # The value of postScriptNameID used by each InstanceRecord must
    # be 6, 0xFFFF, or greater than 255 and less than 32768.

    # The postScriptNameID values in the reference varfont are all valid
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    fvar_table = ttFont["fvar"]
    inst_1 = fvar_table.instances[0]
    inst_2 = fvar_table.instances[1]
    inst_3 = fvar_table.instances[2]
    inst_4 = fvar_table.instances[3]

    # Change the instances' postScriptNameID to
    # 6, 0xFFFF and to the maximum and minimum allowed values
    inst_1.postscriptNameID = 6
    inst_2.postscriptNameID = 0xFFFF
    inst_3.postscriptNameID = 256
    inst_4.postscriptNameID = 32767
    assert_PASS(check(ttFont), "with a good varfont...")

    # Change two instances' postScriptNameID to invalid values
    # (32768 is greater than the maximum, and 255 is less than the minimum)
    inst_3.postscriptNameID = 255
    assert_results_contain(check(ttFont), FAIL, "invalid-postscript-nameid:255")

    inst_4.postscriptNameID = 32768
    assert_results_contain(check(ttFont), FAIL, "invalid-postscript-nameid:32768")

    # Reset two postScriptNameID to valid values,
    # then set two other postScriptNameID to invalid values
    inst_3.postscriptNameID = 256  # valid
    inst_4.postscriptNameID = 32767  # valid
    inst_1.postscriptNameID = 3
    assert_results_contain(check(ttFont), FAIL, "invalid-postscript-nameid:3")

    inst_2.postscriptNameID = 18
    assert_results_contain(check(ttFont), FAIL, "invalid-postscript-nameid:18")

    ####
    # The value of subfamilyNameID used by each InstanceRecord must
    # be 2, 17, or greater than 255 and less than 32768.

    # The subfamilyNameID values in the reference varfont are all valid
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(ttFont), "with a good varfont...")

    fvar_table = ttFont["fvar"]
    inst_1 = fvar_table.instances[0]
    inst_2 = fvar_table.instances[1]
    inst_3 = fvar_table.instances[2]
    inst_4 = fvar_table.instances[3]

    # Change the instances' subfamilyNameID to
    # 2, 17 and to the maximum and minimum allowed values
    inst_1.subfamilyNameID = 2
    inst_2.subfamilyNameID = 17
    inst_3.subfamilyNameID = 256
    inst_4.subfamilyNameID = 32767
    assert_PASS(check(ttFont), "with a good varfont...")

    # Change two instances' subfamilyNameID to invalid values
    # (32768 is greater than the maximum, and 255 is less than the minimum)
    inst_3.subfamilyNameID = 255
    assert_results_contain(check(ttFont), FAIL, "invalid-subfamily-nameid:255")

    inst_4.subfamilyNameID = 32768
    assert_results_contain(check(ttFont), FAIL, "invalid-subfamily-nameid:32768")

    # Reset two subfamilyNameID to valid values,
    # then set two other subfamilyNameID to invalid values
    inst_3.subfamilyNameID = 256  # valid
    inst_4.subfamilyNameID = 32767  # valid
    inst_1.subfamilyNameID = 3
    assert_results_contain(check(ttFont), FAIL, "invalid-subfamily-nameid:3")

    inst_2.subfamilyNameID = 18
    assert_results_contain(check(ttFont), FAIL, "invalid-subfamily-nameid:18")
