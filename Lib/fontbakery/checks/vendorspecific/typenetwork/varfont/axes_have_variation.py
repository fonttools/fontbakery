from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="typenetwork/varfont/axes_have_variation",
    rationale="""
        Axes on a variable font must have variation. In other words min and max values
        need to be different. It’s common to find fonts with unnecesary axes
        added like `ital`.
        """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/61", # Currently private repo.
    ],
)
def check_varfont_axes_have_variation(ttFont):
    """Check if font axes have variation"""
    failedAxes = []
    for axis in ttFont["fvar"].axes:
        if axis.minValue == axis.maxValue:
            failedAxes.append(
                {
                    "tag": axis.axisTag,
                    "minValue": axis.minValue,
                    "maxValue": axis.maxValue,
                }
            )

    if failedAxes:
        for failedAxis in failedAxes:
            yield FAIL, Message(
                "axis-has-no-variation",
                f"'{failedAxis['tag']}' axis has no variation its min and max values"
                f" are {failedAxis['minValue'], failedAxis['maxValue']}",
            )
    else:
        yield PASS, "All font axes has variation."
