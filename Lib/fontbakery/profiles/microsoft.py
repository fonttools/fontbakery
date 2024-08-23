PROFILE = {
    "include_profiles": ["universal"],
    "exclude_checks": [
        "fontbakery_version",  # We update at our own pace
        "STAT_in_statics",  # Difference of opinion
        "tabular_kerning",  # We have tnum_glyphs_equal_widths
    ],
    "pending_review": [
        "unwanted_aat_tables",
        "opentype:cff_ascii_strings",
        "designspace_has_consistent_codepoints",
        "designspace_has_consistent_glyphset",
        "designspace_has_consistent_groups",
        "designspace_has_default_master",
        "designspace_has_sources",
        "gsub/smallcaps_before_ligatures",
        "no_debugging_tables",
        "typoascender_exceeds_Agrave",
        "ufolint",
        "ufo_features_default_languagesystem",
        "ufo_recommended_fields",
        "ufo_required_fields",
        "ufo_unnecessary_fields",
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
    },
}
