from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # NOQA pylint: disable=unused-import

profile_imports = [('.shared_conditions', ('missing_whitespace_chars',))]


@check(
  id = 'com.google.fonts/check/whitespace_widths',
  conditions = ['not missing_whitespace_chars']
)
def com_google_fonts_check_whitespace_widths(ttFont):
  """Whitespace and non-breaking space have the same width?"""
  from fontbakery.utils import get_glyph_name

  space_name = get_glyph_name(ttFont, 0x0020)
  nbsp_name = get_glyph_name(ttFont, 0x00A0)

  space_width = ttFont['hmtx'][space_name][0]
  nbsp_width = ttFont['hmtx'][nbsp_name][0]

  if space_width > 0 and space_width == nbsp_width:
    yield PASS, "Whitespace and non-breaking space have the same width."
  else:
    yield FAIL, ("Whitespace and non-breaking space have differing width:"
                 " Whitespace ({}) is {} font units wide, non-breaking space"
                 " ({}) is {} font units wide. Both should be positive and the"
                 " same.").format(space_name, space_width, nbsp_name,
                                  nbsp_width)
