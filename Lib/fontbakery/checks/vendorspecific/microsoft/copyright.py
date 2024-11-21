from fontbakery.checks.vendorspecific.microsoft import ensure_name_id_exists
from fontbakery.prelude import check


@check(
    id="microsoft/copyright",
    rationale="""
        Check whether the copyright string exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_copyright(ttFont):
    """Validate copyright string in name table."""
    yield from ensure_name_id_exists(ttFont, 0, "copyright")
