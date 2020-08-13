from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )
from fontbakery.utils import (assert_PASS,
                              assert_results_contain)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_varfont_stat_axis_record_for_each_axis():
    """ Check the STAT table has an Axis Record for every axis in the font. """
    from fontbakery.profiles.stat import com_google_fonts_check_varfont_stat_axis_record_for_each_axis as check

    # Our reference varfont, Cabin[wdth,wght].ttf, has
    # all necessary Axis Records
    ttFont = TTFont("data/test/cabinvf/Cabin[wdth,wght].ttf")

    # So it must PASS the test
    assert_PASS(check(ttFont),
                'with all necessary Axis Records...')

    # We then remove the wdth Axis Record so it must FAIL:
    ttFont['STAT'].table.DesignAxisRecord.Axis.pop(0)

    # and now this should FAIL the test:
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-axis-records',
                           'with a missing Axis Record: (wght)...')
