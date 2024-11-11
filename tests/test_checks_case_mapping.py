from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.utils import remove_cmap_entry


@check_id("case_mapping")
def test_check_case_mapping(check):
    """Ensure the font supports case swapping for all its glyphs."""

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    # Glyph present in the font                  Missing case-swapping counterpart
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # U+01D3: LATIN CAPITAL LETTER U WITH CARON  U+01D4: LATIN SMALL LETTER U WITH CARON
    # U+01E6: LATIN CAPITAL LETTER G WITH CARON  U+01E7: LATIN SMALL LETTER G WITH CARON
    # U+01F4: LATIN CAPITAL LETTER G WITH ACUTE  U+01F5: LATIN SMALL LETTER G WITH ACUTE
    assert_results_contain(check(ttFont), FAIL, "missing-case-counterparts")

    # While we'd expect designers to draw the missing counterparts,
    # for testing purposes we can simply delete the glyphs that lack a counterpart
    # to make the check PASS:
    remove_cmap_entry(ttFont, 0x01D3)
    remove_cmap_entry(ttFont, 0x01E6)
    remove_cmap_entry(ttFont, 0x01F4)
    assert_PASS(check(ttFont))

    # Let's add something which *does* have case swapping but which isn't a letter
    # to ensure the check doesn't fail for such glyphs.
    for table in ttFont["cmap"].tables:
        table.cmap[0x2160] = "uni2160"  # ROMAN NUMERAL ONE, which downcases to 0x2170
    assert 0x2170 not in ttFont.getBestCmap()
    assert_PASS(check(ttFont))
