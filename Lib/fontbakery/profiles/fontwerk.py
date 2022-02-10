PROFILE = {
    "include_profiles": ["googlefonts"],
    "sections": {
        "Fontwerk Checks": [
            "com.fontwerk/check/no_mac_entries",
            "com.fontwerk/check/vendor_id",
            "com.fontwerk/check/weight_class_fvar",
            "com.fontwerk/check/inconsistencies_between_fvar_stat",
            "com.fontwerk/check/style_linking",
            "com.fontwerk/check/names_match_default_fvar",
        ],
    },
    "exclude_checks": [
        # don't run these checks on the Fontwerk profile:
        "com.google.fonts/check/canonical_filename",
        "com.google.fonts/check/vendor_id",
        "com.google.fonts/check/fstype",
        "com.google.fonts/check/gasp",
        "com.google.fonts/check/name/description_max_length",
        "com.google.fonts/check/metadata/includes_production_subsets",
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/version_bump",
        "com.google.fonts/check/production_glyphs_similarity",
        "com.google.fonts/check/name/line_breaks",
        "com.google.fonts/check/fontdata_namecheck",
        "com.google.fonts/check/meta/script_lang_tags",
        # The following check they may need some improvements
        # before we decide to include it:
        "com.google.fonts/check/family/italics_have_roman_counterparts",
    ],
    "configuration_defaults": {
        "com.google.fonts/check/file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
