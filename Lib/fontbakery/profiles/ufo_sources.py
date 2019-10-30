import os

from fontbakery.callable import check, condition
from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue
from fontbakery.checkrunner import ERROR, FAIL, PASS, WARN, Section, Profile
from fontbakery.constants import PriorityLevel


class UFOProfile(Profile):

  def setup_argparse(self, argument_parser):
    """Set up custom arguments needed for this profile."""
    import glob
    import logging
    import argparse

    def get_fonts(pattern):

      fonts_to_check = []
      # use glob.glob to accept *.ufo

      for fullpath in glob.glob(pattern):
        fullpath_absolute = os.path.abspath(fullpath)
        if fullpath_absolute.lower().endswith(".ufo") and os.path.isdir(
            fullpath_absolute):
          fonts_to_check.append(fullpath)
        else:
          logging.warning(
              ("Skipping '{}' as it does not seem "
               "to be valid UFO source directory.").format(fullpath))
      return fonts_to_check

    class MergeAction(argparse.Action):

      def __call__(self, parser, namespace, values, option_string=None):
        target = [item for l in values for item in l]
        setattr(namespace, self.dest, target)

    argument_parser.add_argument(
        'fonts',
        # To allow optional commands like "-L" to work without other input
        # files:
        nargs='*',
        type=get_fonts,
        action=MergeAction,
        help='font file path(s) to check.'
        ' Wildcards like *.ufo are allowed.')

    return ('fonts',)


fonts_expected_value = ExpectedValue(
      'fonts'
    , default=[]
    , description='A list of the ufo file paths to check.'
    , validator=lambda fonts: (True, None) if len(fonts) \
                                    else (False, 'Value is empty.')

)

# ----------------------------------------------------------------------------
# This variable serves as an exportable anchor point, see e.g. the
# Lib/fontbakery/commands/check_ufo_sources.py script.
profile = UFOProfile(
    default_section=Section('Default'),
    iterargs={'font': 'fonts'},
    derived_iterables={'ufo_fonts': ('ufo_font', True)},
    expected_values={fonts_expected_value.name: fonts_expected_value})

register_check = profile.register_check
register_condition = profile.register_condition
# ----------------------------------------------------------------------------

basic_checks = Section("Basic UFO checks")


@register_condition
@condition
def ufo_font(font):
  import defcon
  return defcon.Font(font)


@register_check(section=basic_checks)
@check(
  id = 'com.daltonmaag/check/ufolint',
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_daltonmaag_check_ufolint(font):
  """Run ufolint on UFO source directory."""
  import subprocess
  ufolint_cmd = ["ufolint", font]

  try:
    subprocess.check_output(ufolint_cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    yield FAIL, ("ufolint failed the UFO source. Output follows :"
                 "\n\n{}\n").format(e.output.decode())
  except OSError:
    yield ERROR, "ufolint is not available!"
  else:
    yield PASS, "ufolint passed the UFO source."


@register_check(section=basic_checks)
@check(
  id = 'com.daltonmaag/check/ufo-required-fields',
  rationale = """
    ufo2ft requires these info fields to compile a font binary:
    unitsPerEm, ascender, descender, xHeight, capHeight and familyName.
  """
)
def com_daltonmaag_check_required_fields(ufo_font):
  """Check that required fields are present in the UFO fontinfo."""
  recommended_fields = []

  for field in [
      "unitsPerEm", "ascender", "descender", "xHeight", "capHeight",
      "familyName"
  ]:
    if ufo_font.info.__dict__.get("_" + field) is None:
      recommended_fields.append(field)

  if recommended_fields:
    yield FAIL, f"Required field(s) missing: {recommended_fields}"
  else:
    yield PASS, "Required fields present."


@register_check(section=basic_checks)
@check(
  id = 'com.daltonmaag/check/ufo-recommended-fields',
  rationale = """
    This includes fields that should be in any production font.
  """
)
def com_daltonmaag_check_recommended_fields(ufo_font):
  """Check that recommended fields are present in the UFO fontinfo."""
  recommended_fields = []

  for field in [
      "postscriptUnderlineThickness", "postscriptUnderlinePosition",
      "versionMajor", "versionMinor", "styleName", "copyright",
      "openTypeOS2Panose"
  ]:
    if ufo_font.info.__dict__.get("_" + field) is None:
      recommended_fields.append(field)

  if recommended_fields:
    yield WARN, f"Recommended field(s) missing: {recommended_fields}"
  else:
    yield PASS, "Recommended fields present."


@register_check(section=basic_checks)
@check(
  id = 'com.daltonmaag/check/ufo-unnecessary-fields',
  rationale = """
    ufo2ft will generate these.

    openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted
    because it is useful to toggle a range when not _all_ the glyphs in that
    region are present.

    year is deprecated since UFO v2.
  """
)
def com_daltonmaag_check_unnecessary_fields(ufo_font):
  """Check that no unnecessary fields are present in the UFO fontinfo."""
  unnecessary_fields = []

  for field in [
      "openTypeNameUniqueID", "openTypeNameVersion", "postscriptUniqueID",
      "year"
  ]:
    if ufo_font.info.__dict__.get("_" + field) is not None:
      unnecessary_fields.append(field)

  if unnecessary_fields:
    yield WARN, f"Unnecessary field(s) present: {unnecessary_fields}"
  else:
    yield PASS, "Unnecessary fields omitted."


# The following fields are always generated empty by defcon:
# guidelines, postscriptBlueValues, postscriptOtherBlues,
# postscriptFamilyBlues, postscriptFamilyOtherBlues,
# postscriptStemSnapH, postscriptStemSnapV -- not sure if checking for that
# is useful.
