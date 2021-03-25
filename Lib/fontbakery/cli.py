import argparse
import pkgutil
import runpy
import sys
from importlib import import_module

import fontbakery.commands
from fontbakery.commands.check_profile import main as check_profile_main

CLI_PROFILES = [
    "adobefonts",
    "fontval",
    "googlefonts",
    "notofonts",
    "opentype",
    "typenetwork",
    "ufo_sources",
    "universal",
]


def run_profile_check(profilename):
    module = import_module("fontbakery.profiles.%s" % profilename)
    sys.exit(check_profile_main(module.profile))


def main():
    subcommands = [
        pkg[1] for pkg in pkgutil.walk_packages(fontbakery.commands.__path__)
    ] + ["check_" + prof for prof in CLI_PROFILES]

    subcommands = [command.replace("_", "-") for command in sorted(subcommands)]

    if len(sys.argv) >= 2 and sys.argv[1] in subcommands:
        # Relay to subcommand.
        subcommand = sys.argv[1]
        subcommand_module = subcommand.replace("-", "_")
        sys.argv[0] += " " + subcommand
        del sys.argv[1]  # Make this indirection less visible for subcommands.
        if (
            subcommand_module.startswith("check_")
            and subcommand_module[6:] in CLI_PROFILES
        ):
            run_profile_check(subcommand_module[6:])
        else:
            runpy.run_module(
                "fontbakery.commands." + subcommand_module, run_name="__main__"
            )
    else:
        description = (
            "Run fontbakery subcommands. Subcommands have their own help "
            "messages. These are usually accessible with the -h/--help flag "
            "positioned after the subcommand, i.e.: fontbakery subcommand -h")

        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            'subcommand',
            help="The subcommand to execute",
            nargs="?",
            choices=subcommands)
        parser.add_argument(
            '--list-subcommands',
            action='store_true',
            help='print the list of subcommands '
            'to stdout, separated by a space character. This is '
            'usually only used to generate the shell completion code.')
        parser.add_argument(
            '--version',
            action='version',
            version=fontbakery.__version__)
        args = parser.parse_args()

        if args.list_subcommands:
            print(' '.join(subcommands))
        else:
            parser.print_help()
