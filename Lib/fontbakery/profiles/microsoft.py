PROFILE = {
    "include_profiles": ["universal"],
    "sections": {
        "Metadata Checks": [
            "com.microsoft/check/copyright",
            "com.microsoft/check/version",
            "com.microsoft/check/trademark",
            "com.microsoft/check/manufacturer",
            "com.microsoft/check/vendor_url",
            "com.microsoft/check/license_description",
            "com.microsoft/check/fstype",
        ],
        "Name Checks": [
            "com.microsoft/check/name_id_1",
            "com.microsoft/check/name_id_2",
            "com.microsoft/check/office_ribz_req",
            "com.microsoft/check/typographic_family_name",
            "com.microsoft/check/name_length_req",
        ],
        "Metrics Checks": [
            "com.microsoft/check/vertical_metrics",
        ],
        "Variable Fonts Checks": [
            "com.microsoft/check/STAT_axis_values",
            "com.microsoft/check/STAT_table_eliding_bit",
            "com.microsoft/check/STAT_table_axis_order",
            "com.microsoft/check/fvar_STAT_axis_ranges",
        ],
        "Sanity Checks": [
            "com.microsoft/check/vtt_volt_data",
        ],
        "Glyph Checks": [
            "com.microsoft/check/tnum_glyphs_equal_widths",
        ],
    },
    "exclude_checks": [
        "com.google.fonts/check/fontbakery_version",  # We update at our own pace
        "com.google.fonts/check/tabular_kerning",  # We have tnum_glyphs_equal_widths
        "com.google.fonts/check/STAT_in_statics",  # Difference of opinion
    ],
}
