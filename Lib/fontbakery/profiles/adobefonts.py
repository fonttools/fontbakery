# pylint: disable=line-too-long  # This is data, not code
"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
PROFILE = {
    "sections": {
        "Adobe Fonts Checks": [
            "com.adobe.fonts/check/family/consistent_upm",
            "com.adobe.fonts/check/find_empty_letters",
            "com.adobe.fonts/check/nameid_1_win_english",
            "com.adobe.fonts/check/unsupported_tables",
            "com.adobe.fonts/check/STAT_strings",
        ],
        "CFF": [
            "com.adobe.fonts/check/cff2_call_depth",
            "com.adobe.fonts/check/cff_call_depth",
            "com.adobe.fonts/check/cff_deprecated_operators",
        ],
        "fontwerk": [
            "com.fontwerk/check/inconsistencies_between_fvar_stat",  # IS_OVERRIDDEN
            "com.fontwerk/check/weight_class_fvar",  # IS_OVERRIDDEN
        ],
        "fvar": [
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
        ],
        "glyf": [
            "com.google.fonts/check/glyf_non_transformed_duplicate_components",
            "com.google.fonts/check/glyf_unused_data",
            "com.google.fonts/check/points_out_of_bounds",
        ],
        "Google Fonts": [
            "com.google.fonts/check/aat",
            "com.google.fonts/check/fvar_name_entries",
            "com.google.fonts/check/varfont_duplicate_instance_names",
            "com.google.fonts/check/varfont/bold_wght_coord",  # IS_OVERRIDDEN
        ],
        #
        # =======================================
        "gpos": [
            "com.google.fonts/check/gpos_kerning_info",
            #
            # =======================================
        ],
        "head": [
            "com.google.fonts/check/family/equal_font_versions",
            "com.google.fonts/check/font_version",
            "com.google.fonts/check/unitsperem",
            #
            # =======================================
        ],
        "hhea": [
            "com.google.fonts/check/linegaps",
            "com.google.fonts/check/maxadvancewidth",
            #
            # =======================================
        ],
        "kern": [
            "com.google.fonts/check/kern_table",
            #
            # =======================================
        ],
        "layout": [
            "com.google.fonts/check/layout_valid_feature_tags",
            "com.google.fonts/check/layout_valid_language_tags",
            "com.google.fonts/check/layout_valid_script_tags",
            #
            # =======================================
        ],
        "loca": [
            "com.google.fonts/check/loca/maxp_num_glyphs",
            #
            # =======================================
        ],
        "name": [
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
        ],
        "notofonts": [
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
        ],
        "os2": [
            # "com.google.fonts/check/xavgcharwidth",  # PERMANENTLY_EXCLUDED
            "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
            "com.adobe.fonts/check/fsselection_matches_macstyle",
            "com.google.fonts/check/code_pages",
            "com.google.fonts/check/family/panose_familytype",
            #
            # =======================================
        ],
        "post": [
            "com.google.fonts/check/family/underline_thickness",
            "com.google.fonts/check/post_table_version",
            #
            # =======================================
        ],
        "stat": [
            "com.adobe.fonts/check/stat_has_axis_value_tables",  # IS_OVERRIDDEN
            "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
            #
            # =======================================
        ],
        "universal": [
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
        ],
    },
    "overrides": {
        "com.google.fonts/check/whitespace_glyphs": [
            {
                "code": "missing-whitespace-glyph-0x00A0",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check for 0x00A0.",
            }
        ],
        "com.google.fonts/check/name/trailing_spaces": [
            {
                "code": "trailing-space",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check.",
            }
        ],
        "com.google.fonts/check/valid_glyphnames": [
            {
                "code": "found-invalid-names",
                "status": "WARN",
            }
        ],
        "com.google.fonts/check/family/win_ascent_and_descent": [
            {
                "code": "ascent",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check.",
            },
            {
                "code": "descent",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check.",
            },
        ],
        "com.google.fonts/check/os2_metrics_match_hhea": [
            {
                "code": "ascender",
                "status": "WARN",
            },
            {
                "code": "descender",
                "status": "WARN",
            },
            {
                "code": "lineGap",
                "status": "WARN",
            },
        ],
        "com.google.fonts/check/fontbakery_version": [
            {
                "code": "connection-error",
                "status": "SKIP",
                "reason": "For Adobe, users shouldn't be bothered with a failed check if their internet connection isn't functional.",
            }
        ],
        "com.google.fonts/check/name/match_familyname_fullfont": [
            {
                "code": "mismatch-font-names",
                "status": "WARN",
                "reason": "Many CFF OpenType fonts in circulation are built with the Microsoft platform Full font name string identical to the PostScript FontName in the CFF Name INDEX. This practice was documented in the OpenType spec until version 1.5.",
            }
        ],
        "com.google.fonts/check/varfont/bold_wght_coord": [
            {
                "code": "no-bold-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Bold instance, and that instance should have coordinate 700 on the 'wght' axis.",
            },
            {
                "code": "wght-not-700",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Bold instance, and that instance should have coordinate 700 on the 'wght' axis.",
            },
        ],
        "com.google.fonts/check/varfont/regular_ital_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_opsz_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_slnt_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_wdth_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_wght_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "com.adobe.fonts/check/varfont/valid_default_instance_nameids": [
            {
                "code": "invalid-default-instance-subfamily-name",
                "status": "WARN",
                "reason": "Adobe and the OpenType spec strongly recommend following these guidelines, but they are not hard requirements so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet these guidelines might behave inconsistently so please carefully consider trying to meet them.",
            },
            {
                "code": "invalid-default-instance-postscript-name",
                "status": "WARN",
                "reason": "Adobe and the OpenType spec strongly recommend following these guidelines, but they are not hard requirements so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet these guidelines might behave inconsistently so please carefully consider trying to meet them.",
            },
        ],
        "com.adobe.fonts/check/stat_has_axis_value_tables": [
            {
                "code": "missing-axis-value-table",
                "status": "WARN",
                "reason": "Adobe and the OpenType spec strongly recommend following these guidelines, but they are not hard requirements so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet these guidelines might behave inconsistently so please carefully consider trying to meet them.",
            },
            {
                "code": "format-4-axis-count",
                "status": "WARN",
                "reason": "Adobe and the OpenType spec strongly recommend following these guidelines, but they are not hard requirements so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet these guidelines might behave inconsistently so please carefully consider trying to meet them.",
            },
        ],
        "com.fontwerk/check/inconsistencies_between_fvar_stat": [
            {
                "code": "missing-fvar-instance-axis-value",
                "status": "WARN",
                "reason": "Adobe and Fontwerk strongly recommend following this guideline, but it is not a hard requirement so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet this guideline might behave inconsistently so please carefully consider trying to meet it.",
            }
        ],
        "com.fontwerk/check/weight_class_fvar": [
            {
                "code": "bad-weight-class",
                "status": "WARN",
                "reason": "Adobe and Fontwerk strongly recommend following this guideline, but it is not a hard requirement so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet this guideline might behave inconsistently so please carefully consider trying to meet it.",
            },
        ],
    },
}
