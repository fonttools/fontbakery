import os

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import pretty_print_list


@check(
    id="googlefonts/family/has_license",
    conditions=["gfonts_repo_structure"],
    rationale="""
        A license file is required for all fonts in the Google Fonts collection.
        This checks that the font's directory contains a file named OFL.txt or
        LICENSE.txt.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_has_license(licenses, config):
    """Check font has a license."""

    if len(licenses) > 1:
        filenames = pretty_print_list(
            config, [os.path.basename(license) for license in licenses]
        )
        yield FAIL, Message(
            "multiple",
            f"More than a single license file found: {filenames}",
        )
    elif not licenses:
        yield FAIL, Message(
            "no-license",
            "No license file was found."
            " Please add an OFL.txt or a LICENSE.txt file."
            " If you are running fontbakery on a Google Fonts"
            " upstream repo, which is fine, just make sure"
            " there is a temporary license file in the same folder.",
        )
