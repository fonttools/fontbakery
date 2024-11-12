import os

from fontbakery.prelude import INFO, Message, check


@check(
    id="superfamily/list",
    rationale="""
        This is a merely informative check that lists all sibling families
        detected by fontbakery.

        Only the fontfiles in these directories will be considered in
        superfamily-level checks.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1487",
)
def check_superfamily_list(superfamily):
    """List all superfamily filepaths"""
    for family in superfamily:
        yield INFO, Message("family-path", os.path.split(family[0])[0])
