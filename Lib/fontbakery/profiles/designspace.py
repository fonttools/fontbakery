import os

from fontbakery.checkrunner import Section, PASS, FAIL, WARN, ERROR, INFO, SKIP, Profile
from fontbakery.callable import condition, check, disable
from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.utils import pretty_print_list
import defcon

profile_imports = ".shared_conditions"


class DesignspaceProfile(Profile):
    def setup_argparse(self, argument_parser):
        """Set up custom arguments needed for this profile."""
        import glob
        import logging
        import argparse

        def get_fonts(pattern):

            fonts_to_check = []
            # use glob.glob to accept *.designsapce

            for fullpath in glob.glob(pattern):
                fullpath_absolute = os.path.abspath(fullpath)
                if fullpath_absolute.lower().endswith(
                    ".designspace"
                ) and os.path.isfile(fullpath_absolute):
                    fonts_to_check.append(fullpath)
                else:
                    logging.warning(
                        (
                            "Skipping '{}' as it does not seem to be"
                            " valid Designspace file."
                        ).format(fullpath)
                    )
            return fonts_to_check

        class MergeAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                target = [item for l in values for item in l]
                setattr(namespace, self.dest, target)

        argument_parser.add_argument(
            "fonts",
            # To allow optional commands like "-L" to work without other input
            # files:
            nargs="*",
            type=get_fonts,
            action=MergeAction,
            help="font file path(s) to check."
            " Wildcards like *.designspace are allowed.",
        )

        return ("fonts",)


fonts_expected_value = ExpectedValue(
    "fonts",
    default=[],
    description="A list of the designspace file paths to check.",
    validator=lambda fonts: (True, None) if len(fonts) else (False, "Value is empty."),
)

# ----------------------------------------------------------------------------
# This variable serves as an exportable anchor point, see e.g. the
# Lib/fontbakery/commands/check_ufo_sources.py script.
profile = DesignspaceProfile(
    default_section=Section("Default"),
    iterargs={"font": "fonts"},
    expected_values={fonts_expected_value.name: fonts_expected_value},
)

register_check = profile.register_check
register_condition = profile.register_condition

basic_checks = Section("Basic Designspace checks")


@register_condition
@condition
def designspace(font):
    from fontTools.designspaceLib import DesignSpaceDocument

    ds = DesignSpaceDocument.fromfile(font)
    return ds


@register_condition
@condition
def sources(designspace):
    return designspace.loadSourceFonts(defcon.Font)


@register_check(section=basic_checks)
@check(id="com.google.fonts/check/designspace_has_sources")
def com_google_fonts_check_designspace_has_sources(sources):
    """See if we can actually load the source files."""
    if not sources:
        yield FAIL, "Unable to load source files."
    else:
        yield PASS, "We have sources."


@register_check(section=basic_checks)
@check(id="com.google.fonts/check/designspace_has_default_master")
def com_google_fonts_check_designspace_has_default_master(designspace):
    """Ensure a default master is defined."""
    if not designspace.findDefault():
        yield FAIL, "Unable to find a default master."
    else:
        yield PASS, "We located a default master."


@register_check(section=basic_checks)
@check(id="com.google.fonts/check/designspace_has_consistent_glyphset")
def com_google_fonts_check_designspace_has_consistent_glyphset(designspace, sources):
    """Ensure non-default masters don't have glyphs not present in the default."""
    default_glyphset = set(designspace.findDefault().font.keys())
    failures = []
    for source in designspace.sources:
        master_glyphset = set(source.font.keys())
        outliers = master_glyphset - default_glyphset
        if outliers:
            failures.append(
                "Source %s has glyphs not present in the default master: %s"
                % (
                    source.filename,
                    ", ".join(list(outliers)),
                )
            )
    if failures:
        formatted_list = "\t* " + pretty_print_list(failures, sep="\n\t* ")
        yield FAIL, Message(
            "inconsistent-glyphset", "Glyphsets were not consistent:\n" + formatted_list
        )
    else:
        yield PASS, "Glyphsets were consistent."


@register_check(section=basic_checks)
@check(id="com.google.fonts/check/designspace_has_consistent_unicodes")
def com_google_fonts_check_designspace_has_consistent_unicodes(designspace, sources):
    """Ensure Unicode assignments are consistent across sources."""
    default_source = designspace.findDefault()
    default_unicodes = {g.name: g.unicode for g in default_source.font}
    failures = []
    for source in designspace.sources:
        for g in source.font:
            if g.name not in default_unicodes:
                # Previous test will cover this
                continue
            if g.unicode != default_unicodes[g.name]:
                failures.append(
                    "Source %s has %s=%s; default master has %s=%s"
                    % (
                        source.filename,
                        g.name,
                        g.unicode,
                        g.name,
                        default_unicodes[g.name],
                    )
                )
    if failures:
        formatted_list = "\t* " + pretty_print_list(failures, sep="\n\t* ")
        yield FAIL, Message(
            "inconsistent-unicodes",
            "Unicode assignments were not consistent:\n" + formatted_list,
        )
    else:
        yield PASS, "Unicode assignments were consistent."
