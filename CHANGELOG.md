* 0.3.2 (2017-Oct-11):
  - Increased self-testing now covering a bit more than half of the google fonts testsuite (more self-testing to be done on upcoming releases).
  - overall refactoring of all test implementations so that they're all self-contained
  - updated prebuilt FVal binary (built from proper sources)
  - Added APIs used by the web dashboard and report documents
  - whitelist: a few legacy CamelCased familynames (test/109)
  - Added VTT-related tables to the list of unwanted tables (test/053)
  - fixed computation of font_metadata condition
  - fixed crash on fontbakery-check-font-version.py
  - added automated tests for the fixer scripts
  - deprecated pyfontaine tests (132 to 151)
  - deprecated the unified name table entries test (test/017) spliting it up into new individual per-entry tests (156 to 162)
  - overall bugfixing / code-quality improvements.

* 0.3.1 (2017-Aug-11):
  - Emergencial release to address broken 0.3.0 packaging.
  - setup.py: Added modules that were missing in previous release
  - setup.py: Fix Windows pathnames
  - New test: com.google.fonts/test/155 ("Copyright notice name entry matches those on METADATA.pb ?")
  - Updated requirement: Changed Copyright Notice format requirement (regex) on com.google.fonts/test/102 ("METADATA.pb: Copyright notice matches canonical pattern ?")

* 0.3.0 (2017-Aug-08):
  - New modular architecture for our testing framework. (see: https://github.com/googlefonts/fontbakery/issues/1388)
  - A total of 120 GoogleFonts tests.
  - 44 self-tests covering approximately a third of the code. (See: https://github.com/googlefonts/fontbakery/issues/1413)
  - Upstream tests were removed as out-of-scope (See: https://github.com/googlefonts/gf-glyphs-scripts).
  - Plenty of miscelanious fixes for tests; Overall improved reliability.
