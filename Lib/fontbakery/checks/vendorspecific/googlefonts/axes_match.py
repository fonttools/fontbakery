from fontbakery.prelude import SKIP, FAIL, PASS, Message, check


@check(
    id="googlefonts/axes_match",
    conditions=["is_variable_font", "remote_style"],
    rationale="""
        An updated font family must include the same axes found in the Google "
        Fonts version, with the same axis ranges.
    """,
)
def check_axes_match(ttFont, remote_style):
    """Check if the axes match between the font and the Google Fonts version."""
    if "fvar" not in remote_style:
        yield SKIP, "Remote style is a static font."
        return
    remote_axes = {
        a.axisTag: (a.minValue, a.maxValue) for a in remote_style["fvar"].axes
    }
    font_axes = {a.axisTag: (a.minValue, a.maxValue) for a in ttFont["fvar"].axes}

    missing_axes = []
    for axis, remote_axis_range in remote_axes.items():
        if axis not in font_axes:
            missing_axes.append(axis)
            continue
        axis_range = font_axes[axis]
        axis_min, axis_max = axis_range
        remote_axis_min, remote_axis_max = remote_axis_range
        if axis_min > remote_axis_min:
            yield FAIL, Message(
                "axis-min-out-of-range",
                f"Axis '{axis}' min value is out of range."
                f" Expected '{remote_axis_min}', got '{axis_min}'.",
            )
        if axis_max < remote_axis_max:
            yield FAIL, Message(
                "axis-max-out-of-range",
                f"Axis {axis} max value is out of range."
                f" Expected {remote_axis_max}, got {axis_max}.",
            )

    if missing_axes:
        missing_axes = ", ".join(missing_axes)
        yield FAIL, Message("missing-axes", f"Missing axes: {missing_axes}")
    else:
        yield PASS, "Axes match Google Fonts version."
