This document is a recompilation of our CHANGELOG.md info, listing the full set of changes implemented in 2022.

## FontBakery in 2022

There were 13 releases in 2022:
* The 6 stable releases from v0.8.5 in January until v0.8.10 in August.
* And 7 pre-releases of the upcoming version v0.8.11

### New Profile
  - Olli Meier (@moontypespace) contributed a new profile for Fontwerk, https://fontwerk.com/ (PR #3546)

### New Checks
In 2022, there were 45 new checks added to FontBakery across its profiles, as listed below.

#### 10 new checks added to the `Universal` profile
  - **[com.google.fonts/check/cjk_chws_feature]:** Ensure CJK fonts contain chws/vchw features. (issue [#3363](https://github.com/googlefonts/fontbakery/issues/3363))
  - **[com.google.fonts/check/designspace_has_sources]:** Check that all sources in a designspace can be loaded successfully. (PR [#3168](https://github.com/googlefonts/fontbakery/issues/3168))
  - **[com.google.fonts/check/designspace_has_default_master]:** Check that a default master is defined. (PR #3168)
  - **[com.google.fonts/check/designspace_has_consistent_glyphset]:** Check that non-default masters do not contain glyphs not found in the default master. (PR #3168)
  - **[com.google.fonts/check/designspace_has_consistent_codepoints]:** Check that Unicode assignments are consistent between masters. (PR #3168)
  - **[com.google.fonts/check/dotted_circle]:** Check dotted circle is present and correct (issue #3600)
  - **[com.google.fonts/check/gsub5_gpos7]:** Check if font contains any GSUB 5 or GPOS 7 lookups which are not widely supported. (issue #3643)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Checks that the font can be rasterized by FreeType. (issue #3642)
  - **[com.adobe.fonts/check/sfnt_version]:** Ensures the font has the proper sfntVersion value. (issue #3388)
  - **[com.google.fonts/check/interpolation_issues]:** Check for shape order or curve start point interpolation issues within a variable font. (issue #3930)

#### 8 new checks added to the `Open Type` profile
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Validates that STAT table has Axis Value tables. (issue #3090)
  - **[com.adobe.fonts/check/varfont/valid_axis_nameid]:** Validates that the value of axisNameID used by each VariationAxisRecord is greater than 255 and less than 32768. (issue #3702)
  - **[com.adobe.fonts/check/varfont/valid_subfamily_nameid]:** Validates that the value of subfamilyNameID used by each InstanceRecord is 2, 17, or greater than 255 and less than 32768. (issue #3703)
  - **[com.adobe.fonts/check/varfont/valid_postscript_nameid]:** Validates that the value of postScriptNameID used by each InstanceRecord is 6, 0xFFFF, or greater than 255 and less than 32768. (issue #3704)
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** Validates that when an instance record is included for the default instance, its subfamilyNameID value is set to either 2 or 17, and its postScriptNameID value is set to 6. (issue #3708)
  - **[com.adobe.fonts/check/varfont/same_size_instance_records]:** Validates that all of the instance records in a given font have the same size, with all either including or omitting the postScriptNameID field. (issue #3705)
  - **[com.adobe.fonts/check/varfont/distinct_instance_records]:** Validates that all of the instance records in a given font have distinct data. (issue #3706)
  - **[com.thetypefounders/check/vendor_id]:** When a font project's Vendor ID is specified explicitely on FontBakery's configuration file, all binaries must have a matching vendor identifier value in the OS/2 table. (PR #3941)

#### 11 new checks added to the `Google Fonts` profile
  - **[com.google.fonts/check/metadata/unsupported_subsets]:** Check for METADATA subsets with zero support. (issue #3533)
  - **[com.google.fonts/check/metadata/category_hints]:** Check if category on METADATA.pb matches what can be inferred from keywords in the family name. (issue #3624)
  - **[com.google.fonts/check/vertical_metrics]:** Similar to `cjk_vertical_metrics`, this check enforces Google Fonts’ general vertical metrics specifications.
  - **[com.google.fonts/check/font_names]:** Ensure font names match our specification (PR #3800)
  - **[com.google.fonts/check/fvar_instances]:** Ensure fvar instances match our specification (PR #3800)
  - **[com.google.fonts/check/STAT]:** Ensure fonts have compulsory STAT table axis values (PR #3800)
  - **[com.google.fonts/check/colorfont_tables]:** Check if fonts contain the correct color tables. (issue #3886)
  - **[com.google.fonts/check/description/noto_has_article]:** Noto fonts must have an ARTICLE.en_us.html file. (issue #3841)
  - **[com.google.fonts/check/slant_direction]:** Check slant direction of outline to match values of slnt axis extrema. (PR #3910)
  - **[com.google.fonts/check/color_cpal_brightness]:** Warn if COLRv0 layers are colored too dark or too bright instead of foreground color. (PR #3908)
  - **[com.google.fonts/check/empty_glyph_on_gid1_for_colrv0]:** Ensure that GID 1 is empty to work around Windows 10 rendering bug ([gftools issue #609](https://github.com/googlefonts/gftools/issues/609))

#### 9 new checks added to the `Noto Fonts` profile
  - The majority of checks from the Google Fonts profile have been added. (PR #3681)
  - **[com.google.fonts/check/name/noto_manufacturer]:** Checks for a known manufacturer name and correct designer URL in the name table. (PR #3681)
  - **[com.google.fonts/check/name/noto_designer]:** Checks for a known designer name. (PR #3681)
  - **[com.google.fonts/check/name/noto_trademark]:** Checks that the trademark entry in the name table is correct. (PR #3681)
  - **[com.google.fonts/check/cmap/format_12]:** Checks that format 12 cmap tables are used appropriately. (PR #3681)
  - **[com.google.fonts/check/os2/noto_vendor]:** Checks that the vendor ID in the OS/2 table is set to GOOG. (PR #3681)
  - **[com.google.fonts/check/hmtx/encoded_latin_digits]:** Checks that any encoded Latin digits have equal advance width. (PR #3681)
  - **[com.google.fonts/check/hmtx/comma_period]:** Checks that the comma and period glyphs have the same advance width as each other. (PR #3681)
  - **[com.google.fonts/check/hmtx/whitespace_advances]:** Checks that whitespace glyphs have expected advance widths. (PR #3681)
  - **[com.google.fonts/check/cmap/alien_codepoints]:** Checks that there are no surrogate pair or private use area codepoints encoded in the cmap table. (PR #3681)

#### 2 new checks added to the `Adobe Fonts` profile
  - **[com.adobe.fonts/check/nameid_1_win_english]:** Validates that the font has a good nameID 1, Windows/Unicode/US-English `name` table record. (issue #3714)
  - **[com.adobe.fonts/check/unsupported_tables]:** Verifies if fonts contain any tables not supported by Adobe Fonts' font-processing pipeline (PR #3870)

#### 5 new checks added to the `FontWerk` profile
  - **[com.fontwerk/check/no_mac_entries]:** Check if font has Mac name table entries (platform=1) (PR #3545)
  - Include most of the `googlefonts` profile checks. (PR #3579)
  - **[com.fontwerk/check/vendor_id]:** Vendor ID must be 'WERK' on FontWerk fonts. (PR #3579)
  - **[com.fontwerk/check/weight_class_fvar]:** usWeightclass must match fvar default value. (PR #3579)
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Check for inconsistencies in names and values between the fvar instances and STAT table which may cause issues in apps like Adobe InDesign. (PR #3636)
  - **[com.fontwerk/check/style_linking]:** Look for possible style linking issues. (PR #3649)


### Deprecated Checks
#### Removed from the `Google Fonts` profile
  - **[com.google.fonts/check/name/familyname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/name/subfamilyname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/name/fullfontname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/name/postscriptname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/name/typographicfamilyname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/name/typographicsubfamilyname]:** Removed due to new `font_names` check (PR #3800)
  - **[com.google.fonts/check/varfont_has_instances]:** Removed due to new `fvar_instances` check (PR #3800)
  - **[com.google.fonts/check/varfont_weight_instances]:** Removed due to new `fvar_instances` check (PR #3800)
  - **[com.google.fonts/check/varfont_instance_coordinates]:** Removed due to new `fvar_instances` check (PR #3800)
  - **[com.google.fonts/check/varfont_instance_names]:** Removed due to new `fvar_instances` check (PR #3800)
  - **[com.google.fonts/check/description_max_length]**: Recent requirement from GF marketing team is to remove character limit on description. GF specimen page has been updated to allow bigger description text from designers. (issue #3829)

#### Removed from the `Open Type` and `Adobe Fonts` profiles
  - **[com.google.fonts/check/all_glyphs_have_codepoints]:** This check cannot ever fail with fontTools and is therefore redundant. (issue #1793)


### Migrations
#### To the `Universal` profile
  - **[com.google.fonts/check/transformed_components]:** moved from `Google Fonts` profile. It is not strictly a Google Fonts related check as transformed components cause problems in various rendering environments. (issue #3588)
  - **[com.google.fonts/check/whitespace_widths]:** moved from `OpenType` profile. Also added rationale text. (issue #3843)


### Changes to existing checks
#### On the `Universal` profile
  - **[com.google.fonts/check/unreachable_glyphs]:** Glyphs which are components of other glyphs are no longer flagged as unreachable. (issue #3523)
  - **[com.google.fonts/check/dotted_circle]:** Fix ERROR by adding safeguard conditional on `is_complex_shaper_font` function. (issue #3640)
  - **[com.google.fonts/check/repo/upstream_yaml_has_required_fields]:** Remove repository_url field check since METADATA.pb files now include the source field. (issue #3618)
  - **[com.google.fonts/check/valid_glyphnames]:** Ignore colored .notdef glyphs (PR #3807)
  - **[com.google.fonts/check/name/rfn]:** Do not FAIL if an RFN is found but referencing a familyname that differs frmo the currently used name. Just emit an WARN message instead, so that we're careful with font naming. (PR #3739)
  - **[com.google.fonts/check/varfont/unsupported_axes]:** Allow slnt axis (PR #3795)
  - **[com.google.fonts/check/dotted_circle]:** Fix ERROR on fonts without GlyphClassDef.classDefs (issue #3736)
  - **[com.google.fonts/check/transformed_components]:** Check for any component transformation only if font is hinted, otherwise check only for flipped contour direction (one transformation dimension is flipped while the other isn't)
  - **[com.google.fonts/check/gpos7]:** Previously we checked for the existence of GSUB 5 lookups in the erroneous belief that they were not supported; GPOS 7 lookups are not supported in CoreText, but GSUB 5 lookups are fine. (issue #3689)
  - **[com.google.fonts/check/required_tables]:** CFF/CFF2 fonts are now checked instead of skipped. (PR #3742)
  - **[com.google.fonts/check/family/win_ascent_and_descent]:** Fixed the parameter used in the FAIL message that is issued when the value of `usWinAscent` is too large. (PR #3745)
  - **[com.google.fonts/check/fontbakery_version]:** A change introduced in #3432 made this check always be skipped; that's now fixed. (issue #3576)
  - **[com.google.fonts/check/fontbakery_version]:** If the request to PyPI.org is not successful (due to host errors, or lack of internet connection), the check fails. (PR #3756)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** Included lineGap in comparison
  - **[com.google.fonts/check/family/vertical_metrics]:** Included hhea.lineGap in comparison
  - **[com.google.fonts/check/superfamily/vertical_metrics]:** Included hhea.lineGap in comparison
  - **[com.google.fonts/check/contour_count]:** U+0024 DOLLAR SIGN can also have 5 contours, to support glyphs with two strokes. (issue #3780)
  - **[com.google.fonts/check/unreachable_glyphs]:** Do not report glyphs referenced in color fonts graphic compositions on the COLR table as missing. (issue #3837)
  - **[com.google.fonts/check/unreachable_glyphs]:** Fix handling of format 14 'cmap' table. (issue #3915)
  - **[com.google.fonts/check/contour_count]:** U+0E3F THAI CURRENCY SYMBOL BAHT can also have 5 contours (issue #3914)

#### On the `OpenType` profile
  - **[com.google.fonts/check/monospace]:** Update PANOSE requirements for monospaced fonts based on comments by Thomas Phinney (@tphinney) (issue #2857)
  - **[com.google.fonts/check/post_table_version]:** Updated policy on acceptable post table version. Downgraded the check from FAIL to WARN-level (according to discussions at issue #3635)
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** The check was completely rewritten; it now correctly compares full name and family name strings that are from the same platform, same encoding, and same language. (PR #3747)
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** Added rationale text contibuted by Adam Twardoch (issue #3754)
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** Relaxed the implementation to compare name values, not strictly IDs. (PR #3821)
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** The check did not account for nameID 17. (issue #3895)
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** The check was modified to distinguish between a font having no bold
  instance (code: `no-bold-instance`) versus having a bold instance whose wght coord != 700 (existing code `wght-not-700`). (issue #3898)

#### On the `Google Fonts` profile
  - **[com.google.fonts/check/contour_count]:** Four fifths glyph can also be drawn with only 3 contours if the four is open-ended. (issue #3511)
  - **[com.google.fonts/check/glyph_coverage]:** Use the new glyphsets python module. (issue #3533)
  - **[com.google.fonts/check/name/rfn]:** If the OFL text is included in a name table entry, the check should not FAIL, as the full license text contains the term 'Reserved Font Name', which in this case is OK. (issue #3542)
  - **[com.google.fonts/check/layout_valid_feature_tags]:** Allow 'HARF' and 'BUZZ' tags. (issue #3368)
  - **[com.google.fonts/check/glyph_coverage]:** Fix ERROR. (issue #3551)
  - **[com.google.fonts/check/repo/sample_image]:** Declare conditions so that font repos lacking a README.md file will skip this check. (issue #3559)
  - **[com.google.fonts/check/metadata/unsupported_subsets]:** Declare conditions so that font repos lacking a METADATA.pb file will skip this check. (issue #3564)
  - **[com.google.fonts/check/varfont/grade_reflow]:** fix AttributeError: `'NoneType'` object has no attribute `'StartSize'` (issue #3566)
  - **[com.google.fonts/check/varfont/grade_reflow]:** Cleanup log message output: use a set (instead of a list) in order to eliminate multiple reporting of the same glyphs (issue #3561)
  - **[com.google.fonts/check/metadata/os2_weightclass]:** Improve wording of log messages to make the reasoning of expected values clearer to the users (issue #2935)
  - **[com.google.fonts/check/name/familyname]:** Consider camel-case exceptions (issue #3584)
  - **[com.google.fonts/check/name/fullfontname]:** Consider camel-case exceptions (issue #3584)
  - **[com.google.fonts/check/glyph_coverage]:** Use the correct nam-file for checking coverage of the GF-latin-core glyphset (issue #3583)
  - **[com.google.fonts/check/font_copyright]:** Allow Google LLC copyright. These are use in Noto fonts. (PR #3607)
  - **[com.google.fonts/check/license/OFL_copyright]:** Re-use expected copyright format. (PR #3607)
  - **[com.google.fonts/check/metadata/reserved_font_name]:** Added support for an RFN Exception allow-list, but it is kept empty for now while we review potential exceptions (issues #3589 and #3612)
  - **[com.google.fonts/check/name/rfn]:** RFN Exception allow-list (same as above)
  - **[com.google.fonts/check/metadata/can_render_samples]:** Check that the fonts can render the sample texts for all languages specified on METADATA.pb, by using the new `gflanguages` module (issue #3605)
  - **[com.google.fonts/check/unitsperem]:** Auto-SKIP this check inherited from the OpenType profile because Google Fonts has a stricter policy which is enforced by **com.google.fonts/check/unitsperem_strict** (issue #3622)
  - **[com.google.fonts/check/license/OFL_copyright]:** Improve wording of log message to clarify its meaning. It was too easy to think that the displayed copyright string (read from the font binary and reported for reference) was an example of the actually expected string format. (issue #3674)
  - **[com.google.fonts/check/cjk_vertical_metrics_regressions]:** Round calculation of expected sTypoAscender and sTypoDescender values (issue #3645)
  - **[com.google.fonts/check/name/familyname]:** Don't validate localized name table entries compared to the expected English names derived from the font filename (issue #3089)
  - **[com.google.fonts/check/glyph_coverage]:** Check all fonts against all glyphsets and report any glyphsets which are partially filled (PR #3775)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Override this check to make it mandatory for Google Fonts, emitting a FAIL if freetype is not installed, instead of silently skipping. (issue #3871)
  - **[com.google.fonts/check/description/valid_html]:** Fix parser to accept ampersand character in DESCRIPTION files. (issue #3840)
  - **[com.google.fonts/check/glyph_coverage]:** Ensure check doesn't error when font contains all required encoded glyphs (PR #3833)
  - **[com.google.fonts/check/mandatory_avar_table]:** Downgrade it to a mere WARN, even though it is still a high-priority one. (issue #3100)
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Do not raise an error if font is missing AxisValues (issue #3848 PR #3849)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Do not raise an error if font is missing AxisValues (issue #3848 PR #3849)
  - **[com.google.fonts/check/vertical_metrics]:** Check for positive and negative ascender and descender values. (PR #3921)
  - **[com.google.fonts/check/vendor_id]:** PYRS is a default Vendor ID entry from FontLab generated binaries. (issue #3943)
  - **[com.google.fonts/check/colorfont_tables]:** Check for four-digit 'SVG ' table instead of 'SVG' (PR #3903)

#### On the `FontVal` profile
  - **[com.google.fonts/check/fontvalidator]:** Disable a slew of frequent false positive warnings (PR #3951)
  and make the check configurable via the configuration. (PR #3964)

#### On the `ISO-15008` profile
  - Fixed ERRORs by updating usage of internal fonttools `_TTGlyphGlyf` API that changed at https://github.com/fonttools/fonttools/commit/b818e1494ff2bfb7f0cd71d827ba97578c919303

#### On the `Adobe Fonts` profile
  - The profile was updated to exercise only an explicit set of checks, making it impossible for checks from imported profiles to sneak-in unnoticed. As a result, the set of checks that are run now is somewhat different from previous Font Bakery releases. For example, UFO- and designspace-related checks are no longer attempted; and outline and shaping checks are excluded as well. In addition to pairing down the set of checks inherited from the Universal profile, an effort was made to enable specific checks from other profiles such as Fontwerk, GoogleFonts, and Noto Fonts. (PR #3743)
  - **[com.adobe.fonts/check/find_empty_letters]:** Was downgraded to WARN only for a specific set of Korean hangul syllable characters, which are known to be included in fonts as a workaround to undesired behavior from InDesign's Korean IME (Input Method Editor). More details available at issue #2894. (PR #3744)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** This check from the Universal profile is overridden to yield ERROR if FreeType is not installed, ensuring that the check isn't skipped. (PR #3745)
  - **[com.google.fonts/check/family/win_ascent_and_descent]:** This check from the Universal profile is now overridden to yield just WARN instead of FAIL. (PR #3745)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** This check from the Universal profile is now overridden to yield just WARN instead of FAIL. (PR #3745)
  - **[com.google.fonts/check/fontbakery_version]:** This check from the Universal profile is overridden to be skipped instead of failing, when the user's internet connection isn't functional. (PR #3756)
  - **[com.google.fonts/check/cmap/unexpected_subtables]:** This check from the Noto Fonts profile was disabled; CJK vendors still include Macintosh format 2 subtables in their fonts (PR #3870)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** Mismatches of `lineGap` values were downgraded from FAIL to WARN (PR #3870)
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** This check from the OpenType profile was overridden and downgraded from FAIL to WARN. Many OpenType-CFF fonts in circulation are built with the Microsoft platform Full font name string identical to the PostScript FontName in the CFF Name INDEX. This practice was documented in the OpenType specification up until version 1.5 (PR #3870)
  - **[com.google.fonts/check/name/trailing_spaces]:** This check from the Universal profile was overridden and downgraded from FAIL to WARN (PR #3870)
  - **[com.google.fonts/check/unwanted_tables]:** This check from the Universal profile was replaced by the new `com.adobe.fonts/check/unsupported_tables` check (PR #3870)
  - **[com.adobe.fonts/check/nameid_1_win_english]:** Replaced ERROR status by FAIL status (PR #3870)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Replaced ERROR status by FAIL status (PR #3870)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Added check that format 4 AxisValue tables have AxisCount (number of AxisValueRecords) > 1 (issue #3957)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Improved overall check to FAIL when an unknown AxisValue.Format is encountered.
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** Overridden to downgrade `no-bold-instance` from FAIL to WARN. (issue #3898)

#### On the `Fontwerk` profile
  - Added a few more checks to the `CHECKS_NOT_TO_INCLUDE` list. These are checks (most of them from the Google Fonts profile) that Fontwerk is not interested in including in its vendor-specific profile.

### Other Bug Fixes
  - Fixed broken parsing at `@condition def production_metadata()` (issue #3661)
  - Users reading markdown reports are now directed to the "stable" version of our ReadTheDocs documentation instead of the "latest" (git dev) one. (issue #3677)
  - Improve rendering of bullet lists (issue #3691 & PR #3741)
  - fix crash on terminal reporter on specific Windows paths with backslashes (issue #3750)
  - **[setup.py]:** Our protobuf files have been compiled with v3 versions of protobuf which cannot be read by v4. (PR #3946)
  - Added a `--timeout` parameter and set timeouts on all network requests. (PR #3892)
  - Fix summary header in the Github Markdown reporter. (PR #3923)
  - Use `getBestFullName` for the report instead of reading name table identifier 4 directly. (PR #3924)
  - Overriden checks now also properly inherit conditions. (issue #3952)
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Fixed bug that resulted in an ERROR when attempting to access `.AxisIndex` of a format 4 AxisValue table (issue #3904)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Fixed bug that resulted in an ERROR when attempting to access `.AxisIndex` of a format 4 AxisValue table (issue #3904)
  - **[com.google.fonts/check/unreachable_glyphs]:** Fix crash by adding support for color-font legacy COLR v0 format. (issue #3850)
  - Fixed bug on `fontbakery_version` check so that it now understands that v0.x.9 is older than v0.x.10 (issue #3813)
  - Fixed `fontbakery.profiles.shared_conditions.*_*_coord` functions so they work on Italic fonts (issue #3828, PR #3834)
  - **[com.fontwerk/check/weight_class_fvar]:** Fixed ERROR result as the check did not yield any status when a variable font had no `wght` axis. (PR #3866)
  - **[com.google.fonts/check/varfont_duplicate_instance_names]:** Fixed crash caused by trying to decode a non-existant `name`-table record. (PR #3866)
  - **[com.google.fonts/check/linegaps]:** Fixed crash by checking for the existence of tables required by the check before accessing them. (issue #3656, PR #3866)
  - **[com.google.fonts/check/maxadvancewidth]:** Fixed crash by checking for the existence of tables required by the check before accessing them. (issue #3656, PR #3866)
  - **[com.google.fonts/check/unexpected_subtables]:** Fixed crash by checking for the existence of `OS/2` table required by `is_cjk_font` condition before accessing it. (PR #3866)
  - **[com.adobe.fonts/check/varfont/valid_axis_nameid]:** Fixed ERROR result as the check did not yield any status when a variable font had no `name` table. (PR #3866)
  - **[com.adobe.fonts/check/varfont/valid_subfamily_nameid]:** Fixed ERROR result as the check did not yield any status when a variable font had no `name` table. (PR #3866)
  - **[com.adobe.fonts/check/varfont/valid_postscript_nameid]:** Fixed ERROR result as the check did not yield any status when a variable font had no `name` table. (PR #3866)
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** Fixed ERROR result as the check did not yield any status when a variable font had no `name` table. (PR #3866)
  - **[com.adobe.fonts/check/varfont/distinct_instance_records]:** Fixed ERROR result as the check did not yield any status when a variable font had no `name` table. (PR #3866)

### Other noteworthy code-changes
  - We have updated our Code of Conduct. Please read [the updated text](CODE_OF_CONDUCT.md) which corresponds to the `Contributor Covenant version 2.1` available at https://www.contributor-covenant.org/version/2/1/code_of_conduct/
  - We normalized the ordering of log messages of some more checks. To avoid imprevisibility of python set iteration, we sort them before printing. This helps to reduce diffs for people that compare subsequent runs of fontbakery on automated QA setups (issue #3654)
  - New command line flag: `-F, --full-list` to print full lists (`pretty_print_list` method) even when the total number of items exceeds a certain threashold. (issues #3173 and #3512)
  - Listed a few of the more recently added profiles that were still missing on our online docs (issue #3518)
  - Do not accept more than a single dash on font filenames. This ensures FontBakery won't miscompute expected style values used on checks such as `com.google.fonts/check/usweightclass`. (issue #3524)
  - We now ensure that version 0.4.0 of our `collidoscope` dependency is not used because it had a bug that failed to detect an `ïï` collision on Nunito Black. (issues #3556)
  - The `--succinct` flag now generates succinct HTML and MD reports. (PR #3608)
  - On the GitHub Markdown reporter, checks which produce all the same output for a range of fonts are now automatically clustered into a family check result. (PR #3610)
  - More cosmetic improvements to the GitHub Markdown reporter. (PR #3647)
  - Use the new `axisregistry` python module (Google Fonts Variable Font Axis Registry data-set) to eliminate code & data duplication across tools and repos (issue #3633)
  - Improve implementation of `is_italic` condition and provide an `is_bold` counterpart (issue #3693)
  - Nicer cancellation for terminal runner. (issue #3672)
  - The CheckTester class now takes into account the check's own `conditions`. (PR #3766)
  - Windows Terminal displays colors fine. We can now remove the win32 workaround. (issue #3779)
  - On the `Google Fonts` profile, the lists of exceptions for **Reserved Font Names (RFN)** and **CamelCased family names**, are now placed on separate txt files (`Lib/fontbakery/data/googlefonts/*_exceptions.txt`) to facilitate their future editing. (issue #3707)
  - The FontVal checks report will be written to a temporary directory now, making it safe to run the checks in parallel on multiple fonts.
  - Updated the Google Fonts metadata proto format.
  - Always read regression shaping JSON files as UTF-8 text. Windows may otherwise use a different default encoding.

