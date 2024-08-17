# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": ["googlefonts"],
    "sections": {
        "Fontwerk Checks": [
            "fontwerk:names_match_default_fvar",
            "fontwerk:style_linking",
            "fontwerk:vendor_id",
            #
            "inconsistencies_between_fvar_stat",
            "no_mac_entries",
            "weight_class_fvar",
        ],
    },
    "exclude_checks": [
        "googlefonts:canonical_filename",
        "googlefonts:family/italics_have_roman_counterparts",  # May need some improvements before we decide to include this one.
        "googlefonts:font_copyright",
        "googlefonts:fstype",
        "googlefonts:gasp",
        "googlefonts:metadata/includes_production_subsets",
        "googlefonts:meta/script_lang_tags",
        "googlefonts:name/description_max_length",
        "googlefonts:name/line_breaks",
        "googlefonts:production_glyphs_similarity",
        "googlefonts:vendor_id",
        "googlefonts:version_bump",
        #
        "fontdata_namecheck",
    ],
    "configuration_defaults": {
        "googlefonts:file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
