# pylint: disable=line-too-long  # This is data, not code
"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
PROFILE = {
    "include_profiles": ["universal"],
    "exclude_checks": [
        "opentype:name/no_copyright_on_description",
        "opentype:xavgcharwidth",
        #
        "designspace_has_consistent_codepoints",
        "designspace_has_consistent_glyphset",
        "designspace_has_consistent_groups",
        "designspace_has_default_master",
        "designspace_has_sources",
        "ufolint",
        "ufo_features_default_languagesystem",
        "ufo_recommended_fields",
        "ufo_required_fields",
        "ufo_unnecessary_fields",
        "STAT_strings",  # replaced by adobefonts:STAT_strings
        "transformed_components",
        "unreachable_glyphs",
        "whitespace_glyphnames",
        "whitespace_ink",
    ],
    "pending_review": [
        "opentype:caret_slope",
        "opentype:dsig",
        "opentype:fsselection",
        "opentype:gdef_mark_chars",
        "opentype:gdef_non_mark_chars",
        "opentype:gdef_spacing_marks",
        "opentype:italic_angle",
        "opentype:italic_axis_in_stat",
        "opentype:italic_axis_in_stat_is_boolean",
        "opentype:italic_axis_last",
        "opentype:mac_style",
        "opentype:name/italic_names",
        "opentype:slant_direction",
        "opentype:varfont/family_axis_ranges",
        "opentype:varfont/ital_range",
        "opentype:vendor_id",
        "alt_caron",
        "arabic_high_hamza",
        "arabic_spacing_symbols",
        "case_mapping",
        "cjk_chws_feature",  # was temporarily removed
        "contour_count",  # was temporarily removed
        "fontdata_namecheck",
        "glyf_nested_components",
        "gsub/smallcaps_before_ligatures",
        "hinting_impact",
        "interpolation_issues",
        "legacy_accents",
        "math_signs_width",
        "no_debugging_tables",
        "no_mac_entries",
        "render_own_name",
        "soft_hyphen",
        "STAT_in_statics",
        "superfamily/list",
        "superfamily/vertical_metrics",
        "tabular_kerning",
        "typoascender_exceeds_Agrave",
        "unwanted_tables",
        "vtt_volt_data",  # very similar to vttclean, may be a good idea to merge them.
        "vttclean",
    ],
    "sections": {
        "Adobe Fonts Checks": [
            "adobefonts:family/consistent_upm",
            "adobefonts:nameid_1_win_english",
            "adobefonts:unsupported_tables",
            "adobefonts:STAT_strings",
            #
            "empty_letters",
        ],
        "Google Fonts": [
            "googlefonts:varfont/duplicate_instance_names",
            "googlefonts:varfont/bold_wght_coord",  # IS_OVERRIDDEN
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
        "opentype:weight_class_fvar": [
            {
                "code": "bad-weight-class",
                "status": "WARN",
                "reason": "Adobe and Fontwerk strongly recommend following this guideline, but it is not a hard requirement so we are relaxing this to WARN rather than FAIL.\n"
                "Fonts that do not meet this guideline might behave inconsistently so please carefully consider trying to meet it.",
            },
        ],
    },
}
