from copy import copy

import pytest
from conftest import check_id
from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.constants import (
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)
from fontbakery.status import FAIL


@pytest.fixture
def vf_ttFont():
    path = TEST_FILE("varfont/Oswald-VF.ttf")
    return TTFont(path)


@check_id("varfont/duplicate_instance_names")
def test_check_varfont_duplicate_instance_names(check, vf_ttFont):
    assert_PASS(
        check(vf_ttFont), "with a variable font which has unique instance names."
    )

    vf_ttFont2 = copy(vf_ttFont)
    duplicate_instance_name = (
        vf_ttFont2["name"]
        .getName(
            vf_ttFont2["fvar"].instances[0].subfamilyNameID,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
            WindowsLanguageID.ENGLISH_USA,
        )
        .toUnicode()
    )
    vf_ttFont2["name"].setName(
        string=duplicate_instance_name,
        nameID=vf_ttFont2["fvar"].instances[1].subfamilyNameID,
        platformID=PlatformID.WINDOWS,
        platEncID=WindowsEncodingID.UNICODE_BMP,
        langID=WindowsLanguageID.ENGLISH_USA,
    )
    assert_results_contain(check(vf_ttFont2), FAIL, "duplicate-instance-names")

    # Change the nameID of the 3rd named instance to 456,
    # and don't create a name record with that nameID.
    name_id = 456
    vf_ttFont2["fvar"].instances[2].subfamilyNameID = name_id
    msg = assert_results_contain(check(vf_ttFont2), FAIL, "name-record-not-found")
    assert f" and nameID {name_id} was not found." in msg
