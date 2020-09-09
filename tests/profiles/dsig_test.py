from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.checkrunner import FAIL
from fontbakery.profiles import opentype as opentype_profile

from fontTools.ttLib import TTFont


def test_check_dsig():
    """ Does the font have a DSIG table ? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/dsig")

    # Our reference Cabin Regular font is good (theres a DSIG table declared):
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # Then we remove the DSIG table so that we get a FAIL:
    del ttFont['DSIG']
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-signature',
                           'with a font lacking a DSIG table...')
