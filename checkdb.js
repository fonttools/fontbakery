window.fbchecks={
    "com.adobe.fonts/check/cff2_call_depth": {
        "description": "Is the CFF2 subr/gsubr call depth > 10?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "cff",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2425",
        "rationale": "<p>Per &quot;The CFF2 CharString Format&quot;, the &quot;Subr nesting, stack limit&quot; is 10.</p>\n",
        "sections": [
            "fontbakery.profiles.cff"
        ]
    },
    "com.adobe.fonts/check/cff_call_depth": {
        "description": "Is the CFF subr/gsubr call depth > 10?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "cff",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2425",
        "rationale": "<p>Per &quot;The Type 2 Charstring Format, Technical Note #5177&quot;, the &quot;Subr nesting, stack limit&quot; is 10.</p>\n",
        "sections": [
            "fontbakery.profiles.cff"
        ]
    },
    "com.adobe.fonts/check/cff_deprecated_operators": {
        "description": "Does the font use deprecated CFF operators or operations?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "cff",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3033",
        "rationale": "<p>The 'dotsection' operator and the use of 'endchar' to build accented characters from the Adobe Standard Encoding Character Set (&quot;seac&quot;) are deprecated in CFF. Adobe recommends repairing any fonts that use these, especially endchar-as-seac, because a rendering issue was discovered in Microsoft Word with a font that makes use of this operation. The check treats that useage as a FAIL. There are no known ill effects of using dotsection, so that check is a WARN.</p>\n",
        "sections": [
            "fontbakery.profiles.cff"
        ]
    },
    "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1": {
        "description": "Check that OS/2.fsSelection bold & italic settings are unique for each NameID1",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2388",
        "rationale": "<p>Per the OpenType spec: name ID 1 'is used in combination with Font Subfamily name (name ID 2), and should be shared among at most four fonts that differ only in weight or style...\nThis four-way distinction should also be reflected in the OS/2.fsSelection field, using bits 0 and 5.</p>\n",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "com.adobe.fonts/check/family/consistent_upm": {
        "description": "Fonts have consistent Units Per Em?",
        "profiles": [
            "adobefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2372",
        "rationale": "<p>While not required by the OpenType spec, we (Adobe) expect that a group of fonts designed &amp; produced as a family have consistent units per em.</p>\n",
        "sections": [
            "Adobe Fonts"
        ]
    },
    "com.adobe.fonts/check/family/max_4_fonts_per_family_name": {
        "description": "Verify that each group of fonts with the same nameID 1 has maximum of 4 fonts",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "rationale": "<p>Per the OpenType spec:\n'The Font Family name [...] should be shared among at most four fonts that differ only in weight or style [...]'</p>\n",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.adobe.fonts/check/find_empty_letters": {
        "description": "Letters in font have glyphs that are not empty?",
        "profiles": [
            "adobefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2460",
        "rationale": "<p>Font language, script, and character set tagging approaches typically have an underlying assumption that letters (i.e. characters with Unicode general category 'Ll', 'Lm', 'Lo', 'Lt', or 'Lu', which includes CJK ideographs and Hangul syllables) with entries in the 'cmap' table have glyphs with ink (with a few exceptions, notably the Hangul &quot;filler&quot; characters).\nThis check is intended to identify fonts in which such letters have been mapped to empty glyphs (typically done as a form of subsetting). Letters with empty glyphs should have their entries removed from the 'cmap' table, even if the empty glyphs are left in place (e.g. for CID consistency).</p>\n",
        "sections": [
            "Adobe Fonts"
        ]
    },
    "com.adobe.fonts/check/fsselection_matches_macstyle": {
        "description": "Check if OS/2 fsSelection matches head macStyle bold and italic bits.",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2382",
        "rationale": "<p>The bold and italic bits in OS/2.fsSelection must match the bold and italic bits in head.macStyle per the OpenType spec.</p>\n",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "com.adobe.fonts/check/name/empty_records": {
        "description": "Check name table for empty records.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2369",
        "rationale": "<p>Check the name table for empty records, as this can cause problems in Adobe apps.</p>\n",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.adobe.fonts/check/name/postscript_name_consistency": {
        "description": "Name table ID 6 (PostScript name) must be consistent across platforms.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2394",
        "rationale": "<p>The PostScript name entries in the font's 'name' table should be consistent across platforms.\nThis is the TTF/CFF2 equivalent of the CFF 'name/postscript_vs_cff' check.</p>\n",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.adobe.fonts/check/name/postscript_vs_cff": {
        "description": "CFF table FontName must match name table ID 6 (PostScript name).",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2229",
        "rationale": "<p>The PostScript name entries in the font's 'name' table should match the FontName string in the 'CFF ' table.\nThe 'CFF ' table has a lot of information that is duplicated in other tables. This information should be consistent across tables, because there's no guarantee which table an app will get the data from.</p>\n",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.daltonmaag/check/ufo-recommended-fields": {
        "description": "Check that recommended fields are present in the UFO fontinfo.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "ufo_sources",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/1736",
        "rationale": "<p>This includes fields that should be in any production font.</p>\n",
        "sections": [
            "UFO Sources"
        ]
    },
    "com.daltonmaag/check/ufo-required-fields": {
        "description": "Check that required fields are present in the UFO fontinfo.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "ufo_sources",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/1736",
        "rationale": "<p>ufo2ft requires these info fields to compile a font binary:\nunitsPerEm, ascender, descender, xHeight, capHeight and familyName.</p>\n",
        "sections": [
            "UFO Sources"
        ]
    },
    "com.daltonmaag/check/ufo-unnecessary-fields": {
        "description": "Check that no unnecessary fields are present in the UFO fontinfo.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "ufo_sources",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/1736",
        "rationale": "<p>ufo2ft will generate these.\nopenTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted because it is useful to toggle a range when not <em>all</em> the glyphs in that region are present.\nyear is deprecated since UFO v2.</p>\n",
        "sections": [
            "UFO Sources"
        ]
    },
    "com.daltonmaag/check/ufolint": {
        "description": "Run ufolint on UFO source directory.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "ufo_sources",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/1736",
        "sections": [
            "UFO Sources"
        ]
    },
    "com.fontwerk/check/no_mac_entries": {
        "description": "Check if font has Mac name table entries (platform=1)",
        "profiles": [
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/gftools/issues/469",
        "rationale": "<p>Mac name table entries are not needed anymore.\nEven Apple stopped producing name tables with platform 1.\nPlease see for example the following system font:\n/System/Library/Fonts/SFCompact.ttf\nAlso, Dave Opstad, who developed Apple's TrueType specifications, told Olli Meier a couple years ago (as of January/2022) that these entries are outdated and should not be produced anymore.</p>\n",
        "sections": [
            "Fontwerk"
        ]
    },
    "com.google.fonts/check/STAT/axis_order": {
        "description": "Check axis ordering on the STAT table. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3049",
        "rationale": "<p>This is (for now) a merely informative check to detect what's the axis ordering declared on the STAT table of fonts in the Google Fonts collection.\nWe may later update this to enforce some unified axis ordering scheme, yet to be determined.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/STAT/gf-axisregistry": {
        "description": "Validate STAT particle names and values match the fallback names in GFAxisRegistry. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3022",
        "rationale": "<p>Check that particle names and values on STAT table match the fallback names in each axis entry at the Google Fonts Axis Registry, available at <a href=\"https://github.com/google/fonts/tree/main/axisregistry\">https://github.com/google/fonts/tree/main/axisregistry</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/STAT_strings": {
        "description": "Check correctness of STAT table strings ",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2863",
        "rationale": "<p>On the STAT table, the &quot;Italic&quot; keyword must not be used on AxisValues for variation axes other than 'ital'.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/aat": {
        "description": "Are there unwanted Apple tables?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2190",
        "rationale": "<p>Apple's TrueType reference manual [1] describes SFNT tables not in the Microsoft OpenType specification [2] and these can sometimes sneak into final release files, but Google Fonts should only have OpenType tables.\n[1] <a href=\"https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html\">https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html</a>\n[2] <a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/\">https://docs.microsoft.com/en-us/typography/opentype/spec/</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/all_glyphs_have_codepoints": {
        "description": "Check all glyphs have codepoints assigned.",
        "profiles": [
            "universal",
            "notofonts",
            "cmap",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/735",
        "sections": [
            "fontbakery.profiles.cmap"
        ]
    },
    "com.google.fonts/check/canonical_filename": {
        "description": "Checking file is named canonically.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/001",
        "rationale": "<p>A font's filename must be composed in the following manner:\n<familyname>-<stylename>.ttf</p>\n<ul>\n<li>Nunito-Regular.ttf,</li>\n<li>Oswald-BoldItalic.ttf\nVariable fonts must list the axis tags in alphabetical order in square brackets and separated by commas:</li>\n<li>Roboto[wdth,wght].ttf</li>\n<li>Familyname-Italic[wght].ttf</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/cjk_chws_feature": {
        "description": "Does the font contain chws and vchw features?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3363",
        "rationale": "<p>The W3C recommends the addition of chws and vchw features to CJK fonts to enhance the spacing of glyphs in environments which do not fully support JLREQ layout rules.\nThe chws_tool utility (<a href=\"https://github.com/googlefonts/chws_tool\">https://github.com/googlefonts/chws_tool</a>) can be used to add these features automatically.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/cjk_not_enough_glyphs": {
        "description": "Does the font contain less than 40 CJK characters?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3214",
        "rationale": "<p>Hangul has 40 characters and it's the smallest CJK writing system.\nIf a font contains less CJK glyphs than this writing system, we inform the user that some glyphs may be encoded incorrectly.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/cjk_vertical_metrics": {
        "description": "Check font follows the Google Fonts CJK vertical metric schema",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2797",
        "rationale": "<p>CJK fonts have different vertical metrics when compared to Latin fonts. We follow the schema developed by dr Ken Lunde for Source Han Sans and the Noto CJK fonts.\nOur documentation includes further information: <a href=\"https://github.com/googlefonts/gf-docs/tree/main/Spec#cjk-vertical-metrics\">https://github.com/googlefonts/gf-docs/tree/main/Spec#cjk-vertical-metrics</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/cjk_vertical_metrics_regressions": {
        "description": "Check if the vertical metrics of a CJK family are similar to the same family hosted on Google Fonts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3244",
        "rationale": "<p>Check CJK family has the same vertical metrics as the same family hosted on Google Fonts.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/cmap/unexpected_subtables": {
        "description": "Ensure all cmap subtables are the typical types expected in a font.",
        "profiles": [
            "notofonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2676",
        "rationale": "<p>There are just a few typical types of cmap subtables that are used in fonts.\nIf anything different is declared in a font, it will be treated as a FAIL.</p>\n",
        "sections": [
            "Noto Fonts"
        ]
    },
    "com.google.fonts/check/code_pages": {
        "description": "Check code page character ranges",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2474",
        "rationale": "<p>At least some programs (such as Word and Sublime Text) under Windows 7 do not recognize fonts unless code page bits are properly set on the ulCodePageRange1 (and/or ulCodePageRange2) fields of the OS/2 table.\nMore specifically, the fonts are selectable in the font menu, but whichever Windows API these applications use considers them unsuitable for any character set, so anything set in these fonts is rendered with a fallback font of Arial.\nThis check currently does not identify which code pages should be set. Auto-detecting coverage is not trivial since the OpenType specification leaves the interpretation of whether a given code page is &quot;functional&quot; or not open to the font developer to decide.\nSo here we simply detect as a FAIL when a given font has no code page declared at all.</p>\n",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "com.google.fonts/check/contour_count": {
        "description": "Check if each glyph has the recommended amount of contours.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/153",
        "rationale": "<p>Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.\nHowever, a quotedbl should have 2 contours, unless the font belongs to a display family.\nThis check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/description/broken_links": {
        "description": "Does DESCRIPTION file contain broken links?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/003",
        "rationale": "<p>The snippet of HTML in the DESCRIPTION.en_us.html file is added to the font family webpage on the Google Fonts website. For that reason, all hyperlinks in it must be properly working.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/eof_linebreak": {
        "description": "DESCRIPTION.en_us.html should end in a linebreak.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2879",
        "rationale": "<p>Some older text-handling tools sometimes misbehave if the last line of data in a text file is not terminated with a newline character (also known as '\\n').\nWe know that this is a very small detail, but for the sake of keeping all DESCRIPTION.en_us.html files uniformly formatted throughout the GFonts collection, we chose to adopt the practice of placing this final linebreak char on them.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/family_update": {
        "description": "On a family update, the DESCRIPTION.en_us.html file should ideally also be updated.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3182",
        "rationale": "<p>We want to ensure that any significant changes to the font family are properly mentioned in the DESCRIPTION file.\nIn general, it means that the contents of the DESCRIPTION.en_us.html file will typically change if when font files are updated. Please treat this check as a reminder to do so whenever appropriate!</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/git_url": {
        "description": "Does DESCRIPTION file contain a upstream Git repo URL?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2523",
        "rationale": "<p>The contents of the DESCRIPTION.en-us.html file are displayed on the Google Fonts website in the about section of each font family specimen page.\nSince all of the Google Fonts collection is composed of libre-licensed fonts, this check enforces a policy that there must be a hypertext link in that page directing users to the repository where the font project files are made available.\nSuch hosting is typically done on sites like Github, Gitlab, GNU Savannah or any other git-based version control service.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/max_length": {
        "description": "DESCRIPTION.en_us.html must have less than 2000 bytes.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/006",
        "rationale": "<p>The fonts.google.com catalog specimen pages 2016 to 2020 were placed in a narrow area of the page.\nThat meant a maximum limit of 1,000 characters was good, so that the narrow column did not extent that section of the page to be too long.\nBut with the &quot;v4&quot; redesign of 2020, the specimen pages allow for longer texts without upsetting the balance of the page.\nSo currently the limit before warning is 2,000 characters.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/min_length": {
        "description": "DESCRIPTION.en_us.html must have more than 200 bytes.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/005",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/urls": {
        "description": "URLs on DESCRIPTION file must not display http(s) prefix.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3497",
        "rationale": "<p>The snippet of HTML in the DESCRIPTION.en_us.html file is added to the font family webpage on the Google Fonts website.\nGoogle Fonts has a content formatting policy for that snippet that expects the text content of links not to include the http:// or https:// prefixes.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/description/valid_html": {
        "description": "Is this a proper HTML snippet?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": [
            "legacy:check/004",
            "https://github.com/googlefonts/fontbakery/issues/2664"
        ],
        "rationale": "<p>Sometimes people write malformed HTML markup. This check should ensure the file is good.\nAdditionally, when packaging families for being pushed to the <code>google/fonts</code> git repo, if there is no DESCRIPTION.en_us.html file, some older versions of the <code>add_font.py</code> tool insert a placeholder description file which contains invalid html. This file needs to either be replaced with an existing description file or edited by hand.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/designspace_has_consistent_codepoints": {
        "description": "Check codepoints consistency in a designspace file.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3168",
        "rationale": "<p>This check ensures that Unicode assignments are consistent across all sources specified in a designspace file.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/designspace_has_consistent_glyphset": {
        "description": "Check consistency of glyphset in a designspace file.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3168",
        "rationale": "<p>This check ensures that non-default masters don't have glyphs not present in the default one.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/designspace_has_default_master": {
        "description": "Ensure a default master is defined.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3168",
        "rationale": "<p>We expect that designspace files declare on of the masters as default.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/designspace_has_sources": {
        "description": "See if we can actually load the source files.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3168",
        "rationale": "<p>This check parses a designspace file and tries to load the source files specified.\nThis is meant to ensure that the file is not malformed, can be properly parsed and does include valid source file references.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/dsig": {
        "description": "Does the font have a DSIG table?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "dsig",
            "fontwerk"
        ],
        "proposal": [
            "legacy:check/045",
            "https://github.com/googlefonts/fontbakery/issues/3398"
        ],
        "rationale": "<p>Microsoft Office 2013 and below products expect fonts to have a digital signature declared in a DSIG table in order to implement OpenType features. The EOL date for Microsoft Office 2013 products is 4/11/2023. This issue does not impact Microsoft Office 2016 and above products.\nAs we approach the EOL date, it is now considered better to completely remove the table.\nBut if you still want your font to support OpenType features on Office 2013, then you may find it handy to add a fake signature on a placeholder DSIG table by running one of the helper scripts provided at <a href=\"https://github.com/googlefonts/gftools\">https://github.com/googlefonts/gftools</a>\nReference: <a href=\"https://github.com/googlefonts/fontbakery/issues/1845\">https://github.com/googlefonts/fontbakery/issues/1845</a></p>\n",
        "sections": [
            "fontbakery.profiles.dsig"
        ]
    },
    "com.google.fonts/check/epar": {
        "description": "EPAR table present in font?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/226",
        "rationale": "<p>The EPAR table is/was a way of expressing common licensing permissions and restrictions in metadata; while almost nothing supported it, Dave Crossland wonders that adding it to everything in Google Fonts could help make it more popular.\nMore info is available at:\n<a href=\"https://davelab6.github.io/epar/\">https://davelab6.github.io/epar/</a></p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 1
    },
    "com.google.fonts/check/family/control_chars": {
        "description": "Does font file include unacceptable control character glyphs?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2430",
        "rationale": "<p>Use of some unacceptable control characters in the U+0000 - U+001F range can lead to rendering issues on some platforms.\nAcceptable control characters are defined as .null (U+0000) and CR (U+000D) for this test.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/family/equal_font_versions": {
        "description": "Make sure all font files have the same version value.",
        "profiles": [
            "universal",
            "notofonts",
            "head",
            "googlefonts",
            "opentype",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/014",
        "sections": [
            "fontbakery.profiles.head"
        ]
    },
    "com.google.fonts/check/family/equal_unicode_encodings": {
        "description": "Fonts have equal unicode encodings?",
        "profiles": [
            "universal",
            "notofonts",
            "cmap",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/013",
        "sections": [
            "fontbakery.profiles.cmap"
        ]
    },
    "com.google.fonts/check/family/has_license": {
        "description": "Check font has a license.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/028",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/family/italics_have_roman_counterparts": {
        "description": "Ensure Italic styles have Roman counterparts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1733",
        "rationale": "<p>For each font family on Google Fonts, every Italic style must have a Roman sibling.\nThis kind of problem was first observed at [1] where the Bold style was missing but BoldItalic was included.\n[1] <a href=\"https://github.com/google/fonts/pull/1482\">https://github.com/google/fonts/pull/1482</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/family/panose_familytype": {
        "description": "Fonts have consistent PANOSE family type?",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/010",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "com.google.fonts/check/family/panose_proportion": {
        "description": "Fonts have consistent PANOSE proportion?",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/009",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "com.google.fonts/check/family/single_directory": {
        "description": "Checking all files are in the same directory.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/002",
        "rationale": "<p>If the set of font files passed in the command line is not all in the same directory, then we warn the user since the tool will interpret the set of files as belonging to a single family (and it is unlikely that the user would store the files from a single family spreaded in several separate directories).</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/family/tnum_horizontal_metrics": {
        "description": "All tabular figures must have the same width across the RIBBI-family.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2278",
        "rationale": "<p>Tabular figures need to have the same metrics in all styles in order to allow tables to be set with proper typographic control, but to maintain the placement of decimals and numeric columns between rows.\nHere's a good explanation of this:\n<a href=\"https://www.typography.com/techniques/fonts-for-financials/#tabular-figs\">https://www.typography.com/techniques/fonts-for-financials/#tabular-figs</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/family/underline_thickness": {
        "description": "Fonts have consistent underline thickness?",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "post",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/008",
        "rationale": "<p>Dave C Lemon (Adobe Type Team) recommends setting the underline thickness to be consistent across the family.\nIf thicknesses are not family consistent, words set on the same line which have different styles look strange.\nSee also:\n<a href=\"https://twitter.com/typenerd1/status/690361887926697986\">https://twitter.com/typenerd1/status/690361887926697986</a></p>\n",
        "sections": [
            "fontbakery.profiles.post"
        ]
    },
    "com.google.fonts/check/family/vertical_metrics": {
        "description": "Each font in a family must have the same set of vertical metrics values.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1487",
        "rationale": "<p>We want all fonts within a family to have the same vertical metrics so their line spacing is consistent across the family.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/family/win_ascent_and_descent": {
        "description": "Checking OS/2 usWinAscent & usWinDescent.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/040",
        "rationale": "<p>A font's winAscent and winDescent values should be greater than the head table's yMax, abs(yMin) values. If they are less than these values, clipping can occur on Windows platforms (<a href=\"https://github.com/RedHatBrand/Overpass/issues/33\">https://github.com/RedHatBrand/Overpass/issues/33</a>).\nIf the font includes tall/deep writing systems such as Arabic or Devanagari, the winAscent and winDescent can be greater than the yMax and abs(yMin) to accommodate vowel marks.\nWhen the win Metrics are significantly greater than the upm, the linespacing can appear too loose. To counteract this, enabling the OS/2 fsSelection bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 typo values instead. This means the font developer can control the linespacing with the typo values, whilst avoiding clipping by setting the win values to values greater than the yMax and abs(yMin).</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/family_naming_recommendations": {
        "description": "Font follows the family naming recommendations?",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/071",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.google.fonts/check/file_size": {
        "description": "Ensure files are not too large.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3320",
        "rationale": "<p>Serving extremely large font files on Google Fonts causes usability issues. This check ensures that file sizes are reasonable.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/font_copyright": {
        "description": "Copyright notices match canonical pattern in fonts",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2383",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/font_version": {
        "description": "Checking font version fields (head and name table).",
        "profiles": [
            "universal",
            "notofonts",
            "head",
            "googlefonts",
            "opentype",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/044",
        "sections": [
            "fontbakery.profiles.head"
        ]
    },
    "com.google.fonts/check/fontbakery_version": {
        "description": "Do we have the latest version of FontBakery installed?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2093",
        "rationale": "<p>Running old versions of FontBakery can lead to a poor report which may include false WARNs and FAILs due do bugs, as well as outdated quality assurance criteria.\nOlder versions will also not report problems that are detected by new checks added to the tool in more recent updates.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/fontdata_namecheck": {
        "description": "Familyname must be unique according to namecheck.fontdata.com",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/494",
        "rationale": "<p>We need to check names are not already used, and today the best place to check that is <a href=\"http://namecheck.fontdata.com\">http://namecheck.fontdata.com</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/fontv": {
        "description": "Check for font-v versioning.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1563",
        "rationale": "<p>The git sha1 tagging and dev/release features of Source Foundry <code>font-v</code> tool are awesome and we would love to consider upstreaming the approach into fontmake someday. For now we only emit a WARN if a given font does not yet follow the experimental versioning style, but at some point we may start enforcing it.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/fontvalidator": {
        "description": "Checking with Microsoft Font Validator.",
        "profiles": [
            "fontval"
        ],
        "proposal": "legacy:check/037",
        "sections": [
            "Checks inherited from Microsoft Font Validator"
        ]
    },
    "com.google.fonts/check/fsselection": {
        "description": "Checking OS/2 fsSelection value.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/129",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/fstype": {
        "description": "Checking OS/2 fsType does not impose restrictions.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/016",
        "rationale": "<p>The fsType in the OS/2 table is a legacy DRM-related field. Fonts in the Google Fonts collection must have it set to zero (also known as &quot;Installable Embedding&quot;). This setting indicates that the fonts can be embedded in documents and permanently installed by applications on remote systems.\nMore detailed info is available at:\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype\">https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/fvar_name_entries": {
        "description": "All name entries referenced by fvar instances exist on the name table?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2069",
        "rationale": "<p>The purpose of this check is to make sure that all name entries referenced by variable font instances do exist in the name table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/gasp": {
        "description": "Is the Grid-fitting and Scan-conversion Procedure ('gasp') table set to optimize rendering?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/062",
        "rationale": "<p>Traditionally version 0 'gasp' tables were set so that font sizes below 8 ppem had no grid fitting but did have antialiasing. From 9-16 ppem, just grid fitting. And fonts above 17ppem had both antialiasing and grid fitting toggled on. The use of accelerated graphics cards and higher resolution screens make this approach obsolete. Microsoft's DirectWrite pushed this even further with much improved rendering built into the OS and apps.\nIn this scenario it makes sense to simply toggle all 4 flags ON for all font sizes.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/gdef_mark_chars": {
        "description": "Check mark characters are in GDEF mark glyph class.",
        "profiles": [
            "universal",
            "gdef",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2877",
        "rationale": "<p>Mark characters should be in the GDEF mark glyph class.</p>\n",
        "sections": [
            "fontbakery.profiles.gdef"
        ]
    },
    "com.google.fonts/check/gdef_non_mark_chars": {
        "description": "Check GDEF mark glyph class doesn't have characters that are not marks.",
        "profiles": [
            "universal",
            "gdef",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2877",
        "rationale": "<p>Glyphs in the GDEF mark glyph class become non-spacing and may be repositioned if they have mark anchors.\nOnly combining mark glyphs should be in that class. Any non-mark glyph must not be in that class, in particular spacing glyphs.</p>\n",
        "sections": [
            "fontbakery.profiles.gdef"
        ]
    },
    "com.google.fonts/check/gdef_spacing_marks": {
        "description": "Check glyphs in mark glyph class are non-spacing.",
        "profiles": [
            "universal",
            "gdef",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2877",
        "rationale": "<p>Glyphs in the GDEF mark glyph class should be non-spacing.\nSpacing glyphs in the GDEF mark glyph class may have incorrect anchor positioning that was only intended for building composite glyphs during design.</p>\n",
        "sections": [
            "fontbakery.profiles.gdef"
        ]
    },
    "com.google.fonts/check/gf-axisregistry/fvar_axis_defaults": {
        "description": "Validate defaults on fvar table match registered fallback names in GFAxisRegistry. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3141",
        "rationale": "<p>Check that axis defaults have a corresponding fallback name registered at the Google Fonts Axis Registry, available at <a href=\"https://github.com/google/fonts/tree/main/axisregistry\">https://github.com/google/fonts/tree/main/axisregistry</a>\nThis is necessary for the following reasons:\nTo get ZIP files downloads on Google Fonts to be accurate \u2014 otherwise the chosen default font is not generated. The Newsreader family, for instance, has a default value on the 'opsz' axis of 16pt. If 16pt was not a registered fallback position, then the ZIP file would instead include another position as default (such as 14pt).\nFor the Variable fonts to display the correct location on the specimen page.\nFor VF with no weight axis to be displayed at all. For instance, Ballet, which has no weight axis, was not appearing in sandbox because default position on 'opsz' axis was 16pt, and it was not yet a registered fallback positon.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/glyf_nested_components": {
        "description": "Check glyphs do not have components which are themselves components.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2961",
        "rationale": "<p>There have been bugs rendering variable fonts with nested components. Additionally, some static fonts with nested components have been reported to have rendering and printing issues.\nFor more info, see:</p>\n<ul>\n<li><a href=\"https://github.com/googlefonts/fontbakery/issues/2961\">https://github.com/googlefonts/fontbakery/issues/2961</a></li>\n<li><a href=\"https://github.com/arrowtype/recursive/issues/412\">https://github.com/arrowtype/recursive/issues/412</a></li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/glyf_non_transformed_duplicate_components": {
        "description": "Check glyphs do not have duplicate components which have the same x,y coordinates.",
        "profiles": [
            "universal",
            "glyf",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2709",
        "rationale": "<p>There have been cases in which fonts had faulty double quote marks, with each of them containing two single quote marks as components with the same x, y coordinates which makes them visually look like single quote marks.\nThis check ensures that glyphs do not contain duplicate components which have the same x,y coordinates.</p>\n",
        "sections": [
            "fontbakery.profiles.glyf"
        ]
    },
    "com.google.fonts/check/glyf_unused_data": {
        "description": "Is there any unused data at the end of the glyf table?",
        "profiles": [
            "universal",
            "glyf",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/069",
        "sections": [
            "fontbakery.profiles.glyf"
        ]
    },
    "com.google.fonts/check/glyph_coverage": {
        "description": "Check `Google Fonts Latin Core` glyph coverage.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2488",
        "rationale": "<p>Google Fonts expects that fonts in its collection support at least the minimal set of characters defined in the <code>GF-latin-core</code> glyph-set.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/gpos_kerning_info": {
        "description": "Does GPOS table have kerning information? This check skips monospaced fonts as defined by post.isFixedPitch value",
        "profiles": [
            "universal",
            "gpos",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/063",
        "sections": [
            "fontbakery.profiles.gpos"
        ]
    },
    "com.google.fonts/check/has_ttfautohint_params": {
        "description": "Font has ttfautohint params?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1773",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/hinting_impact": {
        "description": "Show hinting filesize impact.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/054",
        "rationale": "<p>This check is merely informative, displaying and useful comparison of filesizes of hinted versus unhinted font files.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/integer_ppem_if_hinted": {
        "description": "PPEM must be an integer on hinted fonts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2338",
        "rationale": "<p>Hinted fonts must have head table flag bit 3 set.\nPer <a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/head\">https://docs.microsoft.com/en-us/typography/opentype/spec/head</a>, bit 3 of Head::flags decides whether PPEM should be rounded. This bit should always be set for hinted fonts.\nNote:\nBit 3 = Force ppem to integer values for all internal scaler math;\nMay use fractional ppem sizes if this bit is clear;</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/iso15008_intercharacter_spacing": {
        "description": "Check if spacing between characters is adequate for display use",
        "profiles": [
            "iso15008"
        ],
        "proposal": [
            "https://github.com/googlefonts/fontbakery/issues/1832",
            "https://github.com/googlefonts/fontbakery/issues/3252"
        ],
        "rationale": "<p>According to ISO 15008, fonts used for in-car displays should not be too narrow or too wide.\nTo ensure legibility of this font on in-car information systems it is recommended that the spacing falls within the following values:</p>\n<ul>\n<li>space between vertical strokes (e.g. &quot;ll&quot;) should be 150%-240% of the stem width.</li>\n<li>space between diagonals and verticals (e.g. &quot;vl&quot;) should be at least 85% of the stem width.</li>\n<li>diagonal characters should not touch (e.g. &quot;vv&quot;).\n(Note that PASSing this check does not guarantee compliance with ISO 15008.)</li>\n</ul>\n",
        "sections": [
            "Suitability for In-Car Display"
        ]
    },
    "com.google.fonts/check/iso15008_interline_spacing": {
        "description": "Check if spacing between lines is adequate for display use",
        "profiles": [
            "iso15008"
        ],
        "proposal": [
            "https://github.com/googlefonts/fontbakery/issues/1832",
            "https://github.com/googlefonts/fontbakery/issues/3254"
        ],
        "rationale": "<p>According to ISO 15008, fonts used for in-car displays should not be too narrow or too wide.\nTo ensure legibility of this font on in-car information systems it is recommended that  the vertical metrics be set to a minimum at least one stem width between the bottom of the descender and the top of the ascender.\n(Note that PASSing this check does not guarantee compliance with ISO 15008.)</p>\n",
        "sections": [
            "Suitability for In-Car Display"
        ]
    },
    "com.google.fonts/check/iso15008_interword_spacing": {
        "description": "Check if spacing between words is adequate for display use",
        "profiles": [
            "iso15008"
        ],
        "proposal": [
            "https://github.com/googlefonts/fontbakery/issues/1832",
            "https://github.com/googlefonts/fontbakery/issues/3253"
        ],
        "rationale": "<p>According to ISO 15008, fonts used for in-car displays should not be too narrow or too wide.\nTo ensure legibility of this font on in-car information systems it is recommended that the space character should have advance width between 250% and 300% of the space between the letters l and m.\n(Note that PASSing this check does not guarantee compliance with ISO 15008.)</p>\n",
        "sections": [
            "Suitability for In-Car Display"
        ]
    },
    "com.google.fonts/check/iso15008_proportions": {
        "description": "Check if 0.65 => (H width / H height) => 0.80",
        "profiles": [
            "iso15008"
        ],
        "proposal": [
            "https://github.com/googlefonts/fontbakery/issues/1832",
            "https://github.com/googlefonts/fontbakery/issues/3250"
        ],
        "rationale": "<p>According to ISO 15008, fonts used for in-car displays should not be too narrow or too wide.\nTo ensure legibility of this font on in-car information systems, it is recommended that the ratio of H width to H height is between 0.65 and 0.80.\n(Note that PASSing this check does not guarantee compliance with ISO 15008.)</p>\n",
        "sections": [
            "Suitability for In-Car Display"
        ]
    },
    "com.google.fonts/check/iso15008_stem_width": {
        "description": "Check if 0.10 <= (stem width / ascender) <= 0.82",
        "profiles": [
            "iso15008"
        ],
        "proposal": [
            "https://github.com/googlefonts/fontbakery/issues/1832",
            "https://github.com/googlefonts/fontbakery/issues/3251"
        ],
        "rationale": "<p>According to ISO 15008, fonts used for in-car displays should not be too light or too bold.\nTo ensure legibility of this font on in-car information systems, it is recommended that the ratio of stem width to ascender height is between 0.10 and 0.20.\n(Note that PASSing this check does not guarantee compliance with ISO 15008.)</p>\n",
        "sections": [
            "Suitability for In-Car Display"
        ]
    },
    "com.google.fonts/check/italic_angle": {
        "description": "Checking post.italicAngle value.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/130",
        "rationale": "<p>The 'post' table italicAngle property should be a reasonable amount, likely not more than -20\u00b0, never more than -30\u00b0, and never greater than 0\u00b0. Note that in the OpenType specification, the value is negative for a lean rightwards.\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/post\">https://docs.microsoft.com/en-us/typography/opentype/spec/post</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/kern_table": {
        "description": "Is there a usable \"kern\" table declared in the font?",
        "profiles": [
            "universal",
            "kern",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": [
            "legacy:check/066",
            "https://github.com/googlefonts/fontbakery/issues/1675",
            "https://github.com/googlefonts/fontbakery/issues/3148"
        ],
        "rationale": "<p>Even though all fonts should have their kerning implemented in the GPOS table, there may be kerning info at the kern table as well.\nSome applications such as MS PowerPoint require kerning info on the kern table. More specifically, they require a format 0 kern subtable from a kern table version 0 with only glyphs defined in the cmap table, which is the only one that Windows understands (and which is also the simplest and more limited of all the kern subtables).\nGoogle Fonts ingests fonts made for download and use on desktops, and does all web font optimizations in the serving pipeline (using libre libraries that anyone can replicate.)\nIdeally, TTFs intended for desktop users (and thus the ones intended for Google Fonts) should have both KERN and GPOS tables.\nGiven all of the above, we currently treat kerning on a v0 kern table as a good-to-have (but optional) feature.</p>\n",
        "sections": [
            "fontbakery.profiles.kern"
        ]
    },
    "com.google.fonts/check/kerning_for_non_ligated_sequences": {
        "description": "Is there kerning info for non-ligated sequences?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1145",
        "rationale": "<p>Fonts with ligatures should have kerning on the corresponding non-ligated sequences for text where ligatures aren't used (eg <a href=\"https://github.com/impallari/Raleway/issues/14\">https://github.com/impallari/Raleway/issues/14</a>).</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/layout_valid_feature_tags": {
        "description": "Does the font have any invalid feature tags?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "layout",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3355",
        "rationale": "<p>Incorrect tags can be indications of typos, leftover debugging code or questionable approaches, or user error in the font editor. Such typos can cause features and language support to fail to work as intended.</p>\n",
        "sections": [
            "fontbakery.profiles.layout"
        ],
        "severity": 8
    },
    "com.google.fonts/check/layout_valid_language_tags": {
        "description": "Does the font have any invalid language tags?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "layout",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3355",
        "rationale": "<p>Incorrect language tags can be indications of typos, leftover debugging code or questionable approaches, or user error in the font editor. Such typos can cause features and language support to fail to work as intended.</p>\n",
        "sections": [
            "fontbakery.profiles.layout"
        ],
        "severity": 8
    },
    "com.google.fonts/check/layout_valid_script_tags": {
        "description": "Does the font have any invalid script tags?",
        "profiles": [
            "adobefonts",
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "layout",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3355",
        "rationale": "<p>Incorrect script tags can be indications of typos, leftover debugging code or questionable approaches, or user error in the font editor. Such typos can cause features and language support to fail to work as intended.</p>\n",
        "sections": [
            "fontbakery.profiles.layout"
        ],
        "severity": 8
    },
    "com.google.fonts/check/license/OFL_body_text": {
        "description": "Check OFL body text is correct.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3352",
        "rationale": "<p>Check OFL body text is correct. Often users will accidently delete parts of the body text.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/license/OFL_copyright": {
        "description": "Check license file has good copyright string.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2764",
        "rationale": "<p>An OFL.txt file's first line should be the font copyright e.g:\n&quot;Copyright 2019 The Montserrat Project Authors (<a href=\"https://github.com/julietaula/montserrat\">https://github.com/julietaula/montserrat</a>)&quot;</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/ligature_carets": {
        "description": "Are there caret positions declared for every ligature?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1225",
        "rationale": "<p>All ligatures in a font must have corresponding caret (text cursor) positions defined in the GDEF table, otherwhise, users may experience issues with caret rendering.\nIf using GlyphsApp or UFOs, ligature carets can be defined as anchors with names starting with 'caret_'. These can be compiled with fontmake as of version v2.4.0.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/linegaps": {
        "description": "Checking Vertical Metric Linegaps.",
        "profiles": [
            "universal",
            "notofonts",
            "hhea",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/041",
        "sections": [
            "fontbakery.profiles.hhea"
        ]
    },
    "com.google.fonts/check/loca/maxp_num_glyphs": {
        "description": "Does the number of glyphs in the loca table match the maxp table?",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk",
            "loca"
        ],
        "proposal": "legacy:check/180",
        "sections": [
            "fontbakery.profiles.loca"
        ]
    },
    "com.google.fonts/check/mac_style": {
        "description": "Checking head.macStyle value.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/131",
        "rationale": "<p>The values of the flags on the macStyle entry on the 'head' OpenType table that describe whether a font is bold and/or italic must be coherent with the actual style of the font as inferred by its filename.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/mandatory_avar_table": {
        "description": "Ensure variable fonts include an avar table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3100",
        "rationale": "<p>Most variable fonts should include an avar table to correctly define axes progression rates.\nFor example, a weight axis from 0% to 100% doesn't map directly to 100 to 1000, because a 10% progression from 0% may be too much to define the 200, while 90% may be too little to define the 900.\nIf the progression rates of axes is linear, this check can be ignored. Fontmake will also skip adding an avar table if the progression rates are linear. However, we still recommend designers visually proof each instance is at the desired weight, width etc.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/mandatory_glyphs": {
        "description": "Font contains '.notdef' as its first glyph?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/046",
        "rationale": "<p>The OpenType specification v1.8.2 recommends that the first glyph is the '.notdef' glyph without a codepoint assigned and with a drawing.\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph\">https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph</a>\nPre-v1.8, it was recommended that fonts should also contain 'space', 'CR' and '.null' glyphs. This might have been relevant for MacOS 9 applications.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/maxadvancewidth": {
        "description": "MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?",
        "profiles": [
            "universal",
            "notofonts",
            "hhea",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/073",
        "sections": [
            "fontbakery.profiles.hhea"
        ]
    },
    "com.google.fonts/check/meta/script_lang_tags": {
        "description": "Ensure fonts have ScriptLangTags declared on the 'meta' table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3349",
        "rationale": "<p>The OpenType 'meta' table originated at Apple. Microsoft added it to OT with just two DataMap records:</p>\n<ul>\n<li>dlng: comma-separated ScriptLangTags that indicate which scripts, or languages and scripts, with possible variants, the font is designed for</li>\n<li>slng: comma-separated ScriptLangTags that indicate which scripts, or languages and scripts, with possible variants, the font supports\nThe slng structure is intended to describe which languages and scripts the font overall supports. For example, a Traditional Chinese font that also contains Latin characters, can indicate Hant,Latn, showing that it supports Hant, the Traditional Chinese variant of the Hani script, and it also supports the Latn script\nThe dlng structure is far more interesting. A font may contain various glyphs, but only a particular subset of the glyphs may be truly &quot;leading&quot; in the design, while other glyphs may have been included for technical reasons. Such a Traditional Chinese font could only list Hant there, showing that it\u2019s designed for Traditional Chinese, but the font would omit Latn, because the developers don\u2019t think the font is really recommended for purely Latin-script use.\nThe tags used in the structures can comprise just script, or also language and script. For example, if a font has Bulgarian Cyrillic alternates in the locl feature for the cyrl BGR OT languagesystem, it could also indicate in dlng explicitly that it supports bul-Cyrl. (Note that the scripts and languages in meta use the ISO language and script codes, not the OpenType ones).\nThis check ensures that the font has the meta table containing the slng and dlng structures.\nAll families in the Google Fonts collection should contain the 'meta' table. Windows 10 already uses it when deciding on which fonts to fall back to. The Google Fonts API and also other environments could use the data for smarter filtering. Most importantly, those entries should be added to the Noto fonts.\nIn the font making process, some environments store this data in external files already. But the meta table provides a convenient way to store this inside the font file, so some tools may add the data, and unrelated tools may read this data. This makes the solution much more portable and universal.</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 3
    },
    "com.google.fonts/check/metadata/broken_links": {
        "description": "Does METADATA.pb copyright field contain broken links?",
        "profiles": [
            "googlefonts"
        ],
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/can_render_samples": {
        "description": "Check samples can be rendered.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3419",
        "rationale": "<p>In order to prevent tofu from being seen on fonts.google.com, this check verifies that all samples provided on METADATA.pb can be properly rendered by the font.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/canonical_style_names": {
        "description": "METADATA.pb: Font styles are named canonically?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/115",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/canonical_weight_value": {
        "description": "METADATA.pb: Check that font weight has a canonical value.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check.111",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/category": {
        "description": "Ensure METADATA.pb category field is valid.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2972",
        "rationale": "<p>There are only five acceptable values for the category field in a METADATA.pb file:</p>\n<ul>\n<li>MONOSPACE</li>\n<li>SANS_SERIF</li>\n<li>SERIF</li>\n<li>DISPLAY</li>\n<li>HANDWRITING\nThis check is meant to avoid typos in this field.</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/consistent_axis_enumeration": {
        "description": "Validate VF axes match the ones declared on METADATA.pb. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3051",
        "rationale": "<p>All font variation axes present in the font files must be properly declared on METADATA.pb so that they can be served by the GFonts API.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/copyright": {
        "description": "METADATA.pb: Copyright notice is the same in all fonts?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/088",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/copyright_max_length": {
        "description": "METADATA.pb: Copyright notice shouldn't exceed 500 chars.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/104",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/designer_profiles": {
        "description": "METADATA.pb: Designers are listed correctly on the Google Fonts catalog?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3083",
        "rationale": "<p>Google Fonts has a catalog of designers.\nThis check ensures that the online entries of the catalog can be found based on the designer names listed on the METADATA.pb file.\nIt also validates the URLs and file formats are all correctly set.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/designer_values": {
        "description": "Multiple values in font designer field in METADATA.pb must be separated by commas.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2479",
        "rationale": "<p>We must use commas instead of forward slashes because the server-side code at the fonts.google.com directory will segment the string on the commas into a list of names and display the first item in the list as the &quot;principal designer&quot; while the remaining names are identified as &quot;contributors&quot;.\nSee eg <a href=\"https://fonts.google.com/specimen/Rubik\">https://fonts.google.com/specimen/Rubik</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/escaped_strings": {
        "description": "Ensure METADATA.pb does not use escaped strings.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2932",
        "rationale": "<p>In some cases we've seen designer names and other fields with escaped strings in METADATA files.\nNowadays the strings can be full unicode strings and do not need escaping.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/family_directory_name": {
        "description": "Check font family directory name.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3421",
        "rationale": "<p>We want the directory name of a font family to be predictable and directly derived from the family name, all lowercased and removing spaces.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/familyname": {
        "description": "Check that METADATA.pb family values are all the same.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/089",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/filenames": {
        "description": "METADATA.pb: Font filenames match font.filename entries?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2597",
        "rationale": "<p>Note:\nThis check only looks for files in the current directory.\nFont files in subdirectories are checked by these other two checks:</p>\n<ul>\n<li>com.google.fonts/check/metadata/undeclared_fonts</li>\n<li>com.google.fonts/check/repo/vf_has_static_fonts\nWe may want to merge them all into a single check.</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/fontname_not_camel_cased": {
        "description": "METADATA.pb: Check if fontname is not camel cased.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/109",
        "rationale": "<p>We currently have a policy of avoiding camel-cased font family names other than in a very small set of exceptions.\nIf you want to have your family name added to the exceptions list, please read the instructions at <a href=\"https://github.com/googlefonts/fontbakery/issues/3270\">https://github.com/googlefonts/fontbakery/issues/3270</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/gf-axisregistry_bounds": {
        "description": "Validate METADATA.pb axes values are within gf-axisregistry bounds. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3010",
        "rationale": "<p>Each axis range in a METADATA.pb file must be registered, and within the bounds of the axis definition in the Google Fonts Axis Registry, available at <a href=\"https://github.com/google/fonts/tree/main/axisregistry\">https://github.com/google/fonts/tree/main/axisregistry</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/gf-axisregistry_valid_tags": {
        "description": "Validate METADATA.pb axes tags are defined in gf-axisregistry. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3022",
        "rationale": "<p>Ensure all axes in a METADATA.pb file are registered in the Google Fonts Axis Registry, available at <a href=\"https://github.com/google/fonts/tree/main/axisregistry\">https://github.com/google/fonts/tree/main/axisregistry</a>\nWhy does Google Fonts have its own Axis Registry?\nWe support a superset of the OpenType axis registry axis set, and use additional metadata for each axis. Axes present in a font file but not in this registry will not function via our API. No variable font is expected to support all of the axes here.\nAny font foundry or distributor library that offers variable fonts has a implicit, latent, de-facto axis registry, which can be extracted by scanning the library for axes' tags, labels, and min/def/max values. While in 2016 Microsoft originally offered to include more axes in the OpenType 1.8 specification (github.com/microsoft/OpenTypeDesignVariationAxisTags), as of August 2020, this effort has stalled. We hope more foundries and distributors will publish documents like this that make their axes explicit, to encourage of adoption of variable fonts throughout the industry, and provide source material for a future update to the OpenType specification's axis registry.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/has_regular": {
        "description": "METADATA.pb: According to Google Fonts standards, families should have a Regular style.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/090",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/includes_production_subsets": {
        "description": "Check METADATA.pb includes production subsets.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2989",
        "rationale": "<p>Check METADATA.pb file includes the same subsets as the family in production.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/italic_style": {
        "description": "METADATA.pb font.style \"italic\" matches font internals?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/106",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/license": {
        "description": "METADATA.pb license is \"APACHE2\", \"UFL\" or \"OFL\"?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/085",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/listed_on_gfonts": {
        "description": "METADATA.pb: Fontfamily is listed on Google Fonts API?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/082",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/match_filename_postscript": {
        "description": "METADATA.pb font.filename and font.post_script_name fields have equivalent values?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/097",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/match_fullname_postscript": {
        "description": "METADATA.pb font.full_name and font.post_script_name fields have equivalent values ?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/096",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/match_name_familyname": {
        "description": "METADATA.pb: Check font name is the same as family name.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/110",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/match_weight_postscript": {
        "description": "METADATA.pb weight matches postScriptName for static fonts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/113",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/menu_and_latin": {
        "description": "METADATA.pb should contain at least \"menu\" and \"latin\" subsets.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": [
            "legacy:check/086",
            "https://github.com/googlefonts/fontbakery/issues/912#issuecomment-237935444"
        ],
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/multiple_designers": {
        "description": "Font designer field in METADATA.pb must not contain 'Multiple designers'.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2766",
        "rationale": "<p>For a while the string &quot;Multiple designers&quot; was used as a placeholder on METADATA.pb files. We should replace all those instances with actual designer names so that proper credits are displayed on the Google Fonts family specimen pages.\nIf there's more than a single designer, the designer names must be separated by commas.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/copyright": {
        "description": "Copyright field for this font on METADATA.pb matches all copyright notice entries on the name table ?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/155",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/family_and_full_names": {
        "description": "METADATA.pb font.name and font.full_name fields match the values declared on the name table?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/108",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/family_name": {
        "description": "Checks METADATA.pb font.name field matches family name declared on the name table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/092",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/font_name": {
        "description": "METADATA.pb font.name value should be same as the family name declared on the name table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/095",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/full_name": {
        "description": "METADATA.pb font.full_name value matches fullname declared on the name table?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/094",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/nameid/post_script_name": {
        "description": "Checks METADATA.pb font.post_script_name matches postscript name declared on the name table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:093",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/normal_style": {
        "description": "METADATA.pb font.style \"normal\" matches font internals?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/107",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/os2_weightclass": {
        "description": "Check METADATA.pb font weights are correct.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": [
            "legacy:check/112",
            "https://github.com/googlefonts/fontbakery/issues/2683"
        ],
        "rationale": "<p>Check METADATA.pb font weights are correct.\nFor static fonts, the metadata weight should be the same as the static font's OS/2 usWeightClass.\nFor variable fonts, the weight value should be 400 if the font's wght axis range includes 400, otherwise it should be the value closest to 400.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/parses": {
        "description": "Check METADATA.pb parse correctly.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2248",
        "rationale": "<p>The purpose of this check is to ensure that the METADATA.pb file is not malformed.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/regular_is_400": {
        "description": "METADATA.pb: Regular should be 400.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/091",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/reserved_font_name": {
        "description": "Copyright notice on METADATA.pb should not contain 'Reserved Font Name'.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/103",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/subsets_order": {
        "description": "METADATA.pb subsets should be alphabetically ordered.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/087",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/undeclared_fonts": {
        "description": "Ensure METADATA.pb lists all font binaries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2575",
        "rationale": "<p>The set of font binaries available, except the ones on a &quot;static&quot; subdir, must match exactly those declared on the METADATA.pb file.\nAlso, to avoid confusion, we expect that font files (other than statics) are not placed on subdirectories.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/unique_full_name_values": {
        "description": "METADATA.pb: check if fonts field only has unique \"full_name\" values.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/083",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/unique_weight_style_pairs": {
        "description": "METADATA.pb: check if fonts field only contains unique style:weight pairs.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/084",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/unknown_designer": {
        "description": "Font designer field in METADATA.pb must not be 'unknown'.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": [
            "legacy:check/007",
            "https://github.com/googlefonts/fontbakery/issues/800"
        ],
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/unsupported_subsets": {
        "description": "Check for METADATA subsets with zero support.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3533",
        "rationale": "<p>This check ensures that the subsets specified on a METADATA.pb file are actually supported (even if only partially) by the font files.\nSubsets for which none of the codepoints are supported will cause the check to FAIL.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/metadata/valid_copyright": {
        "description": "Copyright notices match canonical pattern in METADATA.pb",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/102",
        "rationale": "<p>The expected pattern for the copyright string adheres to the following rules:</p>\n<ul>\n<li>It must say &quot;Copyright&quot; followed by a 4 digit year (optionally followed by a hyphen and another 4 digit year)</li>\n<li>Then it must say &quot;The <familyname> Project Authors&quot;</li>\n<li>And within parentheses, a URL for a git repository must be provided</li>\n<li>The check is case insensitive and does not validate whether the familyname is correct, even though we'd expect it is (and we may soon update the check to validate that aspect as well!)\nHere is an example of a valid copyright string:\n&quot;Copyright 2017 The Archivo Black Project Authors (<a href=\"https://github.com/Omnibus-Type/ArchivoBlack\">https://github.com/Omnibus-Type/ArchivoBlack</a>)&quot;</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/valid_filename_values": {
        "description": "METADATA.pb font.filename field contains font name in right format?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/100",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/valid_full_name_values": {
        "description": "METADATA.pb font.full_name field contains font name in right format?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/099",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/valid_name_values": {
        "description": "METADATA.pb font.name field contains font name in right format?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/098",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/metadata/valid_post_script_name_values": {
        "description": "METADATA.pb font.post_script_name field contains font name in right format?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/101",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/missing_small_caps_glyphs": {
        "description": "Check small caps glyphs are available.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3154",
        "rationale": "<p>Ensure small caps glyphs are available if a font declares smcp or c2sc OT features.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/monospace": {
        "description": "Checking correctness of monospaced metadata.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/033",
        "rationale": "<p>There are various metadata in the OpenType spec to specify if a font is monospaced or not. If the font is not truly monospaced, then no monospaced metadata should be set (as sometimes they mistakenly are...)\nRequirements for monospace fonts:</p>\n<ul>\n<li>post.isFixedPitch - &quot;Set to 0 if the font is proportionally spaced, non-zero if the font is not proportionally spaced (monospaced)&quot;\n<a href=\"http://www.microsoft.com/typography/otspec/post.htm\">www.microsoft.com/typography/otspec/post.htm</a></li>\n<li>hhea.advanceWidthMax must be correct, meaning no glyph's width value is greater.\n<a href=\"http://www.microsoft.com/typography/otspec/hhea.htm\">www.microsoft.com/typography/otspec/hhea.htm</a></li>\n<li>OS/2.panose.bProportion must be set to 9 (monospace). Spec says: &quot;The PANOSE definition contains ten digits each of which currently describes up to sixteen variations. Windows uses bFamilyType, bSerifStyle and bProportion in the font mapper to determine family type. It also uses bProportion to determine if the font is monospaced.&quot;\n<a href=\"http://www.microsoft.com/typography/otspec/os2.htm#pan\">www.microsoft.com/typography/otspec/os2.htm#pan</a>\nmonotypecom-test.monotype.de/services/pan2</li>\n<li>OS/2.xAvgCharWidth must be set accurately.\n&quot;OS/2.xAvgCharWidth is used when rendering monospaced fonts, at least by Windows GDI&quot;\n<a href=\"http://typedrawers.com/discussion/comment/15397/#Comment_15397\">http://typedrawers.com/discussion/comment/15397/#Comment_15397</a>\nAlso we should report an error for glyphs not of average width.\nPlease also note:\nThomas Phinney told us that a few years ago (as of December 2019), if you gave a font a monospace flag in Panose, Microsoft Word would ignore the actual advance widths and treat it as monospaced. Source: <a href=\"https://typedrawers.com/discussion/comment/45140/#Comment_45140\">https://typedrawers.com/discussion/comment/45140/#Comment_45140</a></li>\n</ul>\n",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.google.fonts/check/name/ascii_only_entries": {
        "description": "Are there non-ASCII characters in ASCII-only NAME table entries?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": [
            "legacy:check/074",
            "https://github.com/googlefonts/fontbakery/issues/1663"
        ],
        "rationale": "<p>The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).\nFor COPYRIGHT_NOTICE (nameID 0) ASCII is required because that string should be the same in CFF fonts which also have this requirement in the OpenType spec.\nNote:\nA common place where we find non-ASCII strings is on name table entries with NameID &gt; 18, which are expressly for localising the ASCII-only IDs into Hindi / Arabic / etc.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/copyright_length": {
        "description": "Length of copyright notice must not exceed 500 characters.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1603",
        "rationale": "<p>This is an arbitrary max length for the copyright notice field of the name table. We simply don't want such notices to be too long. Typically such notices are actually much shorter than this with a length of roughly 70 or 80 characters.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/description_max_length": {
        "description": "Description strings in the name table must not exceed 200 characters.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/032",
        "rationale": "<p>An old FontLab version had a bug which caused it to store copyright notices in nameID 10 entries.\nIn order to detect those and distinguish them from actual legitimate usage of this name table entry, we expect that such strings do not exceed a reasonable length of 200 chars.\nLonger strings are likely instances of the FontLab bug.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/family_and_style_max_length": {
        "description": "Combined length of family and style must not exceed 27 characters.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1488",
        "rationale": "<p>According to a GlyphsApp tutorial [1], in order to make sure all versions of Windows recognize it as a valid font file, we must make sure that the concatenated length of the familyname (NameID.FONT_FAMILY_NAME) and style (NameID.FONT_SUBFAMILY_NAME) strings in the name table do not exceed 20 characters.\nAfter discussing the problem in more detail at `FontBakery issue #2179 [2] we decided that allowing up to 27 chars would still be on the safe side, though.\n[1] <a href=\"https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances\">https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances</a>\n[2] <a href=\"https://github.com/googlefonts/fontbakery/issues/2179\">https://github.com/googlefonts/fontbakery/issues/2179</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/familyname": {
        "description": "Check name table: FONT_FAMILY_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/157",
        "rationale": "<p>Checks that the family name infered from the font filename matches the string at nameID 1 (NAMEID_FONT_FAMILY_NAME) if it conforms to RIBBI and otherwise checks that nameID 1 is the family name + the style name.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/familyname_first_char": {
        "description": "Make sure family name does not begin with a digit.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/067",
        "rationale": "<p>Font family names which start with a numeral are often not discoverable in Windows applications.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/fullfontname": {
        "description": "Check name table: FULL_FONT_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/159",
        "rationale": "<p>Requirements for the FULL_FONT_NAME entries in the 'name' table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/license": {
        "description": "Check copyright namerecords match license file.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/029",
        "rationale": "<p>A known licensing description must be provided in the NameID 14 (LICENSE DESCRIPTION) entries of the name table.\nThe source of truth for this check (to determine which license is in use) is a file placed side-by-side to your font project including the licensing terms.\nDepending on the chosen license, one of the following string snippets is expected to be found on the NameID 13 (LICENSE DESCRIPTION) entries of the name table:</p>\n<ul>\n<li>&quot;This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: <a href=\"https://scripts.sil.org/OFL\">https://scripts.sil.org/OFL</a>&quot;</li>\n<li>&quot;Licensed under the Apache License, Version 2.0&quot;</li>\n<li>&quot;Licensed under the Ubuntu Font Licence 1.0.&quot;\nCurrently accepted licenses are Apache or Open Font License.\nFor a small set of legacy families the Ubuntu Font License may be acceptable as well.\nWhen in doubt, please choose OFL for new font projects.</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/license_url": {
        "description": "License URL matches License text on name table?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/030",
        "rationale": "<p>A known license URL must be provided in the NameID 14 (LICENSE INFO URL) entry of the name table.\nThe source of truth for this check is the licensing text found on the NameID 13 entry (LICENSE DESCRIPTION).\nThe string snippets used for detecting licensing terms are:</p>\n<ul>\n<li>&quot;This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: <a href=\"https://scripts.sil.org/OFL\">https://scripts.sil.org/OFL</a>&quot;</li>\n<li>&quot;Licensed under the Apache License, Version 2.0&quot;</li>\n<li>&quot;Licensed under the Ubuntu Font Licence 1.0.&quot;\nCurrently accepted licenses are Apache or Open Font License.\nFor a small set of legacy families the Ubuntu Font License may be acceptable as well.\nWhen in doubt, please choose OFL for new font projects.</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/line_breaks": {
        "description": "Name table entries should not contain line-breaks.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/057",
        "rationale": "<p>There are some entries on the name table that may include more than one line of text. The Google Fonts team, though, prefers to keep the name table entries short and simple without line breaks.\nFor instance, some designers like to include the full text of a font license in the &quot;copyright notice&quot; entry, but for the GFonts collection this entry should only mention year, author and other basic info in a manner enforced by com.google.fonts/check/font_copyright</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/mandatory_entries": {
        "description": "Font has all mandatory 'name' table entries?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/156",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/match_familyname_fullfont": {
        "description": "Does full font name begin with the font family name?",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/068",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.google.fonts/check/name/no_copyright_on_description": {
        "description": "Description strings in the name table must not contain copyright info.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "name",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/031",
        "sections": [
            "fontbakery.profiles.name"
        ]
    },
    "com.google.fonts/check/name/postscriptname": {
        "description": "Check name table: POSTSCRIPT_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/160",
        "rationale": "<p>Requirements for the POSTSCRIPT_NAME entries in the 'name' table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/rfn": {
        "description": "Name table strings must not contain the string 'Reserved Font Name'.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1380",
        "rationale": "<p>Some designers adopt the &quot;Reserved Font Name&quot; clause of the OFL license. This means that the original author reserves the rights to the family name and other people can only distribute modified versions using a different family name.\nGoogle Fonts published updates to the fonts in the collection in order to fix issues and/or implement further improvements to the fonts. It is important to keep the family name so that users of the webfonts can benefit from the updates. Since it would forbid such usage scenario, all families in the GFonts collection are required to not adopt the RFN clause.\nThis check ensures &quot;Reserved Font Name&quot; is not mentioned in the name table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/subfamilyname": {
        "description": "Check name table: FONT_SUBFAMILY_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/158",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/trailing_spaces": {
        "description": "Name table records must not have trailing spaces.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2417",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/name/typographicfamilyname": {
        "description": "Check name table: TYPOGRAPHIC_FAMILY_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/161",
        "rationale": "<p>Requirements for the TYPOGRAPHIC_FAMILY_NAME entries in the 'name' table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/typographicsubfamilyname": {
        "description": "Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/162",
        "rationale": "<p>Requirements for the TYPOGRAPHIC_SUBFAMILY_NAME entries in the 'name' table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/unwanted_chars": {
        "description": "Substitute copyright, registered and trademark symbols in name table entries.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/019",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/name/version_format": {
        "description": "Version format is correct in 'name' table?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/055",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/no_debugging_tables": {
        "description": "Ensure fonts do not contain any pre-production tables.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3357",
        "rationale": "<p>Tables such as <code>Debg</code> are useful in the pre-production stages of font development, but add unnecessary bloat to a production font and should be removed before release.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 6
    },
    "com.google.fonts/check/old_ttfautohint": {
        "description": "Font has old ttfautohint applied?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/056",
        "rationale": "<p>Check if font has been hinted with an outdated version of ttfautohint.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/os2/use_typo_metrics": {
        "description": "OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3241",
        "rationale": "<p>All fonts on the Google Fonts collection should have OS/2.fsSelection bit 7 (USE_TYPO_METRICS) set. This requirement is part of the vertical metrics scheme established as a Google Fonts policy aiming at a common ground supported by all major font rendering environments.\nFor more details, read:\n<a href=\"https://github.com/googlefonts/gf-docs/blob/main/VerticalMetrics/README.md\">https://github.com/googlefonts/gf-docs/blob/main/VerticalMetrics/README.md</a>\nBelow is the portion of that document that is most relevant to this check:\nUse_Typo_Metrics must be enabled. This will force MS Applications to use the OS/2 Typo values instead of the Win values. By doing this, we can freely set the Win values to avoid clipping and control the line height with the typo values. It has the added benefit of future line height compatibility. When a new script is added, we simply change the Win values to the new yMin and yMax, without needing to worry if the line height have changed.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/os2_metrics_match_hhea": {
        "description": "Checking OS/2 Metrics match hhea Metrics.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/042",
        "rationale": "<p>OS/2 and hhea vertical metric values should match. This will produce the same linespacing on Mac, GNU+Linux and Windows.</p>\n<ul>\n<li>Mac OS X uses the hhea values.</li>\n<li>Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.\nWhen OS/2 and hhea vertical metrics match, the same linespacing results on macOS, GNU+Linux and Windows. Unfortunately as of 2018, Google Fonts has released many fonts with vertical metrics that don't match in this way. When we fix this issue in these existing families, we will create a visible change in line/paragraph layout for either Windows or macOS users, which will upset some of them.\nBut we have a duty to fix broken stuff, and inconsistent paragraph layout is unacceptably broken when it is possible to avoid it.\nIf users complain and prefer the old broken version, they have the freedom to take care of their own situation.</li>\n</ul>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/ots": {
        "description": "Checking with ots-sanitize.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/036",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/outline_alignment_miss": {
        "description": "Are there any misaligned on-curve points?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "outline",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3088",
        "rationale": "<p>This check heuristically looks for on-curve points which are close to, but do not sit on, significant boundary coordinates. For example, a point which has a Y-coordinate of 1 or -1 might be a misplaced baseline point. As well as the baseline, here we also check for points near the x-height (but only for lower case Latin letters), cap-height, ascender and descender Y coordinates.\nNot all such misaligned curve points are a mistake, and sometimes the design may call for points in locations near the boundaries. As this check is liable to generate significant numbers of false positives, it will pass if there are more than 100 reported misalignments.</p>\n",
        "sections": [
            "Outline Correctness Checks"
        ]
    },
    "com.google.fonts/check/outline_colinear_vectors": {
        "description": "Do any segments have colinear vectors?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "outline",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3088",
        "rationale": "<p>This check looks for consecutive line segments which have the same angle. This normally happens if an outline point has been added by accident.\nThis check is not run for variable fonts, as they may legitimately have colinear vectors.</p>\n",
        "sections": [
            "Outline Correctness Checks"
        ]
    },
    "com.google.fonts/check/outline_jaggy_segments": {
        "description": "Do outlines contain any jaggy segments?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "outline",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3064",
        "rationale": "<p>This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.</p>\n",
        "sections": [
            "Outline Correctness Checks"
        ]
    },
    "com.google.fonts/check/outline_semi_vertical": {
        "description": "Do outlines contain any semi-vertical or semi-horizontal lines?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "outline",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3088",
        "rationale": "<p>This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.\nThis check is disabled for italic styles, which often contain nearly-upright lines.</p>\n",
        "sections": [
            "Outline Correctness Checks"
        ]
    },
    "com.google.fonts/check/outline_short_segments": {
        "description": "Are any segments inordinately short?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "outline",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3088",
        "rationale": "<p>This check looks for outline segments which seem particularly short (less than 0.6% of the overall path length).\nThis check is not run for variable fonts, as they may legitimately have short segments. As this check is liable to generate significant numbers of false positives, it will pass if there are more than 100 reported short segments.</p>\n",
        "sections": [
            "Outline Correctness Checks"
        ]
    },
    "com.google.fonts/check/points_out_of_bounds": {
        "description": "Check for points out of bounds.",
        "profiles": [
            "universal",
            "glyf",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/735",
        "sections": [
            "fontbakery.profiles.glyf"
        ]
    },
    "com.google.fonts/check/post_table_version": {
        "description": "Font has correct post table version?",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "googlefonts",
            "post",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": [
            "legacy:check/015",
            "https://github.com/google/fonts/issues/215",
            "https://github.com/googlefonts/fontbakery/issues/2638"
        ],
        "rationale": "<p>Apple recommends against using 'post' table format 3 under most circumstances, as it can create problems with some printer drivers and PDF documents. The savings in disk space usually does not justify the potential loss in functionality.\nSource: <a href=\"https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html\">https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html</a>\nThe CFF2 table does not contain glyph names, so variable OTFs should be allowed to use post table version 2.\nThis check expects:</p>\n<ul>\n<li>Version 2 for TTF or OTF CFF2 Variable fonts</li>\n<li>Version 3 for OTF</li>\n</ul>\n",
        "sections": [
            "fontbakery.profiles.post"
        ]
    },
    "com.google.fonts/check/production_glyphs_similarity": {
        "description": "Glyphs are similiar to Google Fonts version?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/118",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/render_own_name": {
        "description": "Check font can render its own name.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3159",
        "rationale": "<p>A base expectation is that a font family's regular/default (400 roman) style can render its 'menu name' (nameID 1) in itself.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/repo/dirname_matches_nameid_1": {
        "description": "Directory name in GFonts repo structure must match NameID 1 of the regular.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2302",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/repo/fb_report": {
        "description": "A font repository should not include fontbakery report files",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2888",
        "rationale": "<p>A FontBakery report is ephemeral and so should be used for posting issues on a bug-tracker instead of being hosted in the font project repository.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/repo/sample_image": {
        "description": "Check README.md has a sample image.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2898",
        "rationale": "<p>In order to showcase what a font family looks like, the project's README.md file should ideally include a sample image and highlight it in the upper portion of the document, no more than 10 lines away from the top of the file.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/repo/upstream_yaml_has_required_fields": {
        "description": "Check upstream.yaml file contains all required fields",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3338",
        "rationale": "<p>If a family has been pushed using the gftools packager, we must check that all the required fields in the upstream.yaml file have been populated.</p>\n",
        "sections": [
            "Google Fonts"
        ],
        "severity": 10
    },
    "com.google.fonts/check/repo/vf_has_static_fonts": {
        "description": "A static fonts directory with at least two fonts must accompany variable fonts",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2654",
        "rationale": "<p>Variable font family directories kept in the google/fonts git repo may include a static/ subdir containing static fonts.\nThese files are meant to be served for users that still lack support for variable fonts in their web browsers.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/repo/zip_files": {
        "description": "A font repository should not include ZIP files",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2903",
        "rationale": "<p>Sometimes people check in ZIPs into their font project repositories. While we accept the practice of checking in binaries, we believe that a ZIP is a step too far ;)\nNote: a source purist position is that only source files and build scripts should be checked in.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/required_tables": {
        "description": "Font contains all required tables?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/052",
        "rationale": "<p>Depending on the typeface and coverage of a font, certain tables are recommended for optimum quality. For example, the performance of a non-linear font is improved if the VDMX, LTSH, and hdmx tables are present. Non-monospaced Latin fonts should have a kern table. A gasp table is necessary if a designer wants to influence the sizes at which grayscaling is used under Windows. Etc.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/rupee": {
        "description": "Ensure indic fonts have the Indian Rupee Sign glyph. ",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2967",
        "rationale": "<p>Per Bureau of Indian Standards every font supporting one of the official Indian languages needs to include Unicode Character \u201c\u20b9\u201d (U+20B9) Indian Rupee Sign.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/shaping/collides": {
        "description": "Check that no collisions are found while shaping",
        "profiles": [
            "shaping",
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3223",
        "rationale": "<p>Fonts with complex layout rules can benefit from regression tests to ensure that the rules are behaving as designed. This checks runs a shaping test suite and reports instances where the glyphs collide in unexpected ways.\nShaping test suites should be written by the font engineer and referenced in the fontbakery configuration file. For more information about write shaping test files and how to configure fontbakery to read the shaping test suites, see <a href=\"https://simoncozens.github.io/tdd-for-otl/\">https://simoncozens.github.io/tdd-for-otl/</a></p>\n",
        "sections": [
            "Shaping Checks"
        ]
    },
    "com.google.fonts/check/shaping/forbidden": {
        "description": "Check that no forbidden glyphs are found while shaping",
        "profiles": [
            "shaping",
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3223",
        "rationale": "<p>Fonts with complex layout rules can benefit from regression tests to ensure that the rules are behaving as designed. This checks runs a shaping test suite and reports if any glyphs are generated in the shaping which should not be produced. (For example, .notdef glyphs, visible viramas, etc.)\nShaping test suites should be written by the font engineer and referenced in the fontbakery configuration file. For more information about write shaping test files and how to configure fontbakery to read the shaping test suites, see <a href=\"https://simoncozens.github.io/tdd-for-otl/\">https://simoncozens.github.io/tdd-for-otl/</a></p>\n",
        "sections": [
            "Shaping Checks"
        ]
    },
    "com.google.fonts/check/shaping/regression": {
        "description": "Check that texts shape as per expectation",
        "profiles": [
            "shaping",
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3223",
        "rationale": "<p>Fonts with complex layout rules can benefit from regression tests to ensure that the rules are behaving as designed. This checks runs a shaping test suite and compares expected shaping against actual shaping, reporting any differences.\nShaping test suites should be written by the font engineer and referenced in the fontbakery configuration file. For more information about write shaping test files and how to configure fontbakery to read the shaping test suites, see <a href=\"https://simoncozens.github.io/tdd-for-otl/\">https://simoncozens.github.io/tdd-for-otl/</a></p>\n",
        "sections": [
            "Shaping Checks"
        ]
    },
    "com.google.fonts/check/smart_dropout": {
        "description": "Font enables smart dropout control in \"prep\" table instructions?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/072",
        "rationale": "<p>This setup is meant to ensure consistent rendering quality for fonts across all devices (with different rendering/hinting capabilities).\nBelow is the snippet of instructions we expect to see in the fonts:\nB8 01 FF    PUSHW 0x01FF\n85          SCANCTRL (unconditinally turn on\ndropout control mode)\nB0 04       PUSHB 0x04\n8D          SCANTYPE (enable smart dropout control)\n&quot;Smart dropout control&quot; means activating rules 1, 2 and 5:\nRule 1: If a pixel's center falls within the glyph outline,\nthat pixel is turned on.\nRule 2: If a contour falls exactly on a pixel's center,\nthat pixel is turned on.\nRule 5: If a scan line between two adjacent pixel centers\n(either vertical or horizontal) is intersected\nby both an on-Transition contour and an off-Transition\ncontour and neither of the pixels was already turned on\nby rules 1 and 2, turn on the pixel which is closer to\nthe midpoint between the on-Transition contour and\noff-Transition contour. This is &quot;Smart&quot; dropout control.\nFor more detailed info (such as other rules not enabled in this snippet), please refer to the TrueType Instruction Set documentation.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/stylisticset_description": {
        "description": "Ensure Stylistic Sets have description.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3155",
        "rationale": "<p>Stylistic sets should provide description text. Programs such as InDesign, TextEdit and Inkscape use that info to display to the users so that they know what a given stylistic set offers.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/superfamily/list": {
        "description": "List all superfamily filepaths",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1487",
        "rationale": "<p>This is a merely informative check that lists all sibling families detected by fontbakery.\nOnly the fontfiles in these directories will be considered in superfamily-level checks.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/superfamily/vertical_metrics": {
        "description": "Each font in set of sibling families must have the same set of vertical metrics values.",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1487",
        "rationale": "<p>We may want all fonts within a super-family (all sibling families) to have the same vertical metrics so their line spacing is consistent across the super-family.\nThis is an experimental extended version of com.google.fonts/check/family/vertical_metrics and for now it will only result in WARNs.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/transformed_components": {
        "description": "Ensure component transforms do not perform scaling or rotation.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2011",
        "rationale": "<p>Some families have glyphs which have been constructed by using transformed components e.g the 'u' being constructed from a flipped 'n'.\nFrom a designers point of view, this sounds like a win (less work). However, such approaches can lead to rasterization issues, such as having the 'u' not sitting on the baseline at certain sizes after running the font through ttfautohint.\nAs of July 2019, Marc Foley observed that ttfautohint assigns cvt values to transformed glyphs as if they are not transformed and the result is they render very badly, and that vttLib does not support flipped components.\nWhen building the font with fontmake, this problem can be fixed by using the &quot;Decompose Transformed Components&quot; filter.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/ttx-roundtrip": {
        "description": "Checking with fontTools.ttx",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1763",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/unicode_range_bits": {
        "description": "Ensure UnicodeRange bits are properly set.",
        "profiles": [
            "notofonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2676",
        "rationale": "<p>When the UnicodeRange bits on the OS/2 table are not properly set, some programs running on Windows may not recognize the font and use a system fallback font instead. For that reason, this check calculates the proper settings by inspecting the glyphs declared on the cmap table and then ensures that their corresponding ranges are enabled.</p>\n",
        "sections": [
            "Noto Fonts"
        ]
    },
    "com.google.fonts/check/unique_glyphnames": {
        "description": "Font contains unique glyph names?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/059",
        "rationale": "<p>Duplicate glyph names prevent font installation on Mac OS X.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/unitsperem": {
        "description": "Checking unitsPerEm value is reasonable.",
        "profiles": [
            "universal",
            "notofonts",
            "head",
            "googlefonts",
            "opentype",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/043",
        "rationale": "<p>According to the OpenType spec:\nThe value of unitsPerEm at the head table must be a value between 16 and 16384. Any value in this range is valid.\nIn fonts that have TrueType outlines, a power of 2 is recommended as this allows performance optimizations in some rasterizers.\nBut 1000 is a commonly used value. And 2000 may become increasingly more common on Variable Fonts.</p>\n",
        "sections": [
            "fontbakery.profiles.head"
        ]
    },
    "com.google.fonts/check/unitsperem_strict": {
        "description": "Stricter unitsPerEm criteria for Google Fonts. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/116",
        "rationale": "<p>Even though the OpenType spec allows unitsPerEm to be any value between 16 and 16384, the Google Fonts project aims at a narrower set of reasonable values.\nThe spec suggests usage of powers of two in order to get some performance improvements on legacy renderers, so those values are acceptable.\nBut values of 500 or 1000 are also acceptable, with the added benefit that it makes upm math easier for designers, while the performance hit of not using a power of two is most likely negligible nowadays.\nAdditionally, values above 2048 would likely result in unreasonable filesize increases.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/unreachable_glyphs": {
        "description": "Check font contains no unreachable glyphs",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3160",
        "rationale": "<p>Glyphs are either accessible directly through Unicode codepoints or through substitution rules. Any glyphs not accessible by either of these means are redundant and serve only to increase the font's file size.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/unwanted_tables": {
        "description": "Are there unwanted tables?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/053",
        "rationale": "<p>Some font editors store source data in their own SFNT tables, and these can sometimes sneak into final release files, which should only have OpenType spec tables.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/usweightclass": {
        "description": "Checking OS/2 usWeightClass.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/020",
        "rationale": "<p>Google Fonts expects variable fonts, static ttfs and static otfs to have differing OS/2 usWeightClass values.\nFor Variable Fonts, Thin-Black must be 100-900\nFor static ttfs, Thin-Black can be 100-900 or 250-900\nFor static otfs, Thin-Black must be 250-900\nIf static otfs are set lower than 250, text may appear blurry in legacy Windows applications.\nGlyphsapp users can change the usWeightClass value of an instance by adding a 'weightClass' customParameter.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/valid_glyphnames": {
        "description": "Glyph names are all valid?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "fontwerk"
        ],
        "proposal": [
            "legacy:check/058",
            "https://github.com/googlefonts/fontbakery/issues/2832"
        ],
        "rationale": "<p>Microsoft's recommendations for OpenType Fonts states the following:\n'NOTE: The PostScript glyph name must be no longer than 31 characters, include only uppercase or lowercase English letters, European digits, the period or the underscore, i.e. from the set [A-Za-z0-9_.] and should start with a letter, except the special glyph name &quot;.notdef&quot; which starts with a period.'\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table\">https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table</a>\nIn practice, though, particularly in modern environments, glyph names can be as long as 63 characters.\nAccording to the &quot;Adobe Glyph List Specification&quot; available at:\n<a href=\"https://github.com/adobe-type-tools/agl-specification\">https://github.com/adobe-type-tools/agl-specification</a></p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/valid_glyphnames:adobefonts": {
        "description": "Glyph names are all valid? (derived from com.google.fonts/check/valid_glyphnames)",
        "profiles": [
            "adobefonts"
        ],
        "rationale": "<p>Microsoft's recommendations for OpenType Fonts states the following:\n'NOTE: The PostScript glyph name must be no longer than 31 characters, include only uppercase or lowercase English letters, European digits, the period or the underscore, i.e. from the set [A-Za-z0-9_.] and should start with a letter, except the special glyph name &quot;.notdef&quot; which starts with a period.'\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table\">https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table</a>\nIn practice, though, particularly in modern environments, glyph names can be as long as 63 characters.\nAccording to the &quot;Adobe Glyph List Specification&quot; available at:\n<a href=\"https://github.com/adobe-type-tools/agl-specification\">https://github.com/adobe-type-tools/agl-specification</a></p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/varfont/bold_wght_coord": {
        "description": "The variable font 'wght' (Weight) axis coordinate must be 700 on the 'Bold' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>The Open-Type spec's registered design-variation tag 'wght' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght</a> does not specify a required value for the 'Bold' instance of a variable font.\nBut Dave Crossland suggested that we should enforce a required value of 700 in this case.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/consistent_axes": {
        "description": "Ensure that all variable font files have the same set of axes and axis ranges.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2810",
        "rationale": "<p>In order to facilitate the construction of intuitive and friendly user interfaces, all variable font files in a given family should have the same set of variation axes. Also, each axis must have a consistent setting of min/max value ranges accross all the files.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont/generate_static": {
        "description": "Check a static ttf can be generated from a variable font.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1727",
        "rationale": "<p>Google Fonts may serve static fonts which have been generated from variable fonts. This test will attempt to generate a static ttf using fontTool's varLib mutator.\nThe target font will be the mean of each axis e.g:\n<strong>VF font axes</strong></p>\n<ul>\n<li>min weight, max weight = 400, 800</li>\n<li>min width, max width = 50, 100\n<strong>Target Instance</strong></li>\n<li>weight = 600</li>\n<li>width = 75</li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont/grade_reflow": {
        "description": "Ensure VFs with the GRAD axis do not vary horizontal advance. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3187",
        "rationale": "<p>The grade (GRAD) axis should not change any advanceWidth or kerning data across its design space. This is because altering the advance width of glyphs can cause text reflow.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont/has_HVAR": {
        "description": "Check that variable fonts have an HVAR table.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2119",
        "rationale": "<p>Not having a HVAR table can lead to costly text-layout operations on some platforms, which we want to avoid.\nSo, all variable fonts on the Google Fonts collection should have an HVAR with valid values.\nMore info on the HVAR table can be found at:\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements\">https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont/regular_ital_coord": {
        "description": "The variable font 'ital' (Italic) axis coordinate must be zero on the 'Regular' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'ital' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_ital\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_ital</a>\nIf a variable font has a 'ital' (Italic) axis, then the coordinate of its 'Regular' instance is required to be zero.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/regular_opsz_coord": {
        "description": "The variable font 'opsz' (Optical Size) axis coordinate should be between 10 and 16 on the 'Regular' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'opsz' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz</a>\nIf a variable font has an 'opsz' (Optical Size) axis, then the coordinate of its 'Regular' instance is recommended to be a value in the range 10 to 16.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/regular_slnt_coord": {
        "description": "The variable font 'slnt' (Slant) axis coordinate must be zero on the 'Regular' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'slnt' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_slnt\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_slnt</a>\nIf a variable font has a 'slnt' (Slant) axis, then the coordinate of its 'Regular' instance is required to be zero.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/regular_wdth_coord": {
        "description": "The variable font 'wdth' (Width) axis coordinate must be 100 on the 'Regular' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'wdth' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth</a>\nIf a variable font has a 'wdth' (Width) axis, then the coordinate of its 'Regular' instance is required to be 100.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/regular_wght_coord": {
        "description": "The variable font 'wght' (Weight) axis coordinate must be 400 on the 'Regular' instance.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1707",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'wght' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght</a>\nIf a variable font has a 'wght' (Weight) axis, then the coordinate of its 'Regular' instance is required to be 400.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/slnt_range": {
        "description": "The variable font 'slnt' (Slant) axis coordinate specifies positive values in its range? ",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2572",
        "rationale": "<p>The OpenType spec says at <a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt\">https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt</a> that:\n[...] the scale for the Slant axis is interpreted as the angle of slant in counter-clockwise degrees from upright. This means that a typical, right-leaning oblique design will have a negative slant value. This matches the scale used for the italicAngle field in the post table.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/stat_axis_record_for_each_axis": {
        "description": "All fvar axes have a correspondent Axis Record on STAT table? ",
        "profiles": [
            "universal",
            "stat",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/3017",
        "rationale": "<p>According to the OpenType spec, there must be an Axis Record for every axis defined in the fvar table.\n<a href=\"https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records\">https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records</a></p>\n",
        "sections": [
            "fontbakery.profiles.stat"
        ]
    },
    "com.google.fonts/check/varfont/unsupported_axes": {
        "description": "Ensure VFs do not contain slnt or ital axes. ",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2866",
        "rationale": "<p>The 'ital' and 'slnt' axes are not supported yet in Google Chrome.\nFor the time being, we need to ensure that VFs do not contain either of these axes. Once browser support is better, we can deprecate this check.\nFor more info regarding browser support, see:\n<a href=\"https://arrowtype.github.io/vf-slnt-test/\">https://arrowtype.github.io/vf-slnt-test/</a></p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont/wdth_valid_range": {
        "description": "The variable font 'wdth' (Weight) axis coordinate must be within spec range of 1 to 1000 on all instances.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2520",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'wdth' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth</a>\nOn the 'wdth' (Width) axis, the valid coordinate range is 1-1000</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont/wght_valid_range": {
        "description": "The variable font 'wght' (Weight) axis coordinate must be within spec range of 1 to 1000 on all instances.",
        "profiles": [
            "universal",
            "notofonts",
            "opentype",
            "fvar",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2264",
        "rationale": "<p>According to the Open-Type spec's registered design-variation tag 'wght' available at <a href=\"https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght\">https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght</a>\nOn the 'wght' (Weight) axis, the valid coordinate range is 1-1000.</p>\n",
        "sections": [
            "fontbakery.profiles.fvar"
        ]
    },
    "com.google.fonts/check/varfont_duplicate_instance_names": {
        "description": "Check variable font instances don't have duplicate names",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2986",
        "rationale": "<p>This check's purpose is to detect duplicate named instances names in a given variable font.\nRepeating instance names may be the result of instances for several VF axes defined in <code>fvar</code>, but since currently only weight+italic tokens are allowed in instance names as per GF specs, they ended up repeating.\nInstead, only a base set of fonts for the most default representation of the family can be defined through instances in the <code>fvar</code> table, all other instances will have to be left to access through the <code>STAT</code> table.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont_has_instances": {
        "description": "A variable font must have named instances.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2127",
        "rationale": "<p>Named instances must be present in all variable fonts in order not to frustrate the users' typical expectations of a traditional static font workflow.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont_instance_coordinates": {
        "description": "Check variable font instances have correct coordinate values",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2520",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont_instance_names": {
        "description": "Check variable font instances have correct names",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/pull/2520",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/varfont_weight_instances": {
        "description": "Variable font weight coordinates must be multiples of 100.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2258",
        "rationale": "<p>The named instances on the weight axis of a variable font must have coordinates that are multiples of 100 on the design space.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/vendor_id": {
        "description": "Checking OS/2 achVendID.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/018",
        "rationale": "<p>Microsoft keeps a list of font vendors and their respective contact info. This list is updated regularly and is indexed by a 4-char &quot;Vendor ID&quot; which is stored in the achVendID field of the OS/2 table.\nRegistering your ID is not mandatory, but it is a good practice since some applications may display the type designer / type foundry contact info on some dialog and also because that info will be visible on Microsoft's website:\n<a href=\"https://docs.microsoft.com/en-us/typography/vendors/\">https://docs.microsoft.com/en-us/typography/vendors/</a>\nThis check verifies whether or not a given font's vendor ID is registered in that list or if it has some of the default values used by the most common font editors.\nEach new FontBakery release includes a cached copy of that list of vendor IDs. If you registered recently, you're safe to ignore warnings emitted by this check, since your ID will soon be included in one of our upcoming releases.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/version_bump": {
        "description": "Version number has increased since previous release on Google Fonts?",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "legacy:check/117",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/vertical_metrics_regressions": {
        "description": "Check if the vertical metrics of a family are similar to the same family hosted on Google Fonts.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/1162",
        "rationale": "<p>If the family already exists on Google Fonts, we need to ensure that the checked family's vertical metrics are similar. This check will test the following schema which was outlined in Fontbakery issue #1162 [1]:</p>\n<ul>\n<li>The family should visually have the same vertical metrics as the Regular style hosted on Google Fonts.</li>\n<li>If the family on Google Fonts has differing hhea and typo metrics, the family being checked should use the typo metrics for both the hhea and typo entries.</li>\n<li>If the family on Google Fonts has use typo metrics not enabled and the family being checked has it enabled, the hhea and typo metrics should use the family on Google Fonts winAscent and winDescent values.</li>\n<li>If the upms differ, the values must be scaled so the visual appearance is the same.\n[1] <a href=\"https://github.com/googlefonts/fontbakery/issues/1162\">https://github.com/googlefonts/fontbakery/issues/1162</a></li>\n</ul>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/vttclean": {
        "description": "There must not be VTT Talk sources in the font.",
        "profiles": [
            "googlefonts"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/2059",
        "rationale": "<p>The goal here is to reduce filesizes and improve pageloading when dealing with webfonts.\nThe VTT Talk sources are not necessary at runtime and endup being just dead weight when left embedded in the font binaries. The sources should be kept on the project files but stripped out when building release binaries.</p>\n",
        "sections": [
            "Google Fonts"
        ]
    },
    "com.google.fonts/check/whitespace_glyphnames": {
        "description": "Font has **proper** whitespace glyph names?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/048",
        "rationale": "<p>This check enforces adherence to recommended whitespace (codepoints 0020 and 00A0) glyph names according to the Adobe Glyph List.</p>\n",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/whitespace_glyphs": {
        "description": "Font contains glyphs for whitespace characters?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "fontwerk"
        ],
        "proposal": "legacy:check/047",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/whitespace_glyphs:adobefonts": {
        "description": "Font contains glyphs for whitespace characters? (derived from com.google.fonts/check/whitespace_glyphs)",
        "profiles": [
            "adobefonts"
        ],
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/whitespace_ink": {
        "description": "Whitespace glyphs have ink?",
        "profiles": [
            "universal",
            "notofonts",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/049",
        "sections": [
            "Universal"
        ]
    },
    "com.google.fonts/check/whitespace_widths": {
        "description": "Space and non-breaking space have the same width?",
        "profiles": [
            "universal",
            "hmtx",
            "notofonts",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/050",
        "sections": [
            "fontbakery.profiles.hmtx"
        ]
    },
    "com.google.fonts/check/xavgcharwidth": {
        "description": "Check if OS/2 xAvgCharWidth is correct.",
        "profiles": [
            "universal",
            "notofonts",
            "os2",
            "opentype",
            "googlefonts",
            "typenetwork",
            "adobefonts",
            "fontwerk"
        ],
        "proposal": "legacy:check/034",
        "sections": [
            "fontbakery.profiles.os2"
        ]
    },
    "io.github.abysstypeco/check/ytlc_sanity": {
        "description": "Check if ytlc values are sane in vf",
        "profiles": [
            "typenetwork"
        ],
        "proposal": "https://github.com/googlefonts/fontbakery/issues/3130",
        "rationale": "<p>This check follows the proposed values of the ytlc axis proposed by font bureau at the site url. add more later.</p>\n",
        "sections": [
            "Type Network"
        ]
    }
}
