import pytest

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import WARN, FAIL
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


mada_fonts = [
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Regular.ttf")
]

@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]


def test_check_family_underline_thickness(mada_ttFonts):
    """ Fonts have consistent underline thickness ? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/family/underline_thickness")

    # We start with our reference Mada font family,
    # which we know has the same value of post.underlineThickness
    # across all of its font files, based on our inspection
    # of the file contents using TTX.
    #
    # So the check should PASS in this case:
    assert_PASS(check(mada_ttFonts),
                'with a good family.')

    # Then we introduce the issue by setting a
    # different underlineThickness value in just
    # one of the font files:
    value = mada_ttFonts[0]['post'].underlineThickness
    incorrect_value = value + 1
    mada_ttFonts[0]['post'].underlineThickness = incorrect_value

    # And now re-running the check on the modified
    # family should result in a FAIL:
    assert_results_contain(check(mada_ttFonts),
                           FAIL, "inconsistent-underline-thickness",
                           'with an inconsistent family.')


def test_check_post_table_version():
    """ Font has correct post table version (2 for TTF, 3 for OTF)? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/post_table_version")

    # our reference Mada family is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with good font.')

    # modify the post table version
    ttFont['post'].formatType = 3

    assert_results_contain(check(ttFont),
                           FAIL, "post-table-version",
                           'with fonts that diverge on the fontRevision field value.')

