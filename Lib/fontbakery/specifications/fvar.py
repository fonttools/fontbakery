from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('is_variable_font'
            , 'regular_wght_coord', 'regular_wdth_coord', 'regular_slnt_coord'
            , 'regular_ital_coord', 'regular_opsz_coord', 'bold_wght_coord'))
]

@check(
  id = 'com.google.fonts/check/167',
  rationale = """
    According to the Open-Type spec's registered
    design-variation tag 'wght' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght

    If a variable font has a 'wght' (Weight) axis, then the coordinate
    of its 'Regular' instance is required to be 400.
  """,
  conditions = ['is_variable_font',
                'regular_wght_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_167(ttFont, regular_wght_coord):
  """The variable font 'wght' (Weight) axis coordinate must be 400 on the
  'Regular' instance."""

  if regular_wght_coord == 400:
    yield PASS, "Regular:wght is 400."
  else:
    yield FAIL, ("The 'wght' axis coordinate of"
                 " the 'Regular' instance must be 400."
                 " Got a '{}' coordinate instead."
                 "").format(regular_wght_coord)


@check(
  id = 'com.google.fonts/check/168',
  rationale = """
    According to the Open-Type spec's registered
    design-variation tag 'wdth' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth

    If a variable font has a 'wdth' (Width) axis, then the coordinate
    of its 'Regular' instance is required to be 100.
  """,
  conditions = ['is_variable_font',
                'regular_wdth_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_168(ttFont, regular_wdth_coord):
  """The variable font 'wdth' (Width) axis coordinate must be 100 on the
  'Regular' instance."""

  if regular_wdth_coord == 100:
    yield PASS, "Regular:wdth is 100."
  else:
    yield FAIL, ("The 'wdth' coordinate of"
                 " the 'Regular' instance must be 100."
                 " Got {} as a default value instead."
                 "").format(regular_wdth_coord)


@check(
  id = 'com.google.fonts/check/169',
  rationale = """
    According to the Open-Type spec's registered
    design-variation tag 'slnt' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_slnt

    If a variable font has a 'slnt' (Slant) axis, then the coordinate
    of its 'Regular' instance is required to be zero.
  """,
  conditions = ['is_variable_font',
                'regular_slnt_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_169(ttFont, regular_slnt_coord):
  """The variable font 'slnt' (Slant) axis coordinate must be zero on the
  'Regular' instance."""

  if regular_slnt_coord == 0:
    yield PASS, "Regular:slnt is zero."
  else:
    yield FAIL, ("The 'slnt' coordinate of"
                 " the 'Regular' instance must be zero."
                 " Got {} as a default value instead."
                 "").format(regular_slnt_coord)


@check(
  id = 'com.google.fonts/check/170',
  rationale = """
    According to the Open-Type spec's registered
    design-variation tag 'ital' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_ital

    If a variable font has a 'ital' (Italic) axis, then the coordinate
    of its 'Regular' instance is required to be zero.
  """,
  conditions = ['is_variable_font',
                'regular_ital_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_170(ttFont, regular_ital_coord):
  """The variable font 'ital' (Italic) axis coordinate must be zero on the
  'Regular' instance."""

  if regular_ital_coord == 0:
    yield PASS, "Regular:ital is zero."
  else:
    yield FAIL, ("The 'ital' coordinate of"
                 " the 'Regular' instance must be zero."
                 " Got {} as a default value instead."
                 "").format(regular_ital_coord)


@check(
  id = 'com.google.fonts/check/171',
  rationale = """
    According to the Open-Type spec's registered
    design-variation tag 'opsz' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz

    If a variable font has a 'opsz' (Optical Size) axis, then the coordinate
    of its 'Regular' instance is recommended to be a value in the range 9 to 13.
  """,
  conditions = ['is_variable_font',
                'regular_opsz_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_171(ttFont, regular_opsz_coord):
  """The variable font 'opsz' (Optical Size) axis coordinate should be between
  9 and 13 on the 'Regular' instance."""

  if regular_opsz_coord >= 9 and regular_opsz_coord <= 13:
    yield PASS, ("Regular:opsz coordinate ({})"
                 " looks good.").format(regular_opsz_coord)
  else:
    yield WARN, ("The 'opsz' (Optical Size) coordinate"
                 " on the 'Regular' instance is recommended"
                 " to be a value in the range 9 to 13."
                 " Got a '{}' coordinate instead."
                 "").format(regular_opsz_coord)


@check(
  id = 'com.google.fonts/check/172',
  rationale = """
    The Open-Type spec's registered
    design-variation tag 'wght' available at
    https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght
    does not specify a required value for the 'Bold' instance of a variable font.
    But Dave Crossland suggested that we should enforce a
    required value of 700 in this case.
  """,
  conditions = ['is_variable_font',
                'bold_wght_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_172(ttFont, bold_wght_coord):
  """The variable font 'wght' (Weight) axis coordinate must be 700 on the
  'Bold' instance."""

  if bold_wght_coord == 700:
    yield PASS, "Bold:wght is 700."
  else:
    yield FAIL, ("The 'wght' axis coordinate of"
                 " the 'Bold' instance must be 700."
                 " Got a '{}' coordinate instead."
                 "").format(bold_wght_coord)
