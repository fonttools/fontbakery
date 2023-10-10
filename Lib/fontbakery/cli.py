import argparse
import pkgutil
import runpy
import signal
import sys
from importlib import import_module

from fontbakery import __version__
import fontbakery.commands
from fontbakery.commands.check_profile import main as check_profile_main

CLI_PROFILES = [
    "adobefonts",
    "fontbureau",
    "fontval",
    "fontwerk",
    "googlefonts",
    "iso15008",
    "notofonts",
    "opentype",
    "shaping",
    "typenetwork",
    "ufo_sources",
    "universal",
    "proposals",
]


def run_profile_check(profilename):
    from fontbakery.utils import set_profile_name

    set_profile_name(profilename)
    module = import_module(f"fontbakery.profiles.{profilename}")
    sys.exit(check_profile_main(module.profile))


def signal_handler(sig, frame):
    print("\nCancelled by user")
    sys.exit(-1)


def main():
    signal.signal(signal.SIGINT, signal_handler)

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
            "Run fontbakery subcommands. Subcommands have their own help messages;\n"
            "to view them add the '-h' (or '--help') option after the subcommand,\n"
            "like in this example:\n    fontbakery universal -h"
        )

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter, description=description
        )
        parser.add_argument(
            "subcommand",
            help="The subcommand to execute",
            nargs="?",
            choices=subcommands,
        )
        parser.add_argument(
            "--list-subcommands",
            action="store_true",
            help="print list of supported subcommands",
        )
        parser.add_argument("--version", action="version", version=__version__)
        args = parser.parse_args()

        if args.list_subcommands:
            print(" ".join(subcommands))
        else:
            parser.print_help()
