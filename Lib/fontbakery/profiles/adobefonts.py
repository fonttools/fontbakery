# pylint: disable=line-too-long  # This is data, not code
"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
PROFILE = {
    "sections": {
        "Adobe Fonts Checks": [
            "adobefonts:family/consistent_upm",
            "adobefonts:nameid_1_win_english",
            "adobefonts:unsupported_tables",
            "adobefonts:STAT_strings",
            #
            "empty_letters",
        ],
        "CFF": [
            "opentype:cff2_call_depth",
            "opentype:cff_call_depth",
            "opentype:cff_deprecated_operators",
            "opentype:cff_ascii_strings",
        ],
        "fontwerk": [
            "inconsistencies_between_fvar_stat",  # IS_OVERRIDDEN
            "weight_class_fvar",  # IS_OVERRIDDEN
        ],
        "fvar": [
            "opentype:varfont/distinct_instance_records",
            "opentype:varfont/foundry_defined_tag_name",
            "opentype:varfont/valid_axis_nameid",
            "opentype:varfont/valid_default_instance_nameids",  # IS_OVERRIDDEN
            "opentype:varfont/valid_postscript_nameid",
            "opentype:varfont/valid_subfamily_nameid",
            "opentype:varfont/regular_ital_coord",  # IS_OVERRIDDEN
            "opentype:varfont/regular_opsz_coord",  # IS_OVERRIDDEN
            "opentype:varfont/regular_slnt_coord",  # IS_OVERRIDDEN
            "opentype:varfont/regular_wdth_coord",  # IS_OVERRIDDEN
            "opentype:varfont/regular_wght_coord",  # IS_OVERRIDDEN
            "opentype:varfont/same_size_instance_records",
            "opentype:varfont/slnt_range",
            "opentype:varfont/wdth_valid_range",
            "opentype:varfont/wght_valid_range",
        ],
        "glyf": [
            "opentype:glyf_non_transformed_duplicate_components",
            "opentype:glyf_unused_data",
            "opentype:points_out_of_bounds",
        ],
        "Google Fonts": [
            "googlefonts:aat",
            "googlefonts:varfont/duplicate_instance_names",
            "googlefonts:varfont/bold_wght_coord",  # IS_OVERRIDDEN
            #
            "fvar_name_entries",
        ],
        "gpos": [
            "opentype:gpos_kerning_info",
        ],
        "head": [
            "opentype:family/equal_font_versions",
            "opentype:font_version",
            "opentype:unitsperem",
        ],
        "hhea": [
            "opentype:maxadvancewidth",
        ],
        "kern": [
            "opentype:kern_table",
        ],
        "layout": [
            "opentype:layout_valid_feature_tags",
            "opentype:layout_valid_language_tags",
            "opentype:layout_valid_script_tags",
        ],
        "loca": [
            "opentype:loca/maxp_num_glyphs",
        ],
        "name": [
            # "opentype:name/no_copyright_on_description",  # PERMANENTLY_EXCLUDED
            "opentype:name/match_familyname_fullfont",  # IS_OVERRIDDEN
            "opentype:family/max_4_fonts_per_family_name",
            "opentype:family/consistent_family_name",
            "opentype:name/empty_records",
            "opentype:postscript_name",
            "opentype:name/postscript_name_consistency",
            "opentype:name/postscript_vs_cff",
            "opentype:family_naming_recommendations",
            "opentype:monospace",
        ],
        "notofonts": [
            # "notofonts:cmap/unexpected_subtables",  # PERMANENTLY_EXCLUDED
            # "notofonts:hmtx/comma_period",          # PERMANENTLY_EXCLUDED
            # "notofonts:hmtx/encoded_latin_digits",  # PERMANENTLY_EXCLUDED
            # "notofonts:hmtx/whitespace_advances",   # PERMANENTLY_EXCLUDED
            # "notofonts:name/designer",              # PERMANENTLY_EXCLUDED
            # "notofonts:name/manufacturer",          # PERMANENTLY_EXCLUDED
            # "notofonts:name/trademark",             # PERMANENTLY_EXCLUDED
            # "notofonts:os2/vendor",                 # PERMANENTLY_EXCLUDED
            # "notofonts:cmap/alien_codepoints",
            # "notofonts:unicode_range_bits",
            #
            "cmap/format_12",
        ],
        "os2": [
            # "opentype:xavgcharwidth",  # PERMANENTLY_EXCLUDED
            "opentype:family/bold_italic_unique_for_nameid1",
            "opentype:fsselection_matches_macstyle",
            "opentype:code_pages",
            "opentype:family/panose_familytype",
        ],
        "post": [
            "opentype:family/underline_thickness",
            "opentype:post_table_version",
        ],
        "stat": [
            "opentype:stat_has_axis_value_tables",  # IS_OVERRIDDEN
            "opentype:varfont/stat_axis_record_for_each_axis",
        ],
        "universal": [
            # "cjk_chws_feature",
            # "contour_count",
            # "dotted_circle",
            "family/win_ascent_and_descent",  # IS_OVERRIDDEN
            "family/single_directory",
            "family/vertical_metrics",
            "fontbakery_version",  # IS_OVERRIDDEN
            "freetype_rasterizer",
            "gpos7",
            "linegaps",
            "mandatory_glyphs",
            "name/trailing_spaces",  # IS_OVERRIDDEN
            "os2_metrics_match_hhea",  # IS_OVERRIDDEN
            "ots",
            "required_tables",
            "rupee",
            "sfnt_version",
            # "STAT_strings",  # replaced by adobefonts:STAT_strings
            # "transformed_components",
            "ttx_roundtrip",
            "unique_glyphnames",
            # "unreachable_glyphs",
            "valid_glyphnames",  # IS_OVERRIDDEN
            # "whitespace_glyphnames",  # PERMANENTLY_EXCLUDED
            "whitespace_glyphs",  # IS_OVERRIDDEN
            # "whitespace_ink",         # PERMANENTLY_EXCLUDED
            "whitespace_widths",
        ],
    },
    "overrides": {
        "whitespace_glyphs": [
            {
                "code": "missing-whitespace-glyph-0x00A0",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check for 0x00A0.",
            }
        ],
        "name/trailing_spaces": [
            {
                "code": "trailing-space",
                "status": "WARN",
                "reason": "For Adobe, this is not as severe as assessed in the original check.",
            }
        ],
        "valid_glyphnames": [
            {
                "code": "found-invalid-names",
                "status": "WARN",
            }
        ],
        "family/win_ascent_and_descent": [
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
        "os2_metrics_match_hhea": [
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
        "fontbakery_version": [
            {
                "code": "connection-error",
                "status": "SKIP",
                "reason": "For Adobe, users shouldn't be bothered with a failed check if their internet connection isn't functional.",
            }
        ],
        "opentype:name/match_familyname_fullfont": [
            {
                "code": "mismatch-font-names",
                "status": "WARN",
                "reason": "Many CFF OpenType fonts in circulation are built with the Microsoft platform Full font name string identical to the PostScript FontName in the CFF Name INDEX. This practice was documented in the OpenType spec until version 1.5.",
            }
        ],
        "googlefonts:varfont/bold_wght_coord": [
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
        "opentype:varfont/regular_ital_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_opsz_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_slnt_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_wdth_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_wght_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe strongly recommends, but does not require having a Regular instance.",
            },
        ],
        "opentype:varfont/valid_default_instance_nameids": [
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
        "opentype:stat_has_axis_value_tables": [
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
        "inconsistencies_between_fvar_stat": [
            {
                "code": "missing-fvar-instance-axis-value",
                "status": "WARN",
                "reason": "Adobe and Fontwerk strongly recommend following this guideline, but it is not a hard requirement so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet this guideline might behave inconsistently so please carefully consider trying to meet it.",
            }
        ],
        "weight_class_fvar": [
            {
                "code": "bad-weight-class",
                "status": "WARN",
                "reason": "Adobe and Fontwerk strongly recommend following this guideline, but it is not a hard requirement so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet this guideline might behave inconsistently so please carefully consider trying to meet it.",
            },
        ],
    },
}
