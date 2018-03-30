# -*- coding: utf-8 -*-
"""
Font Bakery CheckRunner is the driver of a font bakery suite of checks.


"""
from __future__ import absolute_import, print_function, unicode_literals


from fontbakery.checkrunner import Spec
from fontbakery.checkrunner import get_module_specification \
                                        as super_get_module_specification
from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue
from fontbakery.specifications.shared_conditions import ttFont

class FontsSpec(Spec):
  def setup_argparse(self, argument_parser):
    """
    Set up custom arguments needed for this spec.
    """
    import glob
    import logging
    import argparse
    def get_fonts(pattern):

      fonts_to_check = []
      # use glob.glob to accept *.ttf

      for fullpath in glob.glob(pattern):
        if fullpath.endswith(".ttf"):
          fonts_to_check.append(fullpath)
        else:
          logging.warning("Skipping '{}' as it does not seem "
                            "to be valid TrueType font file.".format(fullpath))
      return fonts_to_check


    class MergeAction(argparse.Action):
      def __call__(self, parser, namespace, values, option_string=None):
        target = [item for l in values for item in l]
        setattr(namespace, self.dest, target)

    argument_parser.add_argument('fonts', nargs='*', type=get_fonts,
                        action=MergeAction, help='font file path(s) to check.'
                                            ' Wildcards like *.ttf are allowed.')
    return ('fonts', )

  def register_modules(self, *modules):
    for module in modules:
      specification = get_module_specification(module)
      self.merge_specification(specification)


fonts_expected_value = ExpectedValue(
      'fonts'
    , default=[]
    , description='A list of the font file paths to check.'
)

def spec_factory(**kwds):
  spec = FontsSpec(
      iterargs={'font': 'fonts'}
    , conditions={ttFont.name: ttFont}
    , derived_iterables={'ttFonts': ('ttFont', True)}
    , expected_values={fonts_expected_value.name: fonts_expected_value}
    , **kwds
  )
  return spec

def get_module_specification(module, name=None):
  return super_get_module_specification(spec_factory, module, name=name)
