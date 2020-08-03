from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR,
                                    SKIP, PASS, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_varfont_regular_wght_coord():
    """ The variable font 'wght' (Weight) axis coordinate
        must be 400 on the 'Regular' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_regular_wght_coord as check
    from fontbakery.profiles.shared_conditions import regular_wght_coord

    # Our reference varfont, CabinVFBeta.ttf, has
    # a good Regular:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    regular_weight_coord = regular_wght_coord(ttFont)

    # So it must PASS the test
    assert_PASS(check(ttFont, regular_weight_coord),
                'with a good Regular:wght coordinate...')

    # We then change the value so it must FAIL:
    ttFont["fvar"].instances[0].coordinates["wght"] = 500

    # Then re-read the coord:
    regular_weight_coord = regular_wght_coord(ttFont)

    # and now this should FAIL the test:
    assert_results_contain(check(ttFont,
                                 regular_weight_coord),
                           FAIL, 'not-400',
                           'with a bad Regular:wght coordinate (500)...')


def test_check_varfont_regular_wdth_coord():
    """ The variable font 'wdth' (Width) axis coordinate
        must be 100 on the 'Regular' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_regular_wdth_coord as check
    from fontbakery.profiles.shared_conditions import regular_wdth_coord

    # Our reference varfont, CabinVFBeta.ttf, has
    # a good Regular:wdth coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    regular_width_coord = regular_wdth_coord(ttFont)

    # So it must PASS the test
    assert_PASS(check(ttFont,
                      regular_width_coord),
                'with a good Regular:wdth coordinate...')

    # We then change the value so it must FAIL:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0

    # Then re-read the coord:
    regular_width_coord = regular_wdth_coord(ttFont)

    # and now this should FAIL the test:
    assert_results_contain(check(ttFont,
                                 regular_width_coord),
                           FAIL, 'not-100',
                           'with a bad Regular:wdth coordinate (0)...')


def test_check_varfont_regular_slnt_coord():
    """ The variable font 'slnt' (Slant) axis coordinate
        must be zero on the 'Regular' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_regular_slnt_coord as check
    from fontbakery.profiles.shared_conditions import regular_slnt_coord
    from fontTools.ttLib.tables._f_v_a_r import Axis

    # Our reference varfont, CabinVFBeta.ttf, lacks a 'slnt' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "slnt"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    ttFont["fvar"].instances[0].coordinates["slnt"] = 12
    # Note: I know the correct instance index for this hotfix because
    # I inspected our reference CabinVF using ttx

    # then we test the code of the regular_slnt_coord condition:
    regular_slant_coord = regular_slnt_coord(ttFont)

    # And with this the test must FAIL
    assert_results_contain(check(ttFont,
                                 regular_slant_coord),
                           FAIL, 'non-zero',
                           'with a bad Regular:slnt coordinate (12)...')

    # We then fix the Regular:slnt coordinate value:
    regular_slant_coord = 0

    # and now this should PASS the test:
    assert_PASS(check(ttFont,
                      regular_slant_coord),
                'with a good Regular:slnt coordinate (zero)...')


def test_check_varfont_regular_ital_coord():
    """ The variable font 'ital' (Italic) axis coordinate
        must be zero on the 'Regular' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_regular_ital_coord as check
    from fontbakery.profiles.shared_conditions import regular_ital_coord
    from fontTools.ttLib.tables._f_v_a_r import Axis

    # Our reference varfont, CabinVFBeta.ttf, lacks an 'ital' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "ital"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    ttFont["fvar"].instances[0].coordinates["ital"] = 123
    # Note: I know the correct instance index for this hotfix because
    # I inspected the our reference CabinVF using ttx

    # then we test the code of the regular_ital_coord condition:
    regular_italic_coord = regular_ital_coord(ttFont)

    # So it must FAIL the test
    assert_results_contain(check(ttFont,
                                 regular_italic_coord),
                           FAIL, 'non-zero',
                           'with a bad Regular:ital coordinate (123)...')

    # We then fix the Regular:ital coordinate:
    regular_italic_coord = 0

    # and now this should PASS the test:
    assert_PASS(check(ttFont,
                      regular_italic_coord),
                'with a good Regular:ital coordinate (zero)...')


def test_check_varfont_regular_opsz_coord():
    """ The variable font 'opsz' (Optical Size) axis coordinate
        should be between 9 and 13 on the 'Regular' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_regular_opsz_coord as check
    from fontbakery.profiles.shared_conditions import regular_opsz_coord
    from fontTools.ttLib.tables._f_v_a_r import Axis

    # Our reference varfont, CabinVFBeta.ttf, lacks an 'opsz' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "opsz"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    ttFont["fvar"].instances[0].coordinates["opsz"] = 8
    # Note: I know the correct instance index for this hotfix because
    # I inspected the our reference CabinVF using ttx

    # then we test the regular_opsz_coord condition:
    regular_opticalsize_coord = regular_opsz_coord(ttFont)

    # And it must WARN the test
    assert_results_contain(check(ttFont,
                                 regular_opticalsize_coord),
                           WARN, 'out-of-range',
                           'with a bad Regular:opsz coordinate (8)...')

    # We try yet another bad value
    regular_opticalsize_coord = 14

    # And it must also WARN the test
    assert_results_contain(check(ttFont, regular_opticalsize_coord),
                           WARN, 'out-of-range',
                           'with another bad Regular:opsz value (14)...')

    # We then test with good default opsz values:
    for value in [9, 10, 11, 12, 13]:
        regular_opticalsize_coord = value

        # and now this should PASS the test:
        assert_PASS(check(ttFont,
                          regular_opticalsize_coord),
                    f'with a good Regular:opsz coordinate ({value})...')


def test_check_varfont_bold_wght_coord():
    """ The variable font 'wght' (Weight) axis coordinate
        must be 700 on the 'Bold' instance. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_bold_wght_coord as check
    from fontbakery.profiles.shared_conditions import bold_wght_coord

    # Our reference varfont, CabinVFBeta.ttf, has
    # a good Bold:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    bold_weight_coord = bold_wght_coord(ttFont)

    # So it must PASS the test
    assert_PASS(check(ttFont,
                      bold_weight_coord),
                'with a bad Bold:wght coordinate...')

    # We then change the value so it must FAIL:
    ttFont["fvar"].instances[3].coordinates["wght"] = 600

    # Then re-read the coord:
    bold_weight_coord = bold_wght_coord(ttFont)

    # and now this should FAIL the test:
    assert_results_contain(check(ttFont,
                                 bold_weight_coord),
                           FAIL, 'not-700',
                           'with a bad Bold:wght coordinage (600)...')


def test_check_varfont_wght_valid_range():
    """ The variable font 'wght' (Weight) axis coordinate
        must be within spec range of 1 to 1000 on all instances. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_wght_valid_range as check

    # Our reference varfont, CabinVFBeta.ttf, has
    # all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # so it must PASS the test:
    assert_PASS(check(ttFont),
                'with a good varfont...')

    # We then introduce a bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 0

    # And it must FAIL the test
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=0...')

    # And yet another bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 1001

    # Should also FAIL:
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=1001...')


def test_check_varfont_wdth_valid_range():
    """ The variable font 'wdth' (Width) axis coordinate
        must be within spec range of 1 to 1000 on all instances. """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_wdth_valid_range as check

    # Our reference varfont, CabinVFBeta.ttf, has
    # all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # so it must PASS the test:
    assert_PASS(check(ttFont),
                'with a good varfont...')

    # We then introduce a bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0

    # And it must FAIL the test
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=0...')

    # And yet another bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 1001

    # Should also FAIL:
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=1001...')


def test_check_varfont_slnt_range():
    """ The variable font 'slnt' (Slant) axis coordinate
        specifies positive values in its range? """
    from fontbakery.profiles.fvar import com_google_fonts_check_varfont_slnt_range as check
    from fontbakery.profiles.shared_conditions import slnt_axis

    # Our reference Inter varfont has a bad slnt range
    ttFont = TTFont("data/test/varfont/inter/Inter[slnt,wght].ttf")
    assert_results_contain(check(ttFont,
                                 slnt_axis(ttFont)),
                           WARN, 'unusual-range',
                           'with a varfont that has a bad "slnt" range.')

    # We then fix the font-bug by flipping the slnt axis range:
    for i, axis in enumerate(ttFont["fvar"].axes):
        if axis.axisTag == "slnt":
            minValue, maxValue = axis.minValue, axis.maxValue
            ttFont["fvar"].axes[i].minValue = -maxValue
            ttFont["fvar"].axes[i].maxValue = -minValue

    # And it must now PASS
    assert_PASS(check(ttFont,
                      slnt_axis(ttFont)))

