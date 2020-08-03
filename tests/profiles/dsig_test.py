from fontbakery.codetesting import (TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain)

from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_dsig():
    """ Does the font have a DSIG table ? """
    from fontbakery.profiles.dsig import com_google_fonts_check_dsig as check

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
