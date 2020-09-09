from fontTools.ttLib import TTFont

from fontbakery.checkrunner import INFO
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)

from fontbakery.profiles import opentype as opentype_profile


def test_check_kern_table():
    """ Is there a "kern" table declared in the font? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/kern_table")

    # Our reference Mada Regular is known to be good
    # (does not have a 'kern' table):
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a font without a "kern" table...')

    # add a fake 'kern' table:
    ttFont["kern"] = "foo"

    # and make sure the check emits an INFO message:
    assert_results_contain(check(ttFont),
                           INFO, 'kern-found',
                           'with a font containing a "kern" table...')

