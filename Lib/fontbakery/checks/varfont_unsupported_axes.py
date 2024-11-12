from fontbakery.prelude import check, Message, FAIL


@check(
    id="varfont/unsupported_axes",
    rationale="""
        The 'ital' axis is not supported yet in Google Chrome.

        For the time being, we need to ensure that VFs do not contain this axis.
        Once browser support is better, we can deprecate this check.

        For more info regarding browser support, see:
        https://arrowtype.github.io/vf-slnt-test/
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2866",
)
def check_varfont_unsupported_axes(font):
    """Ensure VFs do not contain (yet) the ital axis."""
    if font.ital_axis:
        yield FAIL, Message(
            "unsupported-ital",
            'The "ital" axis is not yet well supported on Google Chrome.',
        )
