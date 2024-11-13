from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/unitsperem",
    rationale="""
        According to the OpenType spec:

        The value of unitsPerEm at the head table must be a value
        between 16 and 16384. Any value in this range is valid.

        In fonts that have TrueType outlines, a power of 2 is recommended
        as this allows performance optimizations in some rasterizers.

        But 1000 is a commonly used value. And 2000 may become
        increasingly more common on Variable Fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_unitsperem(ttFont):
    """Checking unitsPerEm value is reasonable."""
    upem = ttFont["head"].unitsPerEm
    target_upem = [2**i for i in range(4, 15)]
    target_upem.append(1000)
    target_upem.append(2000)
    if upem < 16 or upem > 16384:
        yield FAIL, Message(
            "out-of-range",
            f"The value of unitsPerEm at the head table"
            f" must be a value between 16 and 16384."
            f" Got {upem} instead.",
        )
    elif upem not in target_upem:
        yield WARN, Message(
            "suboptimal",
            f"In order to optimize performance on some"
            f" legacy renderers, the value of unitsPerEm"
            f" at the head table should ideally be"
            f" a power of 2 between 16 to 16384."
            f" And values of 1000 and 2000 are also"
            f" common and may be just fine as well."
            f" But we got {upem} instead.",
        )
