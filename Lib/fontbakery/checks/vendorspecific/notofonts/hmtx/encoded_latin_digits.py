from fontbakery.prelude import check, FAIL, SKIP, Message
from fontbakery.utils import get_advance_width_for_char


@check(
    id="notofonts/hmtx/encoded_latin_digits",
    rationale="""
        Encoded Latin digits in Noto fonts should have equal advance widths.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_htmx_encoded_latin_digits(ttFont):
    """Check all encoded Latin digits have the same advance width"""
    digits = "0123456789"
    zero_width = get_advance_width_for_char(ttFont, "0")
    if zero_width is None:
        yield SKIP, "No encoded Latin digits"
        return

    for d in digits:
        actual_width = get_advance_width_for_char(ttFont, d)
        if actual_width is None:
            yield FAIL, Message("missing-digit", f"Missing Latin digit {d}")
        elif actual_width != zero_width:
            yield FAIL, Message(
                "bad-digit-width",
                f"Width of {d} was expected to be "
                f"{zero_width} but was {actual_width}",
            )
