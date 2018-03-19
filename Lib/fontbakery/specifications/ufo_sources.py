# -*- coding: utf-8 -*-
#
# This file has been automatically formatted with `yapf --style '
# {based_on_style: google}'` and `docformatter`.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check, condition
from fontbakery.checkrunner import ERROR, FAIL, PASS, Section, Spec
from fontbakery.constants import CRITICAL

default_section = Section('Default')


class UFOSpec(Spec):

    def setup_argparse(self, argument_parser):
        """Set up custom arguments needed for this spec."""
        import glob
        import logging
        import argparse

        def get_fonts(pattern):

            fonts_to_check = []
            # use glob.glob to accept *.ufo

            for fullpath in glob.glob(pattern):
                if fullpath.endswith(".ufo"):
                    fonts_to_check.append(fullpath)
                else:
                    logging.warning(
                        ("Skipping '{}' as it does not seem "
                         "to be valid UFO source directory.").format(fullpath))
            return fonts_to_check

        class MergeAction(argparse.Action):

            def __call__(self, parser, namespace, values, option_string=None):
                target = [item for l in values for item in l]
                setattr(namespace, self.dest, target)

        argument_parser.add_argument(
            'fonts',
            nargs='+',
            type=get_fonts,
            action=MergeAction,
            help='font file path(s) to check.'
            ' Wildcards like *.ufo are allowed.')
        return ('fonts',)


# ----------------------------------------------------------------------------
# This variable serves as an exportable anchor point, see e.g. the
# Lib/fontbakery/commands/check_ufo_sources.py script.
specification = UFOSpec(
    default_section=default_section,
    iterargs={'font': 'fonts'},
    derived_iterables={'ufo_sources': ('ufo_source', True)})

register_check = specification.register_check
register_condition = specification.register_condition
# ----------------------------------------------------------------------------


@register_condition
@condition
def ufo_source(font):
    import defcon
    return defcon.Font(font)


@register_check
@check(id='com.daltonmaag/check/ufolint', priority=CRITICAL)
def com_daltonmaag_check_ufolint(font):
    """Run ufolint on UFO source directory."""
    import subprocess
    ufolint_cmd = ["ufolint", font]

    try:
        subprocess.check_output(ufolint_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        yield FAIL, ("ufolint failed the UFO source. Output follows :"
                     "\n\n{}\n").format(e.output)
    except OSError:
        yield ERROR, "ufolint is not available!"

    yield PASS, "ufolint passed the UFO source."


for section_name, section in specification._sections.items():
    print("There is a total of {} checks on {}.".format(
        len(section._checks), section_name))
