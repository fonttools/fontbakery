import io
import os

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )
from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_results_contain)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_glyf_unused_data():
    """ Is there any unused data at the end of the glyf table? """
    from fontbakery.profiles.glyf import com_google_fonts_check_glyf_unused_data as check

    test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # Always start with a fresh copy, as fT works lazily. Accessing certain data
    # can prevent the test from working because we rely on uninitialized
    # behavior.
    test_font = TTFont(test_font_path)
    test_font["loca"].locations.pop()
    test_file = io.BytesIO()
    test_font.save(test_file)
    test_font = TTFont(test_file)
    assert_results_contain(check(test_font),
                           FAIL, 'unreachable-data')

    test_font = TTFont(test_font_path)
    test_font["loca"].locations.append(50000)
    test_file = io.BytesIO()
    test_font.save(test_file)
    test_font = TTFont(test_file)
    assert_results_contain(check(test_font),
                           FAIL, 'missing-data')


def test_check_points_out_of_bounds():
    """ Check for points out of bounds. """
    from fontbakery.profiles.glyf import com_google_fonts_check_points_out_of_bounds as check

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_results_contain(check(test_font),
                           WARN, 'points-out-of-bounds')

    test_font2 = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(test_font2))


def test_check_glyf_non_transformed_duplicate_components():
    """Check glyphs do not have duplicate components which have the same x,y coordinates."""
    from fontbakery.profiles.glyf import com_google_fonts_check_glyf_non_transformed_duplicate_components as check

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(test_font))

    # Set qutodbl's components to have the same x,y values
    glyph = test_font['glyf']['quotedbl'].components[0].x = 0
    glyph = test_font['glyf']['quotedbl'].components[1].x = 0
    glyph = test_font['glyf']['quotedbl'].components[0].y = 0
    glyph = test_font['glyf']['quotedbl'].components[1].y = 0
    assert_results_contain(check(test_font),
                           FAIL, 'found-duplicates')

