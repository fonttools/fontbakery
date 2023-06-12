Below are the most important changes from each release.
A more detailed list of changes is available in the corresponding milestones for each release in the Github issue tracker (https://github.com/googlefonts/fontbakery/milestones?state=closed).


## Upcoming release: 0.9.0 (2023-Jun-??)
### Note-worthy code changes
  - This is the first version in which we're using the Black auto-formatter on the entire code-base. (Discussions #3397)
  - Also, now software dependencies can be installed based on the user needs. The default FontBakery installation from PyPI includes only the dependencies for running font-binary checks from the Universal profile. To run source-level checks, one needs to enable the `ufo-sources` extra. (issues #3715 and #3874)

### Changes to existing checks
#### On the Universal profile
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Added test-code that segfaults with freetype-py version 2.4.0, so that we make sure the problem won't go unnoticed, and will enable us to know when it gets fixed (issue #4143)


## 0.8.13 (2023-Jun-02)
  - Fix a critical install bug. I had used wrong syntax on setup.py which made v0.8.12 impossible to install when enabling the freetype extra. Sorry! (issue #4157)


## 0.8.12 (2023-May-31)
### New Checks
#### Added to the Universal Profile
  - **[com.google.fonts/check/STAT_in_statics]:** Static fonts with more than a single entry per design axis cause trouble on Windows (issue #4149)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/metadata/unreachable_subsetting]:** Implemented checks to ensure that all encoded glyphs in the font are covered by a subset declared in the METADATA.pb (issue #4097)

#### Added to the Open Type Profile
  - **[com.google.fonts/check/name/italic_names]:** Implemented checks for name IDs 1, 2, 16, 17 for Italic fonts (issues #3666 and #3667)

#### Added to the Adobe Fonts Profile
  - **[com.adobe.fonts/check/family/consistent_family_name]:** Verifies that family names in the name table are consistent across all fonts in a family. Checks Typographic Family name (nameID 16) if present, otherwise uses Font Family name (nameID 1). (issue #4112)

### Migrations of checks
#### Moved to the Universal profile
  - **[com.google.fonts/check/linegaps]:** from the OpenType profile (issue #4133)

### Changes to existing checks
#### On the Google Fonts profile
  - **[com.google.fonts/check/usweightclass]:** use the axisregistry's name builders instead of the parse module (issue #4113)
  - **[com.google.fonts/check/metadata/broken_links]:** We should not keep email addresses on METADATA.pb files (issue #4110)
  - **[com.google.fonts/check/description/broken_links]:** We should not keep email addresses on DESCRIPTION files (issue #4110)
  - **[com.google.fonts/check/metadata/nameid/font_name]:** Use name id 16, when present, to compute the expected font family name (issue #4086)
  - **[com.google.fonts/check/check/colorfont_tables]:** Update checking criteria according to gf-guide (issue #4131)

#### On the Universal Profile
  - **[com.google.fonts/check/soft_hyphen]:** Improve wording of the rationale. (issue #4095)
  - **[com.google.fonts/check/linegaps]:** Added rationale (issue #4133)

### BugFixes
  - Fix crash on markdown reporter by explicitly specifing UTF-8 encoding (issue #4089)

### Code tests
  - Added test for com.google.fonts/soft_doted. (issue #4069)


## 0.8.11 (2023-Mar-03)
### Noteworthy code-changes
  - The terminal reporter now prints out URLs for "more info" (typically github issues) where the user can learn more about how the check was originally proposed/discussed. (PR #3994)
  - Added a `--timeout` parameter and set timeouts on all network requests. (PR #3892)

### BugFixes
  - **[setup.py]:** Our protobuf files have been compiled with v3 versions of protobuf which cannot be read by v4. (PR #3946)
  - Fix summary header in the Github Markdown reporter. (PR #3923)
  - Use `getBestFullName` for the report instead of reading name table identifier 4 directly. (PR #3924)
  - fix crash on iso15008 checks by updating usage of internal fonttools `_TTGlyphGlyf` API that changed at https://github.com/fonttools/fonttools/commit/b818e1494ff2bfb7f0cd71d827ba97578c919303
  - Overriden checks now also properly inherit conditions. (issue #3952)
  - Updated style condition to correctly handle VFs (PR #4007)
  - Do not include an "And" on the last item of bullet lists. (issue #4006)
  - Correctly process expected messages when they are plain strings in assert_results_contain() (PR #4015)

### Migrations of checks
#### Moved to the OpenType profile  
  - **[com.google.fonts/check/italic_angle]:** from the GoogleFonts profile (issue #3663)
  - **[com.google.fonts/check/mac_style]:** from the GoogleFonts profile (issue #3664)
  - **[com.google.fonts/check/fsselection]:** from the GoogleFonts profile (issue #3665)

### New Checks
#### Added to the Universal Profile
  - **[com.google.fonts/check/soft_dotted]:** Ensure soft_dotted characters lose their dot when combined with marks that replace the dot. (issue #4059)
  - **[com.google.fonts/check/interpolation_issues]:** Check for shape order or curve start point interpolation issues within a variable font. (issue #3930)
  - **[com.google.fonts/check/math_signs_width]:** Check that math signs have the same width (issue #3832)
  - **[com.google.fonts/check/soft_hyphen]:** It was originally part of the validation on **check/contour_count**, but it was leading to confusion, so it was split out into a separate check. (issue #4046)

#### Added to the Open Type Profile
  - **[com.thetypefounders/check/vendor_id]:** When a font project's Vendor ID is specified explicitely on FontBakery's configuration file, all binaries must have a matching vendor identifier value in the OS/2 table. (PR #3941)
  - **[com.google.fonts/check/caret_slope]:** Check for hhea.caretSlopeRise and hhea.caretSlopeRun to match post.italicAngle (issues #3670 & #4039)
  - **[com.google.fonts/check/italic_axis_in_stat]:** Check that ital axis exists in STAT table (issue #2934)
  - **[com.google.fonts/check/italic_axis_in_stat_is_boolean]:** Check that STAT ital axis values are boolean (0 or 1) and flags are elided for Upright and not elided for Roman, and Roman is linked to Italic (issue #3668)
  - **[com.google.fonts/check/italic_axis_last]:** Check that STAT ital axis is last in order (issue #3669)
  - **[com.adobe.fonts/check/varfont/foundry_defined_tag_name]:** Check that foundry-defined tags begin with an uppercase letter (0x41 to 0x5A), and use only uppercase letters or digits (issue #4043)

#### Proposed for future inclusion on the Open Type Profile
  - **[com.google.fonts/check/name/italic_names]:** Implemented checks for name IDs 1, 2, 16, 17 for Italic fonts (Proposed at issues #3666 and #3667, but has problems described at issue #4061)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/colorfont_tables]:** Check if fonts contain the correct color tables. (issue #3886)
  - **[com.google.fonts/check/description/noto_has_article]:** Noto fonts must have an ARTICLE.en_us.html file. (issue #3841)
  - **[com.google.fonts/check/slant_direction]:** Check slant direction of outline to match values of slnt axis extrema. (PR #3910)
  - **[com.google.fonts/check/color_cpal_brightness]:** Warn if COLRv0 layers are colored too dark or too bright instead of foreground color. (PR #3908)
  - **[com.google.fonts/check/empty_glyph_on_gid1_for_colrv0]:** Ensure that GID 1 is empty to work around Windows 10 rendering bug ([gftools issue #609](https://github.com/googlefonts/gftools/issues/609))
  - **[com.google.fonts/check/metadata/valid_nameid25]:** Check Name ID 25 for VF Italics (issue #3024)
  - **[com.google.fonts/check/metadata/consistent_repo_urls]:** Check URL on copyright string is the same as in repository_url field. (issue #4056)
  - **[com.google.fonts/check/name/family_name_compliance]:** Expanded and revised version of `metadata/fontname_not_camel_cased` check (issue #4049)

### Renamed check IDs
#### On Google Fonts profile
  - **[com.google.fonts/check/metadata/fontname_not_camel_cased]** => com.google.fonts/check/name/family_name_compliance

### Deprecated checks
#### Removed from the Open Type and Adobe Profiles
  - **[com.google.fonts/check/all_glyphs_have_codepoints]:** This check cannot ever fail with fontTools and is therefore redundant. (issue #1793)

#### Removed from the Google Fonts Profile
  - **[com.google.fonts/check/listed_on_gfonts]:** Did not pass for any new families and was not deemed to be a useful check by the onboarding team. The WARN was actually considered annoying. (issue #3220)

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/unreachable_glyphs]:** Fix handling of format 14 'cmap' table. (issue #3915)
  - **[com.google.fonts/check/contour_count]:** U+0E3F THAI CURRENCY SYMBOL BAHT can also have 5 contours (issue #3914)

#### On the OpenType Profile
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** The check did not account for nameID 17. (issue #3895)
  - **[com.google.fonts/check/varfont/wdth_valid_range]:** Modified (relaxed) to match the OpenType spec's valid range ("strictly greater than zero")
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Fixed bug that resulted in an ERROR when attempting to access `.AxisIndex` of a format 4 AxisValue table (issue #3904)
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** The check was modified to distinguish between a font having no bold
  instance (code: `no-bold-instance`) versus having a bold instance whose wght coord != 700 (existing code `wght-not-700`). (issue #3898)
  - **[com.google.fonts/check/monospace]:** The check was modified to WARN when `hhea.numberOfHMetrics` is not `3` for monospaced fonts, as per [Microsoft's recommendation](https://learn.microsoft.com/en-us/typography/opentype/spec/recom#hhea-table). (PR #4025 & PR #4074)
  - **[com.google.fonts/check/varfont/regular_wght_coord]:** The check was modified to distinguish between a font having no regular
  instance (code: `no-regular-instance`) versus having a regular instance whose wght coord != 400 (existing code `wght-not-400`). (issue #4003)
  - **[com.google.fonts/check/varfont/regular_wdth_coord]:** The check was modified to distinguish between a font having no regular
  instance (code: `no-regular-instance`) versus having a regular instance whose wdth coord != 100 (existing code `wdth-not-100`). (issue #4003)
  - **[com.google.fonts/check/varfont/regular_slnt_coord]:** The check was modified to distinguish between a font having no regular
  instance (code: `no-regular-instance`) versus having a regular instance whose slnt coord != 100 (existing code `slnt-not-0`). (issue #4003)
  - **[com.google.fonts/check/varfont/regular_ital_coord]:** The check was modified to distinguish between a font having no regular
  instance (code: `no-regular-instance`) versus having a regular instance whose ital coord != 100 (existing code `ital-not-0`). (issue #4003)
  - **[com.google.fonts/check/varfont/regular_opsz_coord]:** The check was modified to distinguish between a font having no regular
  instance (code: `no-regular-instance`) versus having a regular instance whose opsz is out of range (existing code `opsz-out-of-range`). (issue #4003)
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** The check was modified to distinguish between a font having no bold
  instance (code: `no-bold-instance`) versus having a bold instance whose wght coord != 700 (existing code `wght-not-700`). (issue #3898)
  - **[com.google.fonts/check/italic_angle]:**  Improve italic_angle check to base reporting on Italic angle as measure from outline. (PR #4031)
  - **[com.google.fonts/check/italic_axis_in_stat_is_boolean]:** Skip check if font doesn't have an ital axis. (PR #4033)
  - **[com.google.fonts/check/kern_table]**: Scour all cmap tables for encoded glyphs.

#### On the AdobeFonts Profile
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Added check that format 4 AxisValue tables have AxisCount (number of AxisValueRecords) > 1 (issue #3957)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Improved overall check to FAIL when an unknown AxisValue.Format is encountered.
  - **[com.adobe.fonts/check/STAT_strings]:** Added a more lenient version of com.google.fonts/check/STAT_strings (allows "Italic" on 'slnt' or 'ital' axes).
  - **[com.google.fonts/check/STAT_strings]:** removed from the list of explicit checks.
  - **[com.google.fonts/check/transformed_components]**: removed from the list of explicit checks.
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]**: relax `invalid-default-instance-subfamily-name` and `invalid-default-instance-postscript-name` from FAIL to WARN.
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]**: relax `missing-axis-value-table` and `format-4-axis-count` from FAIL to WARN.
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]**: relax `missing-fvar-instance-axis-value` from FAIL to WARN.
  - **[com.fontwerk/check/weight_class_fvar]**: relax `bad-weight-class` from FAIL to WARN.
  - **[com.google.fonts/check/varfont/bold_wght_coord]**: relax `wght-not-700` from FAIL to WARN.
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** downgrade `no-bold-instance` from FAIL to WARN. (issue #3898)
  - **[com.adobe.fonts/check/varfont/foundry_defined_tag_name]:** Added check that foundry-defined tags begin with an uppercase letter (0x41 to 0x5A), and use only uppercase letters or digits (issue #4043)

#### Overridden in the Adobe Fonts Profile
  - **[com.google.fonts/check/varfont/regular_wght_coord]:** downgrade `no-regular-instance` from FAIL to WARN. (issue #4003)
  - **[com.google.fonts/check/varfont/regular_wdth_coord]:** downgrade `no-regular-instance` from FAIL to WARN. (issue #4003)
  - **[com.google.fonts/check/varfont/regular_slnt_coord]:** downgrade `no-regular-instance` from FAIL to WARN. (issue #4003)
  - **[com.google.fonts/check/varfont/regular_ital_coord]:** downgrade `no-regular-instance` from FAIL to WARN. (issue #4003)
  - **[com.google.fonts/check/varfont/regular_opsz_coord]:** downgrade `no-regular-instance` from FAIL to WARN. (issue #4003)
  - **[com.google.fonts/check/varfont/bold_wght_coord]:** downgrade `no-bold-instance` from FAIL to WARN. (issue #3898)

#### On the GoogleFonts Profile
  - **[com.google.fonts/check/metadata/can_render_samples]:** Fix false-FAIL by removing '\n' and U+200B (zero width space) characteres from sample strings (issue #3990)
  - **[com.google.fonts/check/metadata/broken_links]:** add special handling for github url (issue #2550)
  - **[com.google.fonts/check/vendor_id]:** PYRS is a default Vendor ID entry from FontLab generated binaries. (issue #3943)
  - **[com.google.fonts/check/colorfont_tables]:** Check for four-digit 'SVG ' table instead of 'SVG' (PR #3903)
  - **[com.google.fonts/check/vertical_metrics]:** Check for positive and negative ascender and descender values (PR #3921)
  - **[com.google.fonts/check/missing_small_caps_glyphs]:** fix ERROR (issue #4030)

#### On the FontVal Profile
  - **[com.google.fonts/check/fontvalidator]:** Disable a slew of frequent false positive warnings and make the check configurable via the configuration.

#### On the FontWerk Profile
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Fixed bug that resulted in an ERROR when attempting to access `.AxisIndex` of a format 4 AxisValue table (issue #3904)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Fixed bug that resulted in an ERROR when attempting to access `.AxisIndex` of a format 4 AxisValue table (issue #3904)


## 0.8.10 (2022-Aug-25)
### Release Notes
  - We have updated our Code of Conduct. Please read [the updated text](CODE_OF_CONDUCT.md) which corresponds to the `Contributor Covenant version 2.1` available at https://www.contributor-covenant.org/version/2/1/code_of_conduct/
  - We normalized the ordering of log messages of some more checks. To avoid imprevisibility of python set iteration, we sort them before printing. This helps to reduce diffs for people that compare subsequent runs of fontbakery on automated QA setups (issue #3654)

### New Checks
#### Added to the Adobe Fonts Profile
  - **[com.adobe.fonts/check/unsupported_tables]:** Verifies if fonts contain any tables not supported by Adobe Fonts' font-processing pipeline (PR #3870)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/font_names]:** Ensure font names match our specification (PR #3800)
  - **[com.google.fonts/check/fvar_instances]:** Ensure fvar instances match our specification (PR #3800)
  - **[com.google.fonts/check/STAT]:** Ensure fonts have compulsory STAT table axis values (PR #3800)
  - **[com.google.fonts/check/description/valid_html]:** Fix parser to accept ampersand character in DESCRIPTION files. (issue #3840)

### Deprecated Checks
#### Removed from the Google Fonts Profile
  - **[com.google.fonts/check/description_max_length]**: Recent requirement from GF marketing team is to remove character limit on description. GF specimen page has been updated to allow bigger description text from designers. (issue #3829)

### Migrations
#### To the `Universal` profile
  - **[com.google.fonts/check/whitespace_widths]:** moved from `OpenType` profile. Also added rationale text. (issue #3843)

### BugFixes
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

### Changes to existing checks
#### On the Adobe Fonts Profile
  - **[com.google.fonts/check/cmap/unexpected_subtables]:** This check from the Noto Fonts profile was disabled; CJK vendors still include Macintosh format 2 subtables in their fonts (PR #3870)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** Mismatches of `lineGap` values were downgraded from FAIL to WARN (PR #3870)
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** This check from the OpenType profile was overridden and downgraded from FAIL to WARN. Many OpenType-CFF fonts in circulation are built with the Microsoft platform Full font name string identical to the PostScript FontName in the CFF Name INDEX. This practice was documented in the OpenType specification up until version 1.5 (PR #3870)
  - **[com.google.fonts/check/name/trailing_spaces]:** This check from the Universal profile was overridden and downgraded from FAIL to WARN (PR #3870)
  - **[com.google.fonts/check/unwanted_tables]:** This check from the Universal profile was replaced by the new `com.adobe.fonts/check/unsupported_tables` check (PR #3870)
  - **[com.adobe.fonts/check/nameid_1_win_english]:** Replaced ERROR status by FAIL status (PR #3870)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Replaced ERROR status by FAIL status (PR #3870)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/glyph_coverage]:** Ensure check doesn't error when font contains all required encoded glyphs (PR #3833)
  - **[com.google.fonts/check/mandatory_avar_table]:** Downgrade it to a mere WARN, even though it is still a high-priority one. (issue #3100)
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Do not raise an error if font is missing AxisValues (issue #3848 PR #3849)
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Do not raise an error if font is missing AxisValues (issue #3848 PR #3849)
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
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Override this check to make it mandatory for Google Fonts, emitting a FAIL if freetype is not installed, instead of silently skipping. (issue #3871)

#### On the OpenType Profile
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** Relaxed the implementation to compare name values, not strictly IDs. (PR #3821)

#### On the Universal Profile
  - **[com.google.fonts/check/unreachable_glyphs]:** Do not report glyphs referenced in color fonts graphic compositions on the COLR table as missing. (issue #3837)


## 0.8.9 (2022-Jun-16)
### Noteworthy code-changes
  - Improve implementation of `is_italic` condition and provide an `is_bold` counterpart (issue #3693)
  - Nicer cancellation for terminal runner. (issue #3672)
  - The CheckTester class now takes into account the check's own `conditions`. (PR #3766)
  - Windows Terminal displays colors fine. We can now remove the win32 workaround. (issue #3779)
  - On the `Google Fonts` profile, the lists of exceptions for **Reserved Font Names (RFN)** and **CamelCased family names**, are now placed on separate txt files (`Lib/fontbakery/data/googlefonts/*_exceptions.txt`) to facilitate their future editing. (issue #3707)
  - The FontVal checks report will be written to a temporary directory now, making it safe to run the checks in parallel on multiple fonts.
  - Updated the Google Fonts metadata proto format.
  - Always read regression shaping JSON files as UTF-8 text. Windows may otherwise use a different default encoding.

### BugFixes
  - Users reading markdown reports are now directed to the "stable" version of our ReadTheDocs documentation instead of the "latest" (git dev) one. (issue #3677)
  - Improve rendering of bullet lists (issue #3691 & PR #3741)
  - fix crash on terminal reporter on specific Windows paths with backslashes (issue #3750)

### Changes to existing checks
#### On the Universal Profile
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

#### On the OpenType Profile
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** The check was completely rewritten; it now correctly compares full name and family name strings that are from the same platform, same encoding, and same language. (PR #3747)
  - **[com.google.fonts/check/name/match_familyname_fullfont]:** Added rationale text contibuted by Adam Twardoch (issue #3754)

#### On the Adobe Fonts Profile
  - The profile was updated to exercise only an explicit set of checks, making it impossible for checks from imported profiles to sneak-in unnoticed. As a result, the set of checks that are run now is somewhat different from previous Font Bakery releases. For example, UFO- and designspace-related checks are no longer attempted; and outline and shaping checks are excluded as well. In addition to pairing down the set of checks inherited from the Universal profile, an effort was made to enable specific checks from other profiles such as Fontwerk, GoogleFonts, and Noto Fonts. (PR #3743)
  - **[com.adobe.fonts/check/find_empty_letters]:** Was downgraded to WARN only for a specific set of Korean hangul syllable characters, which are known to be included in fonts as a workaround to undesired behavior from InDesign's Korean IME (Input Method Editor). More details available at issue #2894. (PR #3744)
  - **[com.adobe.fonts/check/freetype_rasterizer]:** This check from the Universal profile is overridden to yield ERROR if FreeType is not installed, ensuring that the check isn't skipped. (PR #3745)
  - **[com.google.fonts/check/family/win_ascent_and_descent]:** This check from the Universal profile is now overridden to yield just WARN instead of FAIL. (PR #3745)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** This check from the Universal profile is now overridden to yield just WARN instead of FAIL. (PR #3745)
  - **[com.google.fonts/check/fontbakery_version]:** This check from the Universal profile is overridden to be skipped instead of failing, when the user's internet connection isn't functional. (PR #3756)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/unitsperem]:** Auto-SKIP this check inherited from the OpenType profile because Google Fonts has a stricter policy which is enforced by **com.google.fonts/check/unitsperem_strict** (issue #3622)
  - **[com.google.fonts/check/license/OFL_copyright]:** Improve wording of log message to clarify its meaning. It was too easy to think that the displayed copyright string (read from the font binary and reported for reference) was an example of the actually expected string format. (issue #3674)
  - **[com.google.fonts/check/cjk_vertical_metrics_regressions]:** Round calculation of expected sTypoAscender and sTypoDescender values (issue #3645)
  - **[com.google.fonts/check/name/familyname]:** Don't validate localized name table entries compared to the expected English names derived from the font filename (issue #3089)
  - **[com.google.fonts/check/glyph_coverage]:** Check all fonts against all glyphsets and report any glyphsets which are partially filled (PR #3775)

#### On the Fontwerk Profile
  - Added a few more checks to the `CHECKS_NOT_TO_INCLUDE` list. These are checks (most of them from the Google Fonts profile) that Fontwerk is not interested in including in its vendor-specific profile.

### New Checks
#### Added to the Adobe Fonts Profile
  - **[com.adobe.fonts/check/nameid_1_win_english]:** Validates that the font has a good nameID 1, Windows/Unicode/US-English `name` table record. (issue #3714)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/vertical_metrics]:** Similar to `cjk_vertical_metrics`, this check enforces Google Fonts’ general vertical metrics specifications.

#### Added to the Noto Fonts Profile
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

#### Added to the OpenType Profile
  - **[com.adobe.fonts/check/stat_has_axis_value_tables]:** Validates that STAT table has Axis Value tables. (issue #3090)
  - **[com.adobe.fonts/check/varfont/valid_axis_nameid]:** Validates that the value of axisNameID used by each VariationAxisRecord is greater than 255 and less than 32768. (issue #3702)
  - **[com.adobe.fonts/check/varfont/valid_subfamily_nameid]:** Validates that the value of subfamilyNameID used by each InstanceRecord is 2, 17, or greater than 255 and less than 32768. (issue #3703)
  - **[com.adobe.fonts/check/varfont/valid_postscript_nameid]:** Validates that the value of postScriptNameID used by each InstanceRecord is 6, 0xFFFF, or greater than 255 and less than 32768. (issue #3704)
  - **[com.adobe.fonts/check/varfont/valid_default_instance_nameids]:** Validates that when an instance record is included for the default instance, its subfamilyNameID value is set to either 2 or 17, and its postScriptNameID value is set to 6. (issue #3708)
  - **[com.adobe.fonts/check/varfont/same_size_instance_records]:** Validates that all of the instance records in a given font have the same size, with all either including or omitting the postScriptNameID field. (issue #3705)
  - **[com.adobe.fonts/check/varfont/distinct_instance_records]:** Validates that all of the instance records in a given font have distinct data. (issue #3706)

#### Added to the Universal Profile
  - **[com.adobe.fonts/check/freetype_rasterizer]:** Checks that the font can be rasterized by FreeType. (issue #3642)
  - **[com.adobe.fonts/check/sfnt_version]:** Ensures the font has the proper sfntVersion value. (issue #3388)


## 0.8.8 (2022-Mar-23)
### Noteworthy code-changes
  - On the GitHub Markdown reporter, checks which produce all the same output for a range of fonts are now automatically clustered into a family check result. (PR #3610)
  - More cosmetic improvements to the GitHub Markdown reporter. (PR #3647)
  - Use the new `axisregistry` python module (Google Fonts Variable Font Axis Registry data-set) to eliminate code & data duplication across tools and repos (issue #3633)

### BugFixes
  - Fixed broken parsing at `@condition def production_metadata()` (issue #3661)

### New Checks
#### Added to the FontWerk Profile
  - **[com.fontwerk/check/inconsistencies_between_fvar_stat]:** Check for inconsistencies in names and values between the fvar instances and STAT table which may cause issues in apps like Adobe InDesign. (PR #3636)
  - **[com.fontwerk/check/style_linking]:** Look for possible style linking issues. (PR #3649)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/metadata/category_hints]:** Check if category on METADATA.pb matches what can be inferred from keywords in the family name. (issue #3624)

#### Added to the Universal Profile
  - **[com.google.fonts/check/gsub5_gpos7]:** Check if font contains any GSUB 5 or GPOS 7 lookups which are not widely supported. (issue #3643)

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/dotted_circle]:** Fix ERROR by adding safeguard conditional on `is_complex_shaper_font` function. (issue #3640)
  - **[com.google.fonts/check/repo/upstream_yaml_has_required_fields]:** Remove repository_url field check since METADATA.pb files now include the source field. (issue #3618)

#### On the OpenType Profile
  - **[com.google.fonts/check/post_table_version]:** Updated policy on acceptable post table version. Downgraded the check from FAIL to WARN-level (according to discussions at issue #3635)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/metadata/can_render_samples]:** Check that the fonts can render the sample texts for all languages specified on METADATA.pb, by using the new `gflanguages` module (issue #3605)


## 0.8.7 (2022-Feb-17)
### Noteworthy code-changes
  - The `--succinct` flag now generates succinct HTML and MD reports. (PR #3608)

### New Checks
#### Added to the Fontwerk Profile
  - Include most of the `googlefonts` profile checks. (PR #3579)
  - **[com.fontwerk/check/vendor_id]:** Vendor ID must be 'WERK' on FontWerk fonts. (PR #3579)
  - **[com.fontwerk/check/weight_class_fvar]:** usWeightclass must match fvar default value. (PR #3579)

#### Added to the Universal Profile
  - **[com.google.fonts/check/dotted_circle]:** Check dotted circle is present and correct (issue #3600)

### Changes to existing checks
#### On the Google Fonts Profile
  - **[com.google.fonts/check/name/familyname]:** Consider camel-case exceptions (issue #3584)
  - **[com.google.fonts/check/name/fullfontname]:** Consider camel-case exceptions (issue #3584)
  - **[com.google.fonts/check/glyph_coverage]:** Use the correct nam-file for checking coverage of the GF-latin-core glyphset (issue #3583)
  - **[com.google.fonts/check/font_copyright]:** Allow Google LLC copyright. These are use in Noto fonts. (PR #3607)
  - **[com.google.fonts/check/license/OFL_copyright]:** Re-use expected copyright format. (PR #3607)
  - **[com.google.fonts/check/metadata/reserved_font_name]:** Added support for an RFN Exception allow-list, but it is kept empty for now while we review potential exceptions (issues #3589 and #3612)
  - **[com.google.fonts/check/name/rfn]:** RFN Exception allow-list (same as above)

### Migrations
#### To the `Universal` profile
  - **[com.google.fonts/check/transformed_components]:** moved from `Google Fonts` profile. It is not strictly a Google Fonts related check as transformed components cause problems in various rendering environments. (issue #3588)


## 0.8.6 (2022-Jan-29)
### Noteworthy code-changes
  - We now ensure that version 0.4.0 of our `collidoscope` dependency is not used because it had a bug that failed to detect an `ïï` collision on Nunito Black. (issues #3556)

### New Profile
  - Olli Meier (@moontypespace) contributed a new profile for Fontwerk, https://fontwerk.com/ (PR #3546)

### New Checks
#### Added to the Fontwerk Profile
  - **[com.fontwerk/check/no_mac_entries]:** Check if font has Mac name table entries (platform=1) (PR #3545)

#### Added to the Universal Profile
  - **[com.google.fonts/check/designspace_has_sources]:** Check that all sources in a designspace can be loaded successfully. (PR #3168)
  - **[com.google.fonts/check/designspace_has_default_master]:** Check that a default master is defined. (PR #3168)
  - **[com.google.fonts/check/designspace_has_consistent_glyphset]:** Check that non-default masters do not contain glyphs not found in the default master. (PR #3168)
  - **[com.google.fonts/check/designspace_has_consistent_codepoints]:** Check that Unicode assignments are consistent between masters. (PR #3168)

### Changes to existing checks
#### On the Opentype Profile
  - **[com.google.fonts/check/monospace]:** Update PANOSE requirements for monospaced fonts based on comments by Thomas Phinney (@tphinney) (issue #2857)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/name/rfn]:** If the OFL text is included in a name table entry, the check should not FAIL, as the full license text contains the term 'Reserved Font Name', which in this case is OK. (issue #3542)
  - **[com.google.fonts/check/layout_valid_feature_tags]:** Allow 'HARF' and 'BUZZ' tags. (issue #3368)
  - **[com.google.fonts/check/glyph_coverage]:** Fix ERROR. (issue #3551)
  - **[com.google.fonts/check/repo/sample_image]:** Declare conditions so that font repos lacking a README.md file will skip this check. (issue #3559)
  - **[com.google.fonts/check/metadata/unsupported_subsets]:** Declare conditions so that font repos lacking a METADATA.pb file will skip this check. (issue #3564)
  - **[com.google.fonts/check/varfont/grade_reflow]:** fix AttributeError: `'NoneType'` object has no attribute `'StartSize'` (issue #3566)
  - **[com.google.fonts/check/varfont/grade_reflow]:** Cleanup log message output: use a set (instead of a list) in order to eliminate multiple reporting of the same glyphs (issue #3561)
  - **[com.google.fonts/check/metadata/os2_weightclass]:** Improve wording of log messages to make the reasoning of expected values clearer to the users (issue #2935)


## 0.8.5 (2022-Jan-13)
### Noteworthy code-changes
  - New command line flag: `-F, --full-list` to print full lists (`pretty_print_list` method) even when the total number of items exceeds a certain threashold. (issues #3173 and #3512)
  - Included a few of the more recently added profiles that were still missing on our online docs (issue #3518)
  - Do not accept more than a single dash on font filenames. This ensures FontBakery won't miscomputed expected style values use on checks such as `com.google.fonts/check/usweightclass`. (issue #3524)

### New Checks
#### Added to the Universal Profile
  - **[com.google.fonts/check/cjk_chws_feature]:** Ensure CJK fonts contain chws/vchw features. (issue #3363)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/metadata/unsupported_subsets]:** Check for METADATA subsets with zero support. (issue #3533)

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/unreachable_glyphs]:** Glyphs which are components of other glyphs are no longer flagged as unreachable. (issue #3523)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/contour_count]:** Four fifths glyph can also be drawn with only 3 contours if the four is open-ended. (issue #3511)
  - **[com.google.fonts/check/glyph_coverage]:** Use the new glyphsets python module. (issue #3533)


## 0.8.4 (2021-Nov-19)
### Noteworthy code-changes
  - Updated Sphinx-docs extension code to use the latest API so that we can have FontBakery online docs properly build once more at https://font-bakery.readthedocs.io (issue #3313)
  - Also improved the documentation of checks, now displaying the contents of the `proposal` metadata fields. (Also issue #3313)
  - Fixed readability of tracebacks on ERROR messages on the text terminal (issue #3482)
  - Update fonts_public.proto and fonts_public_pb2.py

### New Checks
#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/description/urls]:** Check for http/https in anchor texts and WARN to remove them (issue #3497)

### Changes to existing checks
#### On the Google Fonts Profile
  - **[com.google.fonts/check/contour_count]:** WARN if a font has a softhyphen. Also, if present, it should be non-spacing (and should have no contours). (issue #3486)
  - **[com.google.fonts/check/contour_count]:** Do not expect ZWNJ and ZWJ glyphs to have zero contours. (issue #3487)
  - **[com.google.fonts/check/metadata/can_render_samples]:** Ensure METADATA.pb is present before running check (issue googlefonts/Unified-Font-Repository#62)

### Migrations
#### To the `Universal` profile
  - **[com.google.fonts/check/contour_count]:** moved from `Google Fonts` profile. (issue #3491)


## 0.8.3 (2021-Oct-28)
### Noteworthy code-changes
  - This release drops Python 3.6 support (issue #3459)
  - Check statuses may now also be overriden via configuration file. See USAGE.md for examples. (PR #3469)
  - We now use the CheckTester helper class in all our code-tests. (PR #3453)
  - The `get_family_checks` method also takes into account usage of the `fonts` dependency, in addition to `ttFonts`.

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/shaping/regression]:** Improve reporting of shaping differences. (PR #3472)

### New Checks
#### Added to the Universal Profile
  - **[com.google.fonts/check/unreachable_glyphs]:** Check if the font contains any glyphs not reachable by codepoint or substitution rules (issue #3160)

#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/repo/sample_image]:** The README.md file has a sample image to showcase the font family? (issue #2898)
  - **[com.google.fonts/check/metadata/can_render_samples]:** Ensure sample_text in METADATA.pb can be rendered in the font (issue #3419)

### Deprecated Checks
#### Removed from the Universal Profile
  - **[com.google.fonts/check/ftxvalidator]**: Since ftxvalidator is a proprietary tool, we can't be sure what it does. Font Bakery's mission is to collect font-bug knowledge publicly with "free as in freedom" code. Also, Font Bakery users have been either simply ignoring this third-party tool, or having headaches with installing it (we heard reports of tens of gigabytes and hours of downloading Apple tools just to have ftxvalidator available for this FontBakery check). In the past the reasoning for keeping a Font Bakery wrapper to ftxval was based on the fact that fonts will not install on MacOS if they do not pass ftxval checking routines. But the onboarders on Google Fonts reported that they've never faced that kind of problem, so we're now making the bold move of completely removing the wrapper-check since we believe our collection of FB checks are good enough to make sure fonts are valid for the MacOS font-installer. (PR #3479)
  - **[com.google.fonts/check/ftxvalidator_is_available]**: same reason as stated above.


## 0.8.2 (2021-Sep-01)
### Noteworthy code-changes
  - Fixed build of Read The Docs documentation pages (issue #3313)
  - Now one can invoke Font Bakery with different filetypes (other than just TTFs or OTFs) and the checks will run or skip based on file-type. (issue #3169)
  - For this reason, `UFO Source` checks are now included in the `Universal` profile. (issue #3439)
  - We'll likely have source-level (GlyphsApp) checks soon using this mechanism.
  - Updated font family protobuf files (issue #3443)

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/unwanted_tables]:** Documented reason for rejection of the 'prop' table. It is a table used on Apple's OSX-specific AAT and new fonts should not be using that. (issue #3411)
  - **[com.google.fonts/check/old_ttfautohint]:** Get latest ttfautohint version number from a constant instead of checking the user's system for an installed version of ttfautohint (issue #3423)

#### On the OpenType Profile
  - **[com.google.fonts/check/glyf_nested_components]:** Nested components are permitted by the OpenType specification, so this check has been moved to the Google Fonts profile. (issue #3424)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/metadata/designer_profiles]:** The `link` field is not currently used by the GFonts API, so it should be kept empty for now. (issue #3409)

### New Checks
#### Added to the Google Fonts Profile
  - **[com.google.fonts/check/transformed_components]:** Ensure component transforms do not perform scaling or rotation (which causes hinting and rasterization issues). (issue #2011)
  - **[com.google.fonts/check/metadata/family_directory_name]:** We want the directory name of a font family to be predictable and directly derived from the family name, all lowercased and removing spaces. (issue #3421)
  - **[com.google.fonts/check/file_size]:** Ensure that the absolute file size of the font is not going to cause problems on the Google Fonts platform. (issue #3320)
  - **[com.google.fonts/check/render_own_name]:** Ensure the font can render its own name without .notdef glyphs. (issue #3159)
  - **[com.google.fonts/check/varfont/grade_reflow]:** Ensure that variations on the GRAD axis do not change any horizontal advances. (issue #3187)


## 0.8.1 (2021-Aug-11)
### Bug fixes
  - Fix crash on is_OFL condition when a font project lacks a license. (issue #3393)

### Changes to existing checks
#### On the Universal Profile
  - **[com.google.fonts/check/unwanted_tables]:** Stop rejecting MVAR table (issue #3400)
  - **[com.google.fonts/check/required_tables]:** remove 'DSIG' from list of optional tables and improve wording on the check rationale. (issue #3398)
  - **[com.google.fonts/check/outline_\*]:** Also print codepoints on the log messages (issue #3395)

#### On the OpenType Profile
  - **[com.google.fonts/check/dsig]:** We now recommend (with a WARN) completely removing the 'DSIG' table. We may make this a FAIL by November 2023 when the EOL date for MS Office 2013 is reached. (issue #3398)
  - **[com.google.fonts/check/gdef_mark_chars]:** Also print glyphnames on log messages (issue #3395)
  - **[com.google.fonts/check/gdef_spacing_marks]:** Also print glyphnames on log messages (issue #3395)

#### On the Adobe Fonts Profile
  - Remove **check/dsig** override, which was now outdated because the original check implementation was just changed to actually suggest (with a WARN) the removal of any DSIG tables. (issue #3407)

#### On the Google Fonts Profile
  - **[com.google.fonts/check/metadata/designer_profiles]:** Change "missing-link" FAIL to WARN (issue #3409)


## 0.8.0 (2021-Jul-21)
### New Reporter
  - A reporter for `shields.io` badges, as discussed in https://github.com/googlefonts/Unified-Font-Repository/issues/14. It adds all the severity scores (with a default severity of 5 for those not yet providing a severity score) and uses this to generate a percentage. The JSON file it emits separates each profile into a separate badge.

### New Checks
  - **[com.google.fonts/check/family/italics_have_roman_counterparts]:** Ensure Italic styles have Roman counterparts. (issue #1733)
  - **[com.google.fonts/check/layout_valid_feature_tags]:** Check if the font contains any invalid feature tags. (PR #3359, issue #3355)
  - **[com.google.fonts/check/layout_valid_script_tags]:** Check if the font contains any invalid script tags. (PR #3359, issue #3355)
  - **[com.google.fonts/check/layout_valid_language_tags]:** Check if the font contains any invalid language tags. (PR #3359, issue #3355)
  - **[com.google.fonts/check/meta/script_lang_tags]:** Ensure fonts have ScriptLangTags declared on the 'meta' table. (issue #3349)
  - **[com.google.fonts/check/no_debugging_tables]:** Ensure fonts do not contain any preproduction tables. (issue #3357)

### Bug Fixes
  - Add a code-testing mechanism to ignore spurious ERRORs and use it for not letting the namecheck timeouts break our CI builds. (issue #3366)

### Changes to existing checks
  - **[com.google.fonts/check/license/OFL_body_text]**: Silently tolerate usage of "http://" on the OFL.txt file. (issue #3372)


## 0.7.38 (2021-Jun-23)
### New Checks
  - **[com.google/fonts/check/repo/upstream_yaml_has_required_fields]:** Check upstream.yaml file contains all required fields (PR #3344, issue #3338)
  - **[com.google.fonts/check/license/OFL_body_text]:** Check OFL.txt body text is correct (PR #3353, issue #3352)
  - **[com.google.fonts/check/os2/use_typo_metrics]:** Confirm that OS/2.fsSelection bit 7 (USE TYPO METRICS) is set (PR #3314, issue #3241)

### Bug Fixes
  - Log levels are now correctly honored when using the HTML reporter (issue #3225)

### Dependencies
  - Drop again the usage of unidecode due to licensing policies (issue #3316)

### Bug Fixes
  - **[com.google/fonts/check/whitespace_ink]:** Fixed a bug affecting Ogham Space Mark. The set of codepoints was created incorrectly because we forgot to use parentheses in the expression, which resulted in the set of non-drawing codepoints to still include the ogham space mark codepoint (quite the opposite of what the comment said we were doing there :-P) Now the check handles it properly and I also added a test case to ensure we do not reintroduce the bug. (issue #3345)

### Changes to existing checks
  - **[com.google.fonts/check/description/max_length]:** nowadays the Google Fonts specimen pages allow for longer texts without upsetting the balance of the page. So the new limit is 2,000 characters. (PR #3337)


## 0.7.37 (2021-May-20)
### Bug Fixes
  - fix crash on **com.google.fonts/check/missing_small_caps_glyphs** (issue #3294)

### Changes to existing checks
  - **[com.google.fonts/check/varfont/regular_opsz_coord]:** update the "Regular" instance opsz axis range  guidance to 10 - 16 from 9 - 13 according to updated [OT spec](https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz) (PR #3292)
  - **[com.google.fonts/check/missing_small_caps_glyphs]:** Also look for missing 'c2sc' glyphs (issue #3294)
  - **[com.google.fonts/check/stylisticset_description]:** Temporarily downgrade it to WARN-level (issue #3155)


## 0.7.36 (2021-May-14)
### Release notes
  - bugfixing quick release

### Bug Fixes
  - fix crash on *glyph_metrics_stats* condition (issue #3273)

### Changes to existing checks
  - **[com.google.fonts/check/canonical_filename]:** Split out `variable_font_filename` into a reusable condition (issue #3274)


## 0.7.35 (2021-May-12)
### Release notes
  - Axis Registry has been updated to commit https://github.com/google/fonts/tree/6418bd97834330f245cce4131ec3b8b98cb333be which includes changes to the `opsz` axis.
  - Format status output to improve readability. (issue #2052)
  - Move reporter-specific write logic to reporters, simplify argparse (PR #3206)
  - Profile-specific `fontbakery.commands.check_...` removed and replaced with a call to `check_profile` with the appropriate profile. (PR #3218)
  - HTML and Terminal reporter parses and renders markdown. (PR #3212) (PR #3227)
  - You can now pass (some) options to fontbakery using a configuration file, with the `--configuration` command line parameter. This configuration file is available to check code using the `config` parameter. (PR #3219)
  - All failing tests are now *required* to return a `Message` object containing a message code. (PR #3226)

### New Profile
  - Created a Type Network profile for checking some of their new axis proposals (issue #3130)
  - Created an ISO15008 profile for checking suitability for use in in-car display environments (issue #1832)

### Bugfixes
  - **license** condition now assumes that all license files in a given project repo are identical if more than one is found. With that some checks wont be skipped. We should have a fontbakery check to ensuring that assumption is valid, though. (issue #3172)
  - **license_path** condition: do not cause an ERROR on families lacking a license file. (issue #3201)
  - use Chris Simpkins' dehinter instead of ttfautohint-py to dehint font files while computing the file-size impact of hinting. (issue #3229)

### New Checks
  - **[io.github.abysstypeco/check/ytlc_sanity]:** Check if ytlc values are sane in a varfont (issue #3130)
  - **[com.google.fonts/check/cjk_vertical_metrics_regressions]:** Check CJK family has the same vertical metrics as the same family hosted on Google Fonts (issue #3242)
  - **[com.google.fonts/check/cjk_not_enough_glyphs]:** Warn users if there are less than 40 CJK glyphs in a font. (PR #3214)
  - **[com.google.fonts/check/gf_axisregistry/fvar_axis_defaults]:** Ensure default axis values are registered as fallback on the Google Fonts Axis Registry (issue #3141)
  - **[com.google.fonts/check/description/family_update]:** On a family update, the DESCRIPTION.en_us.html file should ideally also be updated. (issue #3182)
  - **[com.google.fonts/check/missing_small_caps_glyphs]:** Check small caps glyphs are available (issue #3154)
  - **[com.google.fonts/check/shaping/regression]:** Check that OpenType shaping produces results consistent with predefined expectations.
  - **[com.google.fonts/check/shaping/forbidden]:** Check that OpenType shaping does not produce "forbidden" glyphs (e.g. `.notdef`, visible virama, etc.).
  - **[com.google.fonts/check/shaping/collides]:** Check that OpenType shaping does not produce glyphs which collide with one another (e.g. `ïï`).
  - **[com.google.fonts/check/iso15008_proportions]:** Check that fonts designed for use in in-car environments have suitable proportions (issue #3250)
  - **[com.google.fonts/check/iso15008_stem_width]:** Check that fonts designed for use in in-car environments have suitable weight (issue #3251)
  - **[com.google.fonts/check/iso15008_intercharacter_spacing]:** Check that fonts designed for use in in-car environments have suitable intercharacter spacing (issue #3252)
  - **[com.google.fonts/check/iso15008_interword_spacing]:** Check that fonts designed for use in in-car environments have suitable interword spacing (issue #3253)
  - **[com.google.fonts/check/iso15008_interline_spacing]:** Check that fonts designed for use in in-car environments have suitable interline spacing (issue #3254)

### Changes to existing checks
  - **[com.google.fonts/check/vertical_metrics_regressions]:** Skip check if fonts are CJK (issue #3242) and refactor fsSelection bit 7 requirements (issue #3241)
  - **[com.google.fonts/check/kern_table]:** add FAIL when non-character glyph present, WARN when no format-0 subtable present (issue #3148)
  - **[com.google.fonts/check/gf_axisregistry/fvar_axis_defaults]:** Only check axes which are in the GF Axis Registry (PR #3217)
  - **[com.google.fonts/check/mandatory_avar_table]:** Update rationale to mention that this check may be ignored if axis progressions are linear.
  - **[com.google.fonts/check/integer_ppem_if_hinted]:** Format message with newlines.
  - **[com.google.fonts/check/STAT/gf_axisregistry]:** Ensure that STAT tables contain Axis Values
  - **[com.google.fonts/check/repo/dirname_matches_nameid_1]:** Added hints to GF specs for single-weight families to FAIL output (PR #3196)
  - **[com.google.fonts/check/metadata/has_regular]:** Added hints to GF specs for single-weight families to FAIL output (PR #3197)
  - **[com.google.fonts/check/gdef_mark_chars]:** Do not consider chars with Unicode category Mc, Spacing_Marks as (non spacing) mark class glyphs.
  - **[com.google.fonts/check/gdef_non_mark_chars]:** Same as com.google.fonts/check/gdef_mark_chars.
  - **[com.google.fonts/check/kerning_for_non_ligated_sequences]:** Change 'ligatures' condition to match changes in fontTools 4.22.0.
a - **[com.google.fonts/check/ligature_carets]:** Change 'ligature_glyphs' condition to match changes in fontTools 4.22.0. Updated rationale because fontmake 2.4.0 can compile ligature carets.
  - **[com.google.fonts/check/monospace]:** Changed conditions of seems_monospaced returned by glyph_metrics_stats(), if less than 80% of ASCII characters are in the font then it seems monospaced when all glyphs have one of two widths, excluding control character glyphs, mark glyphs and zero-width glyphs, instead of always 80% of ASCII glyphs having the same width.


## 0.7.34 (2021-Jan-06)
### New checks
  - **[com.google.fonts/check/mandatory_avar_table]:** Require variable fonts to include an avar table (issue #3100)

### Changes to existing checks
  - **[com.google.fonts/check/mandatory_glyphs]:** split check into multiple WARNs so that reporting of problems is clearer to users (issue #3086)
  - **[com.google.fonts/check/monospace]:** fix formatting of percentage to only display up to 2 decimals (issue #3117)
  - **[com.google.fonts/check/repo/vf_has_static_fonts]:** Downgrade it to WARN-level. (issue #3099)
  - **[com.google.fonts/check/varfont/unsupported_axes]:** Update rationale that was confusing and outdated (issues #3108 and #2866)

### Bugfixes
  - **[com.google.fonts/check/metadata/consistent_axis_enumeration]:** Add "family_metadata" as a condition to avoid an ERROR (issue #3122)
  - **[com.google.fonts/check/metadata/gf_axisregistry_bounds]:** Add "family_metadata" as a condition to avoid an ERROR (issue #3104)
  - **[com.google.fonts/check/metadata/gf_axisregistry_valid_tags]:** Add "family_metadata" as a condition to avoid an ERROR (issue #3105)
  - **[com.google.fonts/check/STAT/gf_axisregistry]:** Ignore format-4 entries on STAT table because the GF Axis Registry does not list any multi-axis fallback name which is what such entries are designed to describe (issue #3106)


## 0.7.33 (2020-Nov-24)
### Release note
  - This is a quick single bug-fix release because the problem below was disrupting the continuous integration setup of several users.
  - It also includes a small routine update on the cached vendor IDs list fetched from Microsoft's website (as we always do at every new FontBakery release).

### changes to checks
  - **[com.google.fonts/check/metadata/escaped_strings]:** Add "metadata_file" as a condition for the check in order to avoid an ERROR whenever the file is not available (issue #3095)


## 0.7.32 (2020-Nov-19)
### Note-worthy code changes
  - We now use GitHub Actions to run code-tests and linting (still under tox, so the same can be easily executed locally).
  - We now keep a local copy of the Google Fonts Axis Registry textproto files so that the checks do not need to keep always fetch them online at runtime. These files should not change too often, but we should be careful to check for updates on our FontBakery releases. (issue #3022)

### New checks
  - **[com.google.fonts/check/metadata/escaped_strings]:** Ensure fields in METADATA.pb do not use escaped strings (issue #2932)
  - **[com.google.fonts/check/STAT/axis_order]:** INFO-level check to gather stats on usage of the STAT table AxisOrdering field. May be updated in the future to enforce some ordering scheme yet to be defined. (issue #3049)
  - **[com.google.fonts/check/metadata/consistent_axis_enumeration]:** Validate VF axes on the 'fvar' table match the ones declared on METADATA.pb (issue #3051)
  - **[com.google.fonts/check/metadata/gf_axisregistry_valid_tags]:** VF axis tags are registered on GF Axis Registry (issue #3010)
  - **[com.google.fonts/check/metadata/gf_axisregistry_bounds]:** VF axes have ranges compliant to the bounds specified on the GF Axis Registry (issue #3022)
  - **[com.google.fonts/check/STAT/gf_axisregistry]:** Check that particle names and values on STAT table match the fallback names in each axis registry at the Google Fonts Axis Registry (issue #3022)
  - **[com.google.fonts/check/glyf_nested_components]:** Check that components do not reference glyphs which are themselves compontents (issue #2961)
  - **[com.google.fonts/check/outline_alignment_miss]:** Check for outline points near to, but not on, significant Y-axis boundaries. (PR #3088)
  - **[com.google.fonts/check/outline_short_segments]:** Check for outline segments which are suspiciously short. (PR #3088)
  - **[com.google.fonts/check/outline_colinear_vectors]:** Check for colinear segments in outlines. (PR #3088)
  - **[com.google.fonts/check/outline_jaggy_segments]:** Check for segments with a particularly small angle. (issue #3064)
  - **[com.google.fonts/check/outline_semi_vertical]:** Check for semi-vertical and semi-horizontal lines. (PR #3088)
  - **[com.google.fonts/check/metadata/designer_profiles]:** Ensure that the entries in the Designers Catalog are good (issue #3083)

### Changes to existing checks
  - **[com.google.fonts/check/family/win_ascent_and_descent]**: Skip if font is cjk
  - **[com.google.fonts/check/os2_metrics_match_hhea]**: Skip if font is cjk
  - **[com.google.fonts/check/monospace]**: Ignore zero advance-width glyphs (issue #3053)


## 0.7.31 (2020-Sept-24)
### Note-worthy code changes
  - This is a quick new release to address a silly but fatal crash (issue #3044)
  - We normalized the ordering of log messages of some checks. To avoid imprevisibility of python set iteration, we sort them before printing. This helps to reduce diffs for people that compare subsequent runs of fontbakery on automated QA setups (issue #3038)


## 0.7.30 (2020-Sept-24)
### Note-worthy code changes
  - The vast majority of code-tests now use our new style which is less error prone, using the helper CheckTester class. (PR #3035)
  - Adopted 4-spaces indentation. We're changing our codestyle to facilitate collaboration from people who also work with the fontTools and AFDKO codebases. (issue 2997)
  - All rationale text needs to have 8 indentation spaces (because this indentation on the source should not show up on the user-interface when rationale text is printed on the text terminal)
  - Remove PriorityLevel class as it makes classifying checks by priority more complicated then necessary! (issue #2981)
  - Use the http://fonts.google.com/metadata/fonts endpoint to determine if a font is listed in Google Fonts. (issue #2991)
  - Renamed `multiprocessing.py` to `multiproc.py` to avoid conflict with Python
    stdlib module of the same name in some configurations.
  - Re-worked `cff.py` checks using `@condition` to avoid repeated iterations
    over the glyph set.

### New Checks
  - **[com.google.fonts/check/varfont_duplicate_instance_names]**: Avoid duplicate instance names in variable fonts (issue #2986)
  - **[com.google.fonts/check/metadata/includes_production_subsets]**: ensure METADATA.pb files include production subsets. (issue #2989)
  - **[com.google.fonts/check/varfont/stat_axis_record_for_each_axis]**: ensure the STAT table has an Axis Record for every axis in the font (PR #3017)
  - **[com.adobe.fonts/check/cff_deprecated_operators]**: check for deprecated CFF operator `dotsection` and deprecated use of `endchar` operator to build accented characters (`seac`). (PR #3033)

### Changes to existing checks
  - **[com.google.fonts/check/monospace]**: Updated to not report zero width (mark) glyphs (issue #3036)
  - **[com.google.fonts/check/font_version]**: fixed tolerance for warnings (PR #3009)
  - **[com.google.fonts/check/fontbakery_version]**: use pip_api module and PyPI JSON API instead of invoking command-line pip/pip3 via subprocess (#2966)

### Bugfixes
  - Update vertical metric values in test_check_vertical_metrics_regressions. Cabin had recently been updated in Google Fonts and the family now has different vertical metric values (issue #3026)
  - Fix ERROR in com.google.fonts/check/STAT_strings (issue #2992)


## 0.7.29 (2020-Jul-17)
### Note-worthy code changes
  - This version adds initial support for multiprocessing (running multiple checks in parallel to likely speed up execution time) via the -j/--jobs flag, contributed by Lasse Fister (PR #2959)

### Bugfixes
  - **[com.google.fonts/check/description/broken_links]**: Skip when html does not parse. (issue #2664)
  - Checks if GSUB lookup format is 1 for ligature collection in `profiles/shared_conditions.py`; format 1 is the only significant one for `ligatures()` and `ligature_glyphs()`)

### New Checks
  - **[universal: com.google.fonts/check/rupee]**: Ensure indic fonts have the Indian Rupee Sign glyph (issue #2967)
  - **[googlefonts: com.google.fonts/check/metadata/category]**: Ensure category field is valid in METADATA.pb file (issue #2972)

### Changes to existing checks
  - **[com.google.fonts/check/unitsperem_strict]**: updating units per em criteria because the assumptions behind our previous "upm=2000 for VFs" suggestion were not really correct. (issue #2971)
  - **[com.google.fonts/check/ligature_carets]**: Add GlyphsApp instructions for fixing ligature caret WARNs (issue #2955)
  - **[com.google.fonts/check/metadata/broken_links]**: request URLs only once and accept status 429 - "too many requests" (issue #2974)
  - **[com.google.fonts/check/description/broken_links]**: request URLs only once and accept status 429 - "too many requests" (issue #2974)
  - **[com.google.fonts/check/varfont_instance_names]**: Check will now only allow 18 named instances (Thin-Black + Italics). This was decided in a Friday team meeting on the 2020/06/26. Changes also reflect the updated spec, https://github.com/googlefonts/gf-docs/tree/main/Spec#fvar-instances.


## 0.7.28 (2020-Jul-09)
### Note-worthy code changes
  - Major improvement to code-testing framework by adopting the `assert_PASS` and `assert_results_contain` helper methods (issue #2943)

### Changes to existing checks
  - **[com.google.fonts/check/font_version]**: Check now allows more than 3 decimal places to be matched (issue #2928)
  - **[com.google.fonts/check/varfont/unsupported_axes]**: Removed opsz axis and added slnt axis (issue #2866)
  - **[com.google.fonts/check/description/valid_html]**: Verify that html snippets parse correctly (issue #2664)
  - **[com.google.fonts/check/metadata/os2_weightclass]**: Check now allows Thin to have 100, 250 and ExtraLight to have 200, 275 (issue #2947)
  - **[com.google.fonts/check/whitespace_glyphnames]**: Report names that are not Adobe Glyph List compliant (issue #2624)
  - **[com.google.fonts/check/whitespace_glyphnames]**: Reviewed and updated keywords so that they more precisely indicate which specific FAIL or WARN causes a check failure.
  - **[com.google.fonts/check/whitespace_ink]**: Removed OGHAM SPACE MARK U+1680 as it is a whitespace that should have a drawing. (PR #2297 contributed by @drj11)

### Bugfixes
  - **[com.google.fonts/check/valid_glyphnames]**: Improve broken text in the FAIL message (PR #2939)


## 0.7.27 (2020-Jun-10)
### Note-worthy code changes
  - Add a `--succinct` mode. This is a slightly more compact and succint output layout for the text terminal. As requested by @m4rc1e (issue #2915)

### New checks
  - **[com.google.fonts/check/repo/fb_report]**: WARN when upstream repo has fb report files (issue #2888)
  - **[com.google.fonts/check/repo/zip_files]**: FAIL when upstream repo has ZIP files (issue #2903)
  - **[com.google.fonts/check/cjk_vertical_metrics]**: Check cjk fonts follow our cjk metric schema (PR #2797)

### Changes to existing checks
  - **[com.google.fonts/check/metadata/os2_weightclass]**: Check will now work correctly for variable fonts (issue #2683)
  - **[com.google.fonts/check/metadata/match_weight_postscript]**: Disabled for variable fonts
  - **[com.google.fonts/check/usweightclass]**: Check will now work properly for variable fonts and otf fonts (#2788)

### Bugfixes
  - Corrections to UNICODERANGE_DATA constant. Contributed by Bob Hallissy @bobh0303 (PR #2901)
  - Fix implementation of GDEF mark/nonmark checks (issues #2904 and #2877)
  - Ftxvalidator check now treats stderr separately and emits it as a WARN to avoid corrupting plist data and thus breaking its parsing. (issue #2801)
  - Fix crash on **com.google.fonts/check/family/vertical_metrics**. Thanks for reporting, @drj11 (issue #2917)
  - Fix crash on **com.google.fonts/check/family/os2_metrics_match_hhea** (issue #2921)
  - Fix several crashes when OS/2 table is missing: In **com.google.fonts/check/family/panose_proportion**, **com.google.fonts/check/family/panose_familytype**, **com.google.fonts/check/xavgcharwidth**, **com.adobe.fonts/check/fsselection_matches_macstyle**, **com.google.fonts/check/code_pages**, **com.google.fonts/check/family/panose_proportion**, **com.google.fonts/check/family/win_ascent_and_descent**. Contributed by @drj11


## 0.7.26 (2020-May-29)
### Noteworthy code-changes
  - update gfonts protobuf schema, in sync with GFTools (https://github.com/googlefonts/gftools/issues/202) (#issue #2886)

### Bugfixes
  - fix ERROR on com.google.fonts/check/STAT_strings (issue #2889)

### Deprecated checks
  - **[com.google.fonts/check/description/variable_font]**: Not needed anymore since Google Fonts now displays the information in its UI, so no need to also mention it on the description. (issue #2885)

### New checks
  - **[com.google.fonts/check/gdef_spacing_marks]**: warn when glyphs in the GDEF mark glyph class should be non-spacing (issue #2877).
  - **[com.google.fonts/check/gdef_non_mark_chars]**: fails when glyphs mapped to non-mark characters are in the GDEF mark glyph class (issue #2877)
  - **[com.google.fonts/check/gdef_mark_chars]**: warns when glyphs mapped to mark characters are not in the GDEF mark glyph class. (issue #2877)

### Modified checks
- **[com.google.fonts/check/metadata/valid_copyright]**: Accept year range in copyright strings. (issue #2393)


## 0.7.25 (2020-May-15)
### New checks
  - **[com.google.fonts/check/varfont/unsupported_axes]**: Ensure VFs do not contain opsz or ital axes. (issue #2866)
  - **[com.google.fonts/check/STAT_strings]**: Check correctness of name table strings referenced by STAT table. (issue #2863)
  - **[com.google.fonts/check/description/eof_linebreak]**: DESCRIPTION.en_us.html should end in a linebreak. (issue #2879)

### Added rationale metadata to these checks
  - **com.google.fonts/check/vendor_id**

### Changes to existing checks
  - **[com.google.fonts/check/vendor_id]**: improve wording of warning messages (issue #2855)
  - **[com.google.fonts/check/repo/vf_has_static_fonts]**: only run this check if the project follows the Google Fonts repo structure layout. (#2853)
  - **[com.google.fonts/check/unitsperem_strict]**: update requirements on upm values; 2000 is a minimum for VF because lower than that creates less smooth interpolation; and larger than 2048 causes a filesize increase. (issue #2827)
  - **[com.google.fonts/check/whitespace_glyphs]**: yield one unique message (and `message.code`) per missing whitespace case to enable selective overrides based on individual message codes
  - update adobefonts overridden whitespace_glyphs check to WARN on missing 0x00A0 (fail on 0x0020)

### Bug Fixes
  - Family names with more than a single word were not being properly detected when querying GFonts API (issue #2848)
  - fix style_parse handling of file paths containing a "-" char. (issue #2867)


## 0.7.24 (2020-Apr-21)
### Note-worthy changes
  - Fixed rendering of markdown on our read-the-docs documentation (#2819)

### Changes to existing checks
  - **[com.google.fonts/check/whitespace_widths]**: Provide instructions on how to fix the problem at Glyphs App source files (PR #2843)


## 0.7.23 (2020-Apr-17)
### Note-worthy changes
  - We now tell users on the text terminal what each of the check results mean. (issue #2823)

### New Checks
  - **[com.google.fonts/check/varfont/consistent_axes]**: Ensure that all variable font files have the same set of axes and axis ranges. (issue #2810)

### Changes to existing checks
  - **[com.google.fonts/check/valid_glyphnames]**: Increase glyphname max-length to 63 chars. (issue #2832)
  - **[com.google.fonts/check/unitsperem_strict]:** Do not WARN for upem=2048 (issue #2827)

### Bugfixes
  - profiles.googlefonts_conditions.familyname now works on variable fonts.
  - Invoke ftxvalidator binary from path detected by shutil.which (issue #2791)
  - Split too long lines in rationale text such as long URLs (issue #2835)

### Documentation
  - Documentation at ReadTheDocs should default to stable (last release on PyPI) instead of latest (development on 'main' branch). (issue #2819)
  - Clearly mention the list of checks on the top of the documentation front-page. (issue #2814)


## 0.7.22 (2020-Mar-27)
### Note-worthy changes
  - Updated function to extract a font family name from a font filename. Code taken from gftools.util.google_fonts.FamilyName

### Documentation
  - clarify that Xcode version can be 9 or later (issue #2784)

### Bugfixes
  - Ignore git commit hash on ttfautohint version string (issue #2790)

### Changes to existing checks
  - **[com.google.fonts/check/hinting_impact]**: Add support for CFF hints (issue #2802)
  - **[com.google.fonts/check/varfont_instance_names]**: Add ExtraBlack 1000 weight support (issue #2803)
  - **[com.google.fonts/check/varfont_instance_coordinates]**: Add ExtraBlack 1000 weight support (issue #2804)


## 0.7.21 (2020-Mar-06)
### Note-worthy changes
  - The snippet for checking collections is just an example shell script and it is specific to the directory structure of the Google Fonts git repo. We've made this clearer by renaming the script to **snippets/fontbakery-check-gfonts-collection.sh** (issue #2740)
  - The script was also fixed to run properly on MacOS, as it was originally only working on GNU+Linux.

### Changes to existing checks
  - **[com.google.fonts/check/varfont_instance_*]**: Clean up output and ensure that unregistered axes produce a warning. (issue #2701) Output will now display the following:
    - WARN if instance names are not fully parsable. It will also output the unparsable tokens.
    - FAIL if instance coordinates are incorrect for known axes.
    - FAIL if the fvar contains known axes and they're not mentioned in instance names.
    - FAIL if instance name tokens are incorrectly ordered
    - Provide link to our documentation if these checks FAIL or WARN
  - **[com.google.fonts/check/fontdata_namecheck]**: improve log messages when query fails (issue #2719)
  - **[com.google.fonts/check/name/rfn]**: Add rationale and make it a **FAIL** as it is a strong requirement for Google Fonts that families do not use a "Reserved Font Name" (issue #2779)
  - **[com.google.fonts/check/name/line_breaks]**: Add rationale (issue #2778)

### Migration of checks between profiles
  - **[com.google.fonts/check/name/line_breaks]**: From `opentype` to `googlefonts` profile as it is a vendor-specific policy rather than an OpenType spec requirement. (issue #2778)
  - **[com.google.fonts/check/name/rfn]**: From `opentype` to `googlefonts` profile (issue #2779)


## 0.7.20 (2020-Feb-24)
### Emergency bugfix release!
  - FATAL ERROR by adding proper indentation to rationale string on com.google.fonts/check/metadata/valid_copyright (issue #2772)


## 0.7.19 (2020-Feb-22)
### Note-worthy code changes
  - Add support for super-family checks! (issue #1487)

### New checks
  - **[com.google.fonts/check/license/OFL_copyright]**: Check if license file first line contains copyright string (issue #2764)
  - **[com.google.fonts/check/superfamily/list]**: A simple & merely informative check that lists detected sibling family directories (issue #1487)
  - **[com.google.fonts/check/superfamily/vertical_metrics]**: Experimental extended version of **family/vertical_checks**, but only emitting WARNs for now (issues #1487 and #2431)
  - **[com.google.fonts/check/metadata/multiple_designers]**: Ensure explicit designer names are mentioned on METADATA.pb (issue #2766)

### Deprecated checks
  - **[com.google.fonts/check/monospace_max_advancewidth]**: (issue #2749)

### Bugfixes
  - fix generate-glyphdata command (python 3 support) (issue #2765)

### Changes to existing checks
  - **[com.google.fonts/check/post_table_version]**: Support CFF2 OTF Variable Fonts and add rationale (issue #2638)
  - **[com.google.fonts/check/metadata/valid_copyright]**: Add rationale and make it case insensitive (issue #2736)
  - **[com.google.fonts/check/metadata/undeclared_fonts]**: Clarify rationale (issue #2751)
  - **[com.google.fonts/check/metadata/filenames]**: Add rationale (issue #2751)
  - **[com.google.fonts/check/metadata/filenames]**: Consider all files from a directory (issue #2751)
  - **[com.google.fonts/check/monospace]:** Fix typo isFixedWidth is actually isFixedPitch, xAverageWidth is xAvgCharWidth


## 0.7.18 (2020-Feb-05)
### Changes to existing checks
  - **[com.google.fonts/check/name/license]** and **[com.google.fonts/check/name/license_url]**: Accept http URLs but warn that those should ideally be updated to HTTPS. (issue #2731)
  - **[com.google.fonts/check/metadata/undeclared_fonts]**: Accept "static/" subdirs (issue #2737)

### Bugfixes
  - Add Thomas Phinney's comment on rationale of check **com.google.fonts/check/monospace** (issue #2729)
  - **[com.google.fonts/check/name/license_url]** and **com.google.fonts/check/name/license**: Added rationale and improved wording of log messages. (issue #2666)


## 0.7.17 (2020-Jan-15)
### New features
  - Add support for color themes. (issue #2031)
  - Auto-select default color theme based on operating system in use. The vast majority of MacOS users seem to use a light-background on the text terminal. For orther systems like GNU+Linux and Windows, a dark terminal seems to be more common.


## 0.7.16 (2019-Dec-13)
### Note-worthy changes
  - New experimental notofonts profile. Some checks from this profile may be promoted into the universal profile later (issue #2676)
  - New code snippet: An exemple of a custom fontbakery profile (with support for universal profile checks, check filters, and custom checks) has been provided by Chris Simpkins at snippets/check-custom.py (PR #2714)

### Bugfixes
  - **[com.google.fonts/check/glyph_coverage]:** display full list of missing required codepoints in INFO log message (issue #2690)

### Changes to existing checks
- **[com.google.fonts/check/family_naming_recommendation]:** Increase acceptable characters in nameID 6 string to 63 from 29 (PR #2707)

### New checks
  - **[com.google.fonts/check/glyf_non_transformed_duplicate_components]:** Check glyphs do not have duplicate components which have the same x,y coordinates (PR #2709)
  - **[com.google.fonts/check/repo/vf_has_static_fonts]:** Check VF family dirs in google/fonts contain static fonts (issue #2654)
  - **[com.google.fonts/check/unicode_range_bits]:** Ensure UnicodeRange bits are properly set (issue #2676)
  - **[com.google.fonts/check/cmap/unexpected_subtables]:** Ensure all cmap subtables are the typical types expected in a font (issue #2676)


## 0.7.15 (2019-Nov-03)
### Note-worthy changes
  - **Rationale cleanup & render:** Reviewed all rationale metadata entries and added code to properly format them on the github markdown and text terminal output. Later we probably should parse markdown everywhere. (issue #2681)
  - **[com.google.fonts/check/glyph_coverage]:** Removed strong requirement of 0x000D (carriage-return) for the GF Latin Core character set. (issue #2677)

### New features
  - Print rationale of checks (if available) on terminal output (issue #2531)
  - Display rationale text on the github markdown output (when it is available) (issue #2531)


## 0.7.14 (2019-Oct-16)
### Bugfixes
  - **[com.google.fonts/check/contour_count]:** Fix listing of glyphnames with unexpected contour counts. (issue #2647)
  - rewording: bit should be... "reset" => "unset" (issue #2648)
  - **[com.google.fonts/check/os2_metrics_match_hhea]:** Display the actual mismatching values. (issue #2653)
  - **[com.google.fonts/check/namecheck]:** fake user agent on http://namecheck.fontdata.com/ requests to get good query results.


## 0.7.13 (2019-Oct-04)
### New checks
  - **[com.google.fonts/check/metadata/filenames]:** "METADATA.pb: Font filenames match font.filename entries?" (issue #2597)

### Bugfixes
  - **[com.google.fonts/check/usweightclass]:** Italics should not affect the results. (issue #2650)
  - **[com.google.fonts/check/canonical_filename]:** Fix f-string syntax and only check filename (not full path) (issue #2649)

### Changes to checks
  - **[com.google.fonts/check/canonical_filename]:** filenames with underscore characters are considered invalid. (issue #2615)
  - **[com.google.fonts/check/gasp]:** mention how to fix if font is unhinted (issue #2636)


## 0.7.12 (2019-Sep-14)
### Note-worthy code changes
  - Added 'opsz' axis to fontbakery.parse
  - **[com.google.fonts/check/contour_count]:** ignore PUA codepoints (issue #2612)
  - **[com.google.fonts/check/contour_count]:** detect glyphs by both glyphnames and codepoints (issue #2612)
  - **[com.google.fonts/check/canonical_filename]:** Use Typographic Family Name if it exists in the nametable
  - **[com.google.fonts/check/varfont_instance_names]:** warn user if "Text" or "Display" have been used in a varfont instance name. We would prefer point size to be used instead.

### Bugfixes
  - fix crash on html/markdown reporters by declaring DEBUG log-level (issue #2631)

### Changes to checks
  - **[com.google.fonts/check/unwanted_tables]:** Add MVAR table (Issue #2599) and improve FAIL message


## 0.7.11 (2019-Aug-21)
### Note-worthy code changes
  - Adding yet a whole bunch more keywords to log-messages (issue #2558)
  - Refactored EncodingID/LanguageID classes for Mac & Windows name table entries

### Bug Fixes
  - **[com.adobe.fonts/check/family/max_4_fonts_per_family_name]:**  Only run on Win name records (issue #2613)
  - Avoid crash on static fonts by safeguarding the `slnt_axis` condition.

### New checks
  - **[com.google.fonts/check/metadata/undeclared_fonts]:** "Ensure METADATA.pb lists all font binaries" (issue #2575)
  - **[com.google.fonts/check/varfont/slnt_range:]** "The variable font 'slnt' (Slant) axis coordinate specifies positive values in its range?" (issue #2572)

### Renamed check IDs:
  - **[com.google.fonts/check/wdth_valid_range]** => com.google.fonts/check/varfont/wdth_valid_range
  - **[com.google.fonts/check/wght_valid_range]** => com.google.fonts/check/varfont/wght_valid_range


## 0.7.10 (2019-Aug-06)
### Note-worthy code changes
  - Added keywords for non-PASS log messages of a very large set of checks. At some point this will be mandatory for all checks. (issue #2558)
  - Make sure canonical style name checks are strongly enforced. Improve wording of FAIL log message on check/varfont_instance_names (issue #2573)

### Bug fixes
  - fix ERROR on check/metadata/broken_links (issue #2585)


## 0.7.9 (2019-Jul-11)
### Note-worthy code changes
  - update varfont naming scheme: use commas to separate axis tags (issue #2570)

### Disables checks
  - Disabled family checks: **com.google.fonts/check/family/equal_numbers_of_glyphs** and **com.google.fonts/check/family/equal_glyph_names** These will be reintroduced after known problems are addressed. (issue #2567)
  - Temporarily disabled **com.google.fonts/check/production_encoded_glyphs** since GFonts hosted Cabin files seem to have changed in ways that break some of the assumptions in its code-test. (issue #2581)

### Re-enabled checks
  - **[com.google.fonts/check/fontdata_namecheck]:** Web service is online again. (issue #2484)

### Bug fixes
  - **[com.google.fonts/check/fontbakery_version]:** FAIL if unable to detect latest available fontbakery version (issue #2579)
  - perform a hacky fixup to workaround the square-brackets naming scheme currently in use for varfonts in google fonts. (issue #2570)


## 0.7.8 (2019-Jun-22)
### Note-worthy code changes
  - Add GlyphsApp hint to com.google.fonts/check/usweightclass (issue #2423)
  - Fix "metatada" typo on checkid: **com.google.fonts/check/metatada/canonical_style_names** (issue #2561)
  - Reorder loglevels: INFO now has higher priority than SKIP (issue #2560)

### Changes to checks
  - **[com.google.fonts/check/canonical_filename]:**  update variable fonts naming scheme (issue #2549)


## 0.7.7 (2019-Jun-18)
### Note-worthy code changes
  - **[com.google.fonts/check/family/has_license]:** only run check if the fonts are in a google/fonts repo.
  - **[com.google.fonts/check/vendor_id]:** accept NULL-padding on vendor-IDs (issue #2548)

### Bug fixes
  - fix crash on git_gfonts_ttFonts condition (return None when the font is not yet available on GitHub) (issue #2540)

### New Checks
  - **[com.google.fonts/check/metadata/broken_links]:** Ensure the copyright string in METADATA.pb files does not contain broken URLs. (issue #2550)


## 0.7.6 (2019-Jun-10)
### Note-worthy code changes
  - **[com.google.fonts/check/name/subfamilyname]:** has been refactored to use parse.style_parse.
  - **[com.google.fonts/check/name/typographicsubfamilyname]:** has been refactored. It is now acceptable to have a typographic subfamily name if the font is RIBBI since it does not cause any issues

### Bug fixes
  - Render line-breaks on Read The Docs check rationales
  - **[com.adobe.fonts/check/family/bold_italic_unique_for_nameid1]:** restrict check to RIBBI styles only (issue #2501)
  - fix bug in **points_out_of_bounds** check: The coordinates of a component multiplied by a scale factor result in floating-point values. These were causing false-FAILs because we were not rounding them before checking if they are within the glyph bounding-box. This was probably making points at extrema to fall slightly out of the bbox. (issue #2518)
  - also improved the readability of **com.google.fonts/check/points_out_of_bounds**

### New Checks
  - **[com.google.fonts/check/description/variable_font]:** Ensure that variable fonts contain the following message in the DESCRIPTION.en-us.html file: `This family is available as a variable font.` (issue #2538)
  - **[com.google.fonts/check/description/git_url]:** Make sure all font families have an upstream git repo URL declared in the DESCRIPTION.en-us.html file. (issue #2523)
  - **[com.google.fonts/check/varfont_instance_coordinates]:** Check variable font instances have correct axis coordinates (PR #2520)
  - **[com.google.fonts/check/varfont_instance_names]:** Check variable font instances have correct names (PR #2520)
  - **[com.google.fonts/check/wdth_valid_range]:** Check variable font wdth axis has correct range (PR #2520)


## 0.7.5 (2019-May-24)
### Note-worthy code changes
  - The conditions from the `googlefonts` profile were split out into their own separate file

### Dependencies
  - Make docs building dependencies optional using "extras_require"

### Deprecated checks
  - **[com.google.fonts/check/currency_chars]:** we now have a much broader glyph coverage check: com.google.fonts/check/glyph_coverage (issue #2498)

### Bug fixes
  - The HTML report now actually defaults to "sans-serif" as the body font.
  - **[com.google.fonts/check/repo/dirname_matches_nameid_1]:** Restrict it to static fonts as the `fontbakery.util.get_regular` function does not support variable fonts yet. (issue #2509)
  - **[com.google.fonts/check/license_url]:** it now instructs the user which valid URL is actually expected (issue #2502)


## 0.7.4 (2019-May-06)
### Note-worthy code changes
  - We now have documentation of FontBakery checks on ReadTheDocs generated by a custom Sphinx module.
  - Markdown report now links to FB check docs on ReadTheDocs. (issue #2489)

### Dependencies
  - Removed defusedxml dependency. We were only using it for its `defused.lxml` module which is now deprecated (issue #2477)
  - Removed fontforge dependency.

### New checks
  - **[com.google.fonts/check/glyph_coverage]:** Google Fonts expects that fonts support at least the GF-latin-core glyph-set (PR #2488)
  - **[com.google.fonts/check/metadata/designer_values]:** We must use commas instead of forward slashes because the fonts.google.com directory will segment string to list on comma and display the first item in the list as the "principal designer" and the other items as contributors (issue #2479)
  - **[com.google.fonts/check/vertical_metrics_regressions]:** If a family already exists on Google Fonts, the family being checked must have similar vertical metrics (issue #1162)

### Temporarily disabled checks
  - **[com.google.fonts/check/fontdata_namecheck]:** The web-service is down. (issue #2483)

### Deprecated checks
  - **[com.google.fonts/check/fontforge_stderr]:** and **[com.google.fonts/check/fontforge]:** Fontforge does not support python 3. Well... it does, but it is a mess. We'll have to put significant effort if we ever bring back these checks.

### Bug fixes
  - **[com.google.fonts/check/dsig]:** Mention which gftools script can fix the issue.
  - **[com.google.fonts/check/family/has_license]:** Mention which licenses were found if multiple licenses exist.


## 0.7.3 (2019-Apr-19)
### Note-worthy code changes
  - The cupcake artwork is not gone, but it is now much less likely to show up. You can't get a cupcake unless you really deserve it! (issue #2030)
  - Improved --list-checks output. Now uses colors for better legibility on the text terminal (issue #2457)
  - We now autocomplete check IDs on the command line (issue #2457)
  - Even though we trid to add an install-rule for the bash-completion script on setup.py, we ended up removing it because it was not yet done in a cross-platform compatible manner. We'll get back to it later. For now users will have to manually install the script if they want bash completion to work. On MacOS it should typically be saved on `/usr/local/etc/bash_completion.d` and on GNU+Linux a good target directory would typically be `/etc/bash_completion.d`. More info at issue #2465.

### New checks
  - **[com.google.fonts/check/code_pages]:** Detects when no code page was declared on the OS/2 table, fields ulCodePageRange1 and ulCodePageRange2 (issue #2474)
  - **[com.adobe.fonts/check/find_empty_letters]:** "Letters in font have glyphs that are not empty?" (PR #2460)
  - **[com.google.fonts/check/repo/dirname_matches_nameid_1]:** "Directory name in GFonts repo structure must match NameID 1." (issue #2302)
  - **[com.google.fonts/check/family/vertical_metrics]:** "Each font in a family must have the same vertical metrics values." (PR #2468)

### Bug fixes
  - **[com.adobe.fonts/cff_call_depth]:** fixed handling of font dicts in a CFF (PR #2461)
  - Declare fonttools' unicode extra-dependency on our rquirements.txt and setup.py so that unicodedata2 is properly installed. (issue #2462)
  - Shorten too verbose log messages in a few checks. (issue #2436)


## 0.7.2 (2019-Apr-09)
### Note-worthy code changes
  - **[com.google.fonts/check/name/family_and_style_max_length]:** increased max length to 27 chars. After discussing the problem in more detail at issue #2179 we decided that allowing up to 27 chars would still be on the safe side. Please also see issue #2447

### Bug fixes
  - **[com.google.fonts/check/family/equal_glyph_names]:** Fix ERROR. When dealing with variable fonts, we end up getting None from the style condition. So we display filenames in those cases. But we still display styles when dealing with statics fonts. (issue #2375)
  - **[com.adobe.fonts/check/cff_call_depth]:** don't assume private subroutines in a CFF (PR #2437)
  - **[com.adobe.fonts/cff2_call_depth]:** fixed handling of font dicts (and private subroutines) in a CFF2 (PR #2441)
  - **[com.google.fonts/check/contour_count]:** Filter out the .ttfautohint glyph component from the contour count (issue #2443)

### Dependencies
  - Removed the unidecode dependency. It is better to read log messages with the actual unicode strings instead of transliterations of them.


## 0.7.1 (2019-Apr-02)
### Major code-changes
  - The new "universal" profile contains checks for best practices agreed upon on the type design community. (issue #2426)
  - The initial set of checks will be not only the full opentype profile but also those checks original included in both `adobefonts` and `googlefonts` profiles.
  - The goal is to keep the vendor-specific profiles with only the minimal set of checks that are really specific, while the shared ones are placed on the universal profile.

### New checks
  - **[com.adobe.fonts/check/cff_call_depth]:** "Is the CFF subr/gsubr call depth > 10?" (PR #2425)
  - **[com.adobe.fonts/check/cff2_call_depth]:** "Is the CFF2 subr/gsubr call depth > 10?" (PR #2425)
  - **[com.google.fonts/check/family/control_chars]:** "Are there unacceptable control characters in the font?" (PR #2430)
  - **[com.google.fonts/check/name/trailing_spaces]:** "Name table records must not have trailing spaces." (issue #2417)


## 0.7.0 (2019-Mar-22)
### Major code-changes
  - The term "specification" (including directory paths, class names and method names such as Spec, FontsSpec, etc) was replaced by "profile" throughout the codebase. The reason for this renaming was to avoid confusing with other uses of the term such as in "OpenType Specification".
  - All numerical check-IDs were renamed to keyword-based IDs. We may still change them as we see fit and we plan to freeze the check-id naming when Font Bakery 1.0.0 is released.

### Bug fixes
  - **[com.google.fonts/check/canonical_filename]:** Distinguish static from varfont when reporting correctness of fontfile names. There are special naming rules for variable fonts. (issue #2396)
  - Fix bug in handling of `most_common_width` in `glyph_metrics_stats` which affected checking of monospaced metadata. (PR #2391)
  - Fix handling of `post.isFixedPitch` (accept any nonzero value). (PR #2392)
  - **[com.google.fonts/check/metadata/valid_copyright]:** Check was being skipped when run on upstream font repos which don't have a METADATA.pb file. This check will now only test METADATA.pb files. A new check has been added to check the copyright string in fonts.

### Other relevant code-changes
  - We temporarily disabled com.google.fonts/check/metadata/match_filename_postscript for variable fonts until we have a clear definition of the VF naming rules as discussed at https://github.com/google/fonts/issues/1817
  - We are now using portable paths on the code-tests. (issue #2398)
  - The Adobe Fonts profile now includes FontForge checks. (PR #2401)
  - Improve emoji output of `--ghmarkdown` option, so that actual emoji appear in text editors, rather than the previous emoji names
  - The HTML reporter will now display check results more table-like, which makes multi-line check results look better.

### New checks
  - **[com.google.fonts/check/font_copyright]: "Copyright notices match canonical pattern in fonts"** (PR #2409)
  - **[com.adobe.fonts/check/postscript_name_consistency]:** "Name table ID 6 (PostScript name) must be consistent across platforms." (PR #2394)

## Some check id renaming for better naming consistency:
  - **[com.google.fonts/check/tnum_horizontal_metrics]:** com.google.fonts/check/family/tnum_horizontal_metrics
  - **[com.adobe.fonts/check/bold_italic_unique_for_nameid1]:** com.adobe.fonts/check/family/bold_italic_unique_for_nameid1
  - **[com.adobe.fonts/check/max_4_fonts_per_family_name]:** com.adobe.fonts/check/family/max_4_fonts_per_family_name
  - **[com.abobe.fonts/check/postscript_name_cff_vs_name]:** com.abobe.fonts/check/name/postscript_vs_cff
  - **[com.adobe.fonts/check/postscript_name_consistency]:** com.adobe.fonts/check/name/postscript_name_consistency
  - **[com.adobe.fonts/check/name_empty_records]:** com.adobe.fonts/check/name/empty_records

### Renamed numerical check-IDs:
  - **[com.google.fonts/check/001]:** com.google.fonts/check/canonical_filename
  - **[com.google.fonts/check/002]:** com.google.fonts/check/family/single_directory
  - **[com.google.fonts/check/003]:** com.google.fonts/check/description/broken_links
  - **[com.google.fonts/check/004]:** com.google.fonts/check/description/valid_html
  - **[com.google.fonts/check/005]:** com.google.fonts/check/description/min_length
  - **[com.google.fonts/check/006]:** com.google.fonts/check/description/max_length
  - **[com.google.fonts/check/007]:** com.google.fonts/check/metadata/unknown_designer
  - **[com.google.fonts/check/008]:** com.google.fonts/check/family/underline_thickness
  - **[com.google.fonts/check/009]:** com.google.fonts/check/family/panose_proportion
  - **[com.google.fonts/check/010]:** com.google.fonts/check/family/panose_familytype
  - **[com.google.fonts/check/011]:** com.google.fonts/check/family/equal_numbers_of_glyphs
  - **[com.google.fonts/check/012]:** com.google.fonts/check/family/equal_glyph_names
  - **[com.google.fonts/check/013]:** com.google.fonts/check/family/equal_unicode_encodings
  - **[com.google.fonts/check/014]:** com.google.fonts/check/family/equal_font_versions
  - **[com.google.fonts/check/015]:** com.google.fonts/check/post_table_version
  - **[com.google.fonts/check/016]:** com.google.fonts/check/fstype
  - **[com.google.fonts/check/018]:** com.google.fonts/check/vendor_id
  - **[com.google.fonts/check/019]:** com.google.fonts/check/name/unwanted_chars
  - **[com.google.fonts/check/020]:** com.google.fonts/check/usweightclass
  - **[com.google.fonts/check/028]:** com.google.fonts/check/family/has_license
  - **[com.google.fonts/check/029]:** com.google.fonts/check/name/license
  - **[com.google.fonts/check/030]:** com.google.fonts/check/name/license_url
  - **[com.google.fonts/check/031]:** com.google.fonts/check/name/no_copyright_on_description
  - **[com.google.fonts/check/032]:** com.google.fonts/check/name/description_max_length
  - **[com.google.fonts/check/033]:** com.google.fonts/check/monospace
  - **[com.google.fonts/check/034]:** com.google.fonts/check/xavgcharwidth
  - **[com.google.fonts/check/035]:** com.google.fonts/check/ftxvalidator
  - **[com.google.fonts/check/036]:** com.google.fonts/check/ots
  - **[com.google.fonts/check/037]:** com.google.fonts/check/fontvalidator
  - **[com.google.fonts/check/038]:** com.google.fonts/check/fontforge_stderr
  - **[com.google.fonts/check/039]:** com.google.fonts/check/fontforge
  - **[com.google.fonts/check/040]:** com.google.fonts/check/family/win_ascent_and_descent
  - **[com.google.fonts/check/041]:** com.google.fonts/check/linegaps
  - **[com.google.fonts/check/042]:** com.google.fonts/check/os2_metrics_match_hhea
  - **[com.google.fonts/check/043]:** com.google.fonts/check/unitsperem
  - **[com.google.fonts/check/044]:** com.google.fonts/check/font_version
  - **[com.google.fonts/check/045]:** com.google.fonts/check/dsig
  - **[com.google.fonts/check/046]:** com.google.fonts/check/mandatory_glyphs
  - **[com.google.fonts/check/047]:** com.google.fonts/check/whitespace_glyphs
  - **[com.google.fonts/check/048]:** com.google.fonts/check/whitespace_glyphnames
  - **[com.google.fonts/check/049]:** com.google.fonts/check/whitespace_ink
  - **[com.google.fonts/check/050]:** com.google.fonts/check/whitespace_widths
  - **[com.google.fonts/check/052]:** com.google.fonts/check/required_tables
  - **[com.google.fonts/check/053]:** com.google.fonts/check/unwanted_tables
  - **[com.google.fonts/check/054]:** com.google.fonts/check/hinting_impact
  - **[com.google.fonts/check/055]:** com.google.fonts/check/name/version_format
  - **[com.google.fonts/check/056]:** com.google.fonts/check/old_ttfautohint
  - **[com.google.fonts/check/057]:** com.google.fonts/check/name/line_breaks
  - **[com.google.fonts/check/058]:** com.google.fonts/check/valid_glyphnames
  - **[com.google.fonts/check/059]:** com.google.fonts/check/unique_glyphnames
  - **[com.google.fonts/check/061]:** com.google.fonts/check/epar
  - **[com.google.fonts/check/062]:** com.google.fonts/check/gasp
  - **[com.google.fonts/check/063]:** com.google.fonts/check/gpos_kerning_info
  - **[com.google.fonts/check/064]:** com.google.fonts/check/ligature_carets
  - **[com.google.fonts/check/065]:** com.google.fonts/check/kerning_for_non_ligated_sequences
  - **[com.google.fonts/check/066]:** com.google.fonts/check/kern_table
  - **[com.google.fonts/check/067]:** com.google.fonts/check/name/familyname_first_char
  - **[com.google.fonts/check/068]:** com.google.fonts/check/name/match_familyname_fullfont
  - **[com.google.fonts/check/069]:** com.google.fonts/check/glyf_unused_data
  - **[com.google.fonts/check/070]:** com.google.fonts/check/currency_chars
  - **[com.google.fonts/check/071]:** com.google.fonts/check/family_naming_recommendations
  - **[com.google.fonts/check/072]:** com.google.fonts/check/smart_dropout
  - **[com.google.fonts/check/073]:** com.google.fonts/check/maxadvancewidth
  - **[com.google.fonts/check/074]:** com.google.fonts/check/name/ascii_only_entries
  - **[com.google.fonts/check/075]:** com.google.fonts/check/points_out_of_bounds
  - **[com.google.fonts/check/077]:** com.google.fonts/check/all_glyphs_have_codepoints
  - **[com.google.fonts/check/078]:** com.google.fonts/check/glyphnames_max_length
  - **[com.google.fonts/check/079]:** com.google.fonts/check/monospace_max_advancewidth
  - **[com.google.fonts/check/082]:** com.google.fonts/check/metadata/profiles_csv
  - **[com.google.fonts/check/083]:** com.google.fonts/check/metadata_unique_full_name_values
  - **[com.google.fonts/check/084]:** com.google.fonts/check/metadata/unique_weight_style_pairs
  - **[com.google.fonts/check/085]:** com.google.fonts/check/metadata/license
  - **[com.google.fonts/check/086]:** com.google.fonts/check/metadata/menu_and_latin
  - **[com.google.fonts/check/087]:** com.google.fonts/check/metadata/subsets_order
  - **[com.google.fonts/check/088]:** com.google.fonts/check/metadata/copyright
  - **[com.google.fonts/check/089]:** com.google.fonts/check/metadata/familyname
  - **[com.google.fonts/check/090]:** com.google.fonts/check/metadata/has_regular
  - **[com.google.fonts/check/091]:** com.google.fonts/check/metadata/regular_is_400
  - **[com.google.fonts/check/092]:** com.google.fonts/check/metadata/nameid/family_name
  - **[com.google.fonts/check/093]:** com.google.fonts/check/metadata/nameid/post_script_name
  - **[com.google.fonts/check/094]:** com.google.fonts/check/metadata/nameid/full_name
  - **[com.google.fonts/check/095]:** com.google.fonts/check/metadata/nameid/font_name
  - **[com.google.fonts/check/096]:** com.google.fonts/check/metadata/match_fullname_postscript
  - **[com.google.fonts/check/097]:** com.google.fonts/check/metadata/match_filename_postscript
  - **[com.google.fonts/check/098]:** com.google.fonts/check/metadata/valid_name_values
  - **[com.google.fonts/check/099]:** com.google.fonts/check/metadata/valid_full_name_values
  - **[com.google.fonts/check/100]:** com.google.fonts/check/metadata/valid_filename_values
  - **[com.google.fonts/check/101]:** com.google.fonts/check/metadata/valid_post_script_name_values
  - **[com.google.fonts/check/102]:** com.google.fonts/check/metadata/valid_copyright
  - **[com.google.fonts/check/103]:** com.google.fonts/check/metadata/reserved_font_name
  - **[com.google.fonts/check/104]:** com.google.fonts/check/metadata/copyright_max_length
  - **[com.google.fonts/check/105]:** com.google.fonts/check/metadata/canonical_filename
  - **[com.google.fonts/check/106]:** com.google.fonts/check/metadata/italic_style
  - **[com.google.fonts/check/107]:** com.google.fonts/check/metadata/normal_style
  - **[com.google.fonts/check/108]:** com.google.fonts/check/metadata/nameid/family_and_full_names
  - **[com.google.fonts/check/109]:** com.google.fonts/check/metadata/fontname_not_camel_cased
  - **[com.google.fonts/check/110]:** com.google.fonts/check/metadata/match_name_familyname
  - **[com.google.fonts/check/111]:** com.google.fonts/check/metadata/canonical_weight_value
  - **[com.google.fonts/check/112]:** com.google.fonts/check/metadata/os2_weightclass
  - **[com.google.fonts/check/113]:** com.google.fonts/check/metadata/match_weight_postscript
  - **[com.google.fonts/check/115]:** com.google.fonts/check/metatada/canonical_style_names
  - **[com.google.fonts/check/116]:** com.google.fonts/check/unitsperem_strict
  - **[com.google.fonts/check/117]:** com.google.fonts/check/version_bump
  - **[com.google.fonts/check/118]:** com.google.fonts/check/production_glyphs_similarity
  - **[com.google.fonts/check/129]:** com.google.fonts/check/fsselection
  - **[com.google.fonts/check/130]:** com.google.fonts/check/italic_angle
  - **[com.google.fonts/check/131]:** com.google.fonts/check/mac_style
  - **[com.google.fonts/check/152]:** com.google.fonts/check/reserved_font_name
  - **[com.google.fonts/check/153]:** com.google.fonts/check/contour_count
  - **[com.google.fonts/check/154]:** com.google.fonts/check/production_encoded_glyphs
  - **[com.google.fonts/check/155]:** com.google.fonts/check/metadata_nameid_copyright
  - **[com.google.fonts/check/156]:** com.google.fonts/check/name/mandatory_entries
  - **[com.google.fonts/check/157]:** com.google.fonts/check/name/familyname
  - **[com.google.fonts/check/158]:** com.google.fonts/check/name/subfamilyname
  - **[com.google.fonts/check/159]:** com.google.fonts/check/name/fullfontname
  - **[com.google.fonts/check/160]:** com.google.fonts/check/name/postscriptname
  - **[com.google.fonts/check/161]:** com.google.fonts/check/name/typographicfamilyname
  - **[com.google.fonts/check/162]:** com.google.fonts/check/name/typographicsubfamilyname
  - **[com.google.fonts/check/163]:** com.google.fonts/check/name/family_and_style_max_length
  - **[com.google.fonts/check/164]:** com.google.fonts/check/name/copyright_length
  - **[com.google.fonts/check/165]:** com.google.fonts/check/fontdata_namecheck
  - **[com.google.fonts/check/166]:** com.google.fonts/check/fontv
  - **[com.google.fonts/check/167]:** com.google.fonts/check/varfont/regular_wght_coord
  - **[com.google.fonts/check/168]:** com.google.fonts/check/varfont/regular_wdth_coord
  - **[com.google.fonts/check/169]:** com.google.fonts/check/varfont/regular_slnt_coord
  - **[com.google.fonts/check/170]:** com.google.fonts/check/varfont/regular_ital_coord
  - **[com.google.fonts/check/171]:** com.google.fonts/check/varfont/regular_opsz_coord
  - **[com.google.fonts/check/172]:** com.google.fonts/check/varfont/bold_wght_coord
  - **[com.google.fonts/check/173]:** com.google.fonts/check/negative_advance_width
  - **[com.google.fonts/check/174]:** com.google.fonts/check/varfont/generate_static
  - **[com.google.fonts/check/180]:** com.google.fonts/check/loca/maxp_num_glyphs


## 0.6.12 (2019-Mar-11)
### Bug fixes
  - Fix bug in which a singular ttFont condition causes a family-wide (ttFonts) check to be executed once per font. (issue #2370)
  - **[com.google.fonts/check/079]:** Fixed bug in which this check was not confirming that font seemed monospaced before reporting different advance widths. (PR #2368, part of issue #2366)
  - Protect condition ttfautohint_stats against non-ttf fonts (issue #2385)
  - **[com.google/fonts/check/040]:** Cap accepted winDescent and winAscent values. Both should be less than double their respective bounding box values.

### New features
  - We now have an Adobe collection of checks (specification). It will include more checks in future releases. (PR #2369)
  - The `FontSpec` class now has a `get_family_checks()` method that returns a list of family-level checks. (PR #2380)

### New checks
  - **[com.adobe.fonts/check/bold_italic_unique_for_nameid1]:** "OS/2.fsSelection bold & italic are unique for each NameID1" (PR #2388)
  - **[com.adobe.fonts/check/fsselection_matches_macstyle]:**  "OS/2.fsSelection and head.macStyle bold and italic bits match." (PR #2382)
  - **[com.adobe.fonts/check/max_4_fonts_per_family_name]:**  "Each group of fonts with same nameID 1 has maximum of 4 fonts." (PR #2372)
  - **[com.adobe.fonts/check/consistent_upm]:**  "Fonts have consistent units per em." (PR #2372)
  - **[com.adobe.fonts/check/name_empty_records]:** "Check 'name' table for empty records." (PR #2369)


## 0.6.11 (2019-Feb-18)
### Documentation
  - Update maintainer notes so that we do not forget to update the cache of vendor ids list. (issue #2359)

### New checks
  - **[com.google.fonts/check/integer_ppem_if_hinted]:** "PPEM must be an integer on hinted fonts." (issue #2338)

### New conditions
  - **[is_hinted]:** allows restricting certain checks to only run on hinted fonts. Detection is based on the presence of an "fpgm" (Font Program) table.

### Bugfixes
  - **[fontbakery.utils.download_file]:** Fix error message when ssl certificates are not installed. (issue #2346)
  - **[fontbakery.specifications.shared_conditions]:** Determine whether a font is monospaced by analysing the ascii character set only. (issue #2202)
  - **[fontbakery.specifications.googlefonts.registered_vendor_ids]:** Update cache of vendor ID list from Microsoft's website. (issue #2359)

### new Code-tests
  - **[registered_vendor_ids condition]:** Make sure several corner cases are properly parsed. This includes ensuring that vendor IDs lacking a URL are properly handled. (issue #2359)


## 0.6.10 (2019-Feb-11)
### Documentation
  - The documentation was updated incorporating an article that was originally presented at the 9ET conference in Portugal in the end of 2018. The article gives a detailed overview of the goals of the Font Bakery project.

### Bugfixes
  - **[fontbakery.utils.download_file]:** Printing a message with a hint of a possible fix to "SSL bad certificate" when trying to download files. (issue #2274)

### Deprecated checks
  - **[com.google.fonts/check/076]:** "unique unicode codepoints" - This check seemd impossible to FAIL! (issue #2324)

### Dependencies (concrete deps on requirements.txt)
  - **[fontTools]:** upgraded to 3.37.0

### new Code-tests
  - Code-coverage: 63% (same as on v0.6.9)
  - **[com.google.fonts/check/has_ttfautohint_params]:** (issue #2312)
  - **[com.google.fonts/check/077]:** "all glyphs have codepoints" - I am unaware of any font that actually FAILs this check, though... (issue #2325)


## 0.6.9 (2019-Feb-04)
### Bugfixes
  - **[com.google.fonts/check/034]:** fix explanation of xAvgWidth on WARN/INFO messages. (issue #2285)

### Other code changes
  - Adopting python type hint notation.


## 0.6.8 (2019-Jan-28)
### Bugfixes ###
  - **[FontBakeryCondition:licenses]:** Do not crash when font project is not in a git repo (issue #2296)


## 0.6.7 (2019-Jan-21)
### New checks
  - **[com.google.fonts/check/tnum_horizontal_metrics]:** "All tabular figures must have the same width across the whole family." (issue #2278)

### Changes to existing checks
  - **[com.google.fonts/check/056]:** Require ttfautohint. Emit an ERROR when it is not properly installed in the system. (issue #1851)
  - **[com.google.fonts/check/092 & 108]:** Use *Typographic Family Name* instead of *Font Family Name* if it exists in the font's name table.

### Deprecated checks
  - **[com.google.fonts/check/119]:** "TTFAutohint x-height increase value is same as in previous release on Google Fonts?". Marc Foley said: "Since we now have visual diffing, I would like to remove it. This test is also bunk because ttfautohint's results are not consistent when they update it." (issue #2280)

### Other code changes
  - Added more valid options of contour count values for Oslash and f_f_i glyphs (issue #1851)
  - The HTML reporter now places the percentages summary before the check details.
  - updated dependencies on setup.py and requirements.txt to make sure we ship exactly what we test during development (issue #2174)


## 0.6.6 (2018-Dec-20)
### New Checks
  - **[com.google.fonts/check/wght_valid_range]:** Weight axis coordinate must be within spec range of 1 to 1000 on all instances. (issue #2264)

### Bugfixes
  - fixed the checkID variable in our ghmarkdown reporter (the f-string syntax was broken)

### Changes to existing checks
  - **[com.google.fonts/check/153]:** Disable "expected contour count" check for variable fonts. There's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts. (issue #2262)
  - **[com.google.fonts/check/046]:** Removed restriction on CFF2 fonts because the helper method `glyph_has_ink` now handles `CFF2`.
  - **[com.google.fonts/check/049]:** Removed restriction on CFF2 fonts because the helper method `glyph_has_ink` now handles `CFF2`.


## 0.6.5 (2018-Dec-10)
### New Checks
  - **[com.google.fonts/check/metadata/parses]:** "Check METADATA.pb parse correctly." (issue #2248)
  - **[com.google.fonts/check/fvar_name_entries]:** "All name entries referenced by fvar instances exist on the name table?" (issue #2069)
  - **[com.google.fonts/check/varfont_has_instances]:** "A variable font must have named instances." (issue #2127)
  - **[com.google.fonts/check/varfont_weight_instances]:** "Variable font weight coordinates must be multiples of 100." (issue #2258)

### Bug fixes
  - **[com.google.fonts/check/054]:** Correct math in report of font file size change by properly converting result to a percentage.
  - **[com.google.fonts/check/100]:** Fix check that would never FAIL. Now it runs correctly. (issue #1836)

### Changes to existing checks
  - **[com.google.fonts/check/046]:** Removed restriction on CFF fonts (and added restriction on CFF2 pending a fonttools bug fix) because the helper method `glyph_has_ink` now handles `CFF` as well as `glyf`.
  - **[com.google.fonts/check/049]:** Removed restriction on CFF fonts (and added restriction on CFF2 pending a fonttools bug fix) because the helper method `glyph_has_ink` now handles `CFF` as well as `glyf`.


## 0.6.4 (2018-Dec-03)
### New Features
  - Nikolaus Waxweiler has contributed an HTML reporter. It can be used by passing -html filename.html to the command line. Thanks a lot!

### New checks
  - **[com.abobe.fonts/check/postscript_name_cff_vs_name]:** CFF table FontName must match name table ID 6 (PostScript name). (PR #2229)

### Bug fixes
  - **[com.google.fonts/check/011]:** Safeguard against reporting style=`None` by only running the check when all font files are named canonically. (issue #2196)
  - **[com.google.fonts/check/065]:** Fix AttributeError: 'int' object has no attribute 'items'. (issue #2203)
  - **[FontBakeryCondition:remote_styles]:** fix UnboundLocalError. local variable 'remote_style' was referenced before assignment. (issue #2204)

### Changes to existing checks
  - **[com.google.fonts/check/011]:** List which glyphs differ among font files (issue #2196)
  - **[com.google.fonts/check/043]:** unitsPerEm check on OpenType profile is now less opinionated. Only FAILs when strictly invalid according to the spec. (issue #2185)
  - **[com.google.fonts/check/116]:** Implement stricter criteria for the values of unitsPerEm on Google Fonts. (issue #2185)

### Other relevant code changes
  - **[setup.py]:** display README.md as long-description on PyPI webpage. (issue #2225)
  - **[README.md]:** mention our new developer chat channel at https://gitter.im/fontbakery/Lobby
  - **[Dependencies]:** The following 2 modules are actually needed by fontTools: fs and unicodedata2.


## 0.6.3 (2018-Nov-26)
### Bug fixes
  - **[GHMarkdown output]:** PR #2167 (__str__ for Section and Check) was reverted because it was causing the ghmarkdown output to crash. We may get back to it later, but being more careful about the side effects of it. (issue #2194)
  - **[com.google.fonts/check/028]:** Also search for a license file on the git-repo rootdir if the font project is in a repo. (issue #2087)
  - **[com.google.fonts/check/062]:** fix a typo leading to a bad string formatting syntax crash. (issue #2183)
  - **[code-test: check/154]:** Fixed the code-test and made it safer under eventual conectivity issues. (issue #1712)

### Changes to existing checks
  - **[com.google.fonts/check/ttx_roundtrip]:** Improved the FAIL message to give the users a hint about what could have gone wrong. The most likely reason is a shortcoming on fonttools that makes TTX generate corrupt XML files when dealing with contol code chars in the name table. (issue #2212)
  - **[com.google.fonts/check/001]:** Accept variable font filenames with Roman/Italic suffixes (issue #2214)
  - **[com.google.fonts/check/034]:** Downgrade xAvgWidth check from FAIL to WARN since sometimes it diverges from GlyphsApp. Also, it seems that the value is not actually used on relevant programs. I still want to clarify what's going on with GlyphsApp calculations of this value. Once that's figured out, we may redefine the severity of the check once again. (issue #2095)
  - **[com.google.fonts/check/097]:** Accept variable font filenames with Roman/Italic suffixes (issue #2214)
  - **[com.google.fonts/check/102]:** Check for consistency of copyright notice strings on both METADATA.pb and on name table entries. (issue #2210)
  - **[com.google.fonts/check/105]:** Accept variable font filenames with Roman/Italic suffixes (issue #2214)


## 0.6.2 (2018-Nov-19)
### New checks
  - **[com.google.fonts/check/ftxvalidator_is_available]:** Detects whether the ftxvalidator is installed on the system or not.

### Bug fixes
  - **[com.google.fonts/check/098]:** In some cases the check did not yield any result. (issue #2206)
  - **[com.google.fonts/check/ttx_roundtrip]:** Delete temporary XML that is generated by the TTX round-tripping check. (issue #2193)
  - **[com.google.fonts/check/119]:** Fix `'msg'` referenced before assignment (issue #2201)

### Changes to existing checks
  - **[com.google.fonts/check/130]:** update italic angle check with "over -30 degrees" FAIL and "over -20 degrees" WARN (#2197)
  - **[com.google.fonts/check/ttx_roundtrip]:** Emit a FAIL when TTX roundtripping results in a parsing error (ExpatError) since a malformed XML most likely means an issue with the font. (issue #2205)


## 0.6.1 (2018-Nov-11)
### New checks
  - **['com.google.fonts/check/aat']:** "Are there unwanted Apple tables?" (PR #2190)

### Bug fixes
  - **[com.google.fonts/check/fontbakery_version]:** Fix crash
  - **[com.google.fonts/check/153]:** Fix expected contour count for glyphs zerowidthjoiner(uni200D) and zerowidthnonjoiner(uni200C) from 1 to 0

### Changes to existing checks
  - **[com.google.fonts/check/053]**: Clarify unwanted tables


## 0.6.0 (2018-Nov-08)
### Noteworthy changes
  - Now we have our documentation hosted at https://font-bakery.readthedocs.io/
  - Limit ammount of details printed by fontval checks and group fontval checks to make their data more readable.
  - Print Font Bakery version on the header of Markdown reports, so that we know if a report was generated with an old version. (issue #2133)
  - Add 'axes' field to protocol-buffer schema
  - moving FontVal wrapper to a separate spec (issue #2169)
  - Added a CODE_OF_CONDUCT.md

### new checks
  - **[com.google.fonts/check/vttclean]:** There must not be VTT Talk sources in the font. (issue #2059)
  - **[com.google.fonts/check/varfont/has_HVAR]:** Var Fonts have HVAR table to avoid costly text-layout operations on some platforms. (issue #2119)
  - **[com.google.fonts/check/varfont/has_MVAR] (but temporarily disabled):** Var Fonts must have an MVAR table layout-software depend on it. (issue #2118)
  - **[com.google.fonts/check/fontbakery_version]:** A new 'meta' check to ensure Font Bakery is up-to-date so that we avoid relying on out-dated checking routines. (issue #2093)

### modifications to existing checks
  - Correct the error message for the check for identical glyph names. Avialable and missing style names were swapped.
  - Mute FVal E5200 (based on outdated OT spec) for var fonts. (issue #2109)
  - FontVal outline intersection checks should not run for VF. Variable Fonts typically have lots of intersecting contours and components.
  - Adopt FVal W0022 rationale for com.google.fonts/check/052 and disable this FontVal check as it is already covered by check/052 routines.
  - disable FVal check W0020: "Tables are not in optimal order" (fixes issue #2105)
  - Improve rationale for com.google.fonts/check/058
  - check/158: use Message obj to differentiate kinds of FAILs (issue #1974)
  - check/158: test the PASS scenarios for full 18-style family (issue #1974)
  - factor out "style_with_spaces" as a condition. (issue #1974)
  - test FAIL "invalid-entry" on check/158 (issue #1974)
  - test FAIL "bad-familyname" on check/158 (issue #1974)
  - Disable FontVal E4012 (GDEF header v1.3 not yet recognized) (issue #2131)
  - skip check/072 if font is VTT hinted (issue #2139)
  - do not run check/046 on CFF fonts because the helper method `glyph_has_ink` directly references `glyf`. In the future we may refactor it to also deal with CFF fonts. (issue #1994)
  - com.google.fonts/check/018: Downgrade archVendID to WARN
  - com.google.fonts/check/042: Add rationale. (issue #2157)

### Much more funky details...
  This is just a copy of several git log messages. Ideally I shuld clean these up for the sake of clarity...
  - ufo_sources: put existing checks into own section. Using the section name in reports requires using sensible section names.
  - [snippets] fontbakery-check-upstream.py added. This script will allow users to run fontbakery on an upstream github repository. The user has to provide the repo url and the directory containing the ttfs.
  - add code-test and bugfix check/162. Now the check ensures no ribbi font has a nameID=17 and all non-ribbi fonts have it and that it has a correct value. If any of the above is not true, the check emits a FAIL. (issue #1974)
  - add code-test and bugfix check/161. Now the check ensures no ribbi font has a nameID=16 and all non-ribbi fonts have it and that it has a correct value. If any of the above is not true, the check emits a FAIL. (issue #1974)
  - Bump up requests version to mitigate CVE
  - [googlefonts.py] modify ttfa param testing string literal. See https://github.com/googlefonts/fontbakery/pull/2116#issuecomment-431725719
  - Do not check the ttfautohint params if font is not hinted. Skip the com.google.fonts/check/has_ttfautohint_params test if the font is not hinted using ttfautohint
  - fix implementation of blocklisting of FontVal checks (follow up for PRs #2102 and #2104)
  - Add comments to fontval check downgrades and silencing and also fix the implementation of silencing them. (issue #2102)
  - com.google.fonts/check/037: Downgrade missing Mac name table records to warn. Fontmake does not generate mac name table records. Apparently, they're not needed, https://github.com/googlei18n/fontmake/issues/414
  - Decode ufolint output for better text display
  - Remove unnecessary dependencies. Custom Freetype no longer needed because we use Hintak's latest binaries for Ms Font Validator.
  - com.google.fonts/check/037: Simplify Ms Font Val subprocess call. In Windows, a .exe can be run without specifying the .exe extension. Therefore all three platforms can run FontValidator using the same call.
  - travis: Download and install Ms FontValidator
  - Raise NotImplementedError if user's system is not Unix based or Win
  - Run FontValidator.exe if user's OS is Win
  - Improve Font Validator installation and install instructions
    - Removed prebuilt FontVal. Use Hintak's binaries instead.
    - Drop render tests. Diffbrowsers should be used.
    - Added instructions for MAC and GNU Linux
  - [prebuilt] remove ots-sanitize binary. Transitioned to opentype-sanitizer in #2092
  - implement code-test for com.google.fonts/check/157 and bugfix 157 and 158 (were reporting PASS even when FAILing) (issue #1974)
  - specify familyname and familyname_with_spaces as conditions to all checks that rely on those. Otherwise non-cannonical filenames could lead to fontbakery ERRORs. (issue #1974)
  - fix code-test for com.google.fonts/check/156 (issue #1974)
  - INSTALL_*.md: remove ots installation instructions, no longer needed as we install it automatically via pip now
  - general_test.py: test ots with invalid file
  - use ots.sanitize() instead of subprocess in check036
  - setup.py: add opentype-sanitizer to install_requires
  - fix check/028 & add a test for family_directory condition. Now a license file on the current working directory is properly detected. (issue #2087)
  - Remove printing of number of checks in sections
  - Remove Python 2 compatibility remnant
  - check_specification: Use CheckRunner directly instead of runner_factory
  - Add check in/exclude test for no in/excluding
  - Python 3 does not need explicit derivation from object
  - improving the comments in code-test/008 so that it can be used as a didactic example of the purpose of code-tests.
  - Avoid private attribute in test
  - Add test for check selection
  - Make in/exclude check parameters fuzzy
  - Only ignore deprecation warnings from (from|to)string
  - Mute deprecation warnings. Temporarily solves issue #2079
  - Add tests for loading specifications without errors
  - Move vtt_talk_sources to shared conditions
  - PriorityLevel enum (issue #2071)
  - remove PLATID_STR and NAMEID_STR as now those strings can be directly infered from the corresponding enum entries. Thanks for the tip, Nikolaus Waxweiler! (issue #2071)
  - MacStyle and FsSelection enums (issue #2071)
  - PANOSE_Proportion and IsFixedWidth enums (issue #2071)
  - PlatformID and *EncondingID enums (issue #2071)
  - using an enum for the NameIDs (issue #2071)
  - print messages telling the user where JSON and Markdown reports were saved to. (issue #2050)
  - Add code-tests to ttx roundtrip check and fix issue #2048 by not checking ttx roundtripping on fonts that did not yet have VTT Talk sources cleaned out of its TSI* tables (this should always be done prior to release).
  - Add `__main__` entry point. Makes it possible to run fontbakery from `python -m fontbakery`. Useful if Python script path not in PATH.
  - Skip TTF-only checks for OTF fonts (issue #2040)
  - bump up fontTools version requirement due to our usage of the getBestCmap method. (issue #2043)
  - [specifications/googlefonts] condition github_gfonts_ttFont it is LICENSE.txt for apache
  - [specifications/googlefonts] condition registered_vendor_ids open file as utf-8
  - [specifications/general] fix condition fontforge_check_results for python3 usage (bytes to string)
  - [INSTALL.md] added removal steps for ots zip archive file and archive directory
  - [INSTALL.md] modify ots-sanitize installation approach (issue #2041)


## 0.5.1 (2018-Aug-31)
This release-cycle focused on addressing the issues brought up by attendees at the MFDOS - Multiple Font Distributors Onboarding Summit- an event organized by Dave Crossland during TypeCon 2018 in Portland, Oregon.

More info on MFDOS is available at: https://github.com/davelab6/mfdos

### Release highlights & new features / noteworthy bugfixes
  - Added a --version command line switch.
  - We're now using ttfautohint-py to ensure users always run the latest available version.
  - **[BUGFIX]:** Only run regression checks if family is on GF (There was a bug in the implementation that was causing HTTP Errors since it was attempting to fetch the files even though they're not listed on the gfonts API).
  - **[BUGFIX]:** Access kern data and ligatures by looking up features in order to find the correct Lookup entries with the data. Previous implentation was buggy because it included all lookups regardless of whether they were referenced by the specific features or not, resulting in non-sensical FAIL messages in the caret-positioning and ligature related checks.
  - **[INSTALL.md]:** include macOS >= 10.13 for ftxvalidator install docs.

### New dependencies
  - **ttfautohint-py** from PyPI

### deprecated dependencies
  - A system-wide install of ttfautohint is not needed anymore. The ttfautohint-py package from PyPI includes its own ttfautohint together with the python wrapper.

### New checks
  - **[com.google.fonts/check/has_ttfautohint_params]:** "Font has ttfautohint parameters." (issue #1773)

### Deprecated checks:
  - **[com.google.fonts/check/080]** METADATA.pb: Ensure designer simple short name.

### Changes to existing checks
  - **[com.google.fonts/check/044]:** Split code-test and check_parse_version_string function.
  - **[com.google.fonts/check/044]:** Accept rounding fontRevision due to bad interpretations of float values causing false-FAILs (such as 1.001 being interpreted as 1.00099).
  - **[com.google.fonts/check/054]:** Simplified ttfautohint-related checks and implemented their code-tests
  - **[com.google.fonts/check/056]:** Simplified ttfautohint-related checks and implemented their code-tests
  - **[com.google.fonts/check/058]:** Add .ttfautohint glyph to valid glyphs.
  - **[com.google.fonts/check/062]:** Improved verbosity of the gasp-table check
  - **[com.google.fonts/check/062]:** Do not fail or error on absence of 'gasp' table if font contains a 'CFF' or 'CFF2' table.
  - **[com.google.fonts/check/064]:** Fixed buggy implementations of ligatures and caret positions checks.
  - **[com.google.fonts/check/065]:** Fixed buggy implementations of ligatures and caret positions checks.
  - **[com.google.fonts/check/153]:** Do not fail or error on absence of 'glyf' table if font contains a 'CFF' or 'CFF2' table.
  - **[com.google.fonts/check/153]:** Fix typos: change "counters" to "contours".
  - **[com.google.fonts/check/155]:** Added K2D as yet another familyname "camelcase" exception
  - **[com.google.fonts/check/180]:** Do not fail or error on absence of 'loca' table if font contains a 'CFF' or 'CFF2' table.

### Code-Test coverage
  - We currently have code-tests covering 59% of Font Bakery's codebase.


## 0.5.0 (2018-Jul-31)
### Release highlights & new features
  - focused on overall bugfixing and improving codebase test-coverage.
  - first Python 3-only release.
  - We've got a cupcake ASCII art by Tony de Marco! Cheers!!!

### New checks
  - **[com.google.fonts/check/ttx_roundtrip]:** Make sure the font roundtrips nicely on the TTX tool (issue #1763)

### Changes to existing checks
  - **[com.google.fonts/check/001]:** Added support for canonical variable font filenames
  - **[com.google.fonts/check/018]:** Update cached vendor list from microsoft
  - **[com.google.fonts/check/020]:** Move it entirely to GFonts spec and simplify the code
  - **[com.google.fonts/check/032]:** Moved to specs/googlefonts.py
                                      - updating max-length for description name entries
  - **[com.google.fonts/check/035]:** Update plist module API used
  - **[com.google.fonts/check/038]:** fontforge check (038) must only emit WARNs
  - **[com.google.fonts/check/039]:** Custom override of fontforge failure results
  - **[com.google.fonts/check/040]:** Moved to specs/googlefonts.py
  - **[com.google.fonts/check/042]:** Moved to specs/googlefonts.py
  - **[com.google.fonts/check/046]:** Only check for .notdef glyph. Previously, the OpenType spec recommended .notdef, .null, CR and space as the first four glyphs, but OpenType v1.8.0 specification removed this, .notdef is now the only recommended glyph
  - **[com.google.fonts/check/071]:** Remove "usWeight is multiple of 50" checking routine. This should focus on checking strings on the name table
  - **[com.google.fonts/check/072]:** Now emits FAILs instead of WARNs.
                                      - Moved to specs/googlefonts.py
  - **[com.google.fonts/check/090]:** bugfix (it was completely broken)

### Noteworthy bugfixes
  - fix serializer crash on py3 when using check clustering
  - decode subprocess output (fixes python3 crash on check/054)
  - fix py3 crash on check/056 The map func changed on Python 3
  - downgrade a few fval checks from FAIL to WARN
  - fix crash on checks 117 & 154 related to py3 BytesIO usage

### Code-Test coverage
  - We currently have code-tests covering 59% of Font Bakery's codebase.


## 0.4.1 (2018-May-30)
### Release highlights & new features
  - Added shorthand for running checks on the opentype specification with `fontbakery check-opentype`.
  - Added `--exclude-checkid` argument (the opposite of `--checkid`).
  - Improvements to Windows support:
    - Disable color output and progress bar on Windows by default since
      the default Windows terminal doesn't cope too well with either.
    - Also disable the progressbar on Windows.
    - And, for that reason, `--no-progress` and `--no-colors` arguments
      are not recognized anymore on Windows.
  - [checkrunner] rename `check_filter` into `check_skip_filter`, make it into a property.
  - [checkrunner] spec_imports: Try to import names as submodules if they are not attributes.

### Changes to existing checks
  - **[com.google.fonts/check/044]:** Fixed the parsing of fontRevision on the 'head' table.

### Code-Test coverage
  - We currently have code-tests covering 55% of Font Bakery's codebase.

### Miscelaneous code changes & bugfixes
  - improvements to GHMarkdown output:
    - filter the log messages within checks as well, instead of only their final status.
    - and also order them and display the emojis.
    - omit family checks section if empty (no results to display).
  - fix GHMarkdown reporter when using clustered checks (issue #1870).
  - Added loca table tests to the opentype specification.
  - General improvements to the checkrunner infrastructure.


## 0.4.0 (2018-May-16)
### Thanks!
  - Thanks a lot to all new/recent code contributors:
    - **Chris Simpkins** (`@chrissimpkins`), Source Foundry
    - **Nikolaus Waxweiler** (`@madig`), Dalton Maag
    - **Jens Kutilek** (`@jenskutilek`), https://www.kutilek.de/

### Release highlights & new features
  - First release supporting both `Python 2` and `Python 3` interpreters.
  - Automated linting and code-testing on Travis for both interpreters using tox.
  - Initial support for checking UFO sources.
  - Added a `--ghmarkdown` CLI option to output reports in GitHub Markdown format, ideal for submitting font-family pull-requests.
  - Added a `--show-sections` option to enable the printing of partial per-section check results summaries (see issue #1781).
  - Added generation of coverage reports on Travis as well, in order to aim at 100% test coverage.
  - Checks are now split and reorganized in category groupings (called "specifications" in FontBakery jargon).
  - Examples of these specifications include:
    - **(i)** generic OpenType spec checks
    - **(ii)** Google Fonts specific checks
    - and **(iii)** checks focused on aspects of individual OpenType tables
    - as well as the aforementioned **(iv)** checks for UFO sources.
  - Lasse Fister (`@graphicore`) improved the check-runner to enable easier customization of specs, with tools to remove boilerplate
    from specifications and to make maintenance easier. He also wrote technical documentation
    (available at https://github.com/googlefonts/fontbakery/blob/main/docs/writing-specifications.md)
    describing how to create Font Bakery specs with a customized set of checks.

### Code-Test coverage
  - We currently have code-tests covering 55% of Font Bakery's codebase.

### New checks
  - **[com.daltonmaag/check/ufolint]:** "Run ufolint on UFO source directory."

  - **[com.daltonmaag/check/ufo_required_fields]:** "Check that required fields are present in the UFO fontinfo.
                                                    - ufo2ft requires these info fields to compile a font binary:
                                                      unitsPerEm, ascender, descender, xHeight, capHeight and familyName."

  - **[com.daltonmaag/check/ufo_recommended_fields]:** "Check that recommended fields are present in the UFO fontinfo.
                                                       - This includes fields that should be in any production font."

  - **[com.daltonmaag/check/ufo_unnecessary_fields]:** "Check that no unnecessary fields are present in the UFO fontinfo.
                                                       - ufo2ft will generate these.
                                                       - openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted
                                                         because it is useful to toggle a range when not _all_ the glyphs
                                                         in that region are present.
                                                       - year is deprecated since UFO v2."

  - **[com.google.fonts/check/167]:** "The variable font 'wght' (Weight) axis coordinate
                                       must be 400 on the 'Regular' instance:
                                       - If a variable font has a 'wght' (Weight) axis,
                                         then the coordinate of its 'Regular' instance
                                         is required to be 400."

  - **[com.google.fonts/check/168]:** "The variable font 'wdth' (Width) axis coordinate
                                       must be 100 on the 'Regular' instance:
                                       - If a variable font has a 'wdth' (Width) axis,
                                         then the coordinate of its 'Regular' instance
                                         is required to be 100."

  - **[com.google.fonts/check/169]:** "The variable font 'slnt' (Slant) axis coordinate
                                       must be zero on the 'Regular' instance:
                                       - If a variable font has a 'slnt' (Slant) axis,
                                         then the coordinate of its 'Regular' instance
                                         is required to be zero."

  - **[com.google.fonts/check/170]:** "The variable font 'ital' (Italic) axis coordinate
                                       must be zero on the 'Regular' instance:
                                       - If a variable font has a 'ital' (Italic) axis,
                                         then the coordinate of its 'Regular' instance
                                         is required to be zero."

  - **[com.google.fonts/check/171]:** "The variable font 'opsz' (Optical Size) axis coordinate
                                       should be between 9 and 13 on the 'Regular' instance:
                                       - If a variable font has a 'opsz' (Optical Size) axis,
                                         then the coordinate of its 'Regular' instance
                                         is recommended to be a value in the range 9 to 13."

  - **[com.google.fonts/check/172]:** "The variable font 'wght' (Weight) axis coordinate
                                       must be 700 on the 'Bold' instance:
                                       - The Open-Type spec's registered design-variation tag 'wght'
                                         does not specify a required value for the 'Bold' instance
                                         of a variable font. But Dave Crossland suggested that
                                         we should enforce a required value of 700 in this case."

  - **[com.google.fonts/check/173]:** "Check that advance widths cannot be inferred as negative:
                                       - Advance width values in the Horizontal Metrics (htmx)
                                         table cannot be negative since they are encoded as unsigned
                                         16-bit values. But some programs may infer and report
                                         a negative advance by looking up the x-coordinates of
                                         the glyphs directly on the glyf table.
                                       - There are reports of broken versions of Glyphs.app causing
                                         this kind of problem as reported at
                                         https://github.com/googlefonts/fontbakery/issues/1720 and
                                         https://github.com/fonttools/fonttools/pull/1198
                                       - This check detects and reports such malformed
                                         glyf table entries."
                                       (**Note:** New but disabled - See details below)

  - **[com.google.fonts/check/174]:** "Check a static ttf can be generated from a variable font:
                                       - Google Fonts may serve static fonts which have been
                                         generated from variable fonts.
                                       - This test will attempt to generate a static ttf using
                                         fontTool's varLib mutator."

### Changes to existing checks
  - **[com.google.fonts/check/008]:** Add rationale metadata &
                                      List diverging underlineThickness values across a family.
  - **[com.google.fonts/check/011]:** Display divergence on num of glyphs for all styles.
  - **[com.google.fonts/check/012]:** Verbose listing of glyphnames mismatches across families.
  - **[com.google.fonts/check/018]:** Do not require identical vendorid & manufacturer names anymore.
  - **[com.google.fonts/check/030]:** Accept Ubuntu Font License for legacy families.
  - **[com.google.fonts/check/037]:** Remove fval.xsl file after running FontValidator &
                                      FontVal may not create a HTML report, so test for it before removing it.
  - **[com.google.fonts/check/052]:** Reimplementation / Make STAT only required for variable fonts.
  - **[com.google.fonts/check/053]:** Add TSI5 table (VTT or VOLT) as unwanted
  - **[com.google.fonts/check/055]:** Add quotes to log message to remove ambiguity.
  - **[com.google.fonts/check/058]** &
    **[com.google.fonts/check/059]:** `SKIP` when post table format is 3.0, since they contain no glyph names in that table format.
  - **[com.google.fonts/check/062]:** "Is 'gasp' table set to optimize rendering?" - Improve wording of log-messages
                                       and check-results for better clarity.
  - **[com.google.fonts/check/117]:** Check version increments also on github repo. Before we were only checking on prod servers.
  - **[com.google.fonts/check/155]:** Added IBM Plex fonts to the list of exceptions of family names with spaces.
  - **[com.google.fonts/check/165]** &
    **[com.google.fonts/check/166]:** Refactoring of code dealing with font versioning (using font-v dependency).

### Deprecated checks
  - **[com.google.fonts/check/060]:** "No glyph is incorrectly named?"
                                      - The problem is already properly identified by other checks:
                                        (com.google.fonts/check/058 and com.google.fonts/check/059).

### Temporarily disabled checks
  - **[com.google.fonts/check/078]:** "glyph names do not exceed max length". Disabled until we figure out the rationale.
  - **[com.google.fonts/check/082]:** We currently lack a profiles.csv file on the google/fonts git repo, after
                                      https://github.com/google/fonts/commit/188dc570f6610ed1c7ea1aa7d6269a238d4c93ff
                                      (See issue #1728)
  - **[com.google.fonts/check/154]:** It was intermitently failing due to network instability. Needs to be redesigned.
  - **[com.google.fonts/check/173]:** (New but disabled) The initial implementation was bogus due to the way fonttools
                                      encodes the data into the TTF files and the new attempt at targetting the real
                                      problem is still not quite right.

### Miscelaneous code changes & bugfixes
  - Boilerplate code was added on the `tests/specifications/` directory documenting the requirements of all still
    unimplemented code-tests in the hope of inviting new contributions. Feel free to pick a few and submmit pull requests!
  - [condition familyname_with_spaces]: Added special case for handling font family names containing " of ".
  - Implemented is_ttf & is_cff conditions, as suggested by Lasse at issue #1797.
  - Improved MacOSX install instructions based on feedback from https://github.com/cadsondemak/Srisakdi/issues/5
  - Support uppercase '.TTF' extension. Probably a need due to Windows filesystem quirks...
  - Also support loading both TTF and OTF flavours for checking.
  - move all free-form miscelaneous check metadata into a generic misc_metadata field (see issue #1584)
  - Release procedures are now simplified with setuptools_scm
  - Fixed some crashes (See issues #1709, #1723, #1722)


## 0.3.4 (2017-Dec-22)
  - FB Dashboard-related improvements.
  - Added --list-checks command line switch to list all available checks
  - check/052: WebKit in MacOS 10.12 requires 'STAT' tables
  - restrict non-ASCII check to nameids 0 and 6 only
  - Adopted font-v python module as a dependency for managing font version strings
  - check/034: Changed calc of expected value for xAvgCharWidth
  - new check/166: ensure familynames are unique (query namecheck.fontdata.com)
  - Nomenclature change: font tests are now called "checks"
                         code-tests are now "tests"
  - All IDs were updated to use the "check" keyword such as "com.google.fonts/check/001"


## 0.3.3 (2017-Nov-23)
  - All auxiliary scripts have been moved into a separate python
    package called gftools (Google Fonts Tools) available at
    https://github.com/googlefonts/tools/ (source code repo on git) and at
    https://pypi.python.org/pypi/gftools (installable package on PyPI).
  - Fontbakery is now solely focused on font family automated quality checks.
  - new subcommand: list-italicangle (moved to gftools as well)
  - several bugfixes


## 0.3.2 (2017-Oct-11)
  - Increased code testing now covering a bit more than half of the Google Fonts suite of checks (more code testing to be done on upcoming releases).
  - overall refactoring of all check implementations so that they're all self-contained
  - updated prebuilt FVal binary (built from proper sources)
  - Added APIs used by the web dashboard and report documents
  - allowlist: a few legacy CamelCased familynames (check/109)
  - Added VTT-related tables to the list of unwanted tables (check/053)
  - fixed computation of font_metadata condition
  - fixed crash on fontbakery-check-font-version.py
  - added automated code tests for the fixer scripts
  - deprecated pyfontaine checks (132 to 151)
  - deprecated the unified name table entries check (check/017) spliting it up into new individual per-entry checks (156 to 162)
  - overall bugfixing / code-quality improvements.


## 0.3.1 (2017-Aug-11)
  - Emergencial release to address broken 0.3.0 packaging.
  - setup.py: Added modules that were missing in previous release
  - setup.py: Fix Windows pathnames
  - New check: com.google.fonts/check/155 ("Copyright notice name entry matches those on METADATA.pb ?")
  - Updated requirement: Changed Copyright Notice format requirement (regex) on com.google.fonts/check/102 ("METADATA.pb: Copyright notice matches canonical pattern ?")


## 0.3.0 (2017-Aug-08)
  - New modular architecture for our framework of font checks. (see: https://github.com/googlefonts/fontbakery/issues/1388)
  - A total of 120 GoogleFonts checks.
  - 44 code tests covering approximately a third of the code. (See: https://github.com/googlefonts/fontbakery/issues/1413)
  - Upstream checks were removed as out-of-scope (See: https://github.com/googlefonts/gf-glyphs-scripts).
  - Plenty of miscelanious fixes for checks; Overall improved reliability.
