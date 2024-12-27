from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, SKIP, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/varfont/STAT_axis_record_for_each_axis")
def test_check_varfont_STAT_axis_record_for_each_axis(check):
    """Check the STAT table has an Axis Record for every axis in the font."""

    # Our reference Cabin[wdth,wght].ttf variable font
    # has all necessary Axis Records
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # So the check must PASS
    assert_PASS(check(ttFont))

    # We then remove its first Axis Record (`wdth`):
    ttFont["STAT"].table.DesignAxisRecord.Axis.pop(0)

    # And now the problem should be detected:
    msg = assert_results_contain(check(ttFont), FAIL, "missing-axis-records")
    assert msg == (
        "STAT table is missing Axis Records for the following axes:\n\n\t- wdth"
    )

    # Now use a stactic font.
    # The check should be skipped due to an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Black.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_variable_font" in msg


@check_id("opentype/STAT/ital_axis")
def test_check_italic_axis_in_STAT(check):
    """Ensure VFs have 'ital' STAT axis."""
    # PASS
    fonts = [
        TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"),
        TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"),
    ]
    assert_PASS(check(fonts))

    # FAIL
    fonts = [
        TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"),
    ]
    assert_results_contain(check(fonts), FAIL, "missing-roman")

    fonts = [
        TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"),
        TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"),
    ]
    # Remove ital axes
    for font in fonts:
        ttFont = TTFont(font)
        ttFont["STAT"].table.DesignAxisRecord.Axis = ttFont[
            "STAT"
        ].table.DesignAxisRecord.Axis[:-1]
        ttFont.save(font.replace(".ttf", ".missingitalaxis.ttf"))
    fonts = [
        TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].missingitalaxis.ttf"),
        TEST_FILE(
            "shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].missingitalaxis.ttf"
        ),
    ]
    assert_results_contain(check(fonts), FAIL, "missing-ital-axis")
    import os

    for font in fonts:
        os.remove(font)


@check_id("opentype/STAT/ital_axis")
def test_check_italic_axis_in_STAT_is_boolean(check):
    """Ensure 'ital' STAT axis is boolean value"""

    # PASS
    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    results = check(TTFont(font))
    results = [r for r in results if r.message.code == "wrong-ital-axis-value"]
    assert_PASS(results)

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    results = check(TTFont(font))
    results = [r for r in results if r.message.code == "wrong-ital-axis-value"]
    assert_PASS(results)

    # FAIL
    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Value = 1
    assert_results_contain(check(ttFont), WARN, "wrong-ital-axis-value")

    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Flags = 0
    assert_results_contain(check(ttFont), WARN, "wrong-ital-axis-flag")

    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    italfont = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ital_ttFont = TTFont(italfont)
    ital_ttFont["STAT"].table.AxisValueArray.AxisValue[6].Value = 0
    assert_results_contain(check([ttFont, ital_ttFont]), WARN, "wrong-ital-axis-value")

    ital_ttFont = TTFont(italfont)
    ital_ttFont["STAT"].table.AxisValueArray.AxisValue[6].Flags = 2
    assert_results_contain(check([ttFont, ital_ttFont]), WARN, "wrong-ital-axis-flag")

    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].LinkedValue = 0.4
    assert_results_contain(check(ttFont), WARN, "wrong-ital-axis-linkedvalue")


@check_id("opentype/STAT/ital_axis")
def test_check_italic_axis_last(check):
    """Ensure 'ital' STAT axis is last."""

    font_roman = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont_roman = TTFont(font_roman)
    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    # Move last axis (ital) to the front
    ttFont["STAT"].table.DesignAxisRecord.Axis = [
        ttFont["STAT"].table.DesignAxisRecord.Axis[-1]
    ] + ttFont["STAT"].table.DesignAxisRecord.Axis[:-1]
    assert_results_contain(check([ttFont_roman, ttFont]), WARN, "ital-axis-not-last")

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    assert_PASS(check([font_roman, font]))


@check_id("opentype/weight_class_fvar")
def test_check_weight_class_fvar(check):
    ttFont = TTFont(TEST_FILE("varfont/Oswald-VF.ttf"))
    assert_PASS(check(ttFont), "matches fvar default value.")

    ttFont["OS/2"].usWeightClass = 333
    assert_results_contain(
        check(ttFont), FAIL, "bad-weight-class", "but should match fvar default value."
    )

    # Test with a variable font that doesn't have a 'wght' (Weight) axis.
    # The check should yield SKIP.
    ttFont = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: has_wght_axis" in msg
