from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/045'
)
def com_google_fonts_check_045(ttFont):
  """Does the font have a DSIG table?"""
  if "DSIG" in ttFont:
    yield PASS, "Digital Signature (DSIG) exists."
  else:
    yield FAIL, ("This font lacks a digital signature (DSIG table)."
                 " Some applications may require one (even if only a"
                 " dummy placeholder) in order to work properly.")
