PROFILE = {
    "include_profiles": ["universal"],
    "pending_review": [
        "opentype:weight_class_fvar",
        "opentype:slant_direction",
        "fvar_name_entries",
        "fontdata_namecheck",
        "glyf_nested_components",
        "hinting_impact",
        "inconsistencies_between_fvar_stat",
        "no_mac_entries",
        "render_own_name",
        "vtt_volt_data",  # very similar to vttclean, may be a good idea to merge them.
        "vttclean",
    ],
    "sections": {
        "Font Bureau Checks": [
            "fontbureau:ytlc_sanity",
        ],
    },
}
