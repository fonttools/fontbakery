PROFILE = {
    "include_profiles": ["opentype"],
    "pending_review": [
        "opentype:cff_ascii_strings",
    ],
    "sections": {
        "Metadata Checks": [
            "microsoft:copyright",
            "microsoft:fstype",
            "microsoft:license_description",
            "microsoft:manufacturer",
            "microsoft:trademark",
            "microsoft:vendor_url",
            "microsoft:version",
        ],
        "Name Checks": [
            "microsoft:office_ribz_req",
            "microsoft:typographic_family_name",
            #
            "name_id_1",
            "name_id_2",
            "name_length_req",
        ],
        "Metrics Checks": [
            "microsoft:vertical_metrics",
        ],
        "Variable Fonts Checks": [
            "microsoft:fvar_STAT_axis_ranges",
            "microsoft:STAT_axis_values",
            "microsoft:STAT_table_axis_order",
            "microsoft:STAT_table_eliding_bit",
        ],
        "Sanity Checks": [
            "vtt_volt_data",
        ],
        "Glyph Checks": [
            "tnum_glyphs_equal_widths",
        ],
        "Superfamily Checks": [
            "superfamily/list",
            "superfamily/vertical_metrics",
        ],
        "Universal Profile Checks": [
            "alt_caron",
            "arabic_high_hamza",
            "arabic_spacing_symbols",
            "case_mapping",
            "cjk_chws_feature",
            "contour_count",
            "family/single_directory",
            "family/vertical_metrics",
            "family/win_ascent_and_descent",
            # "fontbakery_version",  # We update at our own pace
            "freetype_rasterizer",
            "gpos7",
            "interpolation_issues",
            "legacy_accents",
            "linegaps",
            "mandatory_glyphs",
            "math_signs_width",
            "name/trailing_spaces",
            "os2_metrics_match_hhea",
            "ots",
            "required_tables",
            "rupee",
            "sfnt_version",
            "soft_hyphen",
            # "STAT_in_statics",  # Difference of opinion
            "STAT_strings",
            # "tabular_kerning",  # We have tnum_glyphs_equal_widths
            "transformed_components",
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
}
