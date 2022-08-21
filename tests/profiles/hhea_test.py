from fontTools.ttLib import TTFont

from fontbakery.checkrunner import WARN, FAIL
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


def test_check_linegaps():
    """ Checking Vertical Metric Linegaps. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/linegaps")

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But just to be sure, we first explicitely set
    # the values we're checking for:
    ttFont['hhea'].lineGap = 1
    ttFont['OS/2'].sTypoLineGap = 0
    assert_results_contain(check(ttFont),
                           WARN, 'hhea',
                           'with non-zero hhea.lineGap...')

    # Then we run the check with a non-zero OS/2.sTypoLineGap:
    ttFont['hhea'].lineGap = 0
    ttFont['OS/2'].sTypoLineGap = 1
    assert_results_contain(check(ttFont),
                           WARN, 'OS/2',
                           'with non-zero OS/2.sTypoLineGap...')

    # And finaly we fix it by making both values equal to zero:
    ttFont['hhea'].lineGap = 0
    ttFont['OS/2'].sTypoLineGap = 0
    assert_PASS(check(ttFont))

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont['OS/2']
    assert_results_contain(check(ttFont), FAIL, "lacks-table")


def test_check_maxadvancewidth():
    """ MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/maxadvancewidth")

    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["A"] = (1234567, 1234567)
    assert_results_contain(check(ttFont),
                           FAIL, 'mismatch')

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont['hmtx']
    assert_results_contain(check(ttFont), FAIL, "lacks-table")
