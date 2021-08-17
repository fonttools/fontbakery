import io

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (WARN, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


def test_check_glyf_unused_data():
    """ Is there any unused data at the end of the glyf table? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/glyf_unused_data")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont))

    # Always start with a fresh copy, as fT works lazily. Accessing certain data
    # can prevent the test from working because we rely on uninitialized
    # behavior.
    ttFont = TTFont(font)
    ttFont["loca"].locations.pop()
    _file = io.BytesIO()
    ttFont.save(_file)
    ttFont = TTFont(_file)
    ttFont.reader.file.name = font
    assert_results_contain(check(ttFont),
                           FAIL, 'unreachable-data')

    ttFont = TTFont(font)
    ttFont["loca"].locations.append(50000)
    _file = io.BytesIO()
    ttFont.save(_file)
    ttFont = TTFont(_file)
    ttFont.reader.file.name = font
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-data')


def test_check_points_out_of_bounds():
    """ Check for points out of bounds. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/points_out_of_bounds")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           WARN, 'points-out-of-bounds')

    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(ttFont))


def test_check_glyf_non_transformed_duplicate_components():
    """Check glyphs do not have duplicate components which have the same x,y coordinates."""
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/glyf_non_transformed_duplicate_components")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # Set qutodbl's components to have the same x,y values
    ttFont['glyf']['quotedbl'].components[0].x = 0
    ttFont['glyf']['quotedbl'].components[1].x = 0
    ttFont['glyf']['quotedbl'].components[0].y = 0
    ttFont['glyf']['quotedbl'].components[1].y = 0
    assert_results_contain(check(ttFont),
                           FAIL, 'found-duplicates')
