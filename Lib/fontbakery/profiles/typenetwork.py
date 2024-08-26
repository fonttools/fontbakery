# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": [
        "universal",
        # "fontval",  # Temporarily disabled
    ],
    "exclude_checks": [
        "opentype:family/panose_familytype",
        "opentype:name/no_copyright_on_description",
        "opentype:vendor_id",
        "superfamily/list",
        "alt_caron",
        "cjk_chws_feature",
        "family/single_directory",  # Sometimes we want to run the profile on multiple fonts.
        "fontbakery_version",
        "math_signs_width",  # It really depends on the design and the intended use to make math symbols the same width.
        "os2_metrics_match_hhea",  # Removed in favor of new vmetrics check
        "STAT_strings",  # replaced by adobefonts:STAT_strings
    ],
    "pending_review": [
        "opentype:cff_ascii_strings",
        "opentype:postscript_name",
        "opentype:varfont/family_axis_ranges",
        "opentype:weight_class_fvar",
        # "caps_vertically_centered",  # Disabled: issue #4274
        "case_mapping",
        "designspace_has_consistent_codepoints",
        "designspace_has_consistent_glyphset",
        "designspace_has_consistent_groups",
        "designspace_has_default_master",
        "designspace_has_sources",
        "gsub/smallcaps_before_ligatures",
        "legacy_accents",
        "no_debugging_tables",
        "tabular_kerning",
        "typoascender_exceeds_Agrave",
        "ufolint",
        "ufo_features_default_languagesystem",
        "ufo_recommended_fields",
        "ufo_required_fields",
        "ufo_unnecessary_fields",
    ],
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
        "Fontwerk": [
            "fontwerk:style_linking",
            # "fontwerk:vendor_id", # PERMANENTLY EXCLUDED
            #
            "inconsistencies_between_fvar_stat",
            "no_mac_entries",
        ],
        "Google Fonts": [
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
        "Outline Checks": [
            "outline_alignment_miss",
            "outline_colinear_vectors",
            "outline_jaggy_segments",
            "outline_semi_vertical",
            "outline_short_segments",
        ],
        "Shaping Checks": [
            "dotted_circle",  # REVIEW
            # "shaping/regression", # PERMANENTLY EXCLUDED
            # "shaping/forbidden", # PERMANENTLY EXCLUDED
            # "shaping/collides",  # PERMANENTLY EXCLUDED
            "soft_dotted",
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
