PROFILE = {
    "include_profiles": ["universal"],
    "exclude_checks": [
        "fontbakery_version",  # We update at our own pace
        "STAT_in_statics",  # Difference of opinion
        "tabular_kerning",  # We have tnum_glyphs_equal_widths
    ],
    "pending_review": [
        "opentype:cff_ascii_strings",
        "opentype:slant_direction",
        "opentype:weight_class_fvar",
        "cmap/format_12",
        "designspace_has_consistent_codepoints",
        "designspace_has_consistent_glyphset",
        "designspace_has_consistent_groups",
        "designspace_has_default_master",
        "designspace_has_sources",
        "empty_letters",
        "family/control_chars",
        "fvar_name_entries",
        "fontdata_namecheck",
        "glyf_nested_components",
        "hinting_impact",
        "gsub/smallcaps_before_ligatures",
        "inconsistencies_between_fvar_stat",
        "mandatory_avar_table",
        "missing_small_caps_glyphs",
        "name/family_and_style_max_length",
        "no_debugging_tables",
        "no_mac_entries",
        "render_own_name",
        "stylisticset_description",
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
            "name_id_1",  # TODO: These name id 1 & 2 checks are too simple. Maybe they could be merged.
            "name_id_2",  # TODO: Also, they could be included in some other name table check on the universal profile.
            "name_length_req",  # TODO: Maybe the same applies to this one.
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
            "tnum_glyphs_equal_widths",  # TODO: compare this to 'tabular_kerning' to attempt merging them into a single check.
        ],
    },
}
