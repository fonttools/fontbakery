import io

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN, FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/glyf_unused_data")
def test_check_glyf_unused_data(check):
    """Is there any unused data at the end of the glyf table?"""

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
    assert_results_contain(check(ttFont), FAIL, "unreachable-data")

    ttFont = TTFont(font)
    ttFont["loca"].locations.append(50000)
    _file = io.BytesIO()
    ttFont.save(_file)
    ttFont = TTFont(_file)
    ttFont.reader.file.name = font
    assert_results_contain(check(ttFont), FAIL, "missing-data")


@check_id("opentype/points_out_of_bounds")
def test_check_points_out_of_bounds(check):
    """Check for points out of bounds."""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "points-out-of-bounds")

    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(ttFont))


@check_id("opentype/glyf_non_transformed_duplicate_components")
def test_check_glyf_non_transformed_duplicate_components(check):
    """Check glyphs do not have duplicate components
    which have the same x,y coordinates."""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # Set qutodbl's components to have the same x,y values
    ttFont["glyf"]["quotedbl"].components[0].x = 0
    ttFont["glyf"]["quotedbl"].components[1].x = 0
    ttFont["glyf"]["quotedbl"].components[0].y = 0
    ttFont["glyf"]["quotedbl"].components[1].y = 0
    assert_results_contain(check(ttFont), FAIL, "found-duplicates")
