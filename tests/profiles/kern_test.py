from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )
from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_results_contain)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_kern_table():
    """ Is there a "kern" table declared in the font ? """
    from fontbakery.profiles.kern import com_google_fonts_check_kern_table as check

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

