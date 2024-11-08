import io

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("opentype/loca/maxp_num_glyphs")
def test_check_loca_maxp_num_glyphs(check):
    """Does the number of glyphs in the loca table match the maxp table?"""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["loca"].locations.pop()
    _file = io.BytesIO()
    ttFont.save(_file)
    ttFont = TTFont(_file)
    ttFont.reader.file.name = "foo"  # Make CheckTester class happy... :-P
    assert_results_contain(check(ttFont), FAIL, "corrupt")
