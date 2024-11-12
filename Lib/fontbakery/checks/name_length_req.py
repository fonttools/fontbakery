from fontbakery.prelude import check, FAIL
from fontbakery.utils import get_family_name, get_subfamily_name


@check(
    id="name_length_req",
    rationale="""
        For Office, family and subfamily names must be 31 characters or less total
        to fit in a LOGFONT.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_length_req(ttFont):
    """Maximum allowed length for family and subfamily names."""
    family_name = get_family_name(ttFont)
    subfamily_name = get_subfamily_name(ttFont)
    if family_name is None:
        yield FAIL, "Name ID 1 (family) missing"
    if subfamily_name is None:
        yield FAIL, "Name ID 2 (sub family) missing"

    logfont = (
        family_name
        if subfamily_name in ("Regular", "Bold", "Italic", "Bold Italic")
        else " ".join([family_name, subfamily_name])
    )

    if len(logfont) > 31:
        yield FAIL, (
            f"Family + subfamily name, '{logfont}', is too long: "
            f"{len(logfont)} characters; must be 31 or less"
        )
