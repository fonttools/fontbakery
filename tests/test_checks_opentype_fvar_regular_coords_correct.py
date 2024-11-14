from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import Axis

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
    MockFont,
)


@check_id("opentype/fvar/regular_coords_correct")
def test_check_opentype_fvar_regular_coords_correct(check):
    # test with a static font.
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-It.ttf"))
    assert_SKIP(check(ttFont))

    #### The variable font 'wght' (Weight) axis coordinate
    # must be 400 on the 'Regular' instance.

    # Our reference varfont CabinVFBeta.ttf
    # has a good Regular:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont))

    # We then ensure the check detects it when we
    # introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wght"] = 500
    assert_results_contain(check(ttFont), FAIL, "wght-not-400")

    # Reload the original font.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    # Change the name of the first instance from 'Regular' (nameID 258)
    # to 'Medium' (nameID 259). The font now has no Regular instance.
    ttFont["fvar"].instances[0].subfamilyNameID = 259
    assert_results_contain(check(ttFont), FAIL, "no-regular-instance")

    # Test with an italic variable font. The Italic instance must also be 400
    ttFont = TTFont(TEST_FILE("varfont/OpenSans-Italic[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    #### The variable font 'wdth' (Width) axis coordinate
    # must be 100 on the 'Regular' instance.

    # Our reference varfont CabinVFBeta.ttf
    # has a good Regular:wdth coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont))

    # We then ensure the check detects it when we
    # introduce the problem by setting a bad value:
    ttFont["fvar"].instances[0].coordinates["wdth"] = 0
    assert_results_contain(check(ttFont), FAIL, "wdth-not-100")

    # Reload the original font.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    # Change the name of the first instance from 'Regular' (nameID 258)
    # to 'Medium' (nameID 259). The font now has no Regular instance.
    ttFont["fvar"].instances[0].subfamilyNameID = 259
    assert_results_contain(check(ttFont), FAIL, "no-regular-instance")

    # Test with an italic variable font. The Italic instance must also be 100
    ttFont = TTFont(TEST_FILE("varfont/OpenSans-Italic[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    #### The variable font 'slnt' (Slant) axis coordinate
    # must be zero on the 'Regular' instance.

    # Our reference varfont, CabinVFBeta.ttf, lacks a 'slnt' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "slnt"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    first_instance = ttFont["fvar"].instances[0]
    first_instance.coordinates["slnt"] = 12
    # Note: I know the correct instance index for this hotfix because
    # I inspected our reference CabinVF using ttx

    # And with this the check must detect the problem:
    assert_results_contain(check(ttFont), FAIL, "slnt-not-0")

    # We correct the slant coordinate value to make the check PASS.
    first_instance.coordinates["slnt"] = 0
    assert_PASS(check(ttFont))

    # Change the name of the first instance from 'Regular' (nameID 258)
    # to 'Medium' (nameID 259). The font now has no Regular instance.
    first_instance.subfamilyNameID = 259
    assert_results_contain(check(ttFont), FAIL, "no-regular-instance")

    #### The variable font 'ital' (Italic) axis coordinate
    # must be zero on the 'Regular' instance.

    # Our reference varfont, CabinVFBeta.ttf, lacks an 'ital' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "ital"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    first_instance = ttFont["fvar"].instances[0]
    first_instance.coordinates["ital"] = 123
    # Note: I know the correct instance index for this hotfix because
    # I inspected the our reference CabinVF using ttx

    # And with this the check must detect the problem:
    assert_results_contain(check(ttFont), FAIL, "ital-not-0")

    # We correct the italic coordinate value to make the check PASS.
    first_instance.coordinates["ital"] = 0
    assert_PASS(check(ttFont))

    # Change the name of the first instance from 'Regular' (nameID 258)
    # to 'Medium' (nameID 259). The font now has no Regular instance.
    first_instance.subfamilyNameID = 259
    assert_results_contain(check(ttFont), FAIL, "no-regular-instance")

    #### The variable font 'opsz' (Optical Size) axis coordinate
    # should be between 10 and 16 on the 'Regular' instance.

    # Our reference varfont, CabinVFBeta.ttf, lacks an 'opsz' variation axis.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

    # So we add one:
    new_axis = Axis()
    new_axis.axisTag = "opsz"
    ttFont["fvar"].axes.append(new_axis)

    # and specify a bad coordinate for the Regular:
    first_instance = ttFont["fvar"].instances[0]
    first_instance.coordinates["opsz"] = 9
    # Note: I know the correct instance index for this hotfix because
    # I inspected the our reference CabinVF using ttx

    # Then we ensure the problem is detected:
    assert_results_contain(
        check(ttFont), WARN, "opsz", "with a bad Regular:opsz coordinate (9)..."
    )

    # We try yet another bad value
    # and the check should detect the problem:
    assert_results_contain(
        check(MockFont(ttFont=ttFont, regular_opsz_coord=17)),
        WARN,
        "opsz",
        "with another bad Regular:opsz value (17)...",
    )

    # We then test with good default opsz values:
    for value in [10, 11, 12, 13, 14, 15, 16]:
        assert_PASS(
            check(MockFont(ttFont=ttFont, regular_opsz_coord=value)),
            f"with a good Regular:opsz coordinate ({value})...",
        )

    # Change the name of the first instance from 'Regular' (nameID 258)
    # to 'Medium' (nameID 259). The font now has no Regular instance.
    first_instance.subfamilyNameID = 259
    assert_results_contain(check(ttFont), FAIL, "no-regular-instance")
