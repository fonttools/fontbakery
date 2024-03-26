"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
import unicodedata

from fontbakery.constants import (
    ALL_HANGUL_SYLLABLES_CODEPOINTS,
    MODERN_HANGUL_SYLLABLES_CODEPOINTS,
)
from fontbakery.prelude import check, Message, PASS, FAIL, WARN


@check(
    id="com.adobe.fonts/check/family/consistent_upm",
    rationale="""
        While not required by the OpenType spec, we (Adobe) expect that a group
        of fonts designed & produced as a family have consistent units per em.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2372",
)
def com_adobe_fonts_check_family_consistent_upm(ttFonts):
    """Fonts have consistent Units Per Em?"""
    upm_set = set()
    for ttFont in ttFonts:
        upm_set.add(ttFont["head"].unitsPerEm)
    if len(upm_set) > 1:
        yield FAIL, Message(
            "inconsistent-upem",
            f"Fonts have different units per em: {sorted(upm_set)}.",
        )


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
    id="com.adobe.fonts/check/find_empty_letters",
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
def com_adobe_fonts_check_find_empty_letters(ttFont):
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


@check(
    id="com.adobe.fonts/check/nameid_1_win_english",
    rationale="""
        While not required by the OpenType spec, Adobe Fonts' pipeline requires
        every font to support at least nameID 1 (Font Family name) for platformID 3
        (Windows), encodingID 1 (Unicode), and languageID 1033/0x409 (US-English).
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3714",
)
def com_adobe_fonts_check_nameid_1_win_english(ttFont, has_name_table):
    """Font has a good nameID 1, Windows/Unicode/US-English `name` table record?"""
    if not has_name_table:
        return FAIL, Message("name-table-not-found", "Font has no 'name' table.")

    nameid_1 = ttFont["name"].getName(1, 3, 1, 0x409)

    if nameid_1 is None:
        return FAIL, Message(
            "nameid-1-not-found",
            "Windows nameID 1 US-English record not found.",
        )

    try:
        nameid_1_unistr = nameid_1.toUnicode()
    except UnicodeDecodeError:
        return FAIL, Message(
            "nameid-1-decoding-error",
            "Windows nameID 1 US-English record could not be decoded.",
        )

    if not nameid_1_unistr.strip():
        return FAIL, Message(
            "nameid-1-empty",
            "Windows nameID 1 US-English record is empty.",
        )

    return PASS, "Font contains a good Windows nameID 1 US-English record."


@check(
    id="com.adobe.fonts/check/unsupported_tables",
    rationale="""
        Adobe Fonts' font-processing pipeline does not support all kinds of tables
        that can be included in OpenType font files.⏎
        Fonts that do not pass this check are guaranteed to be rejected by the pipeline.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3870",
)
def com_adobe_fonts_check_unsupported_tables(ttFont):
    """Does the font have any unsupported tables?"""
    SUPPORTED_TABLES = {
        "avar",
        "BASE",
        "CFF ",
        "CFF2",
        "cmap",
        "cvar",
        "cvt ",
        "DSIG",
        "feat",
        "fpgm",
        "fvar",
        "gasp",
        "GDEF",
        "glyf",
        "GPOS",
        "GSUB",
        "gvar",
        "hdmx",
        "head",
        "hhea",
        "hmtx",
        "HVAR",
        "kern",
        "loca",
        "LTSH",
        "maxp",
        "meta",
        "morx",
        "MVAR",
        "name",
        "OS/2",
        "PCLT",
        "post",
        "prep",
        "STAT",
        "SVG ",
        "VDMX",
        "vhea",
        "vmtx",
        "VORG",
        "VVAR",
    }
    font_tables = set(ttFont.keys())
    font_tables.discard("GlyphOrder")  # pseudo-table created by FontTools
    unsupported_tables = sorted(font_tables - SUPPORTED_TABLES)

    if unsupported_tables:
        unsupported_list = "".join(f"* {tag}\n" for tag in unsupported_tables)
        yield FAIL, Message(
            "unsupported-tables",
            f"The following unsupported font tables were found:\n\n{unsupported_list}",
        )


@check(
    id="com.adobe.fonts/check/STAT_strings",
    conditions=["has_STAT_table"],
    rationale="""
        In the STAT table, the "Italic" keyword must not be used on AxisValues
        for variation axes other than 'ital' or 'slnt'. This is a more lenient
        implementation of com.google.fonts/check/STAT_strings which allows "Italic"
        only for the 'ital' axis.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2863",
)
def com_adobe_fonts_check_STAT_strings(ttFont):
    """Check correctness of STAT table strings"""
    stat_table = ttFont["STAT"].table
    ital_slnt_axis_indices = []
    for index, axis in enumerate(stat_table.DesignAxisRecord.Axis):
        if axis.AxisTag in ("ital", "slnt"):
            ital_slnt_axis_indices.append(index)

    nameIDs = set()
    if ttFont["STAT"].table.AxisValueArray:
        for value in stat_table.AxisValueArray.AxisValue:
            if hasattr(value, "AxisIndex"):
                if value.AxisIndex not in ital_slnt_axis_indices:
                    nameIDs.add(value.ValueNameID)

            if hasattr(value, "AxisValueRecord"):
                for record in value.AxisValueRecord:
                    if record.AxisIndex not in ital_slnt_axis_indices:
                        nameIDs.add(value.ValueNameID)

    bad_values = set()
    for name in ttFont["name"].names:
        if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            f"The following AxisValue entries in the STAT table"
            f' should not contain "Italic":\n'
            f" {sorted(bad_values)}",
        )
