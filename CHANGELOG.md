* 0.3.4:
  - Nomenclature change: font tests are now called "checks"
                         code-tests are now "tests"
  - All IDs were updated to use the "check" keyword such as "com.google.fonts/check/001"

* 0.3.3:
  - All auxiliary scripts have been moved into a separate python
    package called gftools (Google Fonts Tools) available at
    https://github.com/googlefonts/tools/ (source code repo on git) and at
    https://pypi.python.org/pypi/gftools (installable package on PyPI).
  - Fontbakery is now solely focused on font family automated quality checks.
  - new subcommand: list-italicangle (moved to gftools as well)
  - several bugfixes

* 0.3.2 (2017-Oct-11):
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

* 0.3.1 (2017-Aug-11):
  - Emergencial release to address broken 0.3.0 packaging.
  - setup.py: Added modules that were missing in previous release
  - setup.py: Fix Windows pathnames
  - New check: com.google.fonts/check/155 ("Copyright notice name entry matches those on METADATA.pb ?")
  - Updated requirement: Changed Copyright Notice format requirement (regex) on com.google.fonts/check/102 ("METADATA.pb: Copyright notice matches canonical pattern ?")

* 0.3.0 (2017-Aug-08):
  - New modular architecture for our framework of font checks. (see: https://github.com/googlefonts/fontbakery/issues/1388)
  - A total of 120 GoogleFonts checks.
  - 44 code tests covering approximately a third of the code. (See: https://github.com/googlefonts/fontbakery/issues/1413)
  - Upstream checks were removed as out-of-scope (See: https://github.com/googlefonts/gf-glyphs-scripts).
  - Plenty of miscelanious fixes for checks; Overall improved reliability.
