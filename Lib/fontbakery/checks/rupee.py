from fontbakery.prelude import check, Message, FAIL, PASS


@check(
    id="rupee",
    rationale="""
        Per Bureau of Indian Standards every font supporting one of the
        official Indian languages needs to include Unicode Character
        “₹” (U+20B9) Indian Rupee Sign.
    """,
    conditions=["is_indic_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2967",
)
def check_rupee(ttFont):
    """Ensure indic fonts have the Indian Rupee Sign glyph."""
    if 0x20B9 not in ttFont["cmap"].getBestCmap().keys():
        yield FAIL, Message(
            "missing-rupee",
            "Please add a glyph for Indian Rupee Sign (₹) at codepoint U+20B9.",
        )
    else:
        yield PASS, "Looks good!"
