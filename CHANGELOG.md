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
