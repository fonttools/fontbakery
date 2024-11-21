from fontbakery.prelude import check
from fontbakery.checks.vendorspecific.microsoft import check_repertoire
from fontbakery.checks.vendorspecific.microsoft.character_repertoires import OGL2


# FIXME: There's no way to run this check, as it is not included in any profile!
@check(
    id="microsoft/ogl2",
    rationale="""
        Check whether the font complies with OGL2.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_ogl2(ttFont):
    """OGL2 compliance."""

    yield from check_repertoire(ttFont, OGL2, "OGL2")
