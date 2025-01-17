# pylint: disable=line-too-long  # This is data, not code

# The dictionary below documents the renaming of checks-IDs that happened
# between version v0.12.10 (keys) and v0.13.0 (values)
renaming_map = {
    "com.adobe.fonts/check/family/consistent_upm":                          "adobefonts/family/consistent_upm",
    "com.adobe.fonts/check/nameid_1_win_english":                           "adobefonts/nameid_1_win_english",
    "com.adobe.fonts/check/STAT_strings":                                   "adobefonts/STAT_strings",
    "com.adobe.fonts/check/unsupported_tables":                             "adobefonts/unsupported_tables",
    "com.google.fonts/check/alt_caron":                                     "alt_caron",
    "com.google.fonts/check/arabic_high_hamza":                             "arabic_high_hamza",
    "com.google.fonts/check/arabic_spacing_symbols":                        "arabic_spacing_symbols",
    "com.google.fonts/check/case_mapping":                                  "case_mapping",
    "com.google.fonts/check/caps_vertically_centered":                      "caps_vertically_centered",
    "com.google.fonts/check/cjk_chws_feature":                              "cjk_chws_feature",
    "com.google.fonts/check/cjk_not_enough_glyphs":                         "cjk_not_enough_glyphs",
    "com.google.fonts/check/cmap/format_12":                                "cmap/format_12",
    "com.google.fonts/check/color_cpal_brightness":                         "color_cpal_brightness",
    "com.google.fonts/check/contour_count":                                 "contour_count",
    "com.google.fonts/check/family/control_chars":                          "control_chars",
    "com.google.fonts/check/designspace_has_consistent_codepoints":         "designspace_has_consistent_codepoints",
    "com.google.fonts/check/designspace_has_consistent_glyphset":           "designspace_has_consistent_glyphset",
    "com.daltonmaag/check/designspace_has_consistent_groups":               "designspace_has_consistent_groups",
    "com.google.fonts/check/designspace_has_default_master":                "designspace_has_default_master",
    "com.google.fonts/check/designspace_has_sources":                       "designspace_has_sources",
    "com.google.fonts/check/dotted_circle":                                 "dotted_circle",
    "com.google.fonts/check/empty_glyph_on_gid1_for_colrv0":                "empty_glyph_on_gid1_for_colrv0",
    "com.adobe.fonts/check/find_empty_letters":                             "empty_letters",
    "com.google.fonts/check/epar":                                          "epar",
    "com.google.fonts/check/family/single_directory":                       "family/single_directory",
    "com.google.fonts/check/family/vertical_metrics":                       "family/vertical_metrics",
    "com.google.fonts/check/family/win_ascent_and_descent":                 "family/win_ascent_and_descent",
    "com.google.fonts/check/file_size":                                     "file_size",
    "com.google.fonts/check/fontbakery_version":                            "fontbakery_version",
    "io.github.abysstypeco/check/ytlc_sanity":                              "fontbureau/ytlc_sanity",
    "com.google.fonts/check/fontdata_namecheck":                            "fontdata_namecheck",
    "com.google.fonts/check/fontvalidator":                                 "fontvalidator",
    "com.fontwerk/check/names_match_default_fvar":                          "fontwerk/names_match_default_fvar",
    "com.fontwerk/check/style_linking":                                     "fontwerk/style_linking",
    "com.fontwerk/check/vendor_id":                                         "fontwerk/vendor_id",
    "com.adobe.fonts/check/freetype_rasterizer":                            "freetype_rasterizer",
    "com.google.fonts/check/fvar_name_entries":                             "fvar_name_entries",
    "com.google.fonts/check/glyphs_file/name/family_and_style_max_length":  "glyphs_file/name/family_and_style_max_length",
    "com.google.fonts/check/article/images":                                "googlefonts/article/images",
    "com.google.fonts/check/gf_axisregistry/fvar_axis_defaults":            "googlefonts/axisregistry/fvar_axis_defaults",
    "com.google.fonts/check/canonical_filename":                            "googlefonts/canonical_filename",
    "com.google.fonts/check/cjk_vertical_metrics":                          "googlefonts/cjk_vertical_metrics",
    "com.google.fonts/check/cjk_vertical_metrics_regressions":              "googlefonts/cjk_vertical_metrics_regressions",
    "com.google.fonts/check/colorfont_tables":                              "googlefonts/colorfont_tables",
    "com.google.fonts/check/description/broken_links":                      "googlefonts/description/broken_links",
    "com.google.fonts/check/description/eof_linebreak":                     "googlefonts/description/eof_linebreak",
    "com.google.fonts/check/description/family_update":                     "googlefonts/description/family_update",
    "com.google.fonts/check/description/git_url":                           "googlefonts/description/git_url",
    "com.google.fonts/check/description/has_article":                       "googlefonts/description/has_article",
    "com.google.fonts/check/description/has_unsupported_elements":          "googlefonts/description/has_unsupported_elements",
    "com.google.fonts/check/description/min_length":                        "googlefonts/description/min_length",
    "com.google.fonts/check/description/urls":                              "googlefonts/description/urls",
    "com.google.fonts/check/description/valid_html":                        "googlefonts/description/valid_html",
    "com.google.fonts/check/name/family_name_compliance":                   "googlefonts/family_name_compliance",
    "com.google.fonts/check/family/equal_codepoint_coverage":               "googlefonts/family/equal_codepoint_coverage",
    "com.google.fonts/check/family/has_license":                            "googlefonts/family/has_license",
    "com.google.fonts/check/family/italics_have_roman_counterparts":        "googlefonts/family/italics_have_roman_counterparts",
    "com.google.fonts/check/family/tnum_horizontal_metrics":                "googlefonts/family/tnum_horizontal_metrics",
    "com.google.fonts/check/font_copyright":                                "googlefonts/font_copyright",
    "com.google.fonts/check/font_names":                                    "googlefonts/font_names",
    "com.google.fonts/check/fstype":                                        "googlefonts/fstype",
    "com.google.fonts/check/fvar_instances":                                "googlefonts/fvar_instances",
    "com.google.fonts/check/gasp":                                          "googlefonts/gasp",
    "com.google.fonts/check/glyph_coverage":                                "googlefonts/glyph_coverage",
    "com.google.fonts/check/glyphsets/shape_languages":                     "googlefonts/glyphsets/shape_language",
    "com.google.fonts/check/has_ttfautohint_params":                        "googlefonts/has_ttfautohint_params",
    "com.google.fonts/check/license/OFL_body_text":                         "googlefonts/license/OFL_body_text",
    "com.google.fonts/check/license/OFL_copyright":                         "googlefonts/license/OFL_copyright",
    "com.google.fonts/check/meta/script_lang_tags":                         "googlefonts/meta/script_lang_tags",
    "com.google.fonts/check/metadata/gf_axisregistry_bounds":               "googlefonts/metadata/axisregistry_bounds",
    "com.google.fonts/check/metadata/gf_axisregistry_valid_tags":           "googlefonts/metadata/axisregistry_valid_tags",
    "com.google.fonts/check/metadata/broken_links":                         "googlefonts/metadata/broken_links",
    "com.google.fonts/check/metadata/can_render_samples":                   "googlefonts/metadata/can_render_samples",
    "com.google.fonts/check/metadata/canonical_style_names":                "googlefonts/metadata/canonical_style_names",
    "com.google.fonts/check/metadata/canonical_weight_value":               "googlefonts/metadata/canonical_weight_value",
    "com.google.fonts/check/metadata/category":                             "googlefonts/metadata/category",
    "com.google.fonts/check/metadata/category_hints":                       "googlefonts/metadata/category_hints",
    "com.google.fonts/check/metadata/consistent_axis_enumeration":          "googlefonts/metadata/consistent_axis_enumeration",
    "com.google.fonts/check/metadata/consistent_repo_urls":                 "googlefonts/metadata/consistent_repo_urls",
    "com.google.fonts/check/metadata/copyright":                            "googlefonts/metadata/copyright",
    "com.google.fonts/check/metadata/date_added":                           "googlefonts/metadata/date_added",
    "com.google.fonts/check/metadata/designer_profiles":                    "googlefonts/metadata/designer_profiles",
    "com.google.fonts/check/metadata/designer_values":                      "googlefonts/metadata/designer_values",
    "com.google.fonts/check/metadata/empty_designer":                       "googlefonts/metadata/empty_designer",
    "com.google.fonts/check/metadata/escaped_strings":                      "googlefonts/metadata/escaped_strings",
    "com.google.fonts/check/metadata/family_directory_name":                "googlefonts/metadata/family_directory_name",
    "com.google.fonts/check/metadata/familyname":                           "googlefonts/metadata/familyname",
    "com.google.fonts/check/metadata/filenames":                            "googlefonts/metadata/filenames",
    "com.google.fonts/check/metadata/has_regular":                          "googlefonts/metadata/has_regular",
    "com.google.fonts/check/metadata/includes_production_subsets":          "googlefonts/metadata/includes_production_subsets",
    "com.google.fonts/check/metadata/license":                              "googlefonts/metadata/license",
    "com.google.fonts/check/metadata/match_filename_postscript":            "googlefonts/metadata/match_filename_postscript",
    "com.google.fonts/check/metadata/match_fullname_postscript":            "googlefonts/metadata/match_fullname_postscript",
    "com.google.fonts/check/metadata/match_name_familyname":                "googlefonts/metadata/match_name_familyname",
    "com.google.fonts/check/metadata/match_weight_postscript":              "googlefonts/metadata/match_weight_postscript",
    "com.google.fonts/check/metadata/menu_and_latin":                       "googlefonts/metadata/menu_and_latin",
    "com.google.fonts/check/metadata/minisite_url":                         "googlefonts/metadata/minisite_url",
    "com.google.fonts/check/metadata/nameid/family_and_full_names":         "googlefonts/metadata/nameid/family_and_full_names",
    "com.google.fonts/check/metadata/nameid/font_name":                     "googlefonts/metadata/nameid/font_name",
    "com.google.fonts/check/metadata/nameid/post_script_name":              "googlefonts/metadata/nameid/post_script_name",
    "com.google.fonts/check/metadata/parses":                               "googlefonts/metadata/parses",
    "com.google.fonts/check/metadata/primary_script":                       "googlefonts/metadata/primary_script",
    "com.google.fonts/check/metadata/regular_is_400":                       "googlefonts/metadata/regular_is_400",
    "com.google.fonts/check/metadata/reserved_font_name":                   "googlefonts/metadata/reserved_font_name",
    "com.google.fonts/check/metadata/single_cjk_subset":                    "googlefonts/metadata/single_cjk_subset",
    "com.google.fonts/check/metadata/subsets_order":                        "googlefonts/metadata/subsets_order",
    "com.google.fonts/check/metadata/undeclared_fonts":                     "googlefonts/metadata/undeclared_fonts",
    "com.google.fonts/check/metadata/unique_full_name_values":              "googlefonts/metadata/unique_full_name_values",
    "com.google.fonts/check/metadata/unique_weight_style_pairs":            "googlefonts/metadata/unique_weight_style_pairs",
    "com.google.fonts/check/metadata/unreachable_subsetting":               "googlefonts/metadata/unreachable_subsetting",
    "com.google.fonts/check/metadata/unsupported_subsets":                  "googlefonts/metadata/unsupported_subsets",
    "com.google.fonts/check/metadata/valid_filename_values":                "googlefonts/metadata/valid_filename_values",
    "com.google.fonts/check/metadata/valid_full_name_values":               "googlefonts/metadata/valid_full_name_values",
    "com.google.fonts/check/metadata/valid_nameid25":                       "googlefonts/metadata/valid_nameid25",
    "com.google.fonts/check/metadata/valid_post_script_name_values":        "googlefonts/metadata/valid_post_script_name_values",
    "com.google.fonts/check/metadata/os2_weightclass":                      "googlefonts/metadata/weightclass",
    "com.google.fonts/check/name/description_max_length":                   "googlefonts/name/description_max_length",
    "com.google.fonts/check/name/familyname_first_char":                    "googlefonts/name/familyname_first_char",
    "com.google.fonts/check/name/license":                                  "googlefonts/name/license",
    "com.google.fonts/check/name/license_url":                              "googlefonts/name/license_url",
    "com.google.fonts/check/name/line_breaks":                              "googlefonts/name/line_breaks",
    "com.google.fonts/check/name/mandatory_entries":                        "googlefonts/name/mandatory_entries",
    "com.google.fonts/check/name/rfn":                                      "googlefonts/name/rfn",
    "com.google.fonts/check/name/version_format":                           "googlefonts/name/version_format",
    "com.google.fonts/check/old_ttfautohint":                               "googlefonts/old_ttfautohint",
    "com.google.fonts/check/production_encoded_glyphs":                     "googlefonts/production_encoded_glyphs",
    "com.google.fonts/check/production_glyphs_similarity":                  "googlefonts/production_glyphs_similarity",
    "com.google.fonts/check/render_own_name":                               "googlefonts/render_own_name",
    "com.google.fonts/check/repo/dirname_matches_nameid_1":                 "googlefonts/repo/dirname_matches_nameid_1",
    "com.google.fonts/check/repo/fb_report":                                "googlefonts/repo/fb_report",
    "com.google.fonts/check/repo/sample_image":                             "googlefonts/repo/sample_image",
    "com.google.fonts/check/repo/upstream_yaml_has_required_fields":        "googlefonts/repo/upstream_yaml_has_required_fields",
    "com.google.fonts/check/repo/vf_has_static_fonts":                      "googlefonts/repo/vf_has_static_fonts",
    "com.google.fonts/check/repo/zip_files":                                "googlefonts/repo/zip_files",
    "com.google.fonts/check/STAT/axis_order":                               "googlefonts/STAT/axis_order",
    "com.google.fonts/check/STAT/gf_axisregistry":                          "googlefonts/STAT/axisregistry",
    "com.google.fonts/check/STAT":                                          "googlefonts/STAT/compulsory_axis_values",
    "com.google.fonts/check/unitsperem_strict":                             "googlefonts/unitsperem",
    "com.google.fonts/check/os2/use_typo_metrics":                          "googlefonts/use_typo_metrics",
    "com.google.fonts/check/varfont/generate_static":                       "googlefonts/varfont/generate_static",
    "com.google.fonts/check/varfont/has_HVAR":                              "googlefonts/varfont/has_HVAR",
    "com.google.fonts/check/vendor_id":                                     "googlefonts/vendor_id",
    "com.google.fonts/check/version_bump":                                  "googlefonts/version_bump",
    "com.google.fonts/check/vertical_metrics":                              "googlefonts/vertical_metrics",
    "com.google.fonts/check/vertical_metrics_regressions":                  "googlefonts/vertical_metrics_regressions",
    "com.google.fonts/check/usweightclass":                                 "googlefonts/weightclass",
    "com.google.fonts/check/gpos_kerning_info":                             "gpos_kerning_info",
    "com.google.fonts/check/gpos7":                                         "gpos7",
    "com.google.fonts/check/hinting_impact":                                "hinting_impact",
    "com.fontwerk/check/inconsistencies_between_fvar_stat":                 "inconsistencies_between_fvar_stat",
    "com.google.fonts/check/integer_ppem_if_hinted":                        "integer_ppem_if_hinted",
    "com.google.fonts/check/interpolation_issues":                          "interpolation_issues",
    "com.google.fonts/check/iso15008_intercharacter_spacing":               "iso15008/intercharacter_spacing",
    "com.google.fonts/check/iso15008_interline_spacing":                    "iso15008/interline_spacing",
    "com.google.fonts/check/iso15008_interword_spacing":                    "iso15008/interword_spacing",
    "com.google.fonts/check/iso15008_proportions":                          "iso15008/proportions",
    "com.google.fonts/check/iso15008_stem_width":                           "iso15008/stem_width",
    "com.google.fonts/check/legacy_accents":                                "legacy_accents",
    "com.google.fonts/check/ligature_carets":                               "ligature_carets",
    "com.google.fonts/check/linegaps":                                      "linegaps",
    "com.google.fonts/check/mandatory_avar_table":                          "mandatory_avar_table",
    "com.google.fonts/check/mandatory_glyphs":                              "mandatory_glyphs",
    "com.google.fonts/check/math_signs_width":                              "math_signs_width",
    "com.microsoft/check/copyright":                                        "microsoft/copyright",
    "com.microsoft/check/fstype":                                           "microsoft/fstype",
    "com.microsoft/check/fvar_STAT_axis_ranges":                            "microsoft/fvar_STAT_axis_ranges",
    "com.microsoft/check/license_description":                              "microsoft/license_description",
    "com.microsoft/check/manufacturer":                                     "microsoft/manufacturer",
    "com.microsoft/check/office_ribz_req":                                  "microsoft/office_ribz_req",
    "com.microsoft/check/ogl2":                                             "microsoft/ogl2",
    "com.microsoft/check/STAT_axis_values":                                 "microsoft/STAT_axis_values",
    "com.microsoft/check/STAT_table_axis_order":                            "microsoft/STAT_table_axis_order",
    "com.microsoft/check/STAT_table_eliding_bit":                           "microsoft/STAT_table_eliding_bit",
    "com.microsoft/check/trademark":                                        "microsoft/trademark",
    "com.microsoft/check/vendor_url":                                       "microsoft/vendor_url",
    "com.microsoft/check/version":                                          "microsoft/version",
    "com.microsoft/check/vertical_metrics":                                 "microsoft/vertical_metrics",
    "com.microsoft/check/wgl4":                                             "microsoft/wgl4",
    "com.google.fonts/check/missing_small_caps_glyphs":                     "missing_small_caps_glyphs",
    "com.microsoft/check/name_id_1":                                        "name_id_1",
    "com.microsoft/check/name_id_2":                                        "name_id_2",
    "com.microsoft/check/name_length_req":                                  "name_length_req",
    "com.google.fonts/check/name/ascii_only_entries":                       "name/char_restrictions",
    "com.google.fonts/check/name/family_and_style_max_length":              "name/family_and_style_max_length",
    "com.google.fonts/check/name/italic_names":                             "name/italic_names",
    "com.google.fonts/check/name/no_copyright_on_description":              "name/no_copyright_on_description",
    "com.google.fonts/check/name/trailing_spaces":                          "name/trailing_spaces",
    "com.google.fonts/check/glyf_nested_components":                        "nested_components",
    "com.google.fonts/check/no_debugging_tables":                           "unwanted_tables",
    "com.fontwerk/check/no_mac_entries":                                    "no_mac_entries",
    "com.google.fonts/check/cmap/alien_codepoints":                         "notofonts/cmap/alien_codepoints",
    "com.google.fonts/check/cmap/unexpected_subtables":                     "notofonts/cmap/unexpected_subtables",
    "com.google.fonts/check/hmtx/comma_period":                             "notofonts/hmtx/comma_period",
    "com.google.fonts/check/hmtx/encoded_latin_digits":                     "notofonts/hmtx/encoded_latin_digits",
    "com.google.fonts/check/hmtx/whitespace_advances":                      "notofonts/hmtx/whitespace_advances",
    "com.google.fonts/check/name/noto_designer":                            "notofonts/name/designer",
    "com.google.fonts/check/name/noto_manufacturer":                        "notofonts/name/manufacturer",
    "com.google.fonts/check/name/noto_trademark":                           "notofonts/name/trademark",
    "com.google.fonts/check/unicode_range_bits":                            "notofonts/unicode_range_bits",
    "com.google.fonts/check/os2/noto_vendor":                               "notofonts/vendor_id",
    "com.google.fonts/check/caret_slope":                                   "opentype/caret_slope",
    "com.adobe.fonts/check/cff_ascii_strings":                              "opentype/cff_ascii_strings",
    "com.adobe.fonts/check/cff_call_depth":                                 "opentype/cff_call_depth",
    "com.adobe.fonts/check/cff_deprecated_operators":                       "opentype/cff_deprecated_operators",
    "com.adobe.fonts/check/cff2_call_depth":                                "opentype/cff2_call_depth",
    "com.google.fonts/check/code_pages":                                    "opentype/code_pages",
    "com.google.fonts/check/family_naming_recommendations":                 "opentype/family_naming_recommendations",
    "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1":          "opentype/family/bold_italic_unique_for_nameid1",
    "com.adobe.fonts/check/family/consistent_family_name":                  "opentype/family/consistent_family_name",
    "com.google.fonts/check/family/equal_font_versions":                    "opentype/family/equal_font_versions",
    "com.adobe.fonts/check/family/max_4_fonts_per_family_name":             "opentype/family/max_4_fonts_per_family_name",
    "com.google.fonts/check/family/panose_familytype":                      "opentype/family/panose_familytype",
    "com.google.fonts/check/family/underline_thickness":                    "opentype/family/underline_thickness",
    "com.google.fonts/check/font_version TODO: double-check this!":         "opentype/font_version",
    "com.google.fonts/check/fsselection":                                   "opentype/fsselection",
    "com.adobe.fonts/check/fsselection_matches_macstyle":                   "opentype/fsselection",
    "com.typenetwork/check/varfont/ital_range":                             "opentype/fvar/axis_ranges_correct",
    "com.google.fonts/check/varfont/slnt_range":                            "opentype/fvar/axis_ranges_correct",
    "com.google.fonts/check/varfont/wdth_valid_range":                      "opentype/fvar/axis_ranges_correct",
    "com.google.fonts/check/varfont/wght_valid_range":                      "opentype/fvar/axis_ranges_correct",
    "com.google.fonts/check/varfont/regular_ital_coord":                    "opentype/fvar/regular_coords_correct",
    "com.google.fonts/check/varfont/regular_opsz_coord":                    "opentype/fvar/regular_coords_correct",
    "com.google.fonts/check/varfont/regular_slnt_coord":                    "opentype/fvar/regular_coords_correct",
    "com.google.fonts/check/varfont/regular_wdth_coord":                    "opentype/fvar/regular_coords_correct",
    "com.google.fonts/check/varfont/regular_wght_coord":                    "opentype/fvar/regular_coords_correct",
    "com.google.fonts/check/gdef_mark_chars":                               "opentype/gdef_mark_chars",
    "com.google.fonts/check/gdef_non_mark_chars":                           "opentype/gdef_non_mark_chars",
    "com.google.fonts/check/gdef_spacing_marks":                            "opentype/gdef_spacing_marks",
    "com.google.fonts/check/glyf_non_transformed_duplicate_components":     "opentype/glyf_non_transformed_duplicate_components",
    "com.google.fonts/check/glyf_unused_data":                              "opentype/glyf_unused_data",
    "com.google.fonts/check/italic_angle":                                  "opentype/italic_angle",
    "com.google.fonts/check/kern_table":                                    "opentype/kern_table",
    "com.google.fonts/check/layout_valid_feature_tags":                     "opentype/layout_valid_feature_tags",
    "com.google.fonts/check/layout_valid_language_tags":                    "opentype/layout_valid_language_tags",
    "com.google.fonts/check/layout_valid_script_tags":                      "opentype/layout_valid_script_tags",
    "com.google.fonts/check/loca/maxp_num_glyphs":                          "opentype/loca/maxp_num_glyphs",
    "com.google.fonts/check/mac_style":                                     "opentype/mac_style",
    "com.google.fonts/check/maxadvancewidth":                               "opentype/maxadvancewidth",
    "com.google.fonts/check/monospace":                                     "opentype/monospace",
    "com.adobe.fonts/check/name/empty_records":                             "opentype/name/empty_records",
    "com.google.fonts/check/name/match_familyname_fullfont":                "opentype/name/match_familyname_fullfont",
    "com.adobe.fonts/check/name/postscript_name_consistency":               "opentype/name/postscript_name_consistency",
    "com.adobe.fonts/check/name/postscript_vs_cff":                         "opentype/name/postscript_vs_cff",
    "com.google.fonts/check/points_out_of_bounds":                          "opentype/points_out_of_bounds",
    "com.google.fonts/check/post_table_version":                            "opentype/post_table_version",
    "com.adobe.fonts/check/postscript_name":                                "opentype/postscript_name",
    "com.google.fonts/check/slant_direction":                               "opentype/slant_direction",
    "com.google.fonts/check/italic_axis_in_stat":                           "opentype/STAT/ital_axis",
    "com.google.fonts/check/italic_axis_in_stat_is_boolean":                "opentype/STAT/ital_axis",
    "com.google.fonts/check/italic_axis_last":                              "opentype/STAT/ital_axis",
    "com.google.fonts/check/unitsperem":                                    "opentype/unitsperem",
    "com.adobe.fonts/check/varfont/distinct_instance_records":              "opentype/varfont/distinct_instance_records",
    "com.google.fonts/check/varfont/family_axis_ranges":                    "opentype/varfont/family_axis_ranges",
    "com.adobe.fonts/check/varfont/foundry_defined_tag_name":               "opentype/varfont/foundry_defined_tag_name",
    "com.adobe.fonts/check/varfont/same_size_instance_records":             "opentype/varfont/same_size_instance_records",
    "com.google.fonts/check/varfont/stat_axis_record_for_each_axis":        "opentype/varfont/STAT_axis_record_for_each_axis",
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids":         "opentype/varfont/valid_default_instance_nameids",
    "com.adobe.fonts/check/varfont/valid_axis_nameid":                      "opentype/varfont/valid_nameids",
    "com.adobe.fonts/check/varfont/valid_postscript_nameid":                "opentype/varfont/valid_nameids",
    "com.adobe.fonts/check/varfont/valid_subfamily_nameid":                 "opentype/varfont/valid_nameids",
    "com.thetypefounders/check/vendor_id":                                  "opentype/vendor_id",
    "com.fontwerk/check/weight_class_fvar":                                 "opentype/weight_class_fvar",
    "com.google.fonts/check/xavgcharwidth":                                 "opentype/xavgcharwidth",
    "com.google.fonts/check/os2_metrics_match_hhea":                        "os2_metrics_match_hhea",
    "com.google.fonts/check/ots":                                           "ots",
    "com.google.fonts/check/outline_alignment_miss":                        "outline_alignment_miss",
    "com.google.fonts/check/outline_colinear_vectors":                      "outline_colinear_vectors",
    "com.google.fonts/check/outline_direction":                             "outline_direction",
    "com.google.fonts/check/outline_jaggy_segments":                        "outline_jaggy_segments",
    "com.google.fonts/check/outline_semi_vertical":                         "outline_semi_vertical",
    "com.google.fonts/check/outline_short_segments":                        "outline_short_segments",
    "com.google.fonts/check/required_tables":                               "required_tables",
    "com.google.fonts/check/rupee":                                         "rupee",
    "com.adobe.fonts/check/sfnt_version":                                   "sfnt_version",
    "com.google.fonts/check/shaping/collides":                              "shaping/collides",
    "com.google.fonts/check/shaping/forbidden":                             "shaping/forbidden",
    "com.google.fonts/check/shaping/regression":                            "shaping/regression",
    "com.google.fonts/check/gsub/smallcaps_before_ligatures":               "smallcaps_before_ligatures",
    "com.google.fonts/check/smart_dropout":                                 "smart_dropout",
    "com.google.fonts/check/soft_dotted":                                   "soft_dotted",
    "com.google.fonts/check/soft_hyphen":                                   "soft_hyphen",
    "com.google.fonts/check/STAT_in_statics":                               "STAT_in_statics",
    "com.google.fonts/check/STAT_strings":                                  "STAT_strings",
    "com.google.fonts/check/stylisticset_description":                      "stylisticset_description",
    "com.google.fonts/check/superfamily/list":                              "superfamily/list",
    "com.google.fonts/check/superfamily/vertical_metrics":                  "superfamily/vertical_metrics",
    "com.google.fonts/check/tabular_kerning":                               "tabular_kerning",
    "com.microsoft/check/tnum_glyphs_equal_widths":                         "tnum_glyphs_equal_widths",
    "com.google.fonts/check/transformed_components":                        "transformed_components",
    "com.google.fonts/check/ttx_roundtrip":                                 "ttx_roundtrip",
    "com.typenetwork/check/composite_glyphs":                               "typenetwork/composite_glyphs",
    "com.typenetwork/check/family/duplicated_names":                        "typenetwork/family/duplicated_names",
    "com.typenetwork/check/family/equal_numbers_of_glyphs":                 "typenetwork/family/equal_numbers_of_glyphs",
    "com.typenetwork/check/family/tnum_horizontal_metrics":                 "typenetwork/family/tnum_horizontal_metrics",
    "com.typenetwork/check/family/valid_strikeout":                         "typenetwork/family/valid_strikeout",
    "com.typenetwork/check/family/valid_underline":                         "typenetwork/family/valid_underline",
    "com.typenetwork/check/font_is_centered_vertically":                    "typenetwork/font_is_centered_vertically",
    "com.typenetwork/check/glyph_coverage":                                 "typenetwork/glyph_coverage",
    "com.typenetwork/check/marks_width":                                    "typenetwork/marks_width",
    "com.typenetwork/check/name/mandatory_entries":                         "typenetwork/name/mandatory_entries",
    "com.typenetwork/check/PUA_encoded_glyphs":                             "typenetwork/PUA_encoded_glyphs",
    "com.typenetwork/check/usweightclass":                                  "typenetwork/weightclass",
    "com.typenetwork/check/varfont/axes_have_variation":                    "typenetwork/varfont/axes_have_variation",
    "com.typenetwork/check/varfont/fvar_axes_order":                        "typenetwork/varfont/fvar_axes_order",
    "com.typenetwork/check/vertical_metrics":                               "typenetwork/vertical_metrics",
    "com.arrowtype.fonts/check/typoascender_exceeds_Agrave":                "typoascender_exceeds_Agrave",
    "com.microsoft/check/typographic_family_name":                          "typographic_family_name",
    "com.google.fonts/check/consistent_curve_type":                         "ufo_consistent_curve_type",
    "com.thetypefounders/check/features_default_languagesystem":            "ufo_features_default_languagesystem",
    "com.daltonmaag/check/no_open_corners":                                 "ufo_no_open_corners",
    "com.daltonmaag/check/ufo_recommended_fields":                          "ufo_recommended_fields",
    "com.daltonmaag/check/ufo_required_fields":                             "ufo_required_fields",
    "com.daltonmaag/check/ufo_unnecessary_fields":                          "ufo_unnecessary_fields",
    "com.daltonmaag/check/ufolint":                                         "ufolint",
    "com.google.fonts/check/unique_glyphnames":                             "unique_glyphnames",
    "com.google.fonts/check/unreachable_glyphs":                            "unreachable_glyphs",
    "com.google.fonts/check/aat":                                           "unwanted_aat_tables",
    "com.google.fonts/check/unwanted_tables":                               "unwanted_tables",
    "com.google.fonts/check/valid_glyphnames":                              "valid_glyphnames",
    "com.google.fonts/check/varfont/bold_wght_coord":                       "varfont/bold_wght_coord",
    "com.google.fonts/check/varfont/consistent_axes":                       "varfont/consistent_axes",
    "com.google.fonts/check/varfont/duplexed_axis_reflow":                  "varfont/duplexed_axis_reflow",
    "com.google.fonts/check/varfont/duplicate_instance_names":              "varfont/duplicate_instance_names",
    "com.google.fonts/check/varfont/instances_in_order":                    "varfont/instances_in_order",
    "com.google.fonts/check/varfont/unsupported_axes":                      "varfont/unsupported_axes",
    "com.microsoft/check/vtt_volt_data":                                    "vtt_volt_data",
    "com.google.fonts/check/vttclean":                                      "unwanted_tables",
    "com.google.fonts/check/whitespace_glyphs":                             "whitespace_glyphs",
    "com.google.fonts/check/whitespace_ink":                                "whitespace_ink",
    "com.google.fonts/check/whitespace_widths":                             "whitespace_widths",
}
