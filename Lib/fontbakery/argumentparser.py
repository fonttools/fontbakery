from __future__ import absolute_import, print_function, unicode_literals

import sys
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

DEFAULT_LOG_LEVEL = WARN

from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter



def FBArgumentParser(specification):
  argument_parser = argparse.ArgumentParser(description="Check a specification.",
                                  formatter_class=argparse.RawTextHelpFormatter)

  argument_parser.add_argument('-c', '--checkid', action='append',
                      help='Explicit check-ids to be executed.\n'
                           'Use this option multiple times to select multiple checks.'
                     )

  def log_levels_get(key):
    if key in log_levels:
      return log_levels[key]
    raise argparse.ArgumentTypeError('Key "{}" must be one of: {}.'.format(
                                          key, ', '.join(log_levels.keys())))
  argument_parser.add_argument('-v', '--verbose', dest='loglevels', const=PASS, action='append_const',
                      help='Shortcut for `-l PASS`.\n')

  argument_parser.add_argument('-l', '--loglevel', dest='loglevels', type=log_levels_get,
                      action='append',
                      metavar= 'LOGLEVEL',
                      help='Report tests with a result of this status or higher.\n'
                           'One of: {}.\n'
                           '(default: {})'.format(', '.join(log_levels.keys())
                                                   , DEFAULT_LOG_LEVEL.name))

  argument_parser.add_argument('-m', '--loglevel-messages', default=None, type=log_levels_get,
                      help=('Report log messages of this status or higher.\n'
                            'Messages are all status lines within a test.\n'
                            'One of: {}.\n'
                            '(default: LOGLEVEL)'
                            ).format(', '.join(log_levels.keys())))

  argument_parser.add_argument('-n', '--no-progress', default=False, action='store_true',
                      help='In a tty as stdout, don\'t render the progress indicators.')

  argument_parser.add_argument('-C', '--no-colors', default=False, action='store_true',
                      help='No colors for tty output.')

  argument_parser.add_argument('-L', '--list-tests', default=False, action='store_true',
                      help='List the tests available in the selected specification.')

  argument_parser.add_argument('--json', default=False, type=argparse.FileType('w'),
                      metavar= 'JSON_FILE',
                      help='Write a json formatted report to JSON_FILE.')

  iterargs = sorted(specification.iterargs.keys())



  gather_by_choices = iterargs + ['*test']
  argument_parser.add_argument('-g','--gather-by', default=None,
                      metavar= 'ITERATED_ARG',
                      choices=gather_by_choices,
                      help='Optional: collect results by ITERATED_ARG\n'
                      'In terminal output: create a summary counter for each ITERATED_ARG.\n'
                      'In json output: structure the document by ITERATED_ARG.\n'
                      'One of: {}'.format(', '.join(gather_by_choices))
                      )

  def parse_order(arg):
    order = filter(len, [n.strip() for n in arg.split(',')])
    return order or None
  argument_parser.add_argument('-o','--order', default=None, type=parse_order,
                      help='Comma separated list of order arguments.\n'
                      'The execution order is determined by the order of the test\n'
                      'definitions and by the order of the iterable arguments.\n'
                      'A section defines its own order. `--order` can be used to\n'
                      'override the order of *all* sections.\n'
                      'Despite the ITERATED_ARGS there are two special\n'
                      'values available:\n'
                      '"*iterargs" -- all remainig ITERATED_ARGS\n'
                      '"*test"     -- order by test\n'
                      'ITERATED_ARGS: {}\n'
                      'A sections default is equivalent to: "*iterargs, *test".\n'
                      'A common use case is `-o "*test"` when testing the whole \n'
                      'collection against a selection of tests picked with `--checkid`.'
                      ''.format(', '.join(iterargs))
                      )
  return argument_parser

class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
