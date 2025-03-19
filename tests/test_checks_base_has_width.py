from io import BytesIO
from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


def get_test_font():
    import defcon
    import ufo2ft

    test_ufo = defcon.Font(TEST_FILE("test.ufo"))
    # Add a PUA character that has no width
    glyph = test_ufo.newGlyph("uniF176")
    glyph.unicode = 0xF176
    test_ttf = ufo2ft.compileTTF(test_ufo)

    # Make the CheckTester class happy... :-P
    stream = BytesIO()
    test_ttf.save(stream)
    stream.seek(0)
    test_ttf = TTFont(stream)
    test_ttf.reader.file.name = "in-memory-data.ttf"
    return test_ttf


@check_id("base_has_width")
def test_check_base_has_width(check):
    """Do some base characters have zero width?"""

    ttfont = get_test_font()

    assert_PASS(check(ttfont), "if acute has width...")

    ttfont["hmtx"].metrics["A"] = (0, 0)

    message = assert_results_contain(
        check(ttfont),
        FAIL,
        "zero-width-bases",
        "following glyphs had zero advance width",
    )
    assert "U+0041" in message
