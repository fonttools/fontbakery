from fontbakery.prelude import check, FAIL, Message


@check(
    id="io.github.abysstypeco/check/ytlc_sanity",
    rationale="""
        This check follows the values of the ytlc axis proposed by Font Bureau.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3130",
)
def io_github_abysstypeco_check_ytlc_sanity(ttFont):
    """Check if ytlc values are sane in vf"""

    for axis in ttFont["fvar"].axes:
        if not axis.axisTag == "ytlc":
            continue

        if axis.minValue < 0 or axis.maxValue > 1000:
            yield FAIL, Message(
                "invalid-range",
                f"The range of ytlc values"
                f" ({axis.minValue} - {axis.maxValue}) does not conform"
                f" to the expected range of ytlc which"
                f" should be min value 0 to max value 1000",
            )
