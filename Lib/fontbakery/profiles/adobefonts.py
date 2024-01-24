"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
import unicodedata

from fontbakery.callable import check
from fontbakery.constants import (
    ALL_HANGUL_SYLLABLES_CODEPOINTS,
    MODERN_HANGUL_SYLLABLES_CODEPOINTS,
)
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message, KEEP_ORIGINAL_MESSAGE
from fontbakery.profiles.fontwerk import FONTWERK_PROFILE_CHECKS
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.notofonts import NOTOFONTS_PROFILE_CHECKS
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN, SKIP
from fontbakery.utils import add_check_overrides

profile_imports = (
    (".", ("shared_conditions", "universal", "fontwerk", "googlefonts", "notofonts")),
)
profile = profile_factory(default_section=Section("Adobe Fonts"))

SET_EXPLICIT_CHECKS = {
    # This is the set of explict checks that will be invoked
    # when fontbakery is run with the 'check-adobefonts' subcommand.
    # The contents of this set were last updated on September 6, 2023.
    #
    # =======================================
    # From adobefonts.py (this file)
    "com.adobe.fonts/check/family/consistent_upm",
    "com.adobe.fonts/check/find_empty_letters",
    "com.adobe.fonts/check/nameid_1_win_english",
    "com.adobe.fonts/check/unsupported_tables",
    "com.adobe.fonts/check/STAT_strings",
    #
    # =======================================
    # From cff.py
    "com.adobe.fonts/check/cff2_call_depth",
    "com.adobe.fonts/check/cff_call_depth",
    "com.adobe.fonts/check/cff_deprecated_operators",
    #
    # =======================================
    # From cmap.py
    "com.google.fonts/check/family/equal_unicode_encodings",
    #
    # =======================================
    # From dsig.py
    # "com.google.fonts/check/dsig",  # PERMANENTLY_EXCLUDED
    #
    # =======================================
    # From fontwerk.py
    # "com.fontwerk/check/style_linking",  # PERMANENTLY_EXCLUDED
    # "com.fontwerk/check/vendor_id",      # PERMANENTLY_EXCLUDED
    # "com.fontwerk/check/no_mac_entries",
    "com.fontwerk/check/inconsistencies_between_fvar_stat",  # IS_OVERRIDDEN
    "com.fontwerk/check/weight_class_fvar",  # IS_OVERRIDDEN
    #
    # =======================================
    # From fvar.py
    "com.adobe.fonts/check/varfont/distinct_instance_records",
    "com.adobe.fonts/check/varfont/same_size_instance_records",
    "com.adobe.fonts/check/varfont/valid_axis_nameid",
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",  # IS_OVERRIDDEN
    "com.adobe.fonts/check/varfont/valid_postscript_nameid",
    "com.adobe.fonts/check/varfont/valid_subfamily_nameid",
    "com.google.fonts/check/varfont/regular_ital_coord",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/regular_opsz_coord",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/regular_slnt_coord",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/regular_wdth_coord",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/regular_wght_coord",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/slnt_range",
    "com.google.fonts/check/varfont/wdth_valid_range",
    "com.google.fonts/check/varfont/wght_valid_range",
    "com.adobe.fonts/check/varfont/foundry_defined_tag_name",
    #
    # =======================================
    # From gdef.py
    # "com.google.fonts/check/gdef_mark_chars",
    # "com.google.fonts/check/gdef_non_mark_chars",
    # "com.google.fonts/check/gdef_spacing_marks",
    #
    # =======================================
    # From glyf.py
    "com.google.fonts/check/glyf_non_transformed_duplicate_components",
    "com.google.fonts/check/glyf_unused_data",
    "com.google.fonts/check/points_out_of_bounds",
    #
    # =======================================
    # From googlefonts.py
    # "com.google.fonts/check/varfont_weight_instances",  # weak rationale
    "com.google.fonts/check/aat",
    "com.google.fonts/check/fvar_name_entries",
    "com.google.fonts/check/varfont_duplicate_instance_names",
    "com.google.fonts/check/varfont/bold_wght_coord",  # IS_OVERRIDDEN
    #
    # =======================================
    # From gpos.py
    "com.google.fonts/check/gpos_kerning_info",
    #
    # =======================================
    # From head.py
    "com.google.fonts/check/family/equal_font_versions",
    "com.google.fonts/check/font_version",
    "com.google.fonts/check/unitsperem",
    #
    # =======================================
    # From hhea.py
    "com.google.fonts/check/linegaps",
    "com.google.fonts/check/maxadvancewidth",
    #
    # =======================================
    # From kern.py
    "com.google.fonts/check/kern_table",
    #
    # =======================================
    # From layout.py
    "com.google.fonts/check/layout_valid_feature_tags",
    "com.google.fonts/check/layout_valid_language_tags",
    "com.google.fonts/check/layout_valid_script_tags",
    #
    # =======================================
    # From loca.py
    "com.google.fonts/check/loca/maxp_num_glyphs",
    #
    # =======================================
    # From name.py
    # "com.google.fonts/check/name/no_copyright_on_description",  # PERMANENTLY_EXCLUDED # noqa
    "com.google.fonts/check/name/match_familyname_fullfont",  # IS_OVERRIDDEN
    "com.adobe.fonts/check/family/max_4_fonts_per_family_name",
    "com.adobe.fonts/check/family/consistent_family_name",
    "com.adobe.fonts/check/name/empty_records",
    "com.adobe.fonts/check/postscript_name",
    "com.adobe.fonts/check/name/postscript_name_consistency",
    "com.adobe.fonts/check/name/postscript_vs_cff",
    "com.google.fonts/check/family_naming_recommendations",
    "com.google.fonts/check/monospace",
    #
    # =======================================
    # From notofonts.py
    # "com.google.fonts/check/cmap/unexpected_subtables",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/comma_period",          # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/encoded_latin_digits",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/whitespace_advances",   # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_designer",         # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_manufacturer",     # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_trademark",        # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/os2/noto_vendor",            # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/cmap/alien_codepoints",
    # "com.google.fonts/check/unicode_range_bits",
    "com.google.fonts/check/cmap/format_12",
    #
    # =======================================
    # From os2.py
    # "com.google.fonts/check/xavgcharwidth",  # PERMANENTLY_EXCLUDED
    "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
    "com.adobe.fonts/check/fsselection_matches_macstyle",
    "com.google.fonts/check/code_pages",
    "com.google.fonts/check/family/panose_familytype",
    "com.google.fonts/check/family/panose_proportion",
    #
    # =======================================
    # From post.py
    "com.google.fonts/check/family/underline_thickness",
    "com.google.fonts/check/post_table_version",
    #
    # =======================================
    # From stat.py
    "com.adobe.fonts/check/stat_has_axis_value_tables",  # IS_OVERRIDDEN
    "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    #
    # =======================================
    # From universal.py
    # "com.google.fonts/check/whitespace_glyphnames",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/whitespace_ink",         # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/cjk_chws_feature",
    # "com.google.fonts/check/contour_count",
    # "com.google.fonts/check/dotted_circle",
    # "com.google.fonts/check/unreachable_glyphs",
    # "com.google.fonts/check/STAT_strings",
    # "com.google.fonts/check/transformed_components",
    # ---
    "com.google.fonts/check/family/win_ascent_and_descent",  # IS_OVERRIDDEN
    "com.google.fonts/check/fontbakery_version",  # IS_OVERRIDDEN
    "com.google.fonts/check/name/trailing_spaces",  # IS_OVERRIDDEN
    "com.google.fonts/check/os2_metrics_match_hhea",  # IS_OVERRIDDEN
    "com.google.fonts/check/valid_glyphnames",  # IS_OVERRIDDEN
    "com.google.fonts/check/whitespace_glyphs",  # IS_OVERRIDDEN
    # ---
    "com.adobe.fonts/check/freetype_rasterizer",
    "com.adobe.fonts/check/sfnt_version",
    "com.google.fonts/check/family/single_directory",
    "com.google.fonts/check/family/vertical_metrics",
    "com.google.fonts/check/gpos7",
    "com.google.fonts/check/mandatory_glyphs",
    "com.google.fonts/check/ots",
    "com.google.fonts/check/required_tables",
    "com.google.fonts/check/rupee",
    "com.google.fonts/check/ttx_roundtrip",
    "com.google.fonts/check/unique_glyphnames",
    "com.google.fonts/check/whitespace_widths",
}

CHECKS_IN_THIS_FILE = [
    "com.adobe.fonts/check/family/consistent_upm",
    "com.adobe.fonts/check/find_empty_letters",
    "com.adobe.fonts/check/nameid_1_win_english",
    "com.adobe.fonts/check/unsupported_tables",
    "com.adobe.fonts/check/STAT_strings",
]

SET_IMPORTED_CHECKS = set(
    UNIVERSAL_PROFILE_CHECKS
    + FONTWERK_PROFILE_CHECKS
    + GOOGLEFONTS_PROFILE_CHECKS
    + NOTOFONTS_PROFILE_CHECKS
)

ADOBEFONTS_PROFILE_CHECKS = [
    c for c in CHECKS_IN_THIS_FILE if c in SET_EXPLICIT_CHECKS
] + [c for c in SET_IMPORTED_CHECKS if c in SET_EXPLICIT_CHECKS]

OVERRIDDEN_CHECKS = [
    "com.adobe.fonts/check/stat_has_axis_value_tables",
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",
    "com.fontwerk/check/inconsistencies_between_fvar_stat",
    "com.fontwerk/check/weight_class_fvar",
    "com.google.fonts/check/family/win_ascent_and_descent",
    "com.google.fonts/check/fontbakery_version",
    "com.google.fonts/check/name/match_familyname_fullfont",
    "com.google.fonts/check/name/trailing_spaces",
    "com.google.fonts/check/os2_metrics_match_hhea",
    "com.google.fonts/check/valid_glyphnames",
    "com.google.fonts/check/varfont/bold_wght_coord",
    "com.google.fonts/check/varfont/regular_ital_coord",
    "com.google.fonts/check/varfont/regular_opsz_coord",
    "com.google.fonts/check/varfont/regular_slnt_coord",
    "com.google.fonts/check/varfont/regular_wdth_coord",
    "com.google.fonts/check/varfont/regular_wght_coord",
    "com.google.fonts/check/whitespace_glyphs",
]


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
    else:
        yield PASS, "Fonts have consistent units per em."


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
    else:
        yield PASS, "No unsupported tables were found."


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
    passed = True
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
            passed = False
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            f"The following AxisValue entries in the STAT table"
            f' should not contain "Italic":\n'
            f" {sorted(bad_values)}",
        )

    if passed:
        yield PASS, "Looks good!"


profile.auto_register(
    globals(),
    filter_func=lambda _, checkid, __: checkid
    not in SET_IMPORTED_CHECKS - SET_EXPLICIT_CHECKS,
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/whitespace_glyphs",
    overrides=(("missing-whitespace-glyph-0x00A0", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "For Adobe, this is not as severe"
        " as assessed in the original check for 0x00A0."
    ),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/name/trailing_spaces",
    overrides=(("trailing-space", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=("For Adobe, this is not as severe as assessed in the original check."),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/valid_glyphnames",
    overrides=(("found-invalid-names", WARN, KEEP_ORIGINAL_MESSAGE),),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/family/win_ascent_and_descent",
    overrides=(
        ("ascent", WARN, KEEP_ORIGINAL_MESSAGE),
        ("descent", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/os2_metrics_match_hhea",
    overrides=(
        ("ascender", WARN, KEEP_ORIGINAL_MESSAGE),
        ("descender", WARN, KEEP_ORIGINAL_MESSAGE),
        ("lineGap", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/fontbakery_version",
    overrides=(("connection-error", SKIP, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "For Adobe, users shouldn't be bothered with a failed check"
        " if their internet connection isn't functional.",
    ),
)


profile.check_log_override(
    # From name.py
    "com.google.fonts/check/name/match_familyname_fullfont",
    overrides=(("mismatch-font-names", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Many CFF OpenType fonts in circulation are built with the Microsoft platform"
        " Full font name string identical to the PostScript FontName in the CFF Name"
        " INDEX. This practice was documented in the OpenType spec until version 1.5.",
    ),
)


profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/varfont/bold_wght_coord",
    overrides=(
        ("no-bold-instance", WARN, KEEP_ORIGINAL_MESSAGE),
        ("wght-not-700", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
    reason=(
        "Adobe strongly recommends, but does not require having a Bold instance,"
        " and that instance should have coordinate 700 on the 'wght' axis."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_ital_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe strongly recommends, but does not require having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_opsz_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe strongly recommends, but does not require having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_slnt_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe strongly recommends, but does not require having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wdth_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe strongly recommends, but does not require having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wght_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe strongly recommends, but does not require having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",
    overrides=(
        ("invalid-default-instance-subfamily-name", WARN, KEEP_ORIGINAL_MESSAGE),
        ("invalid-default-instance-postscript-name", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
    reason=(
        "Adobe and the OpenType spec strongly recommend following these"
        " guidelines, but they are not hard requirements so we are relaxing"
        " this to WARN rather than FAIL.⏎"
        "Fonts that do not meet these guidelines might behave inconsistently"
        " so please carefully consider trying to meet them."
    ),
)


profile.check_log_override(
    # From stat.py
    "com.adobe.fonts/check/stat_has_axis_value_tables",
    overrides=(
        ("missing-axis-value-table", WARN, KEEP_ORIGINAL_MESSAGE),
        ("format-4-axis-count", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
    reason=(
        "Adobe and the OpenType spec strongly recommend following these"
        " guidelines, but they are not hard requirements so we are relaxing"
        " this to WARN rather than FAIL.⏎"
        "Fonts that do not meet these guidelines might behave inconsistently"
        " so please carefully consider trying to meet them."
    ),
)


profile.check_log_override(
    # From fontwerk.py
    "com.fontwerk/check/inconsistencies_between_fvar_stat",
    overrides=(("missing-fvar-instance-axis-value", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Fontwerk strongly recommend following this"
        " guideline, but it is not a hard requirement so we are relaxing"
        " this to WARN rather than FAIL.⏎"
        "Fonts that do not meet this guideline might behave inconsistently"
        " so please carefully consider trying to meet it."
    ),
)


profile.check_log_override(
    # From fontwerk.py
    "com.fontwerk/check/weight_class_fvar",
    overrides=(("bad-weight-class", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Fontwerk strongly recommend following this"
        " guideline, but it is not a hard requirement so we are relaxing"
        " this to WARN rather than FAIL.⏎"
        "Fonts that do not meet this guideline might behave inconsistently"
        " so please carefully consider trying to meet it."
    ),
)


ADOBEFONTS_PROFILE_CHECKS = add_check_overrides(
    ADOBEFONTS_PROFILE_CHECKS, profile.profile_tag, OVERRIDDEN_CHECKS
)

profile.test_expected_checks(ADOBEFONTS_PROFILE_CHECKS, exclusive=True)
