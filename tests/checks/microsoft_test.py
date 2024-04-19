import pytest

from fontTools.ttLib import TTFont

from fontbakery.status import FAIL, PASS, WARN
from fontbakery.codetesting import CheckTester, TEST_FILE, assert_PASS


@pytest.fixture
def test_font():
    return TTFont(TEST_FILE("selawik/Selawik-fvar-test-VTT.ttf"), lazy=True)


check_test_data = [
    ("com.microsoft/check/copyright", [PASS]),
    ("com.microsoft/check/version", [PASS]),
    ("com.microsoft/check/trademark", [PASS]),
    ("com.microsoft/check/manufacturer", [PASS]),
    ("com.microsoft/check/vendor_url", [PASS]),
    ("com.microsoft/check/license_description", [FAIL]),
    ("com.microsoft/check/typographic_family_name", [PASS]),
    ("com.microsoft/check/fstype", [PASS]),
    ("com.microsoft/check/vertical_metrics", [PASS]),
    ("com.microsoft/check/STAT_axis_values", [PASS]),
    ("com.microsoft/check/fvar_STAT_axis_ranges", [PASS]),
    ("com.microsoft/check/STAT_table_eliding_bit", [PASS]),
    ("com.microsoft/check/STAT_table_axis_order", [PASS]),
    ("com.microsoft/check/name_id_1", [PASS]),
    ("com.microsoft/check/name_id_2", [PASS]),
    ("com.microsoft/check/office_ribz_req", [PASS]),
    ("com.microsoft/check/name_length_req", [PASS]),
    (
        "com.microsoft/check/vtt_volt_data",
        [FAIL, FAIL, FAIL, FAIL, FAIL, PASS, PASS, PASS, PASS, PASS, PASS, PASS],
    ),
    ("com.microsoft/check/tnum_glyphs_equal_widths", [PASS]),
    ("com.microsoft/check/wgl4", [FAIL, WARN]),
    ("com.microsoft/check/ogl2", [FAIL]),
]


@pytest.mark.parametrize("check_id,expected_status_results", check_test_data)
def test_check(test_font, check_id, expected_status_results):
    check = CheckTester(check_id)
    status_results = [result.status for result in check(test_font)]
    assert expected_status_results == status_results


@pytest.mark.parametrize(
    "font_path",
    [
        "montserrat/Montserrat-Regular.ttf",
        "ubuntusans/UbuntuSans[wdth,wght].ttf",
    ],
)
def test_tnum_glyphs_equal_widths(font_path):
    check = CheckTester("com.microsoft/check/tnum_glyphs_equal_widths")

    # Pass condition
    font = TTFont(TEST_FILE(font_path))
    assert_PASS(check(font))
