#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
import argparse
import glob

from fontbakery.testrunner import (
              distribute_generator
            , TestRunner
            , Spec
            )
from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.specifications.googlefonts import specificiation as specificiation

parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.")
parser.add_argument('arg_filepaths', nargs='+',
                    help='font file path(s) to check.'
                         ' Wildcards like *.ttf are allowed.')

parser.add_argument('-c', '--checkid', action='append',
                    help='Explicit check-ids to be executed.')

def get_fonts(globs):
  fonts_to_check = []
  for target in globs:
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(target):
      if fullpath.endswith(".ttf"):
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as it does not seem "
                        "to be valid TrueType font file.".format(fullpath))
  return fonts_to_check

if __name__ == '__main__':
  args = parser.parse_args()
  values = dict(fonts=get_fonts(args.arg_filepaths))
  runner = TestRunner(specificiation, values, explicit_tests=args.checkid)
  tr = TerminalReporter(runner=runner, is_async=False, print_progress=True
                                              #, collect_results_by='font'
                                              )
  # sr = SerializeReporter(runner=runner, collect_results_by='font')
  distribute_generator(runner.run(), [tr.receive])# sr.receive
