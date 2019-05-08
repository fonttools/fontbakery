from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/dsig',
  rationale = """
    Some programs expect fonts to have a digital signature
    declared in their DSIG table in order to work properly.

    This checks verifies that such signature is available in the font.

    Typically, even a fake signature would be enough to make the
    fonts work. If needed, such dummy-placeholder can be added to
    the font by using the `gftools fix-dsig` script available at
    https://github.com/googlefonts/gftools
  """
)
def com_google_fonts_check_dsig(ttFont):
  """Does the font have a DSIG table?"""
  if "DSIG" in ttFont:
    yield PASS, "Digital Signature (DSIG) exists."
  else:
    yield FAIL, ("This font lacks a digital signature (DSIG table)."
                 " Some applications may require one (even if only a"
                 " dummy placeholder) in order to work properly. You"
                 " can add a DSIG table by running the"
                 " `gftools fix-dsig` script.")
