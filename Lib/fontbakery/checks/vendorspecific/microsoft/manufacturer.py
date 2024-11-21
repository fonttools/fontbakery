from fontbakery.prelude import check
from fontbakery.checks.vendorspecific.microsoft import ensure_name_id_exists


@check(
    id="microsoft/manufacturer",
    rationale="""
        Check whether Name ID 8 (manufacturer) exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_manufacturer(ttFont):
    """Validate manufacturer field in name table."""
    yield from ensure_name_id_exists(ttFont, 8, "manufacturer")
