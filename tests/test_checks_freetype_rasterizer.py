from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_freetype_rasterizer():
    """Ensure that the font can be rasterized by FreeType."""
    check = CheckTester("freetype_rasterizer")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("ancho/AnchoGX.ttf")
    msg = assert_results_contain(check(font), FAIL, "freetype-crash")
    assert "FT_Exception:  (too many function definitions)" in msg

    font = TEST_FILE("rubik/Rubik-Italic.ttf")
    msg = assert_results_contain(check(font), FAIL, "freetype-crash")
    assert "FT_Exception:  (stack overflow)" in msg

    # Example that segfaults with 'freetype-py' version 2.4.0
    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.ttf")
    assert_PASS(check(font), "with a good font...")
