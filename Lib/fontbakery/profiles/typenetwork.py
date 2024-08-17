PROFILE = {
    # "include_profiles": ["fontval"], # Temporary Disabled
    "sections": {
        "Type Network": [
            "typenetwork:composite_glyphs",
            "typenetwork:family/duplicated_names",
            "typenetwork:family/equal_numbers_of_glyphs",
            "typenetwork:family/tnum_horizontal_metrics",
            "typenetwork:family/valid_strikeout",
            "typenetwork:family/valid_underline",
            "typenetwork:font_is_centered_vertically",
            # "typenetwork:fstype",  # DEPRECATED
            "typenetwork:glyph_coverage",
            "typenetwork:marks_width",
            "typenetwork:name/mandatory_entries",
            "typenetwork:PUA_encoded_glyphs",
            "typenetwork:usweightclass",
            "typenetwork:varfont/axes_have_variation",
            "typenetwork:varfont/fvar_axes_order",
            "typenetwork:vertical_metrics",
        ],
        "Adobe Fonts": [
            "adobefonts:family/consistent_upm",
            "adobefonts:nameid_1_win_english",
            "adobefonts:STAT_strings",
            "adobefonts:unsupported_tables",
            #
            # "empty_letters",  # The check is broken
        ],
        "CFF table": [
            "opentype:cff_call_depth",
            "opentype:cff2_call_depth",
            "opentype:cff_deprecated_operators",
        ],
        "DSIG table": [
            "opentype:dsig",
        ],
        "Fontwerk": [
            "fontwerk:style_linking",
            # "fontwerk:vendor_id", # PERMANENTLY EXCLUDED
            #
            "inconsistencies_between_fvar_stat",
            "no_mac_entries",
            "weight_class_fvar",
        ],
        "fvar table": [
            "opentype:varfont/distinct_instance_records",
            "opentype:varfont/foundry_defined_tag_name",
            "opentype:varfont/ital_range",
            "opentype:varfont/regular_ital_coord",  # OVERRIDEN: Lowered to WARN
            "opentype:varfont/regular_opsz_coord",  # OVERRIDEN: Lowered to WARN
            "opentype:varfont/regular_slnt_coord",  # OVERRIDEN: Lowered to WARN
            "opentype:varfont/regular_wdth_coord",  # OVERRIDEN: Lowered to WARN
            "opentype:varfont/regular_wght_coord",  # OVERRIDEN: Lowered to WARN
            "opentype:varfont/same_size_instance_records",
            "opentype:varfont/slnt_range",
            "opentype:varfont/valid_axis_nameid",
            "opentype:varfont/valid_default_instance_nameids",
            "opentype:varfont/valid_postscript_nameid",
            "opentype:varfont/valid_subfamily_nameid",
            "opentype:varfont/wdth_valid_range",
            "opentype:varfont/wght_valid_range",
        ],
        "GDEF table": [
            "opentype:gdef_mark_chars",
            "opentype:gdef_non_mark_chars",  # OVERRIDEN
            "opentype:gdef_spacing_marks",
        ],
        "glyf table": [
            "opentype:glyf_non_transformed_duplicate_components",
            "opentype:glyf_unused_data",
            "opentype:points_out_of_bounds",
        ],
        "Google Fonts": [
            "googlefonts:aat",
            "googlefonts:family/equal_codepoint_coverage",
            # "googlefonts:gasp", # Review
            # "googlefonts:glyphsets/shape_languages", # Review
            # "googlefonts:kerning_for_non_ligated_sequences", # PERMANENTLY EXCLUDED
            # "googlefonts:ligature_carets", # PERMANENTLY EXCLUDED
            # "googlefonts:metadata/empty_designer", # PERMANENTLY EXCLUDED
            # "googlefonts:metadata/primary_script", # Review
            # "googlefonts:metadata/unreachable_subsetting", # Review
            # "googlefonts:metadata/valid_nameid25", # TEMPORARY EXCLUDED
            # "googlefonts:negative_advance_width",
            # "googlefonts:os2/use_typo_metrics", # Removed in favor of new vmetrics check
            # "googlefonts:STAT/axis_order",
            "googlefonts:varfont/bold_wght_coord",  # OVERRIDEN: Lowered to WARN
            "googlefonts:varfont/duplicate_instance_names",
            # "googlefonts:vendor_id", # PERMANENTLY EXCLUDED
            #
            "family/control_chars",
            "fvar_name_entries",
            "glyf_nested_components",
            "mandatory_avar_table",
            "missing_small_caps_glyphs",
            "name/family_and_style_max_length",
            "slant_direction",
            "smart_dropout",  # OVERRIDEN
            "stylisticset_description",
            "varfont/consistent_axes",
            # "varfont/duplexed_axis_reflow", # Review
            "vttclean",
        ],
        "GPOS Table": [
            "opentype:gpos_kerning_info",
        ],
        "head table": [
            "opentype:family/equal_font_versions",
            "opentype:unitsperem",
            "opentype:font_version",
            "opentype:mac_style",
        ],
        "hhea table": [
            "opentype:maxadvancewidth",
            "opentype:caret_slope",
        ],
        "kern table": [
            "opentype:kern_table",
        ],
        "Layout Checks": [
            "opentype:layout_valid_feature_tags",
            "opentype:layout_valid_language_tags",
            "opentype:layout_valid_script_tags",
        ],
        "loca table": [
            "opentype:loca/maxp_num_glyphs",
        ],
        "name table": [
            "opentype:family/consistent_family_name",
            "opentype:family/max_4_fonts_per_family_name",
            "opentype:family_naming_recommendations",
            "opentype:monospace",
            "opentype:name/empty_records",
            "opentype:name/italic_names",
            "opentype:name/match_familyname_fullfont",  # OVERRIDEN
            # "opentype:name/no_copyright_on_description", # PERMANENTLY_EXCLUDED
            "opentype:name/postscript_name_consistency",
            "opentype:name/postscript_vs_cff",
            "opentype:postscript_name",  # REVIEW
        ],
        "OS/2 table": [
            "opentype:code_pages",
            "opentype:family/bold_italic_unique_for_nameid1",
            # "opentype:family/panose_familytype", # PERMANENTLY EXCLUDED
            "opentype:fsselection",
            "opentype:fsselection_matches_macstyle",
            # "opentype:vendor_id", # PERMANENTLY_EXCLUDED
            "opentype:xavgcharwidth",
        ],
        "Outline Checks": [
            "outline_alignment_miss",
            "outline_colinear_vectors",
            "outline_jaggy_segments",
            "outline_semi_vertical",
            "outline_short_segments",
        ],
        "post table": [
            "opentype:family/underline_thickness",
            "opentype:italic_angle",
            "opentype:post_table_version",
        ],
        "Shaping Checks": [
            "dotted_circle",  # REVIEW
            # "shaping/regression", # PERMANENTLY EXCLUDED
            # "shaping/forbidden", # PERMANENTLY EXCLUDED
            # "shaping/collides",  # PERMANENTLY EXCLUDED
            "soft_dotted",
        ],
        "STAT table": [
            "opentype:italic_axis_in_stat",
            "opentype:italic_axis_in_stat_is_boolean",
            "opentype:italic_axis_last",
            "opentype:stat_has_axis_value_tables",
            "opentype:varfont/stat_axis_record_for_each_axis",
        ],
        "Universal Checks": [
            # "alt_caron",  # PERMANENTLY EXCLUDED
            "arabic_high_hamza",
            "arabic_spacing_symbols",
            # "caps_vertically_centered", # REVIEW
            # 'cjk_chws_feature', # PERMANENTLY EXCLUDED
            "contour_count",
            # "family/single_directory", # PERMANENTLY EXCLUDED
            "family/vertical_metrics",
            "family/win_ascent_and_descent",
            # "fontbakery_version", # PERMANENTLY EXCLUDED
            "freetype_rasterizer",
            "gpos7",
            "interpolation_issues",
            "linegaps",
            "mandatory_glyphs",
            # "math_signs_width",  # PERMANENTLY EXCLUDED
            "name/trailing_spaces",
            # "os2_metrics_match_hhea", # Removed in favor of new vmetrics check
            "ots",  # OVERRIDEN
            "required_tables",
            "rupee",
            "sfnt_version",
            "soft_hyphen",
            "STAT_in_statics",
            # 'superfamily/list', # PERMANENTLY EXCLUDED
            "superfamily/vertical_metrics",
            "transformed_components",  # OVERRIDEN
            "ttx_roundtrip",
            "unique_glyphnames",
            "unreachable_glyphs",
            "unwanted_tables",
            "valid_glyphnames",
            "whitespace_glyphnames",
            "whitespace_glyphs",
            "whitespace_ink",
            "whitespace_widths",
        ],
    },
    "overrides": {
        "no_mac_entries": [
            {
                "code": "mac-names",
                "status": "WARN",
                "reason": "For TN, this is desired but not mandatory.",
            }
        ],
        "family/single_directory": [
            {
                "code": "single-directory",
                "status": "WARN",
                "reason": "Sometimes we want to run the profile on multiple fonts.",
            },
        ],
        "glyf_nested_components": [
            {
                "code": "found-nested-components",
                "status": "WARN",
                "reason": "This is allowed by the spec is not a error in the font but on "
                "the systems.",
            },
        ],
        "googlefonts:ligature_carets": [
            {
                "code": "lacks-caret-pos",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "googlefonts:kerning_for_non_ligated_sequences": [
            {
                "code": "lacks-kern-info",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "googlefonts:varfont/bold_wght_coord": [
            {
                "code": "no-bold-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require having a Bold "
                "instance, and that instance should have coordinate 700 on the 'wght' axis.",
            },
            {
                "code": "wght-not-700",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require having a "
                "Bold instance, and that instance should have coordinate 700 on "
                "the 'wght' axis.",
            },
        ],
        "opentype:varfont/regular_ital_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_opsz_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_slnt_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_wdth_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype:varfont/regular_wght_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype:gdef_non_mark_chars": [
            {
                "code": "non-mark-chars",
                "status": "FAIL",
                "reason": "When non mark characters are on the GDEF Mark class,"
                " will produce an overlap.",
            },
        ],
        "math_signs_width": [
            {
                "code": "width-outliers",
                "status": "INFO",
                "reason": "It really depends on the design and the intended use"
                " to make math symbols the same width.",
            },
        ],
        "dotted_circle": [
            {
                "code": "missing-dotted-circle",
                "status": "INFO",
                "reason": "This is desirable but 'simple script' fonts can work without it.",
            },
        ],
        "soft_dotted": [
            {
                "code": "soft-dotted",
                "status": "WARN",
                "reason": "This is something rather new and really unknown for many partners."
                " It will fail on a lot of fonts and in many cases it will cause"
                " much more headaches than benefits.",
            },
        ],
        "smart_dropout": [
            {
                "code": "lacks-smart-dropout",
                "status": "WARN",
                "reason": "It’s up to foundries to decide.",
            },
        ],
        "opentype:name/match_familyname_fullfont": [
            {
                "code": "mismatch-font-names",
                "status": "WARN",
                "reason": "It’s Microsoft Office specific and not possible to achieve"
                " on some families with abbreviated names.",
            },
        ],
        "transformed_components": [
            {
                "code": "transformed-components",
                "status": "WARN",
                "reason": "Since it can have a big impact on font production, "
                "it’s a foundry decision what to do regarding this situation.",
            },
        ],
        "ots": [
            {
                "code": "ots-sanitize-warn",
                "status": "FAIL",
                "reason": "These issues can be a major fail, for instance a bad avar on VFs"
                " will make the font to not interpolate.",
            },
        ],
    },
}
