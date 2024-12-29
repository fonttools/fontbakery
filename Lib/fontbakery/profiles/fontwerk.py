# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": ["googlefonts"],
    "exclude_checks": [
        "googlefonts/canonical_filename",
        "googlefonts/family/italics_have_roman_counterparts",  # May need some improvements before we decide to include this one.
        "googlefonts/font_copyright",
        "googlefonts/fstype",
        "googlefonts/gasp",
        "googlefonts/metadata/includes_production_subsets",
        "googlefonts/meta/script_lang_tags",
        "googlefonts/name/description_max_length",
        "googlefonts/name/line_breaks",
        "googlefonts/production_glyphs_similarity",
        "googlefonts/vendor_id",
        "googlefonts/version_bump",
        "fontdata_namecheck",
    ],
    "pending_review": [
        "base_has_width",
        "googlefonts/axes_match",
        "overlapping_path_segments",
        "typographic_family_name",
        "vtt_volt_data",  # very similar to vttclean, may be a good idea to merge them.
        #
        # Note: When reviewing these 2 checks below, please check whether googlefonts also includes them or not,
        # since currently they're in googlefonts' pending_review as well.
        "cmap/format_12",
        "empty_letters",
    ],
    "sections": {
        "Fontwerk Checks": [
            "fontwerk/names_match_default_fvar",
            "fontwerk/style_linking",
            "fontwerk/vendor_id",
        ],
    },
    "configuration_defaults": {
        "file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
