from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # NOQA pylint: disable=unused-import

profile_imports = [('.shared_conditions', ('missing_whitespace_chars',))]


@check(
  id = 'com.google.fonts/check/whitespace_widths',
  conditions = ['not missing_whitespace_chars']
)
def com_google_fonts_check_whitespace_widths(ttFont):
  """Space and non-breaking space have the same width?"""
  from fontbakery.utils import get_glyph_name

  space_name = get_glyph_name(ttFont, 0x0020)
  nbsp_name = get_glyph_name(ttFont, 0x00A0)

  space_width = ttFont['hmtx'][space_name][0]
  nbsp_width = ttFont['hmtx'][nbsp_name][0]

  if space_width > 0 and space_width == nbsp_width:
    yield PASS, "Space and non-breaking space have the same width."
  else:
    yield FAIL,\
          Message("different-widths",
                  f"Space and non-breaking space have differing width:"
                  f" The space glyph named {space_name}"
                  f" is {space_width} font units wide,"
                  f" non-breaking space named ({nbsp_name})"
                  f" is {nbsp_width} font units wide, and"
                  f" both should be positive and the same."
                  f" GlyphsApp has \"Sidebearing arithmetic\""
                  f" (https://glyphsapp.com/tutorials/spacing)"
                  f" which allows you to set the non-breaking"
                  f" space width to always equal the space width.")
