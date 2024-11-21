from fontbakery.prelude import check, PASS, FAIL
from fontbakery.utils import get_subfamily_name


@check(
    id="microsoft/office_ribz_req",
    rationale="""
        Office fonts:
        Name IDs 1 & 2 must be set for an RBIZ family model.
        I.e. ID 2 can only be one of “Regular”, “Italic”, “Bold”, or
        “Bold Italic”.
        
        All other style designators (including “Light” or
        “Semilight”) must be in ID 1.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_ribz_req(ttFont):
    """MS Office RBIZ requirements."""

    subfamily_name = get_subfamily_name(ttFont)
    if subfamily_name is None:
        yield FAIL, "Name ID 2 (sub family) missing"

    if subfamily_name not in {"Regular", "Italic", "Bold", "Bold Italic"}:
        yield FAIL, (
            f"Name ID 2 (subfamily) invalid: {subfamily_name}; "
            f"must be one of 'Regular', 'Italic', 'Bold' or 'Bold Italic'"
        )
    else:
        yield PASS, "Name ID 2 (subfamily) OK"
