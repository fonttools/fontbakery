#!/usr/bin/env python
# usage:
# $ fontbakery check-profile fontbakery.profiles.googlefonts -h
import argparse
import importlib.util
import os
import sys
from collections import OrderedDict

from fontbakery.checkrunner import (
              distribute_generator
            , CheckRunner
            , ValueValidationError
            , Profile
            , get_module_profile
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

DEFAULT_LOG_LEVEL = INFO

from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.reporters.ghmarkdown import GHMarkdownReporter
from fontbakery.reporters.html import HTMLReporter

def ArgumentParser(profile, profile_arg=True):
  argument_parser = argparse.ArgumentParser(description="Check TTF files"
                                               " against a profile.",
                                  formatter_class=argparse.RawTextHelpFormatter)

  if profile_arg:
    argument_parser.add_argument('profile',
        help='File/Module name, must define a fontbakery "profile".')


  values_keys = profile.setup_argparse(argument_parser)

  argument_parser.add_argument(
      "-c",
      "--checkid",
      action="append",
      help=(
          "Explicit check-ids (or parts of their name) to be executed. "
          "Use this option multiple times to select multiple checks."
      ),
  )

  argument_parser.add_argument(
      "-x",
      "--exclude-checkid",
      action="append",
      help=(
          "Exclude check-ids (or parts of their name) from execution. "
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
                      help='List the checks available in the selected profile.')

  argument_parser.add_argument('--json', default=False, type=argparse.FileType('w'),
                      metavar= 'JSON_FILE',
                      help='Write a json formatted report to JSON_FILE.')

  argument_parser.add_argument('--ghmarkdown', default=False, type=argparse.FileType('w'),
                      metavar= 'MD_FILE',
                      help='Write a GitHub-Markdown formatted report to MD_FILE.')

  argument_parser.add_argument('--html', default=False,
                      type=argparse.FileType('w', encoding="utf-8"),
                      metavar= 'HTML_FILE',
                      help='Write a HTML report to HTML_FILE.')

  iterargs = sorted(profile.iterargs.keys())

  gather_by_choices = iterargs + ['*check']
  argument_parser.add_argument('-g','--gather-by', default=None,
                      metavar= 'ITERATED_ARG',
                      choices=gather_by_choices,
                      type=str,
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
  # filename = 'my/path/to/file.py'
  # module_name = 'file_module.file_py'
  module_name = 'file_module.{}'.format(os.path.basename(filename).replace('.', '_'))
  profile = importlib.util.spec_from_file_location(module_name, filename)
  module = importlib.util.module_from_spec(profile)
  profile.loader.exec_module(module)
  return module

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

def get_profile():
  """ Prefetch the profile module, to fill some holes in the help text."""
  argument_parser = ThrowingArgumentParser(add_help=False)
  argument_parser.add_argument('profile')
  try:
    args, _ = argument_parser.parse_known_args()
  except ArgumentParserError:
    # silently fails, the main parser will show usage string.
    return Profile()
  imported = get_module(args.profile)
  profile = get_module_profile(imported)
  if not profile:
    raise Exception(f"Can't get a profile from {imported}.")
  return profile

# This stub or alias is kept for compatibility (e.g. check-commands, FontBakery
# Dashboard). The function of the same name previously only passed on all parameters to
# CheckRunner.
runner_factory = CheckRunner

def main(profile=None, values=None):
  # profile can be injected by e.g. check-googlefonts injects it's own profile
  add_profile_arg = False
  if profile is None:
    profile = get_profile()
    add_profile_arg = True

  argument_parser, values_keys = ArgumentParser(profile, profile_arg=add_profile_arg)
  args = argument_parser.parse_args()

  if args.list_checks:
    if args.loglevels == [PASS]: # if verbose:
      from fontbakery.constants import WHITE_STR, CYAN_STR, BLUE_STR
      for section in profile._sections.values():
        print(WHITE_STR.format("\nSection:") + " " + section.name)
        for check in section._checks:
          print(CYAN_STR.format(check.id) + "\n" +
                BLUE_STR.format(f'"{check.description}"') + "\n")
    else:
      for section_name, section in profile._sections.items():
        for check in section._checks:
          print(check.id)
    sys.exit()

  values_ = {}
  if values is not None:
    values_.update(values)

  # values_keys are returned by profile.setup_argparse
  # these are keys for custom arguments required by the profile.
  if values_keys:
    for key in values_keys:
      if hasattr(args, key):
        values_[key] = getattr(args, key)

  try:
    runner = CheckRunner(profile
                        , values=values_
                        , custom_order=args.order
                        , explicit_checks=args.checkid
                        , exclude_checks=args.exclude_checkid
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

  if args.html:
    hr = HTMLReporter(loglevels=args.loglevels,
                      runner=runner,
                      collect_results_by=args.gather_by)
    reporters.append(hr.receive)

  distribute_generator(runner.run(), reporters)

  if args.json:
    import json
    json.dump(sr.getdoc(), args.json, sort_keys=True, indent=4)
    print("A report in JSON format has been"
          " saved to '{}'".format(args.json.name))

  if args.ghmarkdown:
    args.ghmarkdown.write(mdr.get_markdown())
    print("A report in GitHub Markdown format which can be useful\n"
          " for posting issues on a GitHub issue tracker has been\n"
          " saved to '{}'".format(args.ghmarkdown.name))

  if args.html:
    args.html.write(hr.get_html())
    print(f"A report in HTML format has been saved to '{args.html.name}'")

  # Fail and error let the command fail
  return 1 if tr.worst_check_status in (ERROR, FAIL) else 0

if __name__ == '__main__':
    sys.exit(main())
