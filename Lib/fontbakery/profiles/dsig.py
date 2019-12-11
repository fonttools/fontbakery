from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/dsig',
  rationale = """
    Microsoft Office 2013 and below products expect fonts to have a digital signature declared in a DSIG table in order to implement OpenType features. The EOL date for Microsoft Office 2013 products is 4/11/2023. This issue does not impact Microsoft Office 2016 and above products. 

    This checks verifies that this signature is available in the font.

    A fake signature is enough to address this issue. If needed, a dummy table can be added to the font with the `gftools fix-dsig` script available at https://github.com/googlefonts/gftools

    Reference: https://github.com/googlefonts/fontbakery/issues/1845
  """
)
def com_google_fonts_check_dsig(ttFont):
  """Does the font have a DSIG table?"""
  if "DSIG" in ttFont:
    yield PASS, "Digital Signature (DSIG) exists."
  else:
    yield FAIL,\
          Message("lacks-signature",
                  "This font lacks a digital signature (DSIG table)."
                  " Some applications may require one (even if only a"
                  " dummy placeholder) in order to work properly. You"
                  " can add a DSIG table by running the"
                  " `gftools fix-dsig` script.")
