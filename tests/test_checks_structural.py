import pytest

from fontbakery.fonts_profile import checks_by_id, load_all_checks

load_all_checks()


@pytest.mark.parametrize("check", checks_by_id.values())
def test_check_has_rationale(check):
    assert check.rationale is not None, f"Check {check.id} has no rationale"
