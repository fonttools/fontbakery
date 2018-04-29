from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import PASS, FAIL
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = (
    ('.', ('shared_conditions', )),
)

@check(
  id = 'com.google.fonts/check/180'
)
def com_google_fonts_check_180(ttFont):
  """Does the number of glyphs in the loca table match the maxp table?"""
  if len(ttFont['loca']) < (ttFont['maxp'].numGlyphs + 1):
    yield FAIL, "Corrupt 'loca' table, or wrong numGlyphs in 'maxp' table."
  else:
    yield PASS, "'loca' table matches numGlyphs in 'maxp' table."
