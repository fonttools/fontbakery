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
           " the same accross this family. In order to fix this,"
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
  id = 'com.google.fonts/check/post_table_version'
)
def com_google_fonts_check_post_table_version(ttFont, is_ttf):
  """Font has correct post table version (2 for TTF, 3 for OTF)?"""
  formatType = ttFont['post'].formatType
  if is_ttf:
    expected = 2
  else:
    expected = 3
  if formatType != expected:
    yield FAIL, ("Post table should be version {} instead of {}."
                 " More info at https://github.com/google/fonts/"
                 "issues/215").format(expected, formatType)
  else:
    yield PASS, f"Font has post table version {expected}."
