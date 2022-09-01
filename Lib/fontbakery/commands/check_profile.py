#!/usr/bin/env python
# usage:
# $ fontbakery check-profile fontbakery.profiles.googlefonts -h
import argparse
from importlib import import_module
import os
import sys
from collections import OrderedDict

from fontbakery.checkrunner import (
              distribute_generator
            , CheckRunner
            , get_module_from_file
            , DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , SECTIONSUMMARY
            )
from fontbakery.configuration import Configuration
from fontbakery.profile import (Profile, get_module_profile)

from fontbakery.errors import ValueValidationError
from fontbakery.multiproc import multiprocessing_runner
from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.reporters.badge import BadgeReporter
from fontbakery.reporters.ghmarkdown import GHMarkdownReporter
from fontbakery.reporters.html import HTMLReporter
from fontbakery.utils import get_theme


log_levels =  OrderedDict((s.name, s) \
                          for s in sorted((
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )))

DEFAULT_LOG_LEVEL = INFO


class AddReporterAction(argparse.Action):
     def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self.cls = kwargs["cls"]
        del kwargs["cls"]
        super().__init__(option_strings, dest, **kwargs)

     def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, "reporters"):
            namespace.reporters = []
        namespace.reporters.append((self.cls, values))


def ArgumentParser(profile, profile_arg=True):
    argument_parser = \
        argparse.ArgumentParser(description="Check TTF files against a profile.",
                                formatter_class=argparse.RawTextHelpFormatter)

    if profile_arg:
        argument_parser.add_argument('profile',
                                     help='File/Module name,'
                                          ' must define a fontbakery "profile".')


    values_keys = profile.setup_argparse(argument_parser)

    argument_parser.add_argument('--configuration',
                                 dest='configfile',
                                 help='Read configuration file (TOML/YAML).\n')

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

    valid_keys = ', '.join(log_levels.keys())

    def log_levels_get(key):
        if key in log_levels:
            return log_levels[key]
        raise argparse.ArgumentTypeError(f'Key "{key}" must be one of: {valid_keys}.')

    argument_parser.add_argument('-v', '--verbose',
                                 dest='loglevels',
                                 const=PASS,
                                 action='append_const',
                                 help='Shortcut for `-l PASS`.\n')

    argument_parser.add_argument('-l', '--loglevel',
                                 dest='loglevels',
                                 type=log_levels_get,
                                 action='append',
                                 metavar= 'LOGLEVEL',
                                 help=f'Report checks with a result of this status or higher.\n'
                                      f'One of: {valid_keys}.\n'
                                      f'(default: {DEFAULT_LOG_LEVEL.name})')

    argument_parser.add_argument('-m', '--loglevel-messages',
                                 default=None,
                                 type=log_levels_get,
                                 help=f'Report log messages of this status or higher.\n'
                                      f'Messages are all status lines within a check.\n'
                                      f'One of: {valid_keys}.\n'
                                      f'(default: LOGLEVEL)')

    argument_parser.add_argument('--succinct',
                                 action='store_true',
                                 help='This is a slightly more compact and succint'
                                      ' output layout.')

    argument_parser.add_argument('-n', '--no-progress',
                                 default=False, action='store_true',
                                 help='In a tty as stdout, don\'t'
                                      ' render the progress indicators.')

    argument_parser.add_argument('-C', '--no-colors',
                                 default=False, action='store_true',
                                 help='No colors for tty output.')

    argument_parser.add_argument('-S', '--show-sections', default=False, action='store_true',
                                 help='Show section summaries.')

    argument_parser.add_argument('-L', '--list-checks', default=False, action='store_true',
                                 help='List the checks available in the selected profile.')

    argument_parser.add_argument('-F', '--full-lists', default=False, action='store_true',
                                 help='Do not shorten lists of items.')

    argument_parser.add_argument('--dark-theme', default=False, action='store_true',
                                 help='Use a color theme with dark colors.')

    argument_parser.add_argument('--light-theme', default=False, action='store_true',
                                 help='Use a color theme with light colors.')

    argument_parser.add_argument('--timeout', default=10, type=int,
                                 help='Timeout (in seconds) for network operations.')

    argument_parser.add_argument('--json', default=False, action=AddReporterAction, cls=SerializeReporter,
                                 metavar= 'JSON_FILE',
                                 help='Write a json formatted report to JSON_FILE.')

    argument_parser.add_argument('--badges', default=False, action=AddReporterAction, cls=BadgeReporter,
                                 metavar= 'DIRECTORY',
                                 help='Write a set of shields.io badge files to DIRECTORY.')

    argument_parser.add_argument('--ghmarkdown', default=False, action=AddReporterAction, cls=GHMarkdownReporter,
                                 metavar= 'MD_FILE',
                                 help='Write a GitHub-Markdown formatted report to MD_FILE.')

    argument_parser.add_argument('--html', default=False,action=AddReporterAction, cls=HTMLReporter,
                                 metavar= 'HTML_FILE',
                                 help='Write a HTML report to HTML_FILE.')

    iterargs = sorted(profile.iterargs.keys())

    gather_by_choices = iterargs + ['*check']
    comma_separated = ', '.join(gather_by_choices)
    argument_parser.add_argument('-g','--gather-by', default=None,
                                 metavar= 'ITERATED_ARG',
                                 choices=gather_by_choices,
                                 type=str,
                                 help=f'Optional: collect results by ITERATED_ARG\n'
                                      f'In terminal output: create a summary counter for each ITERATED_ARG.\n'
                                      f'In json output: structure the document by ITERATED_ARG.\n'
                                      f'One of: {comma_separated}')

    def parse_order(arg):
        order = filter(len, [n.strip() for n in arg.split(',')])
        return order or None
    comma_separated = ', '.join(iterargs)
    argument_parser.add_argument('-o','--order', default=None, type=parse_order,
                                 help=f'Comma separated list of order arguments.\n'
                                      f'The execution order is determined by the order of the check\n'
                                      f'definitions and by the order of the iterable arguments.\n'
                                      f'A section defines its own order. `--order` can be used to\n'
                                      f'override the order of *all* sections.\n'
                                      f'Despite the ITERATED_ARGS there are two special\n'
                                      f'values available:\n'
                                      f'"*iterargs" -- all remainig ITERATED_ARGS\n'
                                      f'"*check"    -- order by check\n'
                                      f'ITERATED_ARGS: {comma_separated}\n'
                                      f'A sections default is equivalent to: "*iterargs, *check".\n'
                                      f'A common use case is `-o "*check"` when checking the whole \n'
                                      f'collection against a selection of checks picked with `--checkid`.')

    def positive_int(value):
        int_value = int(value)
        if int_value < 0:
            raise argparse.ArgumentTypeError(f'Invalid value "{value}" must be'
                                             f' zero or a positive integer value.')
        return int_value
    argument_parser.add_argument('-J','--jobs', default=0, type=positive_int,
                                 metavar='JOBS', dest='multiprocessing',
                                 help=f'Use multi-processing to run the checks. The argument is the number\n'
                                      f'of worker processes. A sensible number is the cpu count of your\n'
                                      f'system, detected: {os.cpu_count()}.'
                                      f' As an automated shortcut see -j/--auto-jobs.\n'
                                      f'Use 0 to run in single-processing mode (default %(default)s).')
    argument_parser.add_argument('-j','--auto-jobs', const=os.cpu_count(),
                                 action='store_const', dest='multiprocessing',
                                 help='Use the auto detected cpu count (= %(const)s)'
                                      ' as number of worker processes\n'
                                      'in multi-processing. This is equivalent to : `--jobs %(const)s`')
    return argument_parser, values_keys


class ArgumentParserError(Exception): pass

def get_module(name):
    if os.path.isfile(name):
        # This name could also be the name of a module, but if there's a
        # file that we can load the file will win. Otherwise, it's still
        # possible to change the directory
        imported = get_module_from_file(name)
    else:
        # Fails with an appropriate ImportError.
        imported = import_module(name, package=None)
    return imported

def get_profile():
    """ Prefetch the profile module, to fill some holes in the help text. """
    argument_parser, _ = ArgumentParser(Profile(), profile_arg=True)
    # monkey patching will do here
    def error(message): raise ArgumentParserError(message)
    argument_parser.error = error

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

def main(profile=None, values=None):
    # profile can be injected by e.g. check-googlefonts injects it's own profile
    add_profile_arg = False
    if profile is None:
        profile = get_profile()
        add_profile_arg = True

    argument_parser, values_keys = ArgumentParser(profile, profile_arg=add_profile_arg)
    try:
        args = argument_parser.parse_args()
    except ValueValidationError as e:
        print(e)
        argument_parser.print_usage()
        sys.exit(1)

    theme = get_theme(args)
    # the most verbose loglevel wins
    loglevel = min(args.loglevels) if args.loglevels else DEFAULT_LOG_LEVEL

    if args.list_checks:
        list_checks(profile, theme, verbose=loglevel > DEFAULT_LOG_LEVEL)

    values_ = {}
    if values is not None:
        values_.update(values)

    # values_keys are returned by profile.setup_argparse
    # these are keys for custom arguments required by the profile.
    if values_keys:
        for key in values_keys:
            if hasattr(args, key):
                values_[key] = getattr(args, key)

    if args.configfile:
        configuration = Configuration.from_config_file(args.configfile)
    else:
        configuration = Configuration()

    # Since version 0.8.10, we established a convention of never using a dash/hyphen
    # on check IDs. The existing ones were replaced by underscores.
    # All new checks will use underscores when needed.
    # Here we accept dashes to ensure backwards compatibility with the older
    # check IDs that may still be referenced on scripts of our users.
    explicit_checks = None
    exclude_checks = None
    if args.checkid:
        explicit_checks = [c.replace('-', '_') for c in list(args.checkid)]
    if args.exclude_checkid:
        exclude_checks = [x.replace('-', '_') for x in list(args.exclude_checkid)]

    # Command line args overrides config, but only if given
    configuration.maybe_override(Configuration(
        custom_order=args.order,
        explicit_checks=explicit_checks,
        exclude_checks=exclude_checks,
        full_lists=args.full_lists
    ))
    runner_kwds = dict(values=values_, config=configuration)
    try:
        runner = CheckRunner(profile, **runner_kwds)
    except ValueValidationError as e:
        print(e)
        argument_parser.print_usage()
        sys.exit(1)

    is_async = args.multiprocessing != 0

    tr = TerminalReporter(runner=runner, is_async=is_async
                         , print_progress=not args.no_progress
                         , succinct=args.succinct
                         , check_threshold=loglevel
                         , log_threshold=args.loglevel_messages or loglevel
                         , theme=theme
                         , collect_results_by=args.gather_by
                         , skip_status_report=None if args.show_sections \
                                                   else (SECTIONSUMMARY, )
                         )
    reporters = [tr]
    if "reporters" not in args:
        args.reporters = []

    for reporter_class, output_file in args.reporters:
        reporters.append(reporter_class(loglevels=args.loglevels,
                             runner=runner,
                             succinct=args.succinct,
                             collect_results_by=args.gather_by,
                             output_file=output_file
                         ))

    if args.multiprocessing == 0:
        status_generator = runner.run()
    else:
        status_generator = multiprocessing_runner(args.multiprocessing, runner, runner_kwds)

    distribute_generator(status_generator, [reporter.receive for reporter in reporters])

    for reporter in reporters:
        reporter.write()

    # Fail and error let the command fail
    return 1 if tr.worst_check_status in (ERROR, FAIL) else 0


def list_checks(profile, theme, verbose=False):
    if verbose:
        for section in profile._sections.values():
            print(theme["list-checks: section"]("\nSection:") + " " + section.name)
            for check in section._checks:
                print(theme["list-checks: check-id"](check.id) + "\n" +
                      theme["list-checks: description"](f'"{check.description}"') + "\n")
    else:
        for _, section in profile._sections.items():
            for check in section._checks:
                print(check.id)
    sys.exit()


if __name__ == '__main__':
    sys.exit(main())
