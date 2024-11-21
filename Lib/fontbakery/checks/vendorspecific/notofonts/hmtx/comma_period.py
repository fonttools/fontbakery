from fontbakery.prelude import check, FAIL, SKIP, Message
from fontbakery.utils import get_advance_width_for_char


@check(
    id="notofonts/hmtx/comma_period",
    rationale="""
        If Latin comma and period are encoded in Noto fonts,
        they should have equal advance widths.
    """,
)
def check_htmx_comma_period(ttFont):
    """Check comma and period have the same advance width"""
    comma = get_advance_width_for_char(ttFont, ",")
    period = get_advance_width_for_char(ttFont, ".")
    if comma is None or period is None:
        yield SKIP, "No comma and/or period"
    elif comma != period:
        yield FAIL, Message(
            "comma-period",
            f"Advance width of comma ({comma}) != advance width of period {period}",
        )
