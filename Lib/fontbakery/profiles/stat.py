from fontbakery.callable import check
from fontbakery.message import Message
from fontbakery.status import FAIL, PASS
from fontbakery.utils import bullet_list

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import (  # NOQA pylint: disable=unused-import
    profile_factory,
)

profile_imports = ((".", ("shared_conditions",)),)


@check(
    id="com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    rationale="""
        According to the OpenType spec, there must be an Axis Record
        for every axis defined in the fvar table.

        https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/googlefonts/fontbakery/pull/3017",
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

        https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-value-tables
    """,
    conditions=["has_STAT_table"],
    proposal="https://github.com/googlefonts/fontbakery/issues/3090",
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
                if axis_value.AxisIndex != axis_index:
                    # Not the axis we're collecting for, skip.
                    continue

                axis_value_format = axis_value.Format
                if axis_value_format == 2:
                    axis_values.add(axis_value.NominalValue)
                else:
                    axis_values.add(axis_value.Value)

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
