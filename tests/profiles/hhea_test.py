import os

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

def test_check_linegaps():
    """ Checking Vertical Metric Linegaps. """
    from fontbakery.profiles.hhea import com_google_fonts_check_linegaps as check

    print('Test FAIL with non-zero hhea.lineGap...')
    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But just to be sure, we first explicitely set
    # the values we're checking for:
    ttFont['hhea'].lineGap = 1
    ttFont['OS/2'].sTypoLineGap = 0
    assert_results_contain(check(ttFont),
                           WARN, 'hhea')

    # Then we run the check with a non-zero OS/2.sTypoLineGap:
    ttFont['hhea'].lineGap = 0
    ttFont['OS/2'].sTypoLineGap = 1
    assert_results_contain(check(ttFont),
                           WARN, 'OS/2')

    # And finaly we fix it by making both values equal to zero:
    ttFont['hhea'].lineGap = 0
    ttFont['OS/2'].sTypoLineGap = 0
    assert_PASS(check(ttFont))


def test_check_maxadvancewidth():
    """ MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables? """
    from fontbakery.profiles.hhea import com_google_fonts_check_maxadvancewidth as check

    test_font = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))

    assert_PASS(check(test_font))

    test_font["hmtx"].metrics["A"] = (1234567, 1234567)
    assert_results_contain(check(test_font),
                           FAIL, 'mismatch')

