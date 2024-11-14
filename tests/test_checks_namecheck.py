import pytest
from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import INFO


# TODO: Maybe skip this code-test if the service is offline?
# we could use pytest.mark.skipif here together with a piece of code that
# verifies whether or not the namecheck.fontdata.com website is online at the moment
@pytest.mark.skip(
    "The namecheck service is too unreliable"
    " and keeps breaking our CI jobs all the time..."
)
@check_id("fontdata_namecheck")
def test_check_fontdata_namecheck(check):
    """Familyname is unique according to namecheck.fontdata.com"""

    TIMEOUT_MSG = (
        "Sometimes namecheck.fontdata.com times out"
        " and we don't want to stop running all the other"
        " code tests. Unless you touched this portion of"
        " the code, it is generaly safe to ignore this glitch."
    )
    # We dont FAIL because this is meant as a merely informative check
    # There may be frequent cases when fonts are being updated and thus
    # already have a public family name registered on the
    # namecheck.fontdata.com database.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font),
        INFO,
        "name-collision",
        "with an already used name...",
        ignore_error=TIMEOUT_MSG,
    )

    # Here we know that FamilySans has not been (and will not be)
    # registered as a real family.
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font), "with a unique family name...", ignore_error=TIMEOUT_MSG)
