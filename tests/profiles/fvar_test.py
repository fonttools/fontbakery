from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (FAIL, WARN)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester)
from fontbakery.profiles import opentype as opentype_profile


def test_check_varfont_regular_wght_coord():
    """ The variable font 'wght' (Weight) axis coordinate
        must be 400 on the 'Regular' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/regular_wght_coord")

    # Our reference varfont CabinVFBeta.ttf
    # has a good Regular:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont),
                'with a good Regular:wght coordinate...')

    # We then ensure the check detects it when we
    # introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 500
    assert_results_contain(check(ttFont),
                           FAIL, 'not-400',
                           'with a bad Regular:wght coordinate (500)...')


def test_check_varfont_regular_wdth_coord():
    """ The variable font 'wdth' (Width) axis coordinate
        must be 100 on the 'Regular' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/regular_wdth_coord")

    # Our reference varfont CabinVFBeta.ttf
    # has a good Regular:wdth coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont),
                'with a good Regular:wdth coordinate...')

    # We then ensure the check detects it when we
    # introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0
    assert_results_contain(check(ttFont),
                           FAIL, 'not-100',
                           'with a bad Regular:wdth coordinate (0)...')


def test_check_varfont_regular_slnt_coord():
    """ The variable font 'slnt' (Slant) axis coordinate
        must be zero on the 'Regular' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/regular_slnt_coord")

    # Our reference varfont, CabinVFBeta.ttf, lacks a 'slnt' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    from fontTools.ttLib.tables._f_v_a_r import Axis
    new_axis = Axis()
    new_axis.axisTag = "slnt"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    ttFont["fvar"].instances[0].coordinates["slnt"] = 12
    # Note: I know the correct instance index for this hotfix because
    # I inspected our reference CabinVF using ttx

    # And with this the check must detect the problem:
    assert_results_contain(check(ttFont),
                           FAIL, 'non-zero',
                           'with a bad Regular:slnt coordinate (12)...')

    # We then fix the Regular:slnt coordinate value in order to PASS:
    assert_PASS(check(ttFont, {"regular_slnt_coord": 0}),
                'with a good Regular:slnt coordinate (zero)...')


def test_check_varfont_regular_ital_coord():
    """ The variable font 'ital' (Italic) axis coordinate
        must be zero on the 'Regular' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/regular_ital_coord")
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

    # And with this the check must detect the problem:
    assert_results_contain(check(ttFont),
                           FAIL, 'non-zero',
                           'with a bad Regular:ital coordinate (123)...')

    # but with zero it must PASS the check:
    assert_PASS(check(ttFont, {"regular_ital_coord": 0}),
                'with a good Regular:ital coordinate (zero)...')


def test_check_varfont_regular_opsz_coord():
    """ The variable font 'opsz' (Optical Size) axis coordinate
        should be between 10 and 16 on the 'Regular' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/regular_opsz_coord")
    from fontTools.ttLib.tables._f_v_a_r import Axis

    # Our reference varfont, CabinVFBeta.ttf, lacks an 'opsz' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "opsz"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    ttFont["fvar"].instances[0].coordinates["opsz"] = 9
    # Note: I know the correct instance index for this hotfix because
    # I inspected the our reference CabinVF using ttx

    # Then we ensure the problem is detected:
    assert_results_contain(check(ttFont),
                           WARN, 'out-of-range',
                           'with a bad Regular:opsz coordinate (9)...')

    # We try yet another bad value
    # and the check should detect the problem:
    assert_results_contain(check(ttFont, {"regular_opsz_coord": 17}),
                           WARN, 'out-of-range',
                           'with another bad Regular:opsz value (17)...')

    # We then test with good default opsz values:
    for value in [10, 11, 12, 13, 14, 15, 16]:
        assert_PASS(check(ttFont, {"regular_opsz_coord": value}),
                    f'with a good Regular:opsz coordinate ({value})...')


def test_check_varfont_bold_wght_coord():
    """ The variable font 'wght' (Weight) axis coordinate
        must be 700 on the 'Bold' instance. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/bold_wght_coord")

    # Our reference varfont CabinVFBeta.ttf
    # has a good Bold:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont),
                'with a good Bold:wght coordinate...')

    # We then change the value to ensure the problem is properly detected by the check:
    ttFont["fvar"].instances[3].coordinates["wght"] = 600
    assert_results_contain(check(ttFont),
                           FAIL, 'not-700',
                           'with a bad Bold:wght coordinage (600)...')


def test_check_varfont_wght_valid_range():
    """ The variable font 'wght' (Weight) axis coordinate
        must be within spec range of 1 to 1000 on all instances. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/wght_valid_range")

    # Our reference varfont CabinVFBeta.ttf
    # has all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont),
                'with a good varfont...')

    # We then introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 0
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=0...')

    # And yet another bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 1001
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=1001...')


def test_check_varfont_wdth_valid_range():
    """ The variable font 'wdth' (Width) axis coordinate
        must be within spec range of 1 to 1000 on all instances. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/wdth_valid_range")

    # Our reference varfont CabinVFBeta.ttf
    # has all instances within the 1-1000 range
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont),
                'with a good varfont...')

    # We then introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=0...')

    # And yet another bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 1001
    assert_results_contain(check(ttFont),
                           FAIL, 'out-of-range',
                           'with wght=1001...')


def test_check_varfont_slnt_range():
    """ The variable font 'slnt' (Slant) axis coordinate
        specifies positive values in its range? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/varfont/slnt_range")

    # Our reference Inter varfont has a bad slnt range
    ttFont = TTFont("data/test/varfont/inter/Inter[slnt,wght].ttf")
    assert_results_contain(check(ttFont),
                           WARN, 'unusual-range',
                           'with a varfont that has an unusual "slnt" range.')

    # We then fix the font-bug by flipping the slnt axis range:
    for i, axis in enumerate(ttFont["fvar"].axes):
        if axis.axisTag == "slnt":
            minValue, maxValue = axis.minValue, axis.maxValue
            ttFont["fvar"].axes[i].minValue = -maxValue
            ttFont["fvar"].axes[i].maxValue = -minValue

    # And it must now be good ;-)
    assert_PASS(check(ttFont))

