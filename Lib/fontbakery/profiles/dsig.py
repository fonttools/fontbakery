from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/dsig'
)
def com_google_fonts_check_dsig(ttFont):
  """Does the font have a DSIG table?"""
  if "DSIG" in ttFont:
    yield PASS, "Digital Signature (DSIG) exists."
  else:
    yield FAIL, ("This font lacks a digital signature (DSIG table)."
                 " Some applications may require one (even if only a"
                 " dummy placeholder) in order to work properly.")
