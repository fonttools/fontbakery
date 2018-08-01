Below are the most important changes from each release.
A more detailed list of changes is available in the corresponding milestones for each release in the Github issue tracker (https://github.com/googlefonts/fontbakery/milestones?state=closed).

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
