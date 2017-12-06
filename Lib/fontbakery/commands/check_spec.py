#!/usr/bin/env python
# -*- coding: utf-8 -*-

# usage:
# $ fontbakery check-specification fontbakery.specifications.googlefonts -h
from __future__ import absolute_import, print_function, unicode_literals

import sys
import argparse
from collections import OrderedDict

from fontbakery.checkrunner import (
              distribute_generator
            , CheckRunner
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

def ArgumentParser(specification, spec_arg=True):
  argument_parser = argparse.ArgumentParser(description="Check TTF files"
                                               " against a specification.",
                                  formatter_class=argparse.RawTextHelpFormatter)

  if spec_arg:
    argument_parser.add_argument('specification',
        help='Module name, must define a fontbakery "specification".')


  values_keys = specification.setup_argparse(argument_parser);

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
                      help='Report checks with a result of this status or higher.\n'
                           'One of: {}.\n'
                           '(default: {})'.format(', '.join(log_levels.keys())
                                                   , DEFAULT_LOG_LEVEL.name))

  argument_parser.add_argument('-m', '--loglevel-messages', default=None, type=log_levels_get,
                      help=('Report log messages of this status or higher.\n'
                            'Messages are all status lines within a check.\n'
                            'One of: {}.\n'
                            '(default: LOGLEVEL)'
                            ).format(', '.join(log_levels.keys())))

  argument_parser.add_argument('-n', '--no-progress', default=False, action='store_true',
                      help='In a tty as stdout, don\'t render the progress indicators.')

  argument_parser.add_argument('-C', '--no-colors', default=False, action='store_true',
                      help='No colors for tty output.')

  argument_parser.add_argument('-L', '--list-checks', default=False, action='store_true',
                      help='List the checks available in the selected specification.')

  argument_parser.add_argument('--json', default=False, type=argparse.FileType('w'),
                      metavar= 'JSON_FILE',
                      help='Write a json formatted report to JSON_FILE.')

  iterargs = sorted(specification.iterargs.keys())



  gather_by_choices = iterargs + ['*check']
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
                      'The execution order is determined by the order of the check\n'
                      'definitions and by the order of the iterable arguments.\n'
                      'A section defines its own order. `--order` can be used to\n'
                      'override the order of *all* sections.\n'
                      'Despite the ITERATED_ARGS there are two special\n'
                      'values available:\n'
                      '"*iterargs" -- all remainig ITERATED_ARGS\n'
                      '"*check"     -- order by check\n'
                      'ITERATED_ARGS: {}\n'
                      'A sections default is equivalent to: "*iterargs, *check".\n'
                      'A common use case is `-o "*check"` when checking the whole \n'
                      'collection against a selection of checks picked with `--checkid`.'
                      ''.format(', '.join(iterargs))
                      )
  return argument_parser, values_keys

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
  except ArgumentParserError:
    # silently fails, the main parser will show usage string.
    return Spec()

  from importlib import import_module
  # Fails with an appropriate ImportError.
  imported = import_module(args.specification, package=None)
  # Fails with an attribute error if specification is undefined.
  return imported.specification

def runner_factory( specification
                  , explicit_checks=None
                  , custom_order=None
                  , values=None):
  """ Convenience CheckRunner factory. """
  return CheckRunner( specification, values
                    , explicit_checks=explicit_checks
                    , custom_order=custom_order
                    )

def main(specification=None, values=None):
  # specification can be injected by e.g. check-googlefonts injects it's own spec
  add_spec_arg = False
  if specification is None:
    specification = get_spec()
    add_spec_arg = True

  argument_parser, values_keys = ArgumentParser(specification, spec_arg=add_spec_arg)
  args = argument_parser.parse_args()

  if args.list_checks:
    for section_name, section in specification._sections.items():
      checks = section.list_checks()
      sys.exit("Available checks on {} are:\n{}".format(section_name,
                                                        "\n".join(checks)))

  values_ = {}
  if values is not None:
    values_.update(values)

  # values_keys are returned by specification.setup_argparse
  # these are keys for custom arguments required by the spec.
  if values_keys:
    for key in values_keys:
      if hasattr(args, key):
        values_[key] = getattr(args, key)

  runner = runner_factory(specification
                     , explicit_checks=args.checkid
                     , custom_order=args.order
                     , values=values_
                     )

  # the most verbose loglevel wins
  loglevel = min(args.loglevels) if args.loglevels else DEFAULT_LOG_LEVEL
  tr = TerminalReporter(runner=runner, is_async=False
                       , print_progress=not args.no_progress
                       , check_threshold=loglevel
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


