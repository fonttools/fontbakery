# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": ["opentype"],
    "sections": {
        "Superfamily Checks": [
            "superfamily/list",
            "superfamily/vertical_metrics",
        ],
        "UFO Sources": [
            "designspace_has_consistent_codepoints",
            "designspace_has_consistent_glyphset",
            "designspace_has_consistent_groups",
            "designspace_has_default_master",
            "designspace_has_sources",
            "ufolint",
            # "ufo_consistent_curve_type",  # FIXME (orphan check) https://github.com/fonttools/fontbakery/pull/4809
            "ufo_features_default_languagesystem",
            # "ufo_no_open_corners",  # FIXME (orphan check) https://github.com/fonttools/fontbakery/pull/4809
            "ufo_recommended_fields",
            "ufo_required_fields",
            "ufo_unnecessary_fields",
        ],
        "Universal Profile Checks": [
            "alt_caron",
            "arabic_high_hamza",
            "arabic_spacing_symbols",
            "base_has_width",
            "caps_vertically_centered",
            "case_mapping",
            "cjk_chws_feature",
            "cjk_not_enough_glyphs",
            "cmap/format_12",
            "color_cpal_brightness",
            "contour_count",
            "control_chars",
            "empty_glyph_on_gid1_for_colrv0",
            "empty_letters",
            "family/single_directory",
            "family/vertical_metrics",
            "family/win_ascent_and_descent",
            "fvar_name_entries",
            "file_size",
            "fontbakery_version",
            "fontdata_namecheck",
            "freetype_rasterizer",
            "gpos7",
            "gpos_kerning_info",
            "hinting_impact",
            "inconsistencies_between_fvar_STAT",
            "integer_ppem_if_hinted",
            "interpolation_issues",
            "legacy_accents",
            "ligature_carets",
            "linegaps",
            "mandatory_avar_table",
            "mandatory_glyphs",
            "math_signs_width",
            "missing_small_caps_glyphs",
            "name/char_restrictions",
            "name/family_and_style_max_length",
            "name/trailing_spaces",
            "name/no_copyright_on_description",
            "name/italic_names",
            "nested_components",
            "no_mac_entries",
            "os2_metrics_match_hhea",
            "ots",
            "overlapping_path_segments",
            "required_tables",
            "rupee",
            "sfnt_version",
            "smallcaps_before_ligatures",
            "smart_dropout",
            "soft_hyphen",
            "STAT_in_statics",
            "STAT_strings",
            "stylisticset_description",
            "tabular_kerning",
            "transformed_components",
            "ttx_roundtrip",
            "typoascender_exceeds_Agrave",
            "typographic_family_name",
            "unique_glyphnames",
            "unreachable_glyphs",
            "unwanted_aat_tables",
            "unwanted_tables",
            "valid_glyphnames",
            "varfont/bold_wght_coord",
            "varfont/consistent_axes",
            "varfont/duplexed_axis_reflow",
            "varfont/duplicate_instance_names",
            "varfont/instances_in_order",
            "varfont/unsupported_axes",
            "vtt_volt_data",  # very similar to vttclean, may be a good idea to merge them.
            "vttclean",
            "whitespace_glyphs",
            "whitespace_ink",
            "whitespace_widths",
        ],
    },
    "configuration_defaults": {
        "file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
