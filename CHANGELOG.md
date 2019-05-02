Below are the most important changes from each release.
A more detailed list of changes is available in the corresponding milestones for each release in the Github issue tracker (https://github.com/googlefonts/fontbakery/milestones?state=closed).


## 0.7.4 (2019-May-06)
### Dependencies
  - Removed defusedxml dependency. We were only using it for its `defused.lxml` module which is now deprecated (issue #2477)

### New checks
  - **[com.google.fonts/check/metadata/designer_values]:** We must use commas instead of forward slashes because the fonts.google.com directory will segment string to list on comma and display the first item in the list as the "principal designer" and the other items as contributors.

### Bug fixes
  - **[com.google.fonts/check/name_version_format]:** Allow fonts to have version numbers less than v1.000.
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
  - The initial set of checks will be not only the full opentype profile but also those checks original included in both adobefonts and googlefonts profiles.
  - The goal is to keep the vendor-specific profiles with only the minimal set of checks that are really specific, while the shared ones are placed on the universal profile.

### New checks
  - **[com.adobe.fonts/check/cff_call_depth]:** "Is the CFF subr/gsubr call depth > 10?" (PR #2425)
  - **[com.adobe.fonts/check/cff2_call_depth]:** "Is the CFF2 subr/gsubr call depth > 10?" (PR #2425)
  - **[com.google.fonts/check/family/control_chars]:** "Are there unacceptable control characters in the font?" (PR #2430)


## 0.7.0 (2019-Mar-22)
### Major code-changes
  - The term "specification" (including directory paths, class names and method names such as Spec, FontsSpec, etc) was replaced by "profile" throughout the codebase. The reason for this renaming was to avoid confusing with other uses of the term such as is "OpenType Specification".
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
  - **[com.google.fonts/check/font_copyright]: "Copyright notices match canonical pattern in fonts"**
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
  - **[com.google.fonts/check/ttx-roundtrip]:** Improved the FAIL message to give the users a hint about what could have gone wrong. The most likely reason is a shortcoming on fonttools that makes TTX generate corrupt XML files when dealing with contol code chars in the name table. (issue #2212)
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
  - **[com.google.fonts/check/ttx-roundtrip]:** Delete temporary XML that is generated by the TTX round-tripping check. (issue #2193)
  - **[com.google.fonts/check/119]:** Fix `'msg'` referenced before assignment (issue #2201)

### Changes to existing checks
  - **[com.google.fonts/check/130]:** update italic angle check with "over -30 degrees" FAIL and "over -20 degrees" WARN (#2197)
  - **[com.google.fonts/check/ttx-roundtrip]:** Emit a FAIL when TTX roundtripping results in a parsing error (ExpatError) since a malformed XML most likely means an issue with the font. (issue #2205)


## 0.6.1 (2018-Nov-11)
### New checks
  - **['com.google.fonts/check/aat']:** "Are there unwanted Apple tables?"

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
  - com_google_fonts_check_018: Downgrade archVendID to WARN
  - com.google.fonts/check/042 Add rationale. Fixes https://github.com/googlefonts/fontbakery/issues/2157

### Much more funky details...
  This is just a copy of several git log messages. Ideally I shuld clean these up for the sake of clarity...
  - ufo_sources: put existing checks into own section. Using the section name in reports requires using sensible section names.
  - [snippets] fontbakery-check-upstream.py added. This script will allow users to run fontbakery on an upstream github repository. The user has to provide the repo url and the directory containing the ttfs.
  - add code-test and bugfix check/162. Now the check ensures no ribbi font has a nameID=17 and all non-ribbi fonts have it and that it has a correct value. If any of the above is not true, the check emits a FAIL. (issue #1974)
  - add code-test and bugfix check/161. Now the check ensures no ribbi font has a nameID=16 and all non-ribbi fonts have it and that it has a correct value. If any of the above is not true, the check emits a FAIL. (issue #1974)
  - Bump up requests version to mitigate CVE
  - [googlefonts.py] modify ttfa param testing string literal. See https://github.com/googlefonts/fontbakery/pull/2116#issuecomment-431725719
  - Do not check the ttfautohint params if font is not hinted. Skip the com.google.fonts/check/has_ttfautohint_params test if the font is not hinted using ttfautohint
  - fix implementation of blacklisting of FontVal checks (follow up for PRs #2102 and #2104)
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
  - **[com.google.fonts/check/has_ttfautohint_params]:** "Font has ttfautohint parameters."

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
  - **[com.google.fonts/check/ttx-roundtrip]:** Make sure the font roundtrips nicely on the TTX tool.

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
    (available at https://github.com/googlefonts/fontbakery/blob/master/docs/writing-specifications.md)
    describing how to create Font Bakery specs with a customized set of checks.

### Code-Test coverage
  - We currently have code-tests covering 55% of Font Bakery's codebase.

### New checks
  - **[com.daltonmaag/check/ufolint]:** "Run ufolint on UFO source directory."

  - **[com.daltonmaag/check/ufo-required-fields]:** "Check that required fields are present in the UFO fontinfo.
                                                    - ufo2ft requires these info fields to compile a font binary:
                                                      unitsPerEm, ascender, descender, xHeight, capHeight and familyName."

  - **[com.daltonmaag/check/ufo-recommended-fields]:** "Check that recommended fields are present in the UFO fontinfo.
                                                       - This includes fields that should be in any production font."

  - **[com.daltonmaag/check/ufo-unnecessary-fields]:** "Check that no unnecessary fields are present in the UFO fontinfo.
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
  - whitelist: a few legacy CamelCased familynames (check/109)
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
