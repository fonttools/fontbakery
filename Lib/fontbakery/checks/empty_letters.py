import unicodedata

from fontbakery.constants import (
    ALL_HANGUL_SYLLABLES_CODEPOINTS,
    MODERN_HANGUL_SYLLABLES_CODEPOINTS,
)
from fontbakery.prelude import check, Message, FAIL, WARN, PASS


def _quick_and_dirty_glyph_is_empty(font, glyph_name):
    """
    This is meant to be a quick-and-dirty test to see if a glyph is empty.
    Ideally we'd use the glyph_has_ink() method for this, but for a family of
    large CJK CFF fonts with tens of thousands of glyphs each, it's too slow.

    Caveat Utilitor:
    If this method returns True, the glyph is definitely empty.
    If this method returns False, the glyph *might* still be empty.
    """
    if "glyf" in font:
        glyph = font["glyf"][glyph_name]
        if not glyph.isComposite():
            if glyph.numberOfContours == 0:
                return True
        return False

    if "CFF2" in font:
        top_dict = font["CFF2"].cff.topDictIndex[0]
    else:
        top_dict = font["CFF "].cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    char_string = char_strings[glyph_name]
    if len(char_string.bytecode) <= 1:
        return True
    return False


@check(
    id="empty_letters",
    rationale="""
        Font language, script, and character set tagging approaches typically have an
        underlying assumption that letters (i.e. characters with Unicode general
        category 'Ll', 'Lm', 'Lo', 'Lt', or 'Lu', which includes CJK ideographs and
        Hangul syllables) with entries in the 'cmap' table have glyphs with ink (with
        a few exceptions, notably the four Hangul "filler" characters: U+115F, U+1160,
        U+3164, U+FFA0).

        This check is intended to identify fonts in which such letters have been mapped
        to empty glyphs (typically done as a form of subsetting). Letters with empty
        glyphs should have their entries removed from the 'cmap' table, even if the
        empty glyphs are left in place (e.g. for CID consistency).

        The check will yield only a WARN if the blank glyph maps to a character in the
        range of Korean hangul syllable code-points, which are known to be used by font
        designers as a workaround to undesired behavior from InDesign's Korean IME
        (Input Method Editor).

        More details available at https://github.com/fonttools/fontbakery/issues/2894
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2460",
)
def check_empty_letters(ttFont):
    """Letters in font have glyphs that are not empty?"""
    cmap = ttFont.getBestCmap()
    blank_ok_set = ALL_HANGUL_SYLLABLES_CODEPOINTS - MODERN_HANGUL_SYLLABLES_CODEPOINTS
    num_blank_hangul_glyphs = 0
    passed = True

    # http://unicode.org/reports/tr44/#General_Category_Values
    letter_categories = {
        "Ll",
        "Lm",
        "Lo",
        "Lt",
        "Lu",
    }
    invisible_letters = {
        # Hangul filler chars (category='Lo')
        0x115F,
        0x1160,
        0x3164,
        0xFFA0,
    }
    for unicode_val, glyph_name in cmap.items():
        category = unicodedata.category(chr(unicode_val))
        glyph_is_empty = _quick_and_dirty_glyph_is_empty(ttFont, glyph_name)

        if glyph_is_empty and unicode_val in blank_ok_set:
            num_blank_hangul_glyphs += 1
            passed = False

        elif (
            glyph_is_empty
            and (category in letter_categories)
            and (unicode_val not in invisible_letters)
        ):
            yield FAIL, Message(
                "empty-letter",
                f"U+{unicode_val:04X} should be visible, "
                f"but its glyph ({glyph_name!r}) is empty.",
            )
            passed = False

    if passed:
        yield PASS, "No empty glyphs for letters found."

    elif num_blank_hangul_glyphs:
        yield WARN, Message(
            "empty-hangul-letter",
            f"Found {num_blank_hangul_glyphs} empty hangul glyph(s).",
        )
