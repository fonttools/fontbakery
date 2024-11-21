from fontbakery.prelude import check, WARN
from fontbakery.checks.vendorspecific.microsoft import check_repertoire
from fontbakery.checks.vendorspecific.microsoft.character_repertoires import (
    WGL4_OPTIONAL,
    WGL4_REQUIRED,
)


# FIXME: There's no way to run this check, as it is not included in any profile!
@check(
    id="microsoft/wgl4",
    rationale="""
        Check whether the font complies with WGL4.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_wgl4(ttFont):
    """WGL4 compliance."""

    yield from check_repertoire(ttFont, WGL4_REQUIRED, "WGL4")
    yield from check_repertoire(
        ttFont, WGL4_OPTIONAL, "WGL4_OPTIONAL", error_status=WARN
    )
