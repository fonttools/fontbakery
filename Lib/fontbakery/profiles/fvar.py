from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('is_variable_font'
            , 'regular_wght_coord', 'regular_wdth_coord', 'regular_slnt_coord'
            , 'regular_ital_coord', 'regular_opsz_coord', 'bold_wght_coord'))
]

@check(
  id = 'com.google.fonts/check/varfont/regular_wght_coord',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'wght' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght

    If a variable font has a 'wght' (Weight) axis, then the coordinate of its 'Regular' instance is required to be 400.
  """,
  conditions = ['is_variable_font',
                'regular_wght_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_regular_wght_coord(ttFont, regular_wght_coord):
  """The variable font 'wght' (Weight) axis coordinate must be 400 on the
  'Regular' instance."""

  if regular_wght_coord == 400:
    yield PASS, "Regular:wght is 400."
  else:
    yield FAIL,\
          Message("not-400",
                  f'The "wght" axis coordinate of'
                  f' the "Regular" instance must be 400.'
                  f' Got {regular_wght_coord} instead.')


@check(
  id = 'com.google.fonts/check/varfont/regular_wdth_coord',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'wdth' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth

    If a variable font has a 'wdth' (Width) axis, then the coordinate of its 'Regular' instance is required to be 100.
  """,
  conditions = ['is_variable_font',
                'regular_wdth_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_regular_wdth_coord(ttFont, regular_wdth_coord):
  """The variable font 'wdth' (Width) axis coordinate must be 100 on the
  'Regular' instance."""

  if regular_wdth_coord == 100:
    yield PASS, "Regular:wdth is 100."
  else:
    yield FAIL,\
          Message("not-100",
                  f'The "wdth" coordinate of'
                  f' the "Regular" instance must be 100.'
                  f' Got {regular_wdth_coord} as a default value instead.')


@check(
  id = 'com.google.fonts/check/varfont/regular_slnt_coord',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'slnt' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_slnt

    If a variable font has a 'slnt' (Slant) axis, then the coordinate of its 'Regular' instance is required to be zero.
  """,
  conditions = ['is_variable_font',
                'regular_slnt_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_regular_slnt_coord(ttFont, regular_slnt_coord):
  """The variable font 'slnt' (Slant) axis coordinate must be zero on the
  'Regular' instance."""

  if regular_slnt_coord == 0:
    yield PASS, "Regular:slnt is zero."
  else:
    yield FAIL,\
          Message("non-zero",
                  f'The "slnt" coordinate of'
                  f' the "Regular" instance must be zero.'
                  f' Got {regular_slnt_coord} as a default value instead.')


@check(
  id = 'com.google.fonts/check/varfont/regular_ital_coord',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'ital' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_ital

    If a variable font has a 'ital' (Italic) axis, then the coordinate of its 'Regular' instance is required to be zero.
  """,
  conditions = ['is_variable_font',
                'regular_ital_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_regular_ital_coord(ttFont, regular_ital_coord):
  """The variable font 'ital' (Italic) axis coordinate must be zero on the
  'Regular' instance."""

  if regular_ital_coord == 0:
    yield PASS, "Regular:ital is zero."
  else:
    yield FAIL,\
          Message("non-zero",
                  f'The "ital" coordinate of'
                  f' the "Regular" instance must be zero.'
                  f' Got {regular_ital_coord} as a default value instead.')


@check(
  id = 'com.google.fonts/check/varfont/regular_opsz_coord',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'opsz' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz

    If a variable font has a 'opsz' (Optical Size) axis, then the coordinate of its 'Regular' instance is recommended to be a value in the range 9 to 13.
  """,
  conditions = ['is_variable_font',
                'regular_opsz_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_regular_opsz_coord(ttFont, regular_opsz_coord):
  """The variable font 'opsz' (Optical Size) axis coordinate should be between
  9 and 13 on the 'Regular' instance."""

  if regular_opsz_coord >= 9 and regular_opsz_coord <= 13:
    yield PASS, ("Regular:opsz coordinate ({regular_opsz_coord}) looks good.")
  else:
    yield WARN,\
          Message("out-of-range",
                  f'The "opsz" (Optical Size) coordinate'
                  f' on the "Regular" instance is recommended'
                  f' to be a value in the range 9 to 13.'
                  f' Got {regular_opsz_coord} instead.')


@check(
  id = 'com.google.fonts/check/varfont/bold_wght_coord',
  rationale = """
    The Open-Type spec's registered design-variation tag 'wght' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght does not specify a required value for the 'Bold' instance of a variable font.

    But Dave Crossland suggested that we should enforce a required value of 700 in this case.
  """,
  conditions = ['is_variable_font',
                'bold_wght_coord'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1707'
  }
)
def com_google_fonts_check_varfont_bold_wght_coord(ttFont, bold_wght_coord):
  """The variable font 'wght' (Weight) axis coordinate must be 700 on the
  'Bold' instance."""

  if bold_wght_coord == 700:
    yield PASS, "Bold:wght is 700."
  else:
    yield FAIL,\
          Message("not-700",
                  f'The "wght" axis coordinate of'
                  f' the "Bold" instance must be 700.'
                  f' Got {bold_wght_coord} instead.')


@check(
  id = 'com.google.fonts/check/varfont/wght_valid_range',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'wght' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght

    On the 'wght' (Weight) axis, the valid coordinate range is 1-1000.
  """,
  conditions = ['is_variable_font'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2264'
  }
)
def com_google_fonts_check_varfont_wght_valid_range(ttFont):
  """The variable font 'wght' (Weight) axis coordinate
     must be within spec range of 1 to 1000 on all instances."""

  Failed = False
  for instance in ttFont['fvar'].instances:
    if 'wght' in instance.coordinates:
      value = instance.coordinates['wght']
      if value < 1 or value > 1000:
        Failed = True
        yield FAIL,\
              Message("out-of-range",
                      f'Found a bad "wght" coordinate with value {value}'
                      f' outside of the valid range from 1 to 1000.')
        break

  if not Failed:
    yield PASS, ("OK")


@check(
  id = 'com.google.fonts/check/varfont/wdth_valid_range',
  rationale = """
    According to the Open-Type spec's registered design-variation tag 'wdth' available at https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth

    On the 'wdth' (Width) axis, the valid coordinate range is 1-1000
  """,
  conditions = ['is_variable_font'],
  misc_metadata = {
  }
)
def com_google_fonts_check_varfont_wdth_valid_range(ttFont):
  """The variable font 'wdth' (Weight) axis coordinate
     must be within spec range of 1 to 1000 on all instances."""

  Failed = False
  for instance in ttFont['fvar'].instances:
    if 'wdth' in instance.coordinates:
      value = instance.coordinates['wdth']
      if value < 1 or value > 1000:
        Failed = True
        yield FAIL,\
              Message("out-of-range",
                      f'Found a bad "wdth" coordinate with value {value}'
                      f' outside of the valid range from 1 to 1000.')
        break

  if not Failed:
    yield PASS, ("OK")


@check(
  id = 'com.google.fonts/check/varfont/slnt_range',
  rationale = """
    The OpenType spec says at https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt that:

    [...] the scale for the Slant axis is interpreted as the angle of slant in counter-clockwise degrees from upright. This means that a typical, right-leaning oblique design will have a negative slant value. This matches the scale used for the italicAngle field in the post table.
  """,
  conditions = ['is_variable_font',
                'slnt_axis'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2572'
  }
)
def com_google_fonts_check_varfont_slnt_range(ttFont, slnt_axis):
  """ The variable font 'slnt' (Slant) axis coordinate
      specifies positive values in its range? """

  if slnt_axis.minValue < 0 and slnt_axis.maxValue >= 0:
    yield PASS, "Looks good!"
  else:
    yield WARN,\
          Message("unusual-range",
                  f'The range of values for the "slnt" axis in'
                  f' this font only allows positive coordinates'
                  f' (from {slnt_axis.minValue} to {slnt_axis.maxValue}),'
                  f' indicating that this may be a back slanted design,'
                  f' which is rare. If that\'s not the case, then'
                  f' the "slant" axis should be a range of'
                  f' negative values instead.')
