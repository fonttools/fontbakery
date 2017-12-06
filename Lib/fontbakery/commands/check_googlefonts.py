#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from functools import partial
from fontbakery.specifications.googlefonts import specification
from fontbakery.commands.check_spec import main as super_main
import argparse
from fontbakery.argumentparser import FBArgumentParser
import glob
# The values dict will probably get one or more specific blacklists
# for the google font project. It would be good if it was not necessary
# to copy paste this kind of configuration, thus a central init for
# the google/fonts repository is be good.
GOOGLEFONTS_SPECIFICS = {}


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

parser = FBArgumentParser(specification)
parser.add_argument('fonts', nargs='+', type=get_fonts,
                    action=MergeAction, help='font file path(s) to check.'
                                         ' Wildcards like *.ttf are allowed.')
args = parser.parse_args()
main = partial(super_main, args=args,
                           specification=specification,
                           items_label='fonts',
                           values=GOOGLEFONTS_SPECIFICS)
