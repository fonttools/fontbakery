import os

from fontbakery.prelude import check, Message, FAIL, PASS, WARN, SKIP


@check(
    id="opentype/italic_axis_in_stat",
    rationale="""
        Check that related Upright and Italic VFs have a
        'ital' axis in STAT table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2934",
)
def check_italic_axis_in_stat(fonts, config):
    """Ensure VFs have 'ital' STAT axis."""
    from fontTools.ttLib import TTFont

    font_filenames = [f.file for f in fonts]
    italics = [f for f in font_filenames if "Italic" in f]
    missing_roman = []
    italic_to_roman_mapping = {}
    for italic in italics:
        style_from_filename = os.path.basename(italic).split("-")[-1].split(".")[0]
        is_varfont = "[" in style_from_filename

        # to remove the axes syntax used on variable-font filenames:
        if is_varfont:
            style_from_filename = style_from_filename.split("[")[0]

        if style_from_filename == "Italic":
            if is_varfont:
                # "Familyname-Italic[wght,wdth].ttf" => "Familyname[wght,wdth].ttf"
                roman_counterpart = italic.replace("-Italic", "")
            else:
                # "Familyname-Italic.ttf" => "Familyname-Regular.ttf"
                roman_counterpart = italic.replace("Italic", "Regular")
        else:
            # "Familyname-BoldItalic[wght,wdth].ttf" => "Familyname-Bold[wght,wdth].ttf"
            roman_counterpart = italic.replace("Italic", "")

        if is_varfont:
            if roman_counterpart not in font_filenames:
                missing_roman.append(italic)
            else:
                italic_to_roman_mapping[italic] = roman_counterpart

    if missing_roman:
        from fontbakery.utils import pretty_print_list

        missing_roman = pretty_print_list(config, missing_roman)
        yield FAIL, Message(
            "missing-roman",
            f"Italics missing a Roman counterpart, so couldn't check"
            f" both Roman and Italic for 'ital' axis: {missing_roman}",
        )
        return

    # Actual check starts here
    for italic_filename in italic_to_roman_mapping:
        italic = italic_filename
        upright = italic_to_roman_mapping[italic_filename]

        for filepath in (upright, italic):
            ttFont = TTFont(filepath)
            if "ital" not in [
                axis.AxisTag for axis in ttFont["STAT"].table.DesignAxisRecord.Axis
            ]:
                yield FAIL, Message(
                    "missing-ital-axis",
                    f"Font {os.path.basename(filepath)}" f" is missing an 'ital' axis.",
                )


@check(
    id="opentype/italic_axis_in_stat_is_boolean",
    conditions=["style", "has_STAT_table"],
    rationale="""
        Check that the value of the 'ital' STAT axis is boolean (either 0 or 1),
        and elided for the Upright and not elided for the Italic,
        and that the Upright is linked to the Italic.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3668",
)
def check_italic_axis_in_stat_is_boolean(ttFont, style):
    """Ensure 'ital' STAT axis is boolean value"""

    def get_STAT_axis(font, tag):
        for axis in font["STAT"].table.DesignAxisRecord.Axis:
            if axis.AxisTag == tag:
                return axis
        return None

    def get_STAT_axis_value(font, tag):
        for i, axis in enumerate(font["STAT"].table.DesignAxisRecord.Axis):
            if axis.AxisTag == tag:
                for axisValue in font["STAT"].table.AxisValueArray.AxisValue:
                    if axisValue.AxisIndex == i:
                        linkedValue = None
                        if hasattr(axisValue, "LinkedValue"):
                            linkedValue = axisValue.LinkedValue
                        return axisValue.Value, axisValue.Flags, linkedValue
        return None, None, None

    if not get_STAT_axis(ttFont, "ital"):
        yield SKIP, "Font doesn't have an ital axis"
        return

    value, flags, linkedValue = get_STAT_axis_value(ttFont, "ital")
    if (value, flags, linkedValue) == (None, None, None):
        yield SKIP, "No 'ital' axis in STAT."
        return

    passed = True
    # Font has an 'ital' axis in STAT
    if "Italic" in style:
        if value != 1:
            passed = False
            yield WARN, Message(
                "wrong-ital-axis-value",
                f"STAT table 'ital' axis has wrong value."
                f" Expected: 1, got '{value}'.",
            )
        if flags != 0:
            passed = False
            yield WARN, Message(
                "wrong-ital-axis-flag",
                f"STAT table 'ital' axis flag is wrong."
                f" Expected: 0 (not elided), got '{flags}'.",
            )
    else:
        if value != 0:
            passed = False
            yield WARN, Message(
                "wrong-ital-axis-value",
                f"STAT table 'ital' axis has wrong value."
                f" Expected: 0, got '{value}'.",
            )
        if flags != 2:
            passed = False
            yield WARN, Message(
                "wrong-ital-axis-flag",
                f"STAT table 'ital' axis flag is wrong.\n"
                f"Expected: 2 (elided)\n"
                f"Got: '{flags}'",
            )
        if linkedValue != 1:
            passed = False
            yield WARN, Message(
                "wrong-ital-axis-linkedvalue",
                "STAT table 'ital' axis is not linked to Italic.",
            )

    if passed:
        yield PASS, "STAT table ital axis values are good."


@check(
    id="opentype/italic_axis_last",
    conditions=["style", "has_STAT_table"],
    rationale="""
        Check that the 'ital' STAT axis is last in axis order.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3669",
)
def check_italic_axis_last(ttFont, style):
    """Ensure 'ital' STAT axis is last."""

    def get_STAT_axis(font, tag):
        for axis in font["STAT"].table.DesignAxisRecord.Axis:
            if axis.AxisTag == tag:
                return axis
        return None

    axis = get_STAT_axis(ttFont, "ital")
    if not axis:
        yield SKIP, "No 'ital' axis in STAT."
        return

    if ttFont["STAT"].table.DesignAxisRecord.Axis[-1].AxisTag != "ital":
        yield WARN, Message(
            "ital-axis-not-last",
            "STAT table 'ital' axis is not the last in the axis order.",
        )
    else:
        yield PASS, "STAT table ital axis order is good."
