import pytest

from fontTools.ttLib import TTFont

from fontbakery.status import FAIL, PASS, WARN
from fontbakery.codetesting import CheckTester, TEST_FILE


@pytest.fixture
def test_font():
    return TTFont(TEST_FILE("selawik/Selawik-fvar-test-VTT.ttf"), lazy=True)


check_test_data = [
    ("microsoft/copyright", [PASS]),
    ("microsoft/fstype", [PASS]),
    ("microsoft/license_description", [FAIL]),
    ("microsoft/manufacturer", [PASS]),
    ("microsoft/trademark", [PASS]),
    ("microsoft/vendor_url", [PASS]),
    ("microsoft/version", [PASS]),
    ("microsoft/vertical_metrics", [PASS]),
    ("microsoft/fvar_STAT_axis_ranges", [PASS]),
    ("microsoft/wgl4", [FAIL, WARN]),
    ("microsoft/ogl2", [FAIL]),
    ("microsoft/office_ribz_req", [PASS]),
    ("microsoft/STAT_axis_values", [PASS]),
    ("microsoft/STAT_table_axis_order", [PASS]),
    ("microsoft/STAT_table_eliding_bit", [PASS]),
    (
        "vtt_volt_data",
        [FAIL, FAIL, FAIL, FAIL, FAIL, PASS, PASS, PASS, PASS, PASS, PASS, PASS],
    ),
]


@pytest.mark.parametrize("check_id,expected_status_results", check_test_data)
def test_check(test_font, check_id, expected_status_results):
    check = CheckTester(check_id)
    status_results = [result.status for result in check(test_font)]
    assert expected_status_results == status_results
