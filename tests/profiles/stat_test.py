from fontbakery.checkrunner import PASS, FAIL
from fontbakery.codetesting import (TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain)

from fontTools.ttLib import TTFont


def test_check_varfont_stat_axis_record_for_each_axis():
    """ Check the STAT table has an Axis Record for every axis in the font. """
    from fontbakery.profiles.stat \
        import com_google_fonts_check_varfont_stat_axis_record_for_each_axis as check

    # Our reference Cabin[wdth,wght].ttf variable font
    # has all necessary Axis Records
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # So the check must PASS
    assert_PASS(check(ttFont),
                'with all necessary Axis Records...')

    # We then remove its first Axis Record (`wdth`):
    ttFont['STAT'].table.DesignAxisRecord.Axis.pop(0)

    # And now the problem should be detected::
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-axis-records',
                           'with a missing Axis Record: (wght)...')
