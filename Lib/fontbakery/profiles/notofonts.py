PROFILE = {
    "configuration_defaults": {
        "com.google.fonts/check/file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 16 * 1024 * 1024,
        },
    },
    "include_profiles": ["googlefonts"],
    "sections": {
        "Noto Fonts": [
            "com.google.fonts/check/cmap/unexpected_subtables",
            "com.google.fonts/check/unicode_range_bits",
            "com.google.fonts/check/name/noto_manufacturer",
            "com.google.fonts/check/name/noto_designer",
            "com.google.fonts/check/name/noto_trademark",
            "com.google.fonts/check/cmap/format_12",
            "com.google.fonts/check/os2/noto_vendor",
            "com.google.fonts/check/hmtx/encoded_latin_digits",
            "com.google.fonts/check/hmtx/comma_period",
            "com.google.fonts/check/hmtx/whitespace_advances",
            "com.google.fonts/check/cmap/alien_codepoints",
        ]
    },
    # For builds which target Google Fonts, we do want these checks, but as part of
    # onboarding we will be running check-googlefonts on such builds.
    # On other builds (e.g. targetting Android), we still want most of the Google
    # strictures but size is a premium and we will be expecting to deliver a
    # "minimal" font, so we accept the fact that there will be no Latin set and no
    # hinting information at all.
    "exclude_checks": [
        "com.google.fonts/check/render_own_name",
        "com.google.fonts/check/glyph_coverage",
        "com.google.fonts/check/smart_dropout",
        "com.google.fonts/check/gasp",
    ],
}
