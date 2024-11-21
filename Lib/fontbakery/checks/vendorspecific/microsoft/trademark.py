from fontbakery.prelude import check, WARN
from fontbakery.checks.vendorspecific.microsoft import ensure_name_id_exists


@check(
    id="microsoft/trademark",
    rationale="""
        Check whether Name ID 7 (trademark) exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_trademark(ttFont):
    """Validate trademark field in name table."""
    yield from ensure_name_id_exists(ttFont, 7, "trademark", WARN)
