PROFILE = {
    # "include_profiles": ["fontval"], # Temporary Disabled
    "sections": {
        "Type Network": [
            "com.typenetwork/check/glyph_coverage",
            "com.typenetwork/check/vertical_metrics",
            "com.typenetwork/check/font_is_centered_vertically",
            "com.typenetwork/check/family/tnum_horizontal_metrics",
            "com.typenetwork/check/family/equal_numbers_of_glyphs",
            "com.typenetwork/check/usweightclass",
            "com.typenetwork/check/family/valid_underline",
            "com.typenetwork/check/family/valid_strikeout",
            # "com.typenetwork/check/fstype", # DEPRECATED
            "com.typenetwork/check/composite_glyphs",
            "com.typenetwork/check/PUA_encoded_glyphs",
            "com.typenetwork/check/marks_width",
            "com.typenetwork/check/name/mandatory_entries",
            "com.typenetwork/check/varfont/axes_have_variation",
            "com.typenetwork/check/varfont/fvar_axes_order",
            "com.typenetwork/check/family/duplicated_names",
        ],
        "Adobe Fonts": [
            "com.adobe.fonts/check/family/consistent_upm",
            # "com.adobe.fonts/check/find_empty_letters", # The check is broken
            "com.adobe.fonts/check/nameid_1_win_english",
            "com.adobe.fonts/check/unsupported_tables",
            "com.adobe.fonts/check/STAT_strings",
        ],
        "CFF": [
            "com.adobe.fonts/check/cff_call_depth",
            "com.adobe.fonts/check/cff2_call_depth",
            "com.adobe.fonts/check/cff_deprecated_operators",
        ],
        "DSIG": [
            "com.google.fonts/check/dsig",
        ],
        "Fontwerk": [
            "com.fontwerk/check/no_mac_entries",
            # "com.fontwerk/check/vendor_id", # PERMANENTLY EXCLUDED
            "com.fontwerk/check/weight_class_fvar",
            "com.fontwerk/check/inconsistencies_between_fvar_stat",
            "com.fontwerk/check/style_linking",
        ],
        "fvar table": [
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
        ],
        "GDEF table": [
            "com.google.fonts/check/gdef_spacing_marks",
            "com.google.fonts/check/gdef_mark_chars",
            "com.google.fonts/check/gdef_non_mark_chars",  # OVERRIDEN
        ],
        "glyf table": [
            "com.google.fonts/check/glyf_unused_data",
            "com.google.fonts/check/points_out_of_bounds",
            "com.google.fonts/check/glyf_non_transformed_duplicate_components",
        ],
        "Google Fonts": [
            "com.google.fonts/check/family/equal_codepoint_coverage",
            # "com.google.fonts/check/vendor_id", # PERMANENTLY EXCLUDED
            # "com.google.fonts/check/metadata/unreachable_subsetting", # Review
            # "com.google.fonts/check/gasp", # Review
            # "com.google.fonts/check/metadata/valid_nameid25", # TEMPORARY EXCLUDED
            # "com.google.fonts/check/metadata/primary_script", # Review
            # "com.google.fonts/check/glyphsets/shape_languages", # Review
            "com.google.fonts/check/slant_direction",
            # "com.google.fonts/check/negative_advance_width",
            "com.google.fonts/check/glyf_nested_components",
            "com.google.fonts/check/varfont/consistent_axes",
            "com.google.fonts/check/smart_dropout",  # OVERRIDEN
            "com.google.fonts/check/vttclean",
            "com.google.fonts/check/aat",
            "com.google.fonts/check/fvar_name_entries",
            # "com.google.fonts/check/ligature_carets", # PERMANENTLY EXCLUDED
            # "com.google.fonts/check/kerning_for_non_ligated_sequences", # PERMANENTLY EXCLUDED
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
            # "com.google.fonts/check/metadata/empty_designer", # PERMANENTLY EXCLUDED
            "com.google.fonts/check/varfont/bold_wght_coord",  # OVERRIDEN: Lowered to WARN
        ],
        "GPOS Table": [
            "com.google.fonts/check/gpos_kerning_info",
        ],
        "head table": [
            "com.google.fonts/check/family/equal_font_versions",
            "com.google.fonts/check/unitsperem",
            "com.google.fonts/check/font_version",
            "com.google.fonts/check/mac_style",
        ],
        "hhea table": [
            "com.google.fonts/check/maxadvancewidth",
            "com.google.fonts/check/caret_slope",
        ],
        "kern table": [
            "com.google.fonts/check/kern_table",
        ],
        "Layout Checks": [
            "com.google.fonts/check/layout_valid_feature_tags",
            "com.google.fonts/check/layout_valid_script_tags",
            "com.google.fonts/check/layout_valid_language_tags",
        ],
        "loca table": [
            "com.google.fonts/check/loca/maxp_num_glyphs",
        ],
        "name table": [
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
        ],
        "OS/2 table": [
            # "com.google.fonts/check/family/panose_familytype", # PERMANENTLY EXCLUDED
            "com.google.fonts/check/xavgcharwidth",
            "com.adobe.fonts/check/fsselection_matches_macstyle",
            "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
            "com.google.fonts/check/code_pages",
            # "com.thetypefounders/check/vendor_id", # PERMANENTLY_EXCLUDED
            "com.google.fonts/check/fsselection",
        ],
        "Outline Checks": [
            "com.google.fonts/check/outline_alignment_miss",
            "com.google.fonts/check/outline_short_segments",
            "com.google.fonts/check/outline_colinear_vectors",
            "com.google.fonts/check/outline_jaggy_segments",
            "com.google.fonts/check/outline_semi_vertical",
        ],
        "post table": [
            "com.google.fonts/check/family/underline_thickness",
            "com.google.fonts/check/post_table_version",
            "com.google.fonts/check/italic_angle",
        ],
        "Shaping Checks": [
            # "com.google.fonts/check/shaping/regression", # PERMANENTLY EXCLUDED
            # "com.google.fonts/check/shaping/forbidden", # PERMANENTLY EXCLUDED
            # "com.google.fonts/check/shaping/collides",  # PERMANENTLY EXCLUDED
            "com.google.fonts/check/dotted_circle",  # REVIEW
            "com.google.fonts/check/soft_dotted",
        ],
        "STAT table": [
            "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
            "com.adobe.fonts/check/stat_has_axis_value_tables",
            "com.google.fonts/check/italic_axis_in_stat",
            "com.google.fonts/check/italic_axis_in_stat_is_boolean",
            "com.google.fonts/check/italic_axis_last",
        ],
        "Universal Checks": [
            "com.google.fonts/check/name/trailing_spaces",
            "com.google.fonts/check/family/win_ascent_and_descent",
            # "com.google.fonts/check/os2_metrics_match_hhea", # Removed in favor of
            #                                                  # new vmetrics check
            # "com.google.fonts/check/family/single_directory", # PERMANENTLY EXCLUDED
            # "com.google.fonts/check/caps_vertically_centered", # REVIEW
            "com.google.fonts/check/ots",  # OVERRIDEN
            # "com.google.fonts/check/fontbakery_version", # PERMANENTLY EXCLUDED
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
            # "com.google.fonts/check/math_signs_width",  # PERMANENTLY EXCLUDED
            "com.google.fonts/check/linegaps",
            "com.google.fonts/check/STAT_in_statics",
            # "com.google.fonts/check/alt_caron",  # PERMANENTLY EXCLUDED
        ],
    },
    "overrides": {
        "com.fontwerk/check/no_mac_entries": [
            {
                "code": "mac-names",
                "status": "WARN",
                "reason": "For TN, this is desired but not mandatory.",
            }
        ],
        "com.google.fonts/check/family/single_directory": [
            {
                "code": "single-directory",
                "status": "WARN",
                "reason": "Sometimes we want to run the profile on multiple fonts.",
            },
        ],
        "com.google.fonts/check/glyf_nested_components": [
            {
                "code": "found-nested-components",
                "status": "WARN",
                "reason": "This is allowed by the spec is not a error in the font but on "
                "the systems.",
            },
        ],
        "com.google.fonts/check/ligature_carets": [
            {
                "code": "lacks-caret-pos",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "com.google.fonts/check/kerning_for_non_ligated_sequences": [
            {
                "code": "lacks-kern-info",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "com.google.fonts/check/varfont/bold_wght_coord": [
            {
                "code": "no-bold-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require having a Bold "
                "instance, and that instance should have coordinate 700 on the 'wght' "
                "axis.",
            },
            {
                "code": "wght-not-700",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require having a "
                "Bold instance, and that instance should have coordinate 700 on "
                "the 'wght' axis.",
            },
        ],
        "com.google.fonts/check/varfont/regular_ital_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_opsz_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_slnt_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_wdth_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "com.google.fonts/check/varfont/regular_wght_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "com.google.fonts/check/gdef_non_mark_chars": [
            {
                "code": "non-mark-chars",
                "status": "FAIL",
                "reason": "When non mark characters are on the GDEF Mark class,"
                " will produce an overlap.",
            },
        ],
        "com.google.fonts/check/math_signs_width": [
            {
                "code": "width-outliers",
                "status": "INFO",
                "reason": "It really depends on the design and the intended use"
                " to make math symbols the same width.",
            },
        ],
        "com.google.fonts/check/dotted_circle": [
            {
                "code": "missing-dotted-circle",
                "status": "INFO",
                "reason": "This is desirable but 'simple script' fonts can work without it.",
            },
        ],
        "com.google.fonts/check/soft_dotted": [
            {
                "code": "soft-dotted",
                "status": "WARN",
                "reason": "This is something rather new and really unknown for many partners."
                " It will fail on a lot of fonts and in many cases it will cause"
                " much more headaches than benefits.",
            },
        ],
        "com.google.fonts/check/smart_dropout": [
            {
                "code": "lacks-smart-dropout",
                "status": "WARN",
                "reason": "It’s up to foundries to decide.",
            },
        ],
        "com.google.fonts/check/name/match_familyname_fullfont": [
            {
                "code": "mismatch-font-names",
                "status": "WARN",
                "reason": "It’s Microsoft Office specific and not possible to achieve"
                " on some families with abbreviated names.",
            },
        ],
        "com.google.fonts/check/transformed_components": [
            {
                "code": "transformed-components",
                "status": "WARN",
                "reason": "Since it can have a big impact on font production, "
                "it’s a foundry decision what to do regarding this situation.",
            },
        ],
        "com.google.fonts/check/ots": [
            {
                "code": "ots-sanitize-warn",
                "status": "FAIL",
                "reason": "These issues can be a major fail, for instance a bad avar on VFs"
                " will make the font to not interpolate.",
            },
        ],
    },
}
