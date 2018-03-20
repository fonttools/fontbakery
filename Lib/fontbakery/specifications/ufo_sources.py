# -*- coding: utf-8 -*-
#
# This file has been automatically formatted with `yapf --style '
# {based_on_style: google}'` and `docformatter`.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from fontbakery.callable import check, condition
from fontbakery.checkrunner import ERROR, FAIL, PASS, WARN, Section, Spec
from fontbakery.constants import CRITICAL


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
                fullpath_absolute = os.path.abspath(fullpath)
                if fullpath_absolute.endswith(".ufo") and os.path.isdir(
                        fullpath_absolute):
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
    default_section=Section('Default'),
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


@register_check
@check(id='com.daltonmaag/check/required-fields')
def com_daltonmaag_check_required_fields(font):
    """Check that required fields are present in the UFO fontinfo.

    ufo2ft requires these info fields to compile a font binary:
    unitsPerEm, ascender, descender, xHeight, capHeight and familyName.
    """
    import defcon

    recommended_fields = []
    ufo = defcon.Font(font)

    for field in [
            "unitsPerEm", "ascender", "descender", "xHeight", "capHeight",
            "familyName"
    ]:
        if ufo.info.__dict__.get("_" + field) is None:
            recommended_fields.append(field)

    if recommended_fields:
        yield FAIL, "Required field(s) missing: {}".format(recommended_fields)
    else:
        yield PASS, "Required fields present."


@register_check
@check(id='com.daltonmaag/check/recommended-fields')
def com_daltonmaag_check_recommended_fields(font):
    """Check that recommended fields are present in the UFO fontinfo.

    This includes fields that should be in any production font.
    """
    import defcon

    recommended_fields = []
    ufo = defcon.Font(font)

    for field in [
            "postscriptUnderlineThickness", "postscriptUnderlinePosition",
            "versionMajor", "versionMinor", "styleName", "copyright", "panose"
    ]:
        if ufo.info.__dict__.get("_" + field) is None:
            recommended_fields.append(field)

    if recommended_fields:
        yield WARN, "Recommended field(s) missing: {}".format(
            recommended_fields)
    else:
        yield PASS, "Recommended fields present."


@register_check
@check(id='com.daltonmaag/check/unnecessary-fields')
def com_daltonmaag_check_unnecessary_fields(font):
    """Check that no unnecessary fields are present in the UFO fontinfo.

    ufo2ft will generate these.

    openTypeOS2CodePageRanges is exempted because it is useful to toggle a range when not _all_ the glyphs in that region are present.

    year is deprecated since UFO v2.
    """
    import defcon

    unnecessary_fields = []
    ufo = defcon.Font(font)

    for field in [
            "openTypeOS2UnicodeRanges", "openTypeNameUniqueID",
            "openTypeNameVersion", "postscriptUniqueID", "year"
    ]:
        if ufo.info.__dict__.get("_" + field) is not None:
            unnecessary_fields.append(field)

    if unnecessary_fields:
        yield WARN, "Unnecessary field(s) present: {}".format(
            unnecessary_fields)
    else:
        yield PASS, "Unnecessary fields omitted."


@register_check
@check(id='com.daltonmaag/check/empty-fields')
def com_daltonmaag_check_empty_fields(font):
    """Check that no empty fields are present in the UFO fontinfo.

    The following fields are exempt because defcon always generates them:
    postscriptBlueValues, postscriptOtherBlues, postscriptFamilyBlues,
    postscriptFamilyOtherBlues, postscriptStemSnapH,
    postscriptStemSnapV.
    """
    import defcon

    empty_fields = []
    ufo = defcon.Font(font)

    for field in ["guidelines"]:
        field_value = ufo.info.__dict__.get("_" + field)
        if field_value is not None and len(field_value) == 0:
            empty_fields.append(field)

    if empty_fields:
        yield WARN, "Empty field(s) present: {}".format(empty_fields)
    else:
        yield PASS, "No empty fields."


for section_name, section in specification._sections.items():
    print("There is a total of {} checks on {}.".format(
        len(section._checks), section_name))
