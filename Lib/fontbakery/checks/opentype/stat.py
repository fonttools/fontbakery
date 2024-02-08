import os

from fontbakery.callable import check
from fontbakery.message import Message
from fontbakery.status import FAIL, PASS, WARN, SKIP
from fontbakery.utils import bullet_list


@check(
    id="com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    rationale="""
        According to the OpenType spec, there must be an Axis Record
        for every axis defined in the fvar table.

        https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3017",
)
def com_google_fonts_check_varfont_stat_axis_record_for_each_axis(ttFont, config):
    """All fvar axes have a correspondent Axis Record on STAT table?"""
    fvar_axes = set(a.axisTag for a in ttFont["fvar"].axes)
    stat_axes = set(a.AxisTag for a in ttFont["STAT"].table.DesignAxisRecord.Axis)
    missing_axes = fvar_axes - stat_axes
    if len(missing_axes) > 0:
        yield FAIL, Message(
            "missing-axis-records",
            f"STAT table is missing Axis Records for the following axes:\n\n"
            f"{bullet_list(config, sorted(missing_axes))}",
        )
    else:
        yield PASS, "STAT table has all necessary Axis Records."


@check(
    id="com.adobe.fonts/check/stat_has_axis_value_tables",
    rationale="""
        According to the OpenType spec, in a variable font, it is strongly recommended
        that axis value tables be included for every element of typographic subfamily
        names for all of the named instances defined in the 'fvar' table.

        Axis value tables are particularly important for variable fonts, but can also
        be used in non-variable fonts. When used in non-variable fonts, axis value
        tables for particular values should be implemented consistently across fonts
        in the family.

        If present, Format 4 Axis Value tables are checked to ensure they have more than
        one AxisValueRecord (a strong recommendation from the OpenType spec).

        https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-value-tables
    """,
    conditions=["has_STAT_table"],
    proposal="https://github.com/fonttools/fontbakery/issues/3090",
)
def com_adobe_fonts_check_stat_has_axis_value_tables(ttFont, is_variable_font):
    """STAT table has Axis Value tables?"""
    passed = True
    stat_table = ttFont["STAT"].table

    if ttFont["STAT"].table.AxisValueCount == 0:
        yield FAIL, Message(
            "no-axis-value-tables",
            "STAT table has no Axis Value tables.",
        )
        return

    if is_variable_font:
        # Collect all the values defined for each design axis in the STAT table.
        stat_axes_values = {}
        for axis_index, axis in enumerate(stat_table.DesignAxisRecord.Axis):
            axis_tag = axis.AxisTag
            axis_values = set()

            # Iterate over Axis Value tables.
            for axis_value in stat_table.AxisValueArray.AxisValue:
                axis_value_format = axis_value.Format

                if axis_value_format in (1, 2, 3):
                    if axis_value.AxisIndex != axis_index:
                        # Not the axis we're collecting for, skip.
                        continue

                    if axis_value_format == 2:
                        axis_values.add(axis_value.NominalValue)
                    else:
                        axis_values.add(axis_value.Value)

                elif axis_value_format == 4:
                    # check that axisCount > 1. Also, format 4 records DO NOT
                    # contribute to the "stat_axes_values" list used to check
                    # against fvar instances.
                    # see https://github.com/fonttools/fontbakery/issues/3957
                    if axis_value.AxisCount <= 1:
                        yield FAIL, Message(
                            "format-4-axis-count",
                            "STAT Format 4 Axis Value table has axis count <= 1.",
                        )

                else:
                    # FAIL on unknown axis_value_format
                    yield FAIL, Message(
                        "unknown-axis-value-format",
                        f"AxisValue format {axis_value_format} is unknown.",
                    )

            stat_axes_values[axis_tag] = axis_values

        # Iterate over the 'fvar' named instances, and confirm that every coordinate
        # can be represented by the STAT table Axis Value tables.
        for inst in ttFont["fvar"].instances:
            for coord_axis_tag, coord_axis_value in inst.coordinates.items():
                if (
                    coord_axis_tag in stat_axes_values
                    and coord_axis_value in stat_axes_values[coord_axis_tag]
                ):
                    continue

                yield FAIL, Message(
                    "missing-axis-value-table",
                    f"STAT table is missing Axis Value for"
                    f" {coord_axis_tag!r} value '{coord_axis_value}'",
                )
                passed = False

    if passed:
        yield PASS, "STAT table has Axis Value tables."


@check(
    id="com.google.fonts/check/italic_axis_in_stat",
    rationale="""
        Check that related Upright and Italic VFs have a
        'ital' axis in STAT table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2934",
)
def com_google_fonts_check_italic_axis_in_stat(fonts, config):
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
    passed = True
    for italic_filename in italic_to_roman_mapping:
        italic = italic_filename
        upright = italic_to_roman_mapping[italic_filename]

        for filepath in (upright, italic):
            ttFont = TTFont(filepath)
            if "ital" not in [
                axis.AxisTag for axis in ttFont["STAT"].table.DesignAxisRecord.Axis
            ]:
                passed = False
                yield FAIL, Message(
                    "missing-ital-axis",
                    f"Font {os.path.basename(filepath)}" f" is missing an 'ital' axis.",
                )

    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/italic_axis_in_stat_is_boolean",
    conditions=["style", "has_STAT_table"],
    rationale="""
        Check that the value of the 'ital' STAT axis is boolean (either 0 or 1),
        and elided for the Upright and not elided for the Italic,
        and that the Upright is linked to the Italic.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3668",
)
def com_google_fonts_check_italic_axis_in_stat_is_boolean(ttFont, style):
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
    id="com.google.fonts/check/italic_axis_last",
    conditions=["style", "has_STAT_table"],
    rationale="""
        Check that the 'ital' STAT axis is last in axis order.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3669",
)
def com_google_fonts_check_italic_axis_last(ttFont, style):
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
