# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": [
        "universal",
    ],
    "exclude_checks": [
        "opentype/family/panose_familytype",
        "opentype/name/no_copyright_on_description",
        "opentype/vendor_id",
        "superfamily/list",
        "alt_caron",
        "cjk_chws_feature",
        "family/single_directory",  # Sometimes we want to run the profile on multiple fonts.
        "fontbakery_version",
        "math_signs_width",  # It really depends on the design and the intended use to make math symbols the same width.
        "os2_metrics_match_hhea",  # Removed in favor of new vmetrics check
        "STAT_strings",  # replaced by adobefonts/STAT_strings
        "designspace_has_consistent_codepoints", # We (TN) doesn’t check designspace files
        "designspace_has_consistent_glyphset", # We (TN) doesn’t check designspace files
        "designspace_has_consistent_groups", # We (TN) doesn’t check designspace files
        "designspace_has_default_master", # We (TN) doesn’t check designspace files
        "designspace_has_sources", # We (TN) doesn’t check designspace files
        "caps_vertically_centered",  # Disabled: issue #4274
        "ufolint", # We (TN) doesn’t check .ufo files
        "ufo_features_default_languagesystem", # We (TN) doesn’t check .ufo files
        "ufo_recommended_fields", # We (TN) doesn’t check .ufo files
        "ufo_required_fields", # We (TN) doesn’t check .ufo files
        "ufo_unnecessary_fields", # We (TN) doesn’t check .ufo files
        "googlefonts/glyphsets/shape_languages",
        "googlefonts/metadata/primary_script",
        "googlefonts/metadata/unreachable_subsetting",
        "cmap/format_12",
        "cjk_not_enough_glyphs",
        "color_cpal_brightness", # Color fonts 
        "colorfont_tables", # Color fonts 
        "empty_glyph_on_gid1_for_colrv0", # Color fonts 
        "hinting_impact",
        "render_own_name",
        "vtt_volt_data",  # Very similar to 'vttclean' check, it may be a good idea to merge them.
        "varfont/unsupported_axes", # Despite we don’t encourage the use, TN accept fonts with ital axis. 
        "file_size",
        "googlefonts/metadata/valid_nameid25",
        "fontval",  # Temporarily disabled
    ],
    "sections": {
        "Type Network": [
            "typenetwork/composite_glyphs",
            "typenetwork/family/duplicated_names",
            "typenetwork/family/equal_numbers_of_glyphs",
            "typenetwork/family/tnum_horizontal_metrics",
            "typenetwork/family/valid_strikeout",
            "typenetwork/family/valid_underline",
            "typenetwork/font_is_centered_vertically",
            "typenetwork/glyph_coverage",
            "typenetwork/marks_width",
            "typenetwork/name/mandatory_entries",
            "typenetwork/PUA_encoded_glyphs",
            "typenetwork/usweightclass",
            "typenetwork/varfont/axes_have_variation",
            "typenetwork/varfont/fvar_axes_order",
            "typenetwork/vertical_metrics",
        ],
        "Adobe Fonts": [
            "adobefonts/family/consistent_upm",
            "adobefonts/nameid_1_win_english",
            "adobefonts/STAT_strings",
            "adobefonts/unsupported_tables",
        ],
        "Fontwerk": [
            "fontwerk/style_linking",
        ],
        "Google Fonts": [
            "googlefonts/family/equal_codepoint_coverage",
            "googlefonts/varfont/bold_wght_coord",
            "googlefonts/varfont/duplicate_instance_names",
            "googlefonts/negative_advance_width",
            "googlefonts/STAT/axis_order",
        ],
        "Outline Checks": [
            "outline_alignment_miss",
            "outline_colinear_vectors",
            "outline_jaggy_segments",
            "outline_semi_vertical",
            "outline_short_segments",
        ],
        "Shaping Checks": [
            "dotted_circle",
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
        "ligature_carets": [
            {
                "code": "lacks-caret-pos",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "kerning_for_non_ligated_sequences": [
            {
                "code": "lacks-kern-info",
                "status": "INFO",
                "reason": "This is a feature, not really needed to the font perform well.",
            },
        ],
        "googlefonts/varfont/bold_wght_coord": [
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
        "opentype/varfont/regular_ital_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype/varfont/regular_opsz_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype/varfont/regular_slnt_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype/varfont/regular_wdth_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype/varfont/regular_wght_coord": [
            {
                "code": "no-regular-instance",
                "status": "WARN",
                "reason": "Adobe and Type Network recommend, but do not require"
                " having a Regular instance.",
            },
        ],
        "opentype/gdef_non_mark_chars": [
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
        "opentype/name/match_familyname_fullfont": [
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
