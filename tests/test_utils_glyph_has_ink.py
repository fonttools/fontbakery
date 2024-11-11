from fontTools.ttLib import TTFont

from fontbakery.codetesting import TEST_FILE
from fontbakery.utils import glyph_has_ink


def test_glyph_has_ink():
    print()  # so next line doesn't start with '.....'

    cff_test_font = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    print("Test if CFF glyph with ink has ink")
    assert glyph_has_ink(cff_test_font, ".notdef") is True
    print("Test if CFF glyph without ink has ink")
    assert glyph_has_ink(cff_test_font, "space") is False

    ttf_test_font = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Regular.ttf"))
    print("Test if TTF glyph with ink has ink")
    assert glyph_has_ink(ttf_test_font, ".notdef") is True
    print("Test if TTF glyph without ink has ink")
    assert glyph_has_ink(ttf_test_font, "space") is False

    cff2_test_font = TTFont(
        TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    )
    print("Test if CFF2 glyph with ink has ink")
    assert glyph_has_ink(cff2_test_font, ".notdef") is True
    print("Test if CFF2 glyph without ink has ink")
    assert glyph_has_ink(cff2_test_font, "space") is False
