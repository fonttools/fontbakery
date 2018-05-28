#!/usr/bin/env python
# -*- coding: utf-8 -*-

# usage:
# $ fontbakery check-specification fontbakery.specifications.googlefonts -h
from __future__ import absolute_import, print_function, unicode_literals

from builtins import filter
import sys
import os
import argparse
from collections import OrderedDict

from fontbakery.checkrunner import (
              distribute_generator
            , CheckRunner
            , ValueValidationError
            , Spec
            , get_module_specification
            , DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , STARTSECTION
            , ENDSECTION
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
from fontbakery.reporters.ghmarkdown import GHMarkdownReporter

def ArgumentParser(specification, spec_arg=True):
  argument_parser = argparse.ArgumentParser(description="Check TTF files"
                                               " against a specification.",
                                  formatter_class=argparse.RawTextHelpFormatter)

  if spec_arg:
    argument_parser.add_argument('specification',
        help='File/Module name, must define a fontbakery "specification".')


  values_keys = specification.setup_argparse(argument_parser)

  select_group = argument_parser.add_mutually_exclusive_group()

  select_group.add_argument(
      "-c",
      "--checkid",
      action="append",
      help=(
          "Explicit check-ids to be executed. "
          "Use this option multiple times to select multiple checks."
      ),
  )

  select_group.add_argument(
      "-x",
      "--exclude-checkid",
      action="append",
      help=(
          "Exclude check-ids from execution. "
          "Use this option multiple times to exclude multiple checks."
      ),
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

  if sys.platform != "win32":
    argument_parser.add_argument(
        '-n',
        '--no-progress',
        action='store_true',
        help='In a tty as stdout, don\'t render the progress indicators.')

    argument_parser.add_argument(
        '-C',
        '--no-colors',
        action='store_true',
        help='No colors for tty output.')

  argument_parser.add_argument('-S', '--show-sections', default=False, action='store_true',
                      help='Show section start and end info plus summary.')


  argument_parser.add_argument('-L', '--list-checks', default=False, action='store_true',
                      help='List the checks available in the selected specification.')

  argument_parser.add_argument('--json', default=False, type=argparse.FileType('w'),
                      metavar= 'JSON_FILE',
                      help='Write a json formatted report to JSON_FILE.')

  argument_parser.add_argument('--ghmarkdown', default=False, type=argparse.FileType('w'),
                      metavar= 'MD_FILE',
                      help='Write a GitHub-Markdown formatted report to MD_FILE.')

  iterargs = sorted(specification.iterargs.keys())

  def commandline_unicode_arg(bytestring):
    try:
      # py2 has .decode
      return bytestring.decode(sys.getfilesystemencoding())
    except AttributeError:
      # py3 should work with the original argument
      return bytestring

  gather_by_choices = iterargs + ['*check']
  argument_parser.add_argument('-g','--gather-by', default=None,
                      metavar= 'ITERATED_ARG',
                      choices=gather_by_choices,
                      type=commandline_unicode_arg,
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

def get_module_from_file(filename):
  # this is really annoying between python 2 and 3
  # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
  imp = None
  importlib_util = None
  # filename = 'my/path/to/file.py'
  # module_name = 'file_module.file_py'
  module_name = 'file_module.{}'.format(os.path.basename(filename).replace('.', '_'))
  try:
    import importlib.util as importlib_util
  except ImportError:
    import imp

  if importlib_util:
    spec = importlib_util.spec_from_file_location(module_name, filename)
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
  elif imp:
    return imp.load_source(module_name, filename)

def get_module(name):
  if os.path.isfile(name):
    # This name could also be the name of a module, but if there's a
    # file that we can load the file will win. Otherwise, it's still
    # possible to change the directory
    imported = get_module_from_file(name)
  else:
    from importlib import import_module
    # Fails with an appropriate ImportError.
    imported = import_module(name, package=None)
  return imported

def get_spec():
  """ Prefetch the specification module, to fill some holes in the help text."""
  argument_parser = ThrowingArgumentParser(add_help=False)
  argument_parser.add_argument('specification')
  try:
    args, unknown = argument_parser.parse_known_args()
  except ArgumentParserError:
    # silently fails, the main parser will show usage string.
    return Spec()
  imported = get_module(args.specification)
  specification = get_module_specification(imported)
  if not specification:
    raise Exception('Can\'t get a specification from {}.'.format(imported))
  return specification

def runner_factory( specification
                  , explicit_checks=None
                  , exclude_checks=None
                  , custom_order=None
                  , values=None):
  """ Convenience CheckRunner factory. """
  return CheckRunner( specification, values
                    , explicit_checks=explicit_checks
                    , exclude_checks=exclude_checks
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
    print('Available checks')
    for section_name, section in specification._sections.items():
      checks = section.list_checks()
      message = "# {}:\n  {}".format(section_name,"\n  ".join(checks))
      print(message)
    sys.exit()

  values_ = {}
  if values is not None:
    values_.update(values)

  # values_keys are returned by specification.setup_argparse
  # these are keys for custom arguments required by the spec.
  if values_keys:
    for key in values_keys:
      if hasattr(args, key):
        values_[key] = getattr(args, key)

  try:
    runner = runner_factory(specification
                     , explicit_checks=args.checkid
                     , exclude_checks=args.exclude_checkid
                     , custom_order=args.order
                     , values=values_
                     )
  except ValueValidationError as e:
    print(e)
    argument_parser.print_usage()
    sys.exit(1)

  # The default Windows Terminal just displays the escape codes. The argument
  # parser above therefore has these options disabled.
  if sys.platform == "win32":
    args.no_progress = True
    args.no_colors = True

  # the most verbose loglevel wins
  loglevel = min(args.loglevels) if args.loglevels else DEFAULT_LOG_LEVEL
  tr = TerminalReporter(runner=runner, is_async=False
                       , print_progress=not args.no_progress
                       , check_threshold=loglevel
                       , log_threshold=args.loglevel_messages or loglevel
                       , usecolor=not args.no_colors
                       , collect_results_by=args.gather_by
                       , skip_status_report=None if args.show_sections\
                                                      else (STARTSECTION, ENDSECTION)

                       )
  reporters = [tr.receive]

  if args.json:
    sr = SerializeReporter(runner=runner, collect_results_by=args.gather_by)
    reporters.append(sr.receive)

  if args.ghmarkdown:
    mdr = GHMarkdownReporter(loglevels=args.loglevels,
                             runner=runner,
                             collect_results_by=args.gather_by)
    reporters.append(mdr.receive)

  distribute_generator(runner.run(), reporters)

  if args.json:
    import json
    json.dump(sr.getdoc(), args.json, sort_keys=True, indent=4)

  if args.ghmarkdown:
    args.ghmarkdown.write(mdr.get_markdown())

  # Fail and error let the command fail
  return 1 if tr.worst_check_status in (ERROR, FAIL) else 0

if __name__ == '__main__':
    sys.exit(main())
