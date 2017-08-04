#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
import argparse
import glob
from collections import OrderedDict

from fontbakery.testrunner import (
              distribute_generator
            , TestRunner
            , Spec
            , DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

log_levels =  OrderedDict((s.name,s) for s in sorted((
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )))



from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.specifications.googlefonts import specification as specification

parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.",
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('arg_filepaths', nargs='+',
                    help='font file path(s) to check.'
                         ' Wildcards like *.ttf are allowed.')

parser.add_argument('-c', '--checkid', action='append',
                    help='Explicit check-ids to be executed.\n'
                         'Use this option multiple times to select multiple checks.'
                   )


def log_levels_get(key):
  if key in log_levels:
    return log_levels[key]
  raise argparse.ArgumentTypeError('Key "{}" must be one of: {}.'.format(
                                        key, ', '.join(log_levels.keys())))
DEFAULT_LOG_LEVEL = WARN
parser.add_argument('-v', '--verbose', default=DEFAULT_LOG_LEVEL, const=PASS ,action='store_const',
                    help='Shortcut for `-l PASS`.\n')

parser.add_argument('-l', '--loglevel', default=DEFAULT_LOG_LEVEL, type=log_levels_get,
                    metavar= 'LOGLEVEL',
                    help='Report tests with a result of this status or higher.\n'
                         'One of: {}.\n'
                         '(default: {})'.format(', '.join(log_levels.keys())
                                                 , DEFAULT_LOG_LEVEL.name))

parser.add_argument('-m', '--loglevel-messages', default=None, type=log_levels_get,
                    help=('Report log messages of this status or higher.\n'
                          'Messages are all status lines within a test.\n'
                          'One of: {}.\n'
                          '(default: LOGLEVEL)'
                          ).format(', '.join(log_levels.keys())))

parser.add_argument('-n', '--no-progress', default=False, action='store_true',
                    help='In a tty as stdout, don\'t render the progress indicators.')

parser.add_argument('-C', '--no-colors', default=False, action='store_true',
                    help='No colors for tty output')

parser.add_argument('--json', default=False, type=argparse.FileType('w'),
                    metavar= 'JSON_FILE',
                    help='Write a json formatted report to JSON_FILE.')

iterargs = sorted(specification.iterargs.keys())
parser.add_argument('-g','--gather-by', default=None,
                    metavar= 'ITERATED_ARG',
                    choices=iterargs,
                    help='Optional: collect results by ITERATED_ARG\n'
                    'In terminal output: create a summary counter for each ITERATED_ARG.\n'
                    'In json output: structure the document by ITERATED_ARG.\n'
                    'One of: {}'.format(','.join(iterargs))
                    )


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
  runner = TestRunner(specification, values, explicit_tests=args.checkid)

  # the more verbose loglevel wins
  loglevel = min(args.loglevel, args.verbose)

  tr = TerminalReporter(runner=runner, is_async=False
                       , print_progress=not args.no_progress
                       , test_threshold=loglevel
                       , log_threshold=args.loglevel_messages or loglevel
                       , usecolor=not args.no_colors
                       , collect_results_by=args.gather_by
                       )
  reporters = [tr.receive]
  if args.json:
    sr = SerializeReporter(runner=runner, collect_results_by=args.gather_by)
    reporters.append(sr.receive)
  distribute_generator(runner.run(), reporters)

  if args.json:
    import json
    json.dump(sr.getdoc(), args.json, sort_keys=True, indent=4)
