#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

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
from fontbakery.specifications.googlefonts import upstream_spec as upstream_spec

parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.")
parser.add_argument('arg_folders', nargs='+',
                    help='font project folder path(s) to check.'
                         ' Usage of wildcards is allowed.')

parser.add_argument('-c', '--checkid', action='append',
                    help='Explicit check-ids to be executed.')


def log_levels_get(key):
  if key in log_levels:
    return log_levels[key]
  raise argparse.ArgumentTypeError('Key "{}" must be one of: {}.'.format(
                                        key, ', '.join(log_levels.keys())))

parser.add_argument('-l', '--loglevel-tests', default=None, type=log_levels_get,
                    help='Report tests with a result of this status or higher.\n'
                         'One of: {}'.format(', '.join(log_levels.keys())))

parser.add_argument('-m', '--loglevel-messages', default=None, type=log_levels_get,
                    help='Report log messages of this status or higher.\n'
                         'One of: {}'.format(', '.join(log_levels.keys())))

parser.add_argument('-n', '--no-progress', default=False, action='store_true',
                    help='In a tty as stdout, don\'t render the progress indicators.')


def get_folders(globs):
  folders_to_check = []
  for target in globs:
    # use glob.glob to accept wildcards
    for fullpath in glob.glob(target):
      folders_to_check.append(fullpath)
  return folders_to_check

if __name__ == '__main__':
  args = parser.parse_args()
  values = dict(folders=get_folders(args.arg_folders))
  runner = TestRunner(upstream_spec, values, explicit_tests=args.checkid)

  tr = TerminalReporter(runner=runner, is_async=False
                       , print_progress=not args.no_progress
                       , test_threshold=args.loglevel_tests
                       , log_threshold=args.loglevel_messages
                       , collect_results_by='folder'
                       )
  # sr = SerializeReporter(runner=runner, collect_results_by='folder')
  distribute_generator(runner.run(), [tr.receive])# sr.receive
