import re

from fontbakery.prelude import check, PASS, FAIL


@check(
    id="microsoft/version",
    rationale="""
        Check whether Name ID 5 starts with 'Version X.YY'
        where X and Y are digits.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_version(ttFont):
    """Version string formating requirements."""
    version = ttFont["name"].getName(5, 3, 1, 0x0409).toUnicode()
    version_pattern = r"Version \d\.\d\d"
    m = re.match(version_pattern, version)
    if m is None:
        yield FAIL, f"Name ID 5 does not start with 'Version X.YY': '{version}'"
    else:
        yield PASS, "Name ID 5 starts with 'Version X.YY'"
