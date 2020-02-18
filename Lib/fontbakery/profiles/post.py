from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/family/underline_thickness',
  rationale = """
    Dave C Lemon (Adobe Type Team) recommends setting the underline thickness to be consistent across the family.

    If thicknesses are not family consistent, words set on the same line which have different styles look strange.

    See also:
    https://twitter.com/typenerd1/status/690361887926697986
  """,
  misc_metadata = {
    'affects': [('InDesign', 'unspecified')]
  }
)
def com_google_fonts_check_family_underline_thickness(ttFonts):
  """Fonts have consistent underline thickness?"""
  underTs = {}
  underlineThickness = None
  failed = False
  for ttfont in ttFonts:
    fontname = ttfont.reader.file.name
    # stylename = style(fontname)
    ut = ttfont['post'].underlineThickness
    underTs[fontname] = ut
    if underlineThickness is None:
      underlineThickness = ut
    if ut != underlineThickness:
      failed = True

  if failed:
    msg = ("Thickness of the underline is not"
           " the same across this family. In order to fix this,"
           " please make sure that the underlineThickness value"
           " is the same in the 'post' table of all of this family"
           " font files.\n"
           "Detected underlineThickness values are:\n")
    for style in underTs.keys():
      msg += "\t{}: {}\n".format(style, underTs[style])
    yield FAIL, msg
  else:
    yield PASS, "Fonts have consistent underline thickness."


@check(
  id = 'com.google.fonts/check/post_table_version',
  rationale = """
    Apple recommends against using 'post' table format 3 under most circumstances, as it can create problems with some printer drivers and PDF documents. The savings in disk space usually does not justify the potential loss in functionality.
    Source: https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html

    The CFF2 table does not contain glyph names, so variable OTFs should be allowed to use post table version 2.

    This check expects:
    - Version 2 for TTF or OTF CFF2 Variable fonts
    - Version 3 for OTF
  """,
  misc_metadata = {
    'request': [
      'https://github.com/google/fonts/issues/215',
      'https://github.com/googlefonts/fontbakery/issues/2638'
    ]
  }
)
def com_google_fonts_check_post_table_version(ttFont, is_ttf):
  """Font has correct post table version?"""
  formatType = ttFont['post'].formatType
  is_var = "fvar" in ttFont.keys()
  is_cff2 = "CFF2" in ttFont.keys()
  if is_ttf or (is_var and is_cff2):
    expected = 2
  else:
    expected = 3
  if formatType != expected:
    yield FAIL, (f"Post table should be version {expected}"
                 f" instead of {formatType}.")
  else:
    yield PASS, f"Font has post table version {expected}."
