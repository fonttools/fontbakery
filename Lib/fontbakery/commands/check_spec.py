#!/usr/bin/env python
# -*- coding: utf-8 -*-

# usage:
# $ fontbakery check-specification fontbakery.specifications.googlefonts -h
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

DEFAULT_LOG_LEVEL = WARN

from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter

argument_parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.",
                                 formatter_class=argparse.RawTextHelpFormatter)

def ArgumentParser(specification, spec_arg=True):
  argument_parser = argparse.ArgumentParser(description="Check TTF files"
                                               " against a specification.",
                                  formatter_class=argparse.RawTextHelpFormatter)

  if spec_arg:
    argument_parser.add_argument('specification',
        help='Module name, must define a fontbakery "specification".')

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

  argument_parser.add_argument('fonts', nargs='+', type=get_fonts,
                      action=MergeAction, help='font file path(s) to check.'
                                         ' Wildcards like *.ttf are allowed.')

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
                      help='No colors for tty output')

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

def get_spec():
  """ Prefetch the specification module, to fill some holes in the help text."""
  argument_parser = ThrowingArgumentParser(add_help=False)
  argument_parser.add_argument('specification')
  try:
    args, unknown = argument_parser.parse_known_args()
  except ArgumentParserError as e:
    # silently fails, the main parser will show usage string.
    return Spec()

  from importlib import import_module
  # Fails with an appropriate ImportError.
  imported = import_module(args.specification, package=None)
  # Fails with an attribute error if specification is undefined.
  return imported.specification

def runner_factory(specification, fonts, explicit_tests=None, custom_order=None
                                                        , values=None):
  """ Convenience TestRunner factory. """
  values_ = dict(fonts=fonts)
  if values is not None:
    values_.update(values)
  return TestRunner( specification, values_
                   , explicit_tests=explicit_tests
                   , custom_order=custom_order
                   )

def main(specification=None, values=None):
  # this won't be used in check-googlefonts
  add_spec_arg = False
  if specification is None:
    specification = get_spec()
    add_spec_arg = True
  argument_parser = ArgumentParser(specification, spec_arg=add_spec_arg)
  args = argument_parser.parse_args()
  runner = runner_factory(specification, args.fonts
                     , explicit_tests=args.checkid
                     , custom_order=args.order
                     , values=values
                     )

  # the most verbose loglevel wins
  loglevel = min(args.loglevels) if args.loglevels else DEFAULT_LOG_LEVEL
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


