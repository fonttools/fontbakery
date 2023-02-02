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


def test_check_caretslope():
    """Check hhea.caretSlopeRise and hhea.caretSlopeRun"""
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/caret_slope")

    # PASS
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    # FAIL for right-leaning
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    ttFont["post"].italicAngle = -12
    message = assert_results_contain(check(ttFont),
                                     FAIL, 'caretslope-mismatch')
    assert message == (
        "hhea.caretSlopeRise and hhea.caretSlopeRun do not match with post.italicAngle.\n"
        "Got: caretSlopeRise 1000 and caretSlopeRun 190\n"
        "Expected: caretSlopeRise 1000 and caretSlopeRun 206"
    )

    # FIX
    ttFont["hhea"].caretSlopeRun = 206
    assert_PASS(check(ttFont))

    good_value = ttFont["hhea"].caretSlopeRise
    ttFont["hhea"].caretSlopeRise = 0
    assert_results_contain(check(ttFont),
                           FAIL, 'zero-rise')

    # Fix it again from backed up good value
    ttFont["hhea"].caretSlopeRise = good_value

    # FAIL for left-leaning
    ttFont["post"].italicAngle = 12
    message = assert_results_contain(check(ttFont),
                                     FAIL, 'caretslope-mismatch')
    assert message == (
        "hhea.caretSlopeRise and hhea.caretSlopeRun do not match with post.italicAngle.\n"
        "Got: caretSlopeRise 1000 and caretSlopeRun 206\n"
        "Expected: caretSlopeRise 1000 and caretSlopeRun -206"
    )

    # FIX
    ttFont["hhea"].caretSlopeRun = -206
    assert_PASS(check(ttFont))
