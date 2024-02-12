import io

from fontTools.ttLib import TTFont

from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_loca_maxp_num_glyphs():
    """Does the number of glyphs in the loca table match the maxp table?"""
    check = CheckTester("com.google.fonts/check/loca/maxp_num_glyphs")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["loca"].locations.pop()
    _file = io.BytesIO()
    ttFont.save(_file)
    ttFont = TTFont(_file)
    ttFont.reader.file.name = "foo"  # Make CheckTester class happy... :-P
    assert_results_contain(check(ttFont), FAIL, "corrupt")
