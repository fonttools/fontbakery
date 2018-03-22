from __future__ import absolute_import, print_function, unicode_literals

import argparse
import runpy
import sys


def main(args=None):
    subcommands = {
        "build-contributors": "fontbakery.commands.build_contributors",
        "check-googlefonts": "fontbakery.commands.check_googlefonts",
        "check-specification": "fontbakery.commands.check_spec",
        "check-ufo-sources": "fontbakery.commands.check_ufo_sources",
        "generate-glyphdata": "fontbakery.commands.generate_glyphdata"
    }

    if len(sys.argv) >= 2 and sys.argv[1] in subcommands:
        # Relay to subcommand.
        subcommand = subcommands[sys.argv[1]]
        sys.argv[0] += " " + sys.argv[1]
        del sys.argv[1]  # Make this indirection less visible for subcommands.
        runpy.run_module(subcommand, run_name='__main__')
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
            choices=subcommands.keys())
        parser.add_argument(
            '--list-subcommands',
            action='store_true',
            help='print the list of subcommnds '
            'to stdout, separated by a space character. This is '
            'usually only used to generate the shell completion code.')
        args = parser.parse_args()

        if args.list_subcommands:
            print(' '.join(subcommands.keys()))
        else:
            parser.print_help()
