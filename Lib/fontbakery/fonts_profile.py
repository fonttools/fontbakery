"""
Font Bakery CheckRunner is the driver of a font bakery suite of checks.


"""
from fontbakery.checkrunner import Profile
from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue

class FontsProfile(Profile):
  def setup_argparse(self, argument_parser):
    """
    Set up custom arguments needed for this profile.
    """
    import glob
    import logging
    import argparse
    def get_fonts(pattern):

      fonts_to_check = []
      # use glob.glob to accept *.ttf
      # but perform a hacky fixup to workaround the square-brackets naming scheme
      # currently in use for varfonts in google fonts...
      if '].ttf' in pattern:
        pattern = "*.ttf".join(pattern.split('].ttf'))

      for fullpath in glob.glob(pattern):
        if fullpath.lower().rsplit(".", 1)[-1] in ("otf", "ttf"):
          fonts_to_check.append(fullpath)
        else:
          logging.warning("Skipping '{}' as it does not seem "
                          "to be valid OpenType font file.".format(fullpath))
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
        help='font file path(s) to check. Wildcards like *.ttf are allowed.')

    return ('fonts', )

  def get_family_checks(self):
    family_checks = self.get_checks_by_dependencies('ttFonts')
    return family_checks


fonts_expected_value = ExpectedValue(
      'fonts'
    , default=[]
    , description='A list of the font file paths to check.'
    , validator=lambda fonts: (True, None) if len(fonts) \
                                    else (False, 'Value is empty.')
)

def profile_factory(**kwds):
  from fontbakery.profiles.shared_conditions import ttFont
  profile = FontsProfile(
      iterargs={'font': 'fonts'}
    , conditions={ttFont.name: ttFont}
    , derived_iterables={'ttFonts': ('ttFont', True)}
    , expected_values={fonts_expected_value.name: fonts_expected_value}
    , **kwds
  )
  return profile
