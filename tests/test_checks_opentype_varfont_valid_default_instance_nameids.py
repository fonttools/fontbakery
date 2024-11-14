from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/varfont/valid_default_instance_nameids")
def test_check_varfont_valid_default_instance_nameids(check):
    """If an instance record is included for the default instance, then the instance's
    subfamilyName string should match the string of nameID 2 or nameID 17, and the
    instance's postScriptName string should match the string of nameID 6."""

    # The font's 'Regular' instance record has the same coordinates as the default
    # instance, and the record's string matches the string of nameID 2.
    ttFont_1 = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont_1))

    # The font's 'LightCondensed' instance record has the same coordinates as the
    # default instance, and the record's string matches the string of nameID 17.
    ttFont_2 = TTFont(TEST_FILE("mutatorsans-vf/MutatorSans-VF.ttf"))
    assert_PASS(check(ttFont_2))

    # Change subfamilyNameID value of the default instance to another name ID whose
    # string doesn't match the font's Subfamily name, thus making the check fail.
    fvar_table_1 = ttFont_1["fvar"]
    dflt_inst = fvar_table_1.instances[0]
    dflt_inst.subfamilyNameID = 16  # the font doesn't have this record
    msg = assert_results_contain(
        check(ttFont_1), FAIL, "invalid-default-instance-subfamily-name"
    )
    assert (
        "'Instance #1' instance has the same coordinates as the default"
        " instance; its subfamily name should be 'Regular'"
    ) in msg
    # Restore the original ID
    dflt_inst.subfamilyNameID = 258

    fvar_table_2 = ttFont_2["fvar"]
    dflt_inst = fvar_table_2.instances[0]
    dflt_inst.subfamilyNameID = 16
    msg = assert_results_contain(
        check(ttFont_2), FAIL, "invalid-default-instance-subfamily-name"
    )
    assert (
        "'MutatorMathTest' instance has the same coordinates as the default"
        " instance; its subfamily name should be 'LightCondensed'"
    ) in msg
    # Restore the original ID
    dflt_inst.subfamilyNameID = 258

    # The value of postScriptNameID is 0xFFFF for all the instance records in CabinVF.
    # Change one of them, to make the check validate the postScriptNameID value of the
    # default instance (which is currently 0xFFFF).
    inst_2 = fvar_table_1.instances[1]
    inst_2.postscriptNameID = 256  # the font doesn't have this record
    msg = assert_results_contain(
        check(ttFont_1), FAIL, "invalid-default-instance-postscript-name"
    )
    assert (
        "'Regular' instance has the same coordinates as the default instance;"
        " its postscript name should be 'Cabin-Regular', instead of 'None'."
    ) in msg

    # The default instance of MutatorSans-VF has the correct postScriptNameID.
    # Change it to make the check fail.
    inst_1 = fvar_table_2.instances[0]
    inst_1.postscriptNameID = 261
    msg = assert_results_contain(
        check(ttFont_2), FAIL, "invalid-default-instance-postscript-name"
    )
    assert (
        "'LightCondensed' instance has the same coordinates as the default instance;"
        " its postscript name should be 'MutatorMathTest-LightCondensed',"
        " instead of 'MutatorMathTest-BoldCondensed'."
    ) in msg

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont_1["name"]
    assert_results_contain(check(ttFont_1), FAIL, "lacks-table")
