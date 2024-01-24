"""
Checks for Type Network <https://typenetwork.com/>
"""
import unicodedata
import string

from fontbakery.callable import check, condition
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message, KEEP_ORIGINAL_MESSAGE
from fontbakery.profiles.adobefonts import ADOBEFONTS_PROFILE_CHECKS
from fontbakery.profiles.fontwerk import FONTWERK_PROFILE_CHECKS
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.notofonts import NOTOFONTS_PROFILE_CHECKS
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN, SKIP, INFO
from fontbakery.utils import (
    add_check_overrides,
    bullet_list,
    exit_with_install_instructions,
    pretty_print_list,
)
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)

profile_imports = (
    "fontbakery.profiles.shared_conditions",
    "fontbakery.profiles.universal",
    "fontbakery.profiles.fontwerk",
    "fontbakery.profiles.googlefonts",
    "fontbakery.profiles.notofonts",
    "fontbakery.profiles.adobefonts",
)

profile = profile_factory(default_section=Section("Type Network"))

SET_EXPLICIT_CHECKS = {
    # This is the set of explict checks that will be invoked when running thins profile.
    # The contents of this set were last updated on Tue 7, 2023.
    #
    # =======================================
    # From typenetwork.py (this file)
    "com.typenetwork/check/glyph_coverage",
    "com.typenetwork/check/vertical_metrics",
    "com.typenetwork/check/font_is_centered_vertically",
    "com.typenetwork/check/family/tnum_horizontal_metrics",
    "com.typenetwork/check/family/equal_numbers_of_glyphs",
    "com.typenetwork/check/usweightclass",
    "com.typenetwork/check/family/valid_underline",
    "com.typenetwork/check/family/valid_strikeout",
    "com.typenetwork/check/fstype",
    "com.typenetwork/check/composite_glyphs",
    "com.typenetwork/check/PUA_encoded_glyphs",
    "com.typenetwork/check/marks_width",
    "com.typenetwork/check/name/mandatory_entries",
    "com.typenetwork/check/varfont/axes_have_variation",
    "com.typenetwork/check/varfont/fvar_axes_order",
    "com.typenetwork/check/family/duplicated_names",
    #
    # =======================================
    # From adobefonts.py
    "com.adobe.fonts/check/family/consistent_upm",
    # "com.adobe.fonts/check/find_empty_letters", # The check is broken
    "com.adobe.fonts/check/nameid_1_win_english",
    "com.adobe.fonts/check/unsupported_tables",
    "com.adobe.fonts/check/STAT_strings",
    #
    # =======================================
    # From cff.py
    "com.adobe.fonts/check/cff_call_depth",
    "com.adobe.fonts/check/cff2_call_depth",
    "com.adobe.fonts/check/cff_deprecated_operators",
    #
    # =======================================
    # From cmap.py
    "com.google.fonts/check/family/equal_unicode_encodings",
    #
    # =======================================
    # From dsig.py
    "com.google.fonts/check/dsig",
    #
    # =======================================
    # From fontval.py
    "com.google.fonts/check/fontvalidator",
    #
    # =======================================
    # From fontwerk.py
    "com.fontwerk/check/no_mac_entries",
    # "com.fontwerk/check/vendor_id", # PERMANENTLY EXCLUDED
    "com.fontwerk/check/weight_class_fvar",
    "com.fontwerk/check/inconsistencies_between_fvar_stat",
    "com.fontwerk/check/style_linking",
    #
    # =======================================
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wght_coord",  # OVERRIDEN: Lowered to WARN
    "com.google.fonts/check/varfont/regular_wdth_coord",  # OVERRIDEN: Lowered to WARN
    "com.google.fonts/check/varfont/regular_slnt_coord",  # OVERRIDEN: Lowered to WARN
    "com.google.fonts/check/varfont/regular_ital_coord",  # OVERRIDEN: Lowered to WARN
    "com.google.fonts/check/varfont/regular_opsz_coord",  # OVERRIDEN: Lowered to WARN
    "com.google.fonts/check/varfont/wght_valid_range",
    "com.google.fonts/check/varfont/wdth_valid_range",
    "com.google.fonts/check/varfont/slnt_range",
    "com.typenetwork/check/varfont/ital_range",
    "com.adobe.fonts/check/varfont/valid_axis_nameid",
    "com.adobe.fonts/check/varfont/valid_subfamily_nameid",
    "com.adobe.fonts/check/varfont/valid_postscript_nameid",
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",
    "com.adobe.fonts/check/varfont/same_size_instance_records",
    "com.adobe.fonts/check/varfont/distinct_instance_records",
    "com.adobe.fonts/check/varfont/foundry_defined_tag_name",
    #
    # =======================================
    # From gdef.py
    "com.google.fonts/check/gdef_spacing_marks",
    "com.google.fonts/check/gdef_mark_chars",
    "com.google.fonts/check/gdef_non_mark_chars",  # OVERRIDEN
    #
    # =======================================
    # From glyf.py
    "com.google.fonts/check/glyf_unused_data",
    "com.google.fonts/check/points_out_of_bounds",
    "com.google.fonts/check/glyf_non_transformed_duplicate_components",
    #
    # =======================================
    # From googlefonts.py
    "com.google.fonts/check/family/equal_codepoint_coverage",
    "com.google.fonts/check/vendor_id",
    # "com.google.fonts/check/metadata/unreachable_subsetting", # Review
    # "com.google.fonts/check/gasp", # Review
    # "com.google.fonts/check/metadata/valid_nameid25", # TEMPORARY EXCLUDED
    # "com.google.fonts/check/metadata/primary_script", # Review
    # "com.google.fonts/check/glyphsets/shape_languages", # Review
    "com.google.fonts/check/slant_direction",
    "com.google.fonts/check/negative_advance_width",
    "com.google.fonts/check/glyf_nested_components",
    "com.google.fonts/check/varfont/consistent_axes",
    "com.google.fonts/check/smart_dropout",  # OVERRIDEN
    "com.google.fonts/check/vttclean",
    "com.google.fonts/check/aat",
    "com.google.fonts/check/fvar_name_entries",
    "com.google.fonts/check/ligature_carets",
    "com.google.fonts/check/kerning_for_non_ligated_sequences",
    "com.google.fonts/check/name/family_and_style_max_length",
    "com.google.fonts/check/family/control_chars",
    "com.google.fonts/check/varfont_duplicate_instance_names",
    # "com.google.fonts/check/varfont/duplexed_axis_reflow", # Review
    # "com.google.fonts/check/STAT/axis_order",
    "com.google.fonts/check/mandatory_avar_table",
    "com.google.fonts/check/missing_small_caps_glyphs",
    "com.google.fonts/check/stylisticset_description",
    # "com.google.fonts/check/os2/use_typo_metrics", # Removed in favor of
    #                                                # new vmetrics check
    # "com.google.fonts/check/metadata/empty_designer", # Review
    "com.google.fonts/check/varfont/bold_wght_coord",  # OVERRIDEN: Lowered to WARN
    #
    # =======================================
    # From gpos.py
    "com.google.fonts/check/gpos_kerning_info",
    #
    # =======================================
    # From head.py
    "com.google.fonts/check/family/equal_font_versions",
    "com.google.fonts/check/unitsperem",
    "com.google.fonts/check/font_version",
    "com.google.fonts/check/mac_style",
    #
    # =======================================
    # From hhea.py
    "com.google.fonts/check/maxadvancewidth",
    "com.google.fonts/check/caret_slope",
    #
    # =======================================
    # From kern.py
    "com.google.fonts/check/kern_table",
    #
    # =======================================
    # From layout.py
    "com.google.fonts/check/layout_valid_feature_tags",
    "com.google.fonts/check/layout_valid_script_tags",
    "com.google.fonts/check/layout_valid_language_tags",
    #
    # =======================================
    # From loca.py
    "com.google.fonts/check/loca/maxp_num_glyphs",
    #
    # =======================================
    # From name.py
    "com.adobe.fonts/check/name/empty_records",
    # "com.google.fonts/check/name/no_copyright_on_description", # PERMANENTLY_EXCLUDED
    "com.google.fonts/check/monospace",
    "com.google.fonts/check/name/match_familyname_fullfont",  # OVERRIDEN
    "com.adobe.fonts/check/postscript_name",  # REVIEW
    "com.google.fonts/check/family_naming_recommendations",
    "com.adobe.fonts/check/name/postscript_vs_cff",
    "com.adobe.fonts/check/name/postscript_name_consistency",
    "com.adobe.fonts/check/family/max_4_fonts_per_family_name",
    "com.adobe.fonts/check/family/consistent_family_name",
    "com.google.fonts/check/name/italic_names",
    #
    # =======================================
    # From notofonts.py
    # "com.google.fonts/check/cmap/unexpected_subtables", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/unicode_range_bits", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_manufacturer", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_designer", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_trademark", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/cmap/format_12", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/os2/noto_vendor", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/encoded_latin_digits", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/comma_period", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/whitespace_advances", # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/cmap/alien_codepoints", # PERMANENTLY_EXCLUDED
    #
    # =======================================
    # From os2.py
    "com.google.fonts/check/family/panose_proportion",
    "com.google.fonts/check/family/panose_familytype",
    "com.google.fonts/check/xavgcharwidth",
    "com.adobe.fonts/check/fsselection_matches_macstyle",
    "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
    "com.google.fonts/check/code_pages",
    # "com.thetypefounders/check/vendor_id", # PERMANENTLY_EXCLUDED
    "com.google.fonts/check/fsselection",
    #
    # =======================================
    # From outline.py
    "com.google.fonts/check/outline_alignment_miss",
    "com.google.fonts/check/outline_short_segments",
    "com.google.fonts/check/outline_colinear_vectors",
    "com.google.fonts/check/outline_jaggy_segments",
    "com.google.fonts/check/outline_semi_vertical",
    #
    # =======================================
    # From post.py
    "com.google.fonts/check/family/underline_thickness",
    "com.google.fonts/check/post_table_version",
    "com.google.fonts/check/italic_angle",
    #
    # =======================================
    # From shaping.py
    # "com.google.fonts/check/shaping/regression",
    # "com.google.fonts/check/shaping/forbidden",
    # "com.google.fonts/check/shaping/collides",
    "com.google.fonts/check/dotted_circle",  # REVIEW
    "com.google.fonts/check/soft_dotted",  # REVIEW
    #
    # =======================================
    # From stat.py
    "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    "com.adobe.fonts/check/stat_has_axis_value_tables",
    "com.google.fonts/check/italic_axis_in_stat",
    "com.google.fonts/check/italic_axis_in_stat_is_boolean",
    "com.google.fonts/check/italic_axis_last",
    #
    # =======================================
    # From universal.py
    "com.google.fonts/check/name/trailing_spaces",
    "com.google.fonts/check/family/win_ascent_and_descent",
    # "com.google.fonts/check/os2_metrics_match_hhea", # Removed in favor of
    #                                                  # new vmetrics check
    "com.google.fonts/check/family/single_directory",
    # "com.google.fonts/check/caps_vertically_centered", # REVIEW
    "com.google.fonts/check/ots",  # OVERRIDEN
    # "com.google.fonts/check/fontbakery_version", # Permanently Removed
    "com.google.fonts/check/mandatory_glyphs",
    "com.google.fonts/check/whitespace_glyphs",
    "com.google.fonts/check/whitespace_glyphnames",
    "com.google.fonts/check/whitespace_ink",
    "com.google.fonts/check/arabic_spacing_symbols",
    "com.google.fonts/check/arabic_high_hamza",
    "com.google.fonts/check/required_tables",
    "com.google.fonts/check/unwanted_tables",
    "com.google.fonts/check/valid_glyphnames",
    "com.google.fonts/check/unique_glyphnames",
    "com.google.fonts/check/ttx_roundtrip",
    "com.google.fonts/check/family/vertical_metrics",
    # 'com.google.fonts/check/superfamily/list', # PERMANENTLY EXCLUDED
    "com.google.fonts/check/superfamily/vertical_metrics",
    "com.google.fonts/check/rupee",
    "com.google.fonts/check/unreachable_glyphs",
    "com.google.fonts/check/contour_count",
    "com.google.fonts/check/soft_hyphen",
    # 'com.google.fonts/check/cjk_chws_feature', # PERMANENTLY EXCLUDED
    "com.google.fonts/check/transformed_components",  # OVERRIDEN
    "com.google.fonts/check/gpos7",
    "com.adobe.fonts/check/freetype_rasterizer",
    "com.adobe.fonts/check/sfnt_version",
    "com.google.fonts/check/whitespace_widths",
    "com.google.fonts/check/interpolation_issues",
    "com.google.fonts/check/math_signs_width",  # OVERRIDEN
    "com.google.fonts/check/linegaps",
    "com.google.fonts/check/STAT_in_statics",
    # "com.google.fonts/check/alt_caron",  # PERMANENTLY EXCLUDED
}

CHECKS_IN_THIS_FILE = [
    "com.typenetwork/check/glyph_coverage",
    "com.typenetwork/check/vertical_metrics",
    "com.typenetwork/check/font_is_centered_vertically",
    "com.typenetwork/check/family/tnum_horizontal_metrics",
    "com.typenetwork/check/family/equal_numbers_of_glyphs",
    "com.typenetwork/check/usweightclass",
    "com.typenetwork/check/family/valid_underline",
    "com.typenetwork/check/family/valid_strikeout",
    "com.typenetwork/check/fstype",
    "com.typenetwork/check/composite_glyphs",
    "com.typenetwork/check/PUA_encoded_glyphs",
    "com.typenetwork/check/marks_width",
    "com.typenetwork/check/name/mandatory_entries",
    "com.typenetwork/check/varfont/axes_have_variation",
    "com.typenetwork/check/varfont/fvar_axes_order",
    "com.typenetwork/check/family/duplicated_names",
]

SET_IMPORTED_CHECKS = set(
    UNIVERSAL_PROFILE_CHECKS
    + ADOBEFONTS_PROFILE_CHECKS
    + FONTWERK_PROFILE_CHECKS
    + GOOGLEFONTS_PROFILE_CHECKS
    + NOTOFONTS_PROFILE_CHECKS
)

TYPENETWORK_PROFILE_CHECKS = [
    c for c in CHECKS_IN_THIS_FILE if c in SET_EXPLICIT_CHECKS
] + [c for c in SET_IMPORTED_CHECKS if c in SET_EXPLICIT_CHECKS]

OVERRIDDEN_CHECKS = [
    "com.fontwerk/check/no_mac_entries",
    "com.google.fonts/check/family/single_directory",
    "com.google.fonts/check/glyf_nested_components",
    "com.google.fonts/check/ligature_carets",
    "com.google.fonts/check/kerning_for_non_ligated_sequences",
    "com.google.fonts/check/varfont/bold_wght_coord",
    "com.google.fonts/check/varfont/regular_ital_coord",
    "com.google.fonts/check/varfont/regular_opsz_coord",
    "com.google.fonts/check/varfont/regular_slnt_coord",
    "com.google.fonts/check/varfont/regular_wdth_coord",
    "com.google.fonts/check/varfont/regular_wght_coord",
    "com.google.fonts/check/gdef_non_mark_chars",
    "com.google.fonts/check/math_signs_width",
    "com.google.fonts/check/dotted_circle",
    "com.google.fonts/check/soft_dotted",
    "com.google.fonts/check/smart_dropout",
    "com.google.fonts/check/name/match_familyname_fullfont",
    "com.google.fonts/check/transformed_components",
    "com.google.fonts/check/ots",
]


@check(
    id="com.typenetwork/check/glyph_coverage",
    rationale="""
        Type Network expects that fonts in its catalog support at least the minimal
        set of characters.
    """,
    conditions=["font_codepoints"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_glyph_coverage(ttFont, font_codepoints, config):
    """Check Type Network minimum glyph coverage."""
    try:
        import unicodedata2
    except ImportError:
        exit_with_install_instructions()

    TN_latin_set = {
        0x0020: (" ", "SPACE"),
        0x0021: ("!", "EXCLAMATION MARK"),
        0x0022: ('"', "QUOTATION MARK"),
        0x0023: ("#", "NUMBER SIGN"),
        0x0024: ("$", "DOLLAR SIGN"),
        0x0025: ("%", "PERCENT SIGN"),
        0x0026: ("&", "AMPERSAND"),
        0x0027: ("'", "APOSTROPHE"),
        0x0028: ("(", "LEFT PARENTHESIS"),
        0x0029: (")", "RIGHT PARENTHESIS"),
        0x002A: ("*", "ASTERISK"),
        0x002B: ("+", "PLUS SIGN"),
        0x002C: (",", "COMMA"),
        0x002D: ("-", "HYPHEN-MINUS"),
        0x002E: (".", "FULL STOP"),
        0x002F: ("/", "SOLIDUS"),
        0x0030: ("0", "DIGIT ZERO"),
        0x0031: ("1", "DIGIT ONE"),
        0x0032: ("2", "DIGIT TWO"),
        0x0033: ("3", "DIGIT THREE"),
        0x0034: ("4", "DIGIT FOUR"),
        0x0035: ("5", "DIGIT FIVE"),
        0x0036: ("6", "DIGIT SIX"),
        0x0037: ("7", "DIGIT SEVEN"),
        0x0038: ("8", "DIGIT EIGHT"),
        0x0039: ("9", "DIGIT NINE"),
        0x003A: (":", "COLON"),
        0x003B: (";", "SEMICOLON"),
        0x003C: ("<", "LESS-THAN SIGN"),
        0x003D: ("=", "EQUALS SIGN"),
        0x003E: (">", "GREATER-THAN SIGN"),
        0x003F: ("?", "QUESTION MARK"),
        0x0040: ("@", "COMMERCIAL AT"),
        0x0041: ("A", "LATIN CAPITAL LETTER A"),
        0x0042: ("B", "LATIN CAPITAL LETTER B"),
        0x0043: ("C", "LATIN CAPITAL LETTER C"),
        0x0044: ("D", "LATIN CAPITAL LETTER D"),
        0x0045: ("E", "LATIN CAPITAL LETTER E"),
        0x0046: ("F", "LATIN CAPITAL LETTER F"),
        0x0047: ("G", "LATIN CAPITAL LETTER G"),
        0x0048: ("H", "LATIN CAPITAL LETTER H"),
        0x0049: ("I", "LATIN CAPITAL LETTER I"),
        0x004A: ("J", "LATIN CAPITAL LETTER J"),
        0x004B: ("K", "LATIN CAPITAL LETTER K"),
        0x004C: ("L", "LATIN CAPITAL LETTER L"),
        0x004D: ("M", "LATIN CAPITAL LETTER M"),
        0x004E: ("N", "LATIN CAPITAL LETTER N"),
        0x004F: ("O", "LATIN CAPITAL LETTER O"),
        0x0050: ("P", "LATIN CAPITAL LETTER P"),
        0x0051: ("Q", "LATIN CAPITAL LETTER Q"),
        0x0052: ("R", "LATIN CAPITAL LETTER R"),
        0x0053: ("S", "LATIN CAPITAL LETTER S"),
        0x0054: ("T", "LATIN CAPITAL LETTER T"),
        0x0055: ("U", "LATIN CAPITAL LETTER U"),
        0x0056: ("V", "LATIN CAPITAL LETTER V"),
        0x0057: ("W", "LATIN CAPITAL LETTER W"),
        0x0058: ("X", "LATIN CAPITAL LETTER X"),
        0x0059: ("Y", "LATIN CAPITAL LETTER Y"),
        0x005A: ("Z", "LATIN CAPITAL LETTER Z"),
        0x005B: ("[", "LEFT SQUARE BRACKET"),
        0x005C: ("\\", "REVERSE SOLIDUS"),
        0x005D: ("]", "RIGHT SQUARE BRACKET"),
        0x005E: ("^", "ASCII CIRCUMFLEX ACCENT"),
        0x005F: ("_", "LOW LINE"),
        0x0060: ("`", "GRAVE ACCENT"),
        0x0061: ("a", "LATIN SMALL LETTER A"),
        0x0062: ("b", "LATIN SMALL LETTER B"),
        0x0063: ("c", "LATIN SMALL LETTER C"),
        0x0064: ("d", "LATIN SMALL LETTER D"),
        0x0065: ("e", "LATIN SMALL LETTER E"),
        0x0066: ("f", "LATIN SMALL LETTER F"),
        0x0067: ("g", "LATIN SMALL LETTER G"),
        0x0068: ("h", "LATIN SMALL LETTER H"),
        0x0069: ("i", "LATIN SMALL LETTER I"),
        0x006A: ("j", "LATIN SMALL LETTER J"),
        0x006B: ("k", "LATIN SMALL LETTER K"),
        0x006C: ("l", "LATIN SMALL LETTER L"),
        0x006D: ("m", "LATIN SMALL LETTER M"),
        0x006E: ("n", "LATIN SMALL LETTER N"),
        0x006F: ("o", "LATIN SMALL LETTER O"),
        0x0070: ("p", "LATIN SMALL LETTER P"),
        0x0071: ("q", "LATIN SMALL LETTER Q"),
        0x0072: ("r", "LATIN SMALL LETTER R"),
        0x0073: ("s", "LATIN SMALL LETTER S"),
        0x0074: ("t", "LATIN SMALL LETTER T"),
        0x0075: ("u", "LATIN SMALL LETTER U"),
        0x0076: ("v", "LATIN SMALL LETTER V"),
        0x0077: ("w", "LATIN SMALL LETTER W"),
        0x0078: ("x", "LATIN SMALL LETTER X"),
        0x0079: ("y", "LATIN SMALL LETTER Y"),
        0x007A: ("z", "LATIN SMALL LETTER Z"),
        0x007B: ("{", "LEFT CURLY BRACKET"),
        0x007C: ("|", "VERTICAL LINE"),
        0x007D: ("}", "RIGHT CURLY BRACKET"),
        0x007E: ("~", "TILDE"),
        0x00A0: (" ", "NO-BREAK SPACE"),
        0x00A1: ("¡", "INVERTED EXCLAMATION MARK"),
        0x00A2: ("¢", "CENT SIGN"),
        0x00A3: ("£", "POUND SIGN"),
        0x00A4: ("¤", "CURRENCY SIGN"),
        0x00A5: ("¥", "YEN SIGN"),
        0x00A6: ("¦", "BROKEN BAR"),
        0x00A7: ("§", "SECTION SIGN"),
        0x00A8: ("¨", "DIAERESIS"),
        0x00A9: ("©", "COPYRIGHT SIGN"),
        0x00AA: ("ª", "FEMININE ORDINAL INDICATOR"),
        0x00AB: ("«", "LEFT-POINTING DOUBLE ANGLE QUOTATION MARK"),
        0x00AC: ("¬", "NOT SIGN"),
        0x00AD: ("­", "SOFT HYPHEN"),
        0x00AE: ("®", "REGISTERED SIGN"),
        0x00AF: ("¯", "MACRON"),
        0x00B0: ("°", "DEGREE SIGN"),
        0x00B1: ("±", "PLUS-MINUS SIGN"),
        0x00B2: ("²", "SUPERSCRIPT TWO"),
        0x00B3: ("³", "SUPERSCRIPT THREE"),
        0x00B4: ("´", "ACUTE ACCENT"),
        0x00B6: ("¶", "PILCROW SIGN"),
        0x00B7: ("·", "MIDDLE DOT"),
        0x00B8: ("¸", "CEDILLA"),
        0x00B9: ("¹", "SUPERSCRIPT ONE"),
        0x00BA: ("º", "MASCULINE ORDINAL INDICATOR"),
        0x00BB: ("»", "RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK"),
        0x00BC: ("¼", "VULGAR FRACTION ONE QUARTER"),
        0x00BD: ("½", "VULGAR FRACTION ONE HALF"),
        0x00BE: ("¾", "VULGAR FRACTION THREE QUARTERS"),
        0x00BF: ("¿", "INVERTED QUESTION MARK"),
        0x00C0: ("À", "LATIN CAPITAL LETTER A WITH GRAVE"),
        0x00C1: ("Á", "LATIN CAPITAL LETTER A WITH ACUTE"),
        0x00C2: ("Â", "LATIN CAPITAL LETTER A WITH CIRCUMFLEX"),
        0x00C3: ("Ã", "LATIN CAPITAL LETTER A WITH TILDE"),
        0x00C4: ("Ä", "LATIN CAPITAL LETTER A WITH DIAERESIS"),
        0x00C5: ("Å", "LATIN CAPITAL LETTER A WITH RING ABOVE"),
        0x00C6: ("Æ", "LATIN CAPITAL LETTER AE"),
        0x00C7: ("Ç", "LATIN CAPITAL LETTER C WITH CEDILLA"),
        0x00C8: ("È", "LATIN CAPITAL LETTER E WITH GRAVE"),
        0x00C9: ("É", "LATIN CAPITAL LETTER E WITH ACUTE"),
        0x00CA: ("Ê", "LATIN CAPITAL LETTER E WITH CIRCUMFLEX"),
        0x00CB: ("Ë", "LATIN CAPITAL LETTER E WITH DIAERESIS"),
        0x00CC: ("Ì", "LATIN CAPITAL LETTER I WITH GRAVE"),
        0x00CD: ("Í", "LATIN CAPITAL LETTER I WITH ACUTE"),
        0x00CE: ("Î", "LATIN CAPITAL LETTER I WITH CIRCUMFLEX"),
        0x00CF: ("Ï", "LATIN CAPITAL LETTER I WITH DIAERESIS"),
        0x00D0: ("Ð", "LATIN CAPITAL LETTER ETH"),
        0x00D1: ("Ñ", "LATIN CAPITAL LETTER N WITH TILDE"),
        0x00D2: ("Ò", "LATIN CAPITAL LETTER O WITH GRAVE"),
        0x00D3: ("Ó", "LATIN CAPITAL LETTER O WITH ACUTE"),
        0x00D4: ("Ô", "LATIN CAPITAL LETTER O WITH CIRCUMFLEX"),
        0x00D5: ("Õ", "LATIN CAPITAL LETTER O WITH TILDE"),
        0x00D6: ("Ö", "LATIN CAPITAL LETTER O WITH DIAERESIS"),
        0x00D7: ("×", "MULTIPLICATION SIGN"),
        0x00D8: ("Ø", "LATIN CAPITAL LETTER O WITH STROKE"),
        0x00D9: ("Ù", "LATIN CAPITAL LETTER U WITH GRAVE"),
        0x00DA: ("Ú", "LATIN CAPITAL LETTER U WITH ACUTE"),
        0x00DB: ("Û", "LATIN CAPITAL LETTER U WITH CIRCUMFLEX"),
        0x00DC: ("Ü", "LATIN CAPITAL LETTER U WITH DIAERESIS"),
        0x00DD: ("Ý", "LATIN CAPITAL LETTER Y WITH ACUTE"),
        0x00DE: ("Þ", "LATIN CAPITAL LETTER THORN"),
        0x00DF: ("ß", "LATIN SMALL LETTER SHARP S"),
        0x00E0: ("à", "LATIN SMALL LETTER A WITH GRAVE"),
        0x00E1: ("á", "LATIN SMALL LETTER A WITH ACUTE"),
        0x00E2: ("â", "LATIN SMALL LETTER A WITH CIRCUMFLEX"),
        0x00E3: ("ã", "LATIN SMALL LETTER A WITH TILDE"),
        0x00E4: ("ä", "LATIN SMALL LETTER A WITH DIAERESIS"),
        0x00E5: ("å", "LATIN SMALL LETTER A WITH RING ABOVE"),
        0x00E6: ("æ", "LATIN SMALL LETTER AE"),
        0x00E7: ("ç", "LATIN SMALL LETTER C WITH CEDILLA"),
        0x00E8: ("è", "LATIN SMALL LETTER E WITH GRAVE"),
        0x00E9: ("é", "LATIN SMALL LETTER E WITH ACUTE"),
        0x00EA: ("ê", "LATIN SMALL LETTER E WITH CIRCUMFLEX"),
        0x00EB: ("ë", "LATIN SMALL LETTER E WITH DIAERESIS"),
        0x00EC: ("ì", "LATIN SMALL LETTER I WITH GRAVE"),
        0x00ED: ("í", "LATIN SMALL LETTER I WITH ACUTE"),
        0x00EE: ("î", "LATIN SMALL LETTER I WITH CIRCUMFLEX"),
        0x00EF: ("ï", "LATIN SMALL LETTER I WITH DIAERESIS"),
        0x00F0: ("ð", "LATIN SMALL LETTER ETH"),
        0x00F1: ("ñ", "LATIN SMALL LETTER N WITH TILDE"),
        0x00F2: ("ò", "LATIN SMALL LETTER O WITH GRAVE"),
        0x00F3: ("ó", "LATIN SMALL LETTER O WITH ACUTE"),
        0x00F4: ("ô", "LATIN SMALL LETTER O WITH CIRCUMFLEX"),
        0x00F5: ("õ", "LATIN SMALL LETTER O WITH TILDE"),
        0x00F6: ("ö", "LATIN SMALL LETTER O WITH DIAERESIS"),
        0x00F7: ("÷", "DIVISION SIGN"),
        0x00F8: ("ø", "LATIN SMALL LETTER O WITH STROKE"),
        0x00F9: ("ù", "LATIN SMALL LETTER U WITH GRAVE"),
        0x00FA: ("ú", "LATIN SMALL LETTER U WITH ACUTE"),
        0x00FB: ("û", "LATIN SMALL LETTER U WITH CIRCUMFLEX"),
        0x00FC: ("ü", "LATIN SMALL LETTER U WITH DIAERESIS"),
        0x00FD: ("ý", "LATIN SMALL LETTER Y WITH ACUTE"),
        0x00FE: ("þ", "LATIN SMALL LETTER THORN"),
        0x00FF: ("ÿ", "LATIN SMALL LETTER Y WITH DIAERESIS"),
        0x0100: ("Ā", "LATIN CAPITAL LETTER A WITH MACRON"),
        0x0101: ("ā", "LATIN SMALL LETTER A WITH MACRON"),
        0x0102: ("Ă", "LATIN CAPITAL LETTER A WITH BREVE"),
        0x0103: ("ă", "LATIN SMALL LETTER A WITH BREVE"),
        0x0104: ("Ą", "LATIN CAPITAL LETTER A WITH OGONEK"),
        0x0105: ("ą", "LATIN SMALL LETTER A WITH OGONEK"),
        0x0106: ("Ć", "LATIN CAPITAL LETTER C WITH ACUTE"),
        0x0107: ("ć", "LATIN SMALL LETTER C WITH ACUTE"),
        0x0108: ("Ĉ", "LATIN CAPITAL LETTER C WITH CIRCUMFLEX"),
        0x0109: ("ĉ", "LATIN SMALL LETTER C WITH CIRCUMFLEX"),
        0x010A: ("Ċ", "LATIN CAPITAL LETTER C WITH DOT ABOVE"),
        0x010B: ("ċ", "LATIN SMALL LETTER C WITH DOT ABOVE"),
        0x010C: ("Č", "LATIN CAPITAL LETTER C WITH CARON"),
        0x010D: ("č", "LATIN SMALL LETTER C WITH CARON"),
        0x010E: ("Ď", "LATIN CAPITAL LETTER D WITH CARON"),
        0x010F: ("ď", "LATIN SMALL LETTER D WITH CARON"),
        0x0110: ("Đ", "LATIN CAPITAL LETTER D WITH STROKE"),
        0x0111: ("đ", "LATIN SMALL LETTER D WITH STROKE"),
        0x0112: ("Ē", "LATIN CAPITAL LETTER E WITH MACRON"),
        0x0113: ("ē", "LATIN SMALL LETTER E WITH MACRON"),
        0x0114: ("Ĕ", "LATIN CAPITAL LETTER E WITH BREVE"),
        0x0115: ("ĕ", "LATIN SMALL LETTER E WITH BREVE"),
        0x0116: ("Ė", "LATIN CAPITAL LETTER E WITH DOT ABOVE"),
        0x0117: ("ė", "LATIN SMALL LETTER E WITH DOT ABOVE"),
        0x0118: ("Ę", "LATIN CAPITAL LETTER E WITH OGONEK"),
        0x0119: ("ę", "LATIN SMALL LETTER E WITH OGONEK"),
        0x011A: ("Ě", "LATIN CAPITAL LETTER E WITH CARON"),
        0x011B: ("ě", "LATIN SMALL LETTER E WITH CARON"),
        0x011C: ("Ĝ", "LATIN CAPITAL LETTER G WITH CIRCUMFLEX"),
        0x011D: ("ĝ", "LATIN SMALL LETTER G WITH CIRCUMFLEX"),
        0x011E: ("Ğ", "LATIN CAPITAL LETTER G WITH BREVE"),
        0x011F: ("ğ", "LATIN SMALL LETTER G WITH BREVE"),
        0x0120: ("Ġ", "LATIN CAPITAL LETTER G WITH DOT ABOVE"),
        0x0121: ("ġ", "LATIN SMALL LETTER G WITH DOT ABOVE"),
        0x0122: ("Ģ", "LATIN CAPITAL LETTER G WITH CEDILLA"),
        0x0123: ("ģ", "LATIN SMALL LETTER G WITH CEDILLA"),
        0x0124: ("Ĥ", "LATIN CAPITAL LETTER H WITH CIRCUMFLEX"),
        0x0125: ("ĥ", "LATIN SMALL LETTER H WITH CIRCUMFLEX"),
        0x0126: ("Ħ", "LATIN CAPITAL LETTER H WITH STROKE"),
        0x0127: ("ħ", "LATIN SMALL LETTER H WITH STROKE"),
        0x0128: ("Ĩ", "LATIN CAPITAL LETTER I WITH TILDE"),
        0x0129: ("ĩ", "LATIN SMALL LETTER I WITH TILDE"),
        0x012A: ("Ī", "LATIN CAPITAL LETTER I WITH MACRON"),
        0x012B: ("ī", "LATIN SMALL LETTER I WITH MACRON"),
        0x012C: ("Ĭ", "LATIN CAPITAL LETTER I WITH BREVE"),
        0x012D: ("ĭ", "LATIN SMALL LETTER I WITH BREVE"),
        0x012E: ("Į", "LATIN CAPITAL LETTER I WITH OGONEK"),
        0x012F: ("į", "LATIN SMALL LETTER I WITH OGONEK"),
        0x0130: ("İ", "LATIN CAPITAL LETTER I WITH DOT ABOVE"),
        0x0131: ("ı", "LATIN SMALL LETTER DOTLESS I"),
        0x0132: ("Ĳ", "LATIN CAPITAL LIGATURE IJ"),
        0x0133: ("ĳ", "LATIN SMALL LIGATURE IJ"),
        0x0134: ("Ĵ", "LATIN CAPITAL LETTER J WITH CIRCUMFLEX"),
        0x0135: ("ĵ", "LATIN SMALL LETTER J WITH CIRCUMFLEX"),
        0x0136: ("Ķ", "LATIN CAPITAL LETTER K WITH CEDILLA"),
        0x0137: ("ķ", "LATIN SMALL LETTER K WITH CEDILLA"),
        0x0139: ("Ĺ", "LATIN CAPITAL LETTER L WITH ACUTE"),
        0x013A: ("ĺ", "LATIN SMALL LETTER L WITH ACUTE"),
        0x013B: ("Ļ", "LATIN CAPITAL LETTER L WITH CEDILLA"),
        0x013C: ("ļ", "LATIN SMALL LETTER L WITH CEDILLA"),
        0x013D: ("Ľ", "LATIN CAPITAL LETTER L WITH CARON"),
        0x013E: ("ľ", "LATIN SMALL LETTER L WITH CARON"),
        0x013F: ("Ŀ", "LATIN CAPITAL LETTER L WITH MIDDLE DOT"),
        0x0140: ("ŀ", "LATIN SMALL LETTER L WITH MIDDLE DOT"),
        0x0141: ("Ł", "LATIN CAPITAL LETTER L WITH STROKE"),
        0x0142: ("ł", "LATIN SMALL LETTER L WITH STROKE"),
        0x0143: ("Ń", "LATIN CAPITAL LETTER N WITH ACUTE"),
        0x0144: ("ń", "LATIN SMALL LETTER N WITH ACUTE"),
        0x0145: ("Ņ", "LATIN CAPITAL LETTER N WITH CEDILLA"),
        0x0146: ("ņ", "LATIN SMALL LETTER N WITH CEDILLA"),
        0x0147: ("Ň", "LATIN CAPITAL LETTER N WITH CARON"),
        0x0148: ("ň", "LATIN SMALL LETTER N WITH CARON"),
        0x014A: ("Ŋ", "LATIN CAPITAL LETTER ENG"),
        0x014B: ("ŋ", "LATIN SMALL LETTER ENG"),
        0x014C: ("Ō", "LATIN CAPITAL LETTER O WITH MACRON"),
        0x014D: ("ō", "LATIN SMALL LETTER O WITH MACRON"),
        0x014E: ("Ŏ", "LATIN CAPITAL LETTER O WITH BREVE"),
        0x014F: ("ŏ", "LATIN SMALL LETTER O WITH BREVE"),
        0x0150: ("Ő", "LATIN CAPITAL LETTER O WITH DOUBLE ACUTE"),
        0x0151: ("ő", "LATIN SMALL LETTER O WITH DOUBLE ACUTE"),
        0x0152: ("Œ", "LATIN CAPITAL LIGATURE OE"),
        0x0153: ("œ", "LATIN SMALL LIGATURE OE"),
        0x0154: ("Ŕ", "LATIN CAPITAL LETTER R WITH ACUTE"),
        0x0155: ("ŕ", "LATIN SMALL LETTER R WITH ACUTE"),
        0x0156: ("Ŗ", "LATIN CAPITAL LETTER R WITH CEDILLA"),
        0x0157: ("ŗ", "LATIN SMALL LETTER R WITH CEDILLA"),
        0x0158: ("Ř", "LATIN CAPITAL LETTER R WITH CARON"),
        0x0159: ("ř", "LATIN SMALL LETTER R WITH CARON"),
        0x015A: ("Ś", "LATIN CAPITAL LETTER S WITH ACUTE"),
        0x015B: ("ś", "LATIN SMALL LETTER S WITH ACUTE"),
        0x015C: ("Ŝ", "LATIN CAPITAL LETTER S WITH CIRCUMFLEX"),
        0x015D: ("ŝ", "LATIN SMALL LETTER S WITH CIRCUMFLEX"),
        0x015E: ("Ş", "LATIN CAPITAL LETTER S WITH CEDILLA"),
        0x015F: ("ş", "LATIN SMALL LETTER S WITH CEDILLA"),
        0x0160: ("Š", "LATIN CAPITAL LETTER S WITH CARON"),
        0x0161: ("š", "LATIN SMALL LETTER S WITH CARON"),
        0x0164: ("Ť", "LATIN CAPITAL LETTER T WITH CARON"),
        0x0165: ("ť", "LATIN SMALL LETTER T WITH CARON"),
        0x0166: ("Ŧ", "LATIN CAPITAL LETTER T WITH STROKE"),
        0x0167: ("ŧ", "LATIN SMALL LETTER T WITH STROKE"),
        0x0168: ("Ũ", "LATIN CAPITAL LETTER U WITH TILDE"),
        0x0169: ("ũ", "LATIN SMALL LETTER U WITH TILDE"),
        0x016A: ("Ū", "LATIN CAPITAL LETTER U WITH MACRON"),
        0x016B: ("ū", "LATIN SMALL LETTER U WITH MACRON"),
        0x016C: ("Ŭ", "LATIN CAPITAL LETTER U WITH BREVE"),
        0x016D: ("ŭ", "LATIN SMALL LETTER U WITH BREVE"),
        0x016E: ("Ů", "LATIN CAPITAL LETTER U WITH RING ABOVE"),
        0x016F: ("ů", "LATIN SMALL LETTER U WITH RING ABOVE"),
        0x0170: ("Ű", "LATIN CAPITAL LETTER U WITH DOUBLE ACUTE"),
        0x0171: ("ű", "LATIN SMALL LETTER U WITH DOUBLE ACUTE"),
        0x0172: ("Ų", "LATIN CAPITAL LETTER U WITH OGONEK"),
        0x0173: ("ų", "LATIN SMALL LETTER U WITH OGONEK"),
        0x0174: ("Ŵ", "LATIN CAPITAL LETTER W WITH CIRCUMFLEX"),
        0x0175: ("ŵ", "LATIN SMALL LETTER W WITH CIRCUMFLEX"),
        0x0176: ("Ŷ", "LATIN CAPITAL LETTER Y WITH CIRCUMFLEX"),
        0x0177: ("ŷ", "LATIN SMALL LETTER Y WITH CIRCUMFLEX"),
        0x0178: ("Ÿ", "LATIN CAPITAL LETTER Y WITH DIAERESIS"),
        0x0179: ("Ź", "LATIN CAPITAL LETTER Z WITH ACUTE"),
        0x017A: ("ź", "LATIN SMALL LETTER Z WITH ACUTE"),
        0x017B: ("Ż", "LATIN CAPITAL LETTER Z WITH DOT ABOVE"),
        0x017C: ("ż", "LATIN SMALL LETTER Z WITH DOT ABOVE"),
        0x017D: ("Ž", "LATIN CAPITAL LETTER Z WITH CARON"),
        0x017E: ("ž", "LATIN SMALL LETTER Z WITH CARON"),
        0x01FC: ("Ǽ", "LATIN CAPITAL LETTER AE WITH ACUTE"),
        0x01FD: ("ǽ", "LATIN SMALL LETTER AE WITH ACUTE"),
        0x01FE: ("Ǿ", "LATIN CAPITAL LETTER O WITH STROKE AND ACUTE"),
        0x01FF: ("ǿ", "LATIN SMALL LETTER O WITH STROKE AND ACUTE"),
        0x0218: ("Ș", "LATIN CAPITAL LETTER S WITH COMMA BELOW"),
        0x0219: ("ș", "LATIN SMALL LETTER S WITH COMMA BELOW"),
        0x021A: ("Ț", "LATIN CAPITAL LETTER T WITH COMMA BELOW"),
        0x021B: ("ț", "LATIN SMALL LETTER T WITH COMMA BELOW"),
        0x0237: ("ȷ", "LATIN SMALL LETTER DOTLESS J"),
        0x02C6: ("ˆ", "CIRCUMFLEX ACCENT"),
        0x02C7: ("ˇ", "CARON"),
        0x02D8: ("˘", "BREVE"),
        0x02D9: ("˙", "DOT ABOVE"),
        0x02DA: ("˚", "RING ABOVE"),
        0x02DB: ("˛", "OGONEK"),
        0x02DC: ("˜", "TILDE"),
        0x02DD: ("˝", "DOUBLE ACUTE ACCENT"),
        0x1E80: ("Ẁ", "LATIN CAPITAL LETTER W WITH GRAVE"),
        0x1E81: ("ẁ", "LATIN SMALL LETTER W WITH GRAVE"),
        0x1E82: ("Ẃ", "LATIN CAPITAL LETTER W WITH ACUTE"),
        0x1E83: ("ẃ", "LATIN SMALL LETTER W WITH ACUTE"),
        0x1E84: ("Ẅ", "LATIN CAPITAL LETTER W WITH DIAERESIS"),
        0x1E85: ("ẅ", "LATIN SMALL LETTER W WITH DIAERESIS"),
        0x1E9E: ("ẞ", "LATIN CAPITAL LETTER SHARP S"),
        0x1EF2: ("Ỳ", "LATIN CAPITAL LETTER Y WITH GRAVE"),
        0x1EF3: ("ỳ", "LATIN SMALL LETTER Y WITH GRAVE"),
        0x2013: ("–", "EN DASH"),
        0x2014: ("—", "EM DASH"),
        0x2018: ("‘", "LEFT SINGLE QUOTATION MARK"),
        0x2019: ("’", "RIGHT SINGLE QUOTATION MARK"),
        0x201A: ("‚", "SINGLE LOW-9 QUOTATION MARK"),
        0x201C: ("“", "LEFT DOUBLE QUOTATION MARK"),
        0x201D: ("”", "RIGHT DOUBLE QUOTATION MARK"),
        0x201E: ("„", "DOUBLE LOW-9 QUOTATION MARK"),
        0x2020: ("†", "DAGGER"),
        0x2021: ("‡", "DOUBLE DAGGER"),
        0x2022: ("•", "BULLET"),
        0x2026: ("…", "HORIZONTAL ELLIPSIS"),
        0x2030: ("‰", "PER MILLE SIGN"),
        0x2039: ("‹", "SINGLE LEFT-POINTING ANGLE QUOTATION MARK"),
        0x203A: ("›", "SINGLE RIGHT-POINTING ANGLE QUOTATION MARK"),
        0x2044: ("⁄", "FRACTION SLASH"),
        0x20AC: ("€", "EURO SIGN"),
        0x2122: ("™", "TRADE MARK SIGN"),
        0x2248: ("≈", "ALMOST EQUAL TO"),
        0x2260: ("≠", "NOT EQUAL TO"),
        0x2264: ("≤", "LESS-THAN OR EQUAL TO"),
        0x2265: ("≥", "GREATER-THAN OR EQUAL TO"),
        # 0x00B5: ("µ", "MICRO SIGN"),
        # 0x0394: ("Δ", "GREEK CAPITAL LETTER DELTA"),
        # 0x03A9: ("Ω", "GREEK CAPITAL LETTER OMEGA"),
        # 0x03BC: ("μ", "GREEK SMALL LETTER MU"),
        # 0x03C0: ("π", "GREEK SMALL LETTER PI"),
        # 0x2126: ("Ω", "OHM SIGN"),
        # 0x2202: ("∂", "PARTIAL DIFFERENTIAL"),
        # 0x2206: ("∆", "INCREMENT"),
        # 0x220F: ("∏", "N-ARY PRODUCT"),
        # 0x2211: ("∑", "N-ARY SUMMATION"),
        # 0x2212: ("−", "MINUS SIGN"),
        # 0x221A: ("√", "SQUARE ROOT"),
        # 0x221E: ("∞", "INFINITY"),
        # 0x222B: ("∫", "INTEGRAL"),
        # 0x25CA: ("◊", "LOZENGE"),
        # 0xFB01: ("ﬁ", "LATIN SMALL LIGATURE FI"),
        # 0xFB02: ("ﬂ", "LATIN SMALL LIGATURE FL"),
    }

    required_codepoints = set(TN_latin_set)
    diff = required_codepoints - font_codepoints
    missing = []
    for c in sorted(diff):
        try:
            missing.append("uni%04X %s (%s)\n" % (c, chr(c), unicodedata2.name(chr(c))))
        except ValueError:
            pass
    if missing:
        yield WARN, Message(
            "missing-codepoints",
            f"Missing required codepoints:\n\n" f"{bullet_list(config, missing)}",
        )
    else:
        yield PASS, "OK"


@check(
    id="com.typenetwork/check/vertical_metrics",
    rationale="""
        OS/2 and hhea vertical metric values should match. This will produce the
        same linespacing on Mac, GNU+Linux and Windows.

        - Mac OS X uses the hhea values.⏎
        - Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.

        When OS/2 and hhea vertical metrics match, the same linespacing results on
        macOS, GNU+Linux and Windows.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_vertical_metrics(ttFont):
    """Checking vertical metrics."""

    # Check required tables exist on font
    required_tables = {"hhea", "OS/2"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    useTypoMetric = ttFont["OS/2"].fsSelection & (1 << 7)

    hheaAscent_equals_typoAscent = ttFont["hhea"].ascent == ttFont["OS/2"].sTypoAscender
    hheaDescent_equals_typoDescent = abs(ttFont["hhea"].descent) == abs(
        ttFont["OS/2"].sTypoDescender
    )

    hheaAscent_equals_winAscent = ttFont["hhea"].ascent == ttFont["OS/2"].usWinAscent
    hheaDescent_equals_winDescent = (
        abs(ttFont["hhea"].descent) == ttFont["OS/2"].usWinDescent
    )

    typoMetricsSum = (
        ttFont["OS/2"].sTypoAscender
        + abs(ttFont["OS/2"].sTypoDescender)
        + ttFont["OS/2"].sTypoLineGap
    )
    hheaMetricsSum = (
        ttFont["hhea"].ascent + abs(ttFont["hhea"].descent) + ttFont["hhea"].lineGap
    )

    if useTypoMetric:
        if not hheaAscent_equals_typoAscent:
            yield FAIL, Message(
                "ascender",
                f"OS/2 sTypoAscender ({ttFont['OS/2'].sTypoAscender})"
                f" and hhea ascent ({ttFont['hhea'].ascent}) must be equal.",
            )
        elif not hheaDescent_equals_typoDescent:
            yield FAIL, Message(
                "descender",
                f"OS/2 sTypoDescender ({ttFont['OS/2'].sTypoDescender})"
                f" and hhea descent ({ttFont['hhea'].descent}) must be equal.",
            )
        elif ttFont["OS/2"].sTypoLineGap != 0:
            yield FAIL, Message("hhea", "typo lineGap is not equal to 0.")
        elif ttFont["hhea"].lineGap != 0:
            yield FAIL, Message("hhea", "hhea lineGap is not equal to 0.")
        else:
            yield PASS, "Typo and hhea metrics are equal."
    else:
        yield WARN, Message(
            "metrics-recommendation",
            "OS/2 fsSelection USE_TYPO_METRICS is not enabled.\n\n"
            "Type Networks recommends to enable it and follow the vertical metrics"
            " scheme where basically hhea matches typo metrics. Read in more detail"
            " about it in our vertical metrics guide.",
        )

        if hheaAscent_equals_typoAscent and hheaDescent_equals_winDescent:
            yield FAIL, Message(
                "useTypoMetricsDisabled",
                "OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is not enabled",
            )
        elif not hheaAscent_equals_winAscent:
            yield FAIL, Message(
                "ascender",
                f"hhea ascent ({ttFont['hhea'].ascent})"
                f" and OS/2 win ascent ({ttFont['OS/2'].usWinAscent}) must be equal.",
            )
        elif not hheaDescent_equals_winDescent:
            yield FAIL, Message(
                "descender",
                f"hhea descent ({ttFont['hhea'].descent})"
                f" and OS/2 win ascent ({ttFont['OS/2'].usWinDescent}) must be equal.",
            )
        elif typoMetricsSum != hheaMetricsSum:
            yield FAIL, Message(
                "typo-and-hhea-sum",
                f"OS/2 typo metrics sum ({typoMetricsSum}) must be"
                f" equal to win metrics sum ({hheaMetricsSum})",
            )
        else:
            yield PASS, "hhea and Win metrics are equal and useTypoMetrics is disabled."


@check(
    id="com.typenetwork/check/font_is_centered_vertically",
    rationale="""
        FIXME! This check still does not have rationale documentation.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_font_is_centered_vertically(ttFont):
    """Checking if font is vertically centered."""

    # Check required tables exist on font
    required_tables = {"hhea", "OS/2"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    capHeight = ttFont["OS/2"].sCapHeight
    ascent = ttFont["hhea"].ascent - capHeight
    descent = abs(ttFont["hhea"].descent)

    ratio = abs(ascent - descent) / max(ascent, descent)
    threshold1 = 0.1
    threshold2 = 0.3

    if threshold1 >= ratio > threshold2:
        yield WARN, Message(
            "uncentered",
            "The font will display slightly vertically uncentered on"
            " web environments.",
        )
        yield WARN, Message(
            "uncentered",
            f"The font will display vertically uncentered on"
            f" web environments. Top space above cap height is {ascent}"
            f" and under baseline is {descent}",
        )
    elif ratio >= threshold2:
        yield FAIL, Message(
            "very-uncentered",
            f"The font will display significantly vertically uncentered on"
            f" web environments. Top space above cap height is {ascent}"
            f" and under baseline is {descent}",
        )
    else:
        yield PASS, Message(
            "centered",
            "The font will display vertically centered on web environments.",
        )


@condition
def stylename(ttFont):
    if ttFont["name"].getDebugName(16):
        styleName = ttFont["name"].getDebugName(17)
    else:
        styleName = ttFont["name"].getDebugName(2)
    return styleName


@condition
def tn_expected_os2_weight(stylename):
    """The weight name and the expected OS/2 usWeightClass value inferred from
    the style part of the font name.
    Here the common/expected values and weight names:
    250, Thin
    275, ExtraLight
    300, Light
    400, Regular
    500, Medium
    600, SemiBold
    700, Bold
    800, ExtraBold
    900, Black
    Thin is not set to 100 because of legacy Windows GDI issues:
    https://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html
    """
    if not stylename:
        return None
    # Weight name to value mapping:
    TN_EXPECTED_WEIGHTS = {
        "Thin": 100,
        "ExtraLight": 200,
        "Light": 300,
        "Regular": 400,
        "Medium": 500,
        "SemiBold": 600,
        "Bold": 700,
        "ExtraBold": 800,
        "Black": 900,
    }
    if stylename == "Italic":
        weight_name = "Regular"
    elif stylename.endswith("Italic"):
        weight_name = stylename.replace("Italic", "").rstrip()
    elif stylename.endswith("Oblique"):
        weight_name = stylename.replace("Oblique", "").rstrip()
    else:
        weight_name = stylename

    expected = None
    for expectedWeightName, expectedWeightValue in TN_EXPECTED_WEIGHTS.items():
        if expectedWeightName.lower() in weight_name.lower().split(" "):
            expected = expectedWeightValue
            break

    return {"name": weight_name, "weightClass": expected}


@check(
    id="com.typenetwork/check/usweightclass",
    conditions=["tn_expected_os2_weight"],
    rationale="""
        For Variable Fonts, it should be equal to default wght, for static ttfs,
        Thin-Black can be 100-900 or 250-900,
        for static otfs, Thin-Black must be 250-900.

        If static otfs are set lower than 250, text may appear blurry in
        legacy Windows applications.
        Glyphsapp users can change the usWeightClass value of an instance by adding
        a 'weightClass' customParameter.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_usweightclass(ttFont, tn_expected_os2_weight):
    """Checking OS/2 usWeightClass."""
    from fontbakery.profiles.shared_conditions import (
        is_ttf,
        is_cff,
        is_variable_font,
        has_wght_axis,
    )

    failed = False
    expected_value = tn_expected_os2_weight["weightClass"]
    weight_name = tn_expected_os2_weight["name"]
    os2_value = ttFont["OS/2"].usWeightClass

    fail_message = "OS/2 usWeightClass is '{}' when it should be '{}'."
    no_value_message = "OS/2 usWeightClass is '{}' and weight name is '{}'."

    if is_variable_font(ttFont):
        fvar = ttFont["fvar"]
        if has_wght_axis(ttFont):
            default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}
            fvar_value = default_axis_values.get("wght")

            if os2_value != int(fvar_value):
                failed = True
                yield FAIL, Message(
                    "bad-value", fail_message.format(os2_value, fvar_value)
                )
        else:
            if os2_value != 400:
                failed = True
                yield FAIL, Message("bad-value", fail_message.format(os2_value, 400))
    # overrides for static Thin and ExtaLight fonts
    # for static ttfs, we don't mind if Thin is 250 and ExtraLight is 275.
    # However, if the values are incorrect we will recommend they set Thin
    # to 100 and ExtraLight to 250.
    # for static otfs, Thin must be 250 and ExtraLight must be 275

    elif not expected_value:
        failed = True
        yield INFO, Message("no-value", no_value_message.format(os2_value, weight_name))

    elif "Thin" == weight_name.split(" "):
        if is_ttf(ttFont) and os2_value not in [100, 250]:
            failed = True
            yield FAIL, Message(
                "bad-value", fail_message.format(os2_value, expected_value)
            )
        if is_cff(ttFont) and os2_value != 250:
            failed = True
            yield FAIL, Message("bad-value", fail_message.format(os2_value, 250))

    elif "ExtraLight" in weight_name.split(" "):
        if is_ttf(ttFont) and os2_value not in [200, 275]:
            failed = True
            yield FAIL, Message(
                "bad-value", fail_message.format(os2_value, expected_value)
            )
        if is_cff(ttFont) and os2_value != 275:
            failed = True
            yield FAIL, Message("bad-value", fail_message.format(os2_value, 275))

    elif os2_value != expected_value:
        failed = True
        yield FAIL, Message("bad-value", fail_message.format(os2_value, expected_value))

    if not failed:
        yield PASS, "OS/2 usWeightClass is good"


@check(
    id="com.typenetwork/check/family/tnum_horizontal_metrics",
    rationale="""
        Tabular figures need to have the same metrics in all styles in order to allow
        tables to be set with proper typographic control, but to maintain the placement
        of decimals and numeric columns between rows.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_family_tnum_horizontal_metrics(ttFonts, config):
    """All tabular figures must have the same width across the family."""
    tnum_widths = {}
    half_width_glyphs = {}
    for ttFont in list(ttFonts):
        glyphs = ttFont.getGlyphSet()

        tabular_suffixes = (".tnum", ".tf", ".tosf", ".tsc", ".tab", ".tabular")
        tnum_glyphs = [
            (glyph_id, glyphs[glyph_id])
            for glyph_id in glyphs.keys()
            if any(suffix in glyph_id for suffix in tabular_suffixes)
        ]

        for glyph_id, glyph in tnum_glyphs:
            if glyph.width not in tnum_widths:
                tnum_widths[glyph.width] = [glyph_id]
            else:
                tnum_widths[glyph.width].append(glyph_id)

    max_num = 0
    most_common_width = None
    half_width = None

    # Get most common width
    for width, glyphs in tnum_widths.items():
        if len(glyphs) > max_num:
            max_num = len(glyphs)
            most_common_width = width
    if most_common_width:
        del tnum_widths[most_common_width]

    # Get Half width
    for width, glyphs in tnum_widths.items():
        if round(most_common_width / 2) == width:
            half_width = width
            half_width_glyphs = glyphs

    if half_width:
        del tnum_widths[half_width]

    if half_width:
        yield INFO, Message(
            "half-widths",
            f"The are other glyphs with half of the width ({half_width}) of the"
            f" most common width such as the following ones:\n\n"
            f"{bullet_list(config, half_width_glyphs)}.",
        )

    if len(tnum_widths.keys()):
        # prepare string to display
        tnumWidthsString = ""
        for width, glyphs in tnum_widths.items():
            tnumWidthsString += f"{width}: {pretty_print_list(config, glyphs)}\n\n"
        yield WARN, Message(
            "inconsistent-widths",
            f"The most common tabular glyph width is {most_common_width}."
            f" But there are other tabular glyphs with different widths"
            f" such as the following ones:\n\n{tnumWidthsString}.",
        )
    else:
        yield PASS, "OK"


@condition
def roman_ttFonts(ttFonts):
    from fontbakery.profiles.shared_conditions import is_italic

    return [ttFont for ttFont in ttFonts if not is_italic(ttFont)]


@condition
def italic_ttFonts(ttFonts):
    italicFonts = []
    from fontbakery.profiles.shared_conditions import is_italic

    for ttFont in ttFonts:
        if is_italic(ttFont):
            italicFonts.append(ttFont)
    return italicFonts


@check(
    id="com.typenetwork/check/family/equal_numbers_of_glyphs",
    rationale="""
        Check if all fonts in a family have the same number of glyphs.
    """,
    conditions=["roman_ttFonts", "italic_ttFonts"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def equal_numbers_of_glyphs(roman_ttFonts, italic_ttFonts):
    """Equal number of glyphs"""
    max_roman_count = 0
    max_roman_font = None
    roman_failed_fonts = {}

    # Checks roman
    for ttFont in list(roman_ttFonts):
        fontname = ttFont.reader.file.name
        this_count = ttFont["maxp"].numGlyphs
        if this_count > max_roman_count:
            max_roman_count = this_count
            max_roman_font = fontname

    for ttFont in list(roman_ttFonts):
        this_count = ttFont["maxp"].numGlyphs
        fontname = ttFont.reader.file.name
        if this_count != max_roman_count:
            roman_failed_fonts[fontname] = this_count

    max_italic_count = 0
    max_italic_font = None
    italic_failed_fonts = {}

    # Checks Italics
    for ttFont in list(italic_ttFonts):
        fontname = ttFont.reader.file.name
        this_count = ttFont["maxp"].numGlyphs
        if this_count > max_italic_count:
            max_italic_count = this_count
            max_italic_font = fontname

    for ttFont in list(italic_ttFonts):
        this_count = ttFont["maxp"].numGlyphs
        fontname = ttFont.reader.file.name
        if this_count != max_italic_count:
            italic_failed_fonts[fontname] = this_count

    if len(roman_failed_fonts) > 0:
        yield WARN, Message(
            "roman-different-number-of-glyphs",
            f"Romans doesn’t have the same number of glyphs"
            f"{max_roman_font} has {max_roman_count} and \n\t{roman_failed_fonts}",
        )
    else:
        yield PASS, (
            "All roman files in this family have an equal total ammount of glyphs."
        )

    if len(italic_failed_fonts) > 0:
        yield WARN, Message(
            "italic-different-number-of-glyphs",
            f"Italics doesn’t have the same number of glyphs"
            f"{max_italic_font} has {max_italic_count} and \n\t{italic_failed_fonts}",
        )
    else:
        yield PASS, (
            "All italics files in this family have an equal total ammount of glyphs."
        )


@check(
    id="com.typenetwork/check/family/valid_underline",
    rationale="""
        If underline thickness is not set nothing gets rendered on Figma.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
    misc_metadata={"affects": [("Figma", "unspecified")]},
)
def com_typenetwork_check_family_valid_underline(ttFont):
    """Fonts have underline thickness?"""
    underlineThickness = None
    failedThickness = False

    underlineThickness = ttFont["post"].underlineThickness
    if underlineThickness is None or underlineThickness == 0:
        failedThickness = True

    if failedThickness:
        msg = f"Thickness of the underline is {underlineThickness} which is not valid."
        yield FAIL, Message("invalid-underline-thickness", msg)
    else:
        yield PASS, "Fonts have a valid underline thickness."


@check(
    id="com.typenetwork/check/family/valid_strikeout",
    rationale="""
        If strikeout size is not set, nothing gets rendered on Figma.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
    misc_metadata={"affects": [("Figma", "unspecified")]},
)
def com_typenetwork_check_family_valid_strikeout(ttFont):
    """Fonts have strikeout size?"""
    strikeoutSize = None
    failedThickness = False

    strikeoutSize = ttFont["OS/2"].yStrikeoutSize
    if strikeoutSize is None or strikeoutSize == 0:
        failedThickness = True

    if failedThickness:
        msg = f"Size of the strikeout is {strikeoutSize} which is not valid."
        yield FAIL, Message("invalid-strikeout-size", msg)
    else:
        yield PASS, "Fonts have a valid strikeout size."


@check(
    id="com.typenetwork/check/fstype",
    rationale="""
        The fsType in the OS/2 table is a legacy DRM-related field.
        Type Network's EULA is more accurately represented by setting it to 4,
        also known as 'Print & Preview'.

        This setting indicates that the fonts may be embedded, and temporarily loaded
        on the remote system, but documents that use it must not be editable.

        More detailed info is available at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_fstype(ttFont):
    """Checking OS/2 fsType does not impose restrictions."""
    value = ttFont["OS/2"].fsType

    FSTYPE_RESTRICTIONS = {
        0x0002: (
            "* The font must not be modified, embedded or exchanged in"
            " any manner without first obtaining permission of"
            " the legal owner."
        ),
        0x0004: (
            "The font may be embedded, and temporarily loaded on the"
            " remote system, but documents that use it must"
            " not be editable."
        ),
        0x0008: (
            "The font may be embedded but must only be installed"
            " temporarily on other systems."
        ),
        0x0100: ("The font may not be subsetted prior to embedding."),
        0x0200: (
            "Only bitmaps contained in the font may be embedded."
            " No outline data may be embedded."
        ),
    }
    restrictions = ""
    for bit_mask in FSTYPE_RESTRICTIONS.keys():
        if value & bit_mask:
            restrictions += FSTYPE_RESTRICTIONS[bit_mask]

    if value & 0b1111110011110001:
        restrictions += (
            "* There are reserved bits set, which indicates an invalid setting."
        )

    if value != 0x0004:
        yield WARN, Message(
            "no-preview-print",
            f"In this font fsType is set to {value} meaning that:\n"
            f"{restrictions}\n"
            "\n"
            "TN advises setting the fsType to bit 4, Print & Preview, which"
            "matches TN’s EULA.",
        )
    else:
        yield PASS, "OS/2 fsType is properly set to 'Print & Preview'."


@check(
    id="com.typenetwork/check/composite_glyphs",
    rationale="""
        For performance reasons, it is recommended that TTF fonts use composite glyphs.
    """,
    conditions=["is_ttf"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_composite_glyphs(ttFont):
    """Check if TTF font uses composite glyphs."""
    baseGlyphs = [*string.printable]
    failed = []

    numberOfGlyphs = ttFont["maxp"].numGlyphs
    for glyph_name in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyph_name]
        if glyph_name not in baseGlyphs and glyph.isComposite() is False:
            failed.append(glyph_name)

    percentageOfNotCompositeGlyphs = round(len(failed) * 100 / numberOfGlyphs)
    if percentageOfNotCompositeGlyphs > 50:
        yield WARN, Message(
            "low-composites",
            f"{percentageOfNotCompositeGlyphs}% of the glyphs are not composites.",
        )
    else:
        yield PASS, (
            f"{100-percentageOfNotCompositeGlyphs}% of the glyphs are composites."
        )


@check(
    id="com.typenetwork/check/PUA_encoded_glyphs",
    rationale="""
        Using Private Use Area (PUA) encodings is not recommended. They are
        defined by users and are not standardized. That said, PUA are font
        specific so they will break if the user tries to copy/paste,
        search/replace, or change the font. Using PUA to encode small caps,
        for example, is not recommended as small caps can and should be
        accessible via Open Type substitution instead.

        If you must encode your characters in the Private Use Area (PUA),
        do so with great caution.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_PUA_encoded_glyphs(ttFont, config):
    """Check if font has PUA encoded glyphs."""

    def in_PUA_range(codepoint):
        """
        Three private use areas are defined:
        one in the Basic Multilingual Plane (U+E000–U+F8FF),
        and one each in, and nearly covering, planes 15 and 16
        (U+F0000–U+FFFFD, U+100000–U+10FFFD).
        """
        return (
            (codepoint >= 0xE000 and codepoint <= 0xF8FF)
            or (codepoint >= 0xF0000 and codepoint <= 0xFFFFD)
            or (codepoint >= 0x100000 and codepoint <= 0x10FFFD)
        )

    pua_encoded_glyphs = []

    for cp, glyphName in ttFont.getBestCmap().items():
        if in_PUA_range(cp) and cp != 0xF8FF:
            pua_encoded_glyphs.append(glyphName + f" U+{cp:02x}".upper())

    if pua_encoded_glyphs:
        yield WARN, Message(
            "pua-encoded",
            f"Glyphs with PUA codepoints:\n\n"
            f"{bullet_list(config, pua_encoded_glyphs)}",
        )
    else:
        yield PASS, "No PUA encoded glyphs."


@check(
    id="com.typenetwork/check/marks_width",
    rationale="""
        To avoid incorrect overlappings when typing, glyphs that are spacing marks
        must have width, on the other hand, combining marks should be 0 width.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_marks_width(ttFont, config):
    """Check if marks glyphs have the correct width."""

    def _is_non_spacing_mark_char(charcode):
        category = unicodedata.category(chr(charcode))
        if category in ("Mn", "Me"):
            return True

    def _is_spacing_mark_char(charcode):
        category = unicodedata.category(chr(charcode))
        if category in ("Sk", "Lm"):
            return True

    cmap = ttFont["cmap"].getBestCmap()
    glyphSet = ttFont.getGlyphSet()

    failed_non_spacing_mark_chars = []
    failed_spacing_mark_chars = []

    for charcode, glypname in cmap.items():
        if _is_non_spacing_mark_char(charcode):
            if glyphSet[glypname].width != 0:
                failed_non_spacing_mark_chars.append(glypname)

        if _is_spacing_mark_char(charcode):
            if glyphSet[glypname].width == 0:
                failed_spacing_mark_chars.append(glypname)

    if failed_non_spacing_mark_chars:
        yield FAIL, Message(
            "non-spacing-not-zero",
            f"Combining accents with width advance width:\n\n"
            f"{bullet_list(config, failed_non_spacing_mark_chars)}",
        )

    if failed_spacing_mark_chars:
        yield FAIL, Message(
            "non-spacing-not-zero",
            f"Spacing marks without advance width:\n\n"
            f"{bullet_list(config, failed_spacing_mark_chars)}",
        )

    if not failed_non_spacing_mark_chars and not failed_spacing_mark_chars:
        yield PASS, "Marks have correct widths."


@check(
    id="com.typenetwork/check/name/mandatory_entries",
    conditions=["style"],
    rationale="""
        For proper functioning, fonts must have some specific records.
        Other name records are optional but desireable to be present.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def com_typenetwork_check_name_mandatory_entries(ttFont, style):
    """Font has all mandatory 'name' table entries?"""
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import RIBBI_STYLE_NAMES

    unnecessary_nameIDs = []
    optional_nameIDs = [
        NameID.COPYRIGHT_NOTICE,
        NameID.UNIQUE_FONT_IDENTIFIER,
        NameID.VERSION_STRING,
        NameID.TRADEMARK,
        NameID.MANUFACTURER_NAME,
        NameID.DESIGNER,
        NameID.DESCRIPTION,
        NameID.VENDOR_URL,
        NameID.DESIGNER_URL,
        NameID.LICENSE_DESCRIPTION,
        NameID.LICENSE_INFO_URL,
    ]

    required_nameIDs = [
        NameID.FONT_FAMILY_NAME,
        NameID.FONT_SUBFAMILY_NAME,
        NameID.FULL_FONT_NAME,
        NameID.POSTSCRIPT_NAME,
    ]

    if style not in RIBBI_STYLE_NAMES:
        required_nameIDs += [
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ]
    else:
        unnecessary_nameIDs += [
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ]

    passed = True
    # The font must have at least these name IDs:
    for nameId in required_nameIDs:
        for entry in get_name_entry_strings(ttFont, nameId):
            if len(entry) == 0:
                passed = False
                yield FAIL, Message(
                    "missing-required-entry",
                    f"Font lacks entry with nameId={nameId}"
                    f" ({NameID(nameId).name})",
                )

    # The font should have these name IDs:
    for nameId in optional_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) == 0:
            passed = False
            yield INFO, Message(
                "missing-optional-entry",
                f"Font lacks entry with nameId={nameId} ({NameID(nameId).name})",
            )

    # The font should NOT have these name IDs:
    for nameId in unnecessary_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) != 0:
            passed = False
            yield INFO, Message(
                "unnecessary-entry",
                f"Font have unnecessary name entry with nameId={nameId}"
                f" ({NameID(nameId).name})",
            )

    if passed:
        yield PASS, "Font contains values for all mandatory name table entries."


@check(
    id="com.typenetwork/check/varfont/axes_have_variation",
    rationale="""
        Axes on a variable font must have variation. In other words min and max values
        need to be different. It’s common to find fonts with unnecesary axes
        added like `ital`.
        """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/61", # Currently private repo.
    ],
)
def com_typenetwork_check_varfont_axes_have_variation(ttFont):
    """Check if font axes have variation"""
    failedAxes = []
    for axis in ttFont["fvar"].axes:
        if axis.minValue == axis.maxValue:
            failedAxes.append(
                {
                    "tag": axis.axisTag,
                    "minValue": axis.minValue,
                    "maxValue": axis.maxValue,
                }
            )

    if failedAxes:
        for failedAxis in failedAxes:
            yield FAIL, Message(
                "axis-has-no-variation",
                f"'{failedAxis['tag']}' axis has no variation its min and max values"
                f" are {failedAxis['minValue'], failedAxis['maxValue']}",
            )
    else:
        yield PASS, "All font axes has variation."


@check(
    id="com.typenetwork/check/varfont/fvar_axes_order",
    rationale="""
        If a font doesn’t have a STAT table, instances get sorted better on Adobe Apps
        when fvar axes follow a specific order: 'opsz', 'wdth', 'wght','ital', 'slnt'.

        We should deprecate this check since STAT is a required table.
        """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/25", # Currently private repo.
    ],
)
def com_typenetwork_check_varfont_fvar_axes_order(ttFont):
    """Check fvar axes order"""
    prefferedOrder = ["opsz", "wdth", "wght", "ital", "slnt"]
    fontRegisteredAxes = []
    customAxes = []

    if "STAT" in ttFont.keys():
        yield SKIP, "The font has a STAT table. This will control instances order."
    else:
        for index, axis in enumerate(ttFont["fvar"].axes):
            if axis.axisTag in prefferedOrder:
                fontRegisteredAxes.append(axis.axisTag)
            else:
                customAxes.append((axis.axisTag, index))

        filtered = [axis for axis in prefferedOrder if axis in fontRegisteredAxes]

        if filtered != fontRegisteredAxes:
            yield FAIL, Message(
                "axes-incorrect-order",
                "Font’s registered axes are not in a correct order to get good"
                "instances sorting on Adobe apps.\n\n"
                f"Current order is {fontRegisteredAxes}, but it should be {filtered}",
            )
        else:
            yield PASS, "Font’s axes follow the preferred sorting."

        if customAxes:
            yield INFO, Message(
                "custom-axes",
                "The font has custom axes with the indicated order:\n\n"
                f"{customAxes}\n\n"
                "Its order can depend on the kind of variation and the subfamily"
                "groups that may create.",
            )


@check(
    id="com.typenetwork/check/family/duplicated_names",
    rationale="""
        Having duplicated name records can produce several issues like not all fonts
        being listed on design apps or incorrect automatic creation of CSS classes
        and @font-face rules.
        """,
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/25", # Currently private repo.
    ],
)
def com_typenetwork_check_family_duplicated_names(ttFonts):
    """Check if font doesn’t have duplicated names within a family."""
    duplicate_subfamilyNames = set()
    seen_fullNames = set()
    duplicate_fullNames = set()
    seen_postscriptNames = set()
    duplicate_postscriptNames = set()

    PLAT_ID = PlatformID.WINDOWS
    ENC_ID = WindowsEncodingID.UNICODE_BMP
    LANG_ID = WindowsLanguageID.ENGLISH_USA

    for ttFont in list(ttFonts):
        # # Subfamily name
        # if ttFont["name"].getName(17, PLAT_ID, ENC_ID, LANG_ID):
        #     subfamName = ttFont["name"].getName(17, PLAT_ID, ENC_ID, LANG_ID)
        # else:
        #     subfamName = ttFont["name"].getName(2, PLAT_ID, ENC_ID, LANG_ID)

        # if subfamName:
        #     subfamName = subfamName.toUnicode()
        #     if subfamName in seen_subfamilyNames:
        #         duplicate_subfamilyNames.add(subfamName)
        #     else:
        #         seen_subfamilyNames.add(subfamName)

        # FullName name
        fullName = ttFont["name"].getName(4, PLAT_ID, ENC_ID, LANG_ID)

        if fullName:
            fullName = fullName.toUnicode()
            if fullName in seen_fullNames:
                duplicate_fullNames.add(fullName)
            else:
                seen_fullNames.add(fullName)

        # Postscript name
        postscriptName = ttFont["name"].getName(6, PLAT_ID, ENC_ID, LANG_ID)
        if postscriptName:
            postscriptName = postscriptName.toUnicode()
            if postscriptName in seen_postscriptNames:
                duplicate_subfamilyNames.add(postscriptName)
            else:
                seen_postscriptNames.add(postscriptName)

    # if duplicate_subfamilyNames:
    #     duplicate_subfamilyNamesString = \
    #         "".join(f"* {inst}\n" for inst in sorted(duplicate_subfamilyNames))
    #     yield FAIL, Message(
    #         "duplicate-subfamily-names",
    #         "Following subfamily names are duplicate:\n\n"
    #         f"{duplicate_subfamilyNamesString}",
    #     )

    if duplicate_fullNames:
        duplicate_fullNamesString = "".join(
            f"* {inst}\n" for inst in sorted(duplicate_fullNames)
        )
        yield FAIL, Message(
            "duplicate-full-names",
            "Following full names are duplicate:\n\n" f"{duplicate_fullNamesString}",
        )

    if duplicate_postscriptNames:
        duplicate_postscriptNamesString = "".join(
            f"* {inst}\n" for inst in sorted(duplicate_postscriptNames)
        )
        yield FAIL, Message(
            "duplicate-postscript-names",
            "Following postscript names are duplicate:\n\n"
            f"{duplicate_postscriptNamesString}",
        )

    if not duplicate_fullNames and not duplicate_postscriptNames:
        yield PASS, "All names are unique"


profile.auto_register(
    globals(),
    filter_func=lambda _, checkid, __: checkid
    not in SET_IMPORTED_CHECKS - SET_EXPLICIT_CHECKS,
)

# ---------------------------------------------------------------------------- #
#                               OVERRIDEN CHECKS                               #
# ---------------------------------------------------------------------------- #

profile.check_log_override(
    # From fontwerk.py
    "com.fontwerk/check/no_mac_entries",
    overrides=(("mac-names", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=("For TN, this is desired but not mandatory."),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/family/single_directory",
    overrides=(("single-directory", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=("Sometimes we want to run the profile on multiple fonts."),
)

profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/glyf_nested_components",
    overrides=(("found-nested-components", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "This is allowed by the spec is not a error in the font but on the systems."
    ),
)


profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/ligature_carets",
    overrides=(("lacks-caret-pos", INFO, KEEP_ORIGINAL_MESSAGE),),
    reason=("This is a feature, not really needed to the font perform well."),
)

profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/kerning_for_non_ligated_sequences",
    overrides=(("lacks-kern-info", INFO, KEEP_ORIGINAL_MESSAGE),),
    reason=("This is a feature, not really needed to the font perform well."),
)

profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/varfont/bold_wght_coord",
    overrides=(
        ("no-bold-instance", WARN, KEEP_ORIGINAL_MESSAGE),
        ("wght-not-700", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
    reason=(
        "Adobe and Type Network recommend, but do not require having a Bold instance,"
        " and that instance should have coordinate 700 on the 'wght' axis."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_ital_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Type Network recommend, but do not require"
        " having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_opsz_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Type Network recommend, but do not require"
        " having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_slnt_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Type Network recommend, but do not require"
        " having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wdth_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Type Network recommend, but do not require"
        " having a Regular instance."
    ),
)


profile.check_log_override(
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wght_coord",
    overrides=(("no-regular-instance", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Adobe and Type Network recommend, but do not require"
        " having a Regular instance."
    ),
)

profile.check_log_override(
    # From gdef.py
    "com.google.fonts/check/gdef_non_mark_chars",
    overrides=(("non-mark-chars", FAIL, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "When non mark characters are on the GDEF Mark class, will produce an overlap."
    ),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/math_signs_width",
    overrides=(("width-outliers", INFO, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "It really depends on the design and the intended use"
        " to make math symbols the same width."
    ),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/dotted_circle",
    overrides=(("missing-dotted-circle", INFO, KEEP_ORIGINAL_MESSAGE),),
    reason=("This is desirable but 'simple script' fonts can work without it."),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/soft_dotted",
    overrides=(("soft-dotted", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "This is something rather new and really unknown for many partners."
        " It will fail on a lot of fonts and in many cases it will cause"
        " much more headaches than benefits."
    ),
)

profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/smart_dropout",
    overrides=(("lacks-smart-dropout", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=("It’s up to foundries to decide."),
)

profile.check_log_override(
    # From googlefonts.py
    "com.google.fonts/check/name/match_familyname_fullfont",
    overrides=(("mismatch-font-names", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "It’s Microsoft Office specific and not possible to achieve"
        " on some families with abbreviated names."
    ),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/transformed_components",
    overrides=(("transformed-components", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "Since it can have a big impact on font production, it’s a foundry decision"
        " what to do regarding this situation."
    ),
)

profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/ots",
    overrides=(("ots-sanitize-warn", FAIL, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "These issues can be a major fail, for instance a bad avar on VFs"
        " will make the font to not interpolate."
    ),
)


TYPENETWORK_PROFILE_CHECKS = add_check_overrides(
    TYPENETWORK_PROFILE_CHECKS, profile.profile_tag, OVERRIDDEN_CHECKS
)

profile.test_expected_checks(TYPENETWORK_PROFILE_CHECKS, exclusive=True)
