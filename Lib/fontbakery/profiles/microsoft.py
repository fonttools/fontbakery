PROFILE = {
    "include_profiles": ["universal"],
    "exclude_checks": [
        "fontbakery_version",  # We update at our own pace
        "STAT_in_statics",  # Difference of opinion
        "tabular_kerning",  # We have tnum_glyphs_equal_widths
    ],
    "pending_review": [
        "opentype:cff_ascii_strings",
        "opentype:weight_class_fvar",
        "designspace_has_consistent_codepoints",
        "designspace_has_consistent_glyphset",
        "designspace_has_consistent_groups",
        "designspace_has_default_master",
        "designspace_has_sources",
        "fvar_name_entries",
        "fontdata_namecheck",
        "glyf_nested_components",
        "hinting_impact",
        "gsub/smallcaps_before_ligatures",
        "inconsistencies_between_fvar_stat",
        "no_debugging_tables",
        "no_mac_entries",
        "typoascender_exceeds_Agrave",
        "ufolint",
        "ufo_features_default_languagesystem",
        "ufo_recommended_fields",
        "ufo_required_fields",
        "ufo_unnecessary_fields",
        "unwanted_aat_tables",
        "vttclean",  # very similar to vtt_volt_data, may be a good idea to merge them.
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
            #
            "name_id_1",
            "name_id_2",
            "name_length_req",
            "typographic_family_name",
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
        "Glyph Checks": [
            "tnum_glyphs_equal_widths",
        ],
    },
}
