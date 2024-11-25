import re

from fontbakery.prelude import check, Message, FAIL
from fontbakery.checks.vendorspecific.googlefonts.constants import (
    DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    EXPECTED_COPYRIGHT_PATTERN,
)


@check(
    id="googlefonts/license/OFL_copyright",
    conditions=["license_contents"],
    rationale="""
        An OFL.txt file's first line should be the font copyright.

    """
    + DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="https://github.com/fonttools/fontbakery/issues/2764",
)
def check_license_OFL_copyright(license_contents):
    """Check license file has good copyright string."""

    string = license_contents.strip().split("\n")[0].lower()
    if not re.search(EXPECTED_COPYRIGHT_PATTERN, string):
        yield FAIL, Message(
            "bad-format",
            f"First line in license file is:\n\n"
            f'"{string}"\n\n'
            f"which does not match the expected format, similar to:\n\n"
            f'"Copyright 2022 The Familyname Project Authors (git url)"',
        )
