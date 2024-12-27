from fontbakery.prelude import check, Message, FAIL, PASS, SKIP


@check(
    id="varfont/bold_wght_coord",
    rationale="""
        The OpenType spec's registered
        design-variation tag 'wght' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght
        does not specify a required value for the 'Bold' instance of a variable font.

        But Dave Crossland suggested that a required value of 700 should be enforced 
        in this case (NOTE: a distinction is made between "no bold instance present"
        vs "bold instance is present but its wght coordinate is not == 700").
    """,
    conditions=["is_variable_font", "has_wght_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_bold_wght_coord(font):
    """
    The variable font 'wght' (Weight) axis coordinate must be 700 on the 'Bold'
    instance.
    """
    wght = font.wght_axis
    if font.bold_wght_coord is None:
        if wght and wght.maxValue < 700:
            yield SKIP, Message("no-bold-weight", "Weight axis doesn't go up to bold")
            return
        yield FAIL, Message("no-bold-instance", '"Bold" instance not present.')
    elif font.bold_wght_coord == 700:
        yield PASS, "Bold:wght is 700."
    else:
        yield FAIL, Message(
            "wght-not-700",
            f'The "wght" axis coordinate of the "Bold" instance must be 700.'
            f" Got {font.bold_wght_coord} instead.",
        )
