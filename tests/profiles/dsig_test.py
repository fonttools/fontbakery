from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.checkrunner import WARN
from fontbakery.profiles import opentype as opentype_profile

from fontTools.ttLib import TTFont


def test_check_dsig():
    """Does the font have a DSIG table ?"""
    check = CheckTester(opentype_profile, "com.google.fonts/check/dsig")

    # Our reference Cabin Regular font is bad (theres a DSIG table declared):
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(
        check(ttFont), WARN, "found-DSIG", "with a font containing a DSIG table..."
    )

    # Then we remove the DSIG table and it should now PASS the check:
    del ttFont["DSIG"]
    assert_PASS(check(ttFont), "with a good font...")
