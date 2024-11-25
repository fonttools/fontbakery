from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/STAT/compulsory_axis_values",
    conditions=["is_variable_font", "expected_font_names"],
    rationale="""
        Check a font's STAT table contains compulsory Axis Values which exist
        in the Google Fonts Axis Registry.

        We cannot determine what Axis Values the user will set for axes such as
        opsz, GRAD since these axes are unique for each font so we'll skip them.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def check_stat(ttFont, expected_font_names):
    """Check a font's STAT table contains compulsory Axis Values."""
    if "STAT" not in ttFont:
        yield FAIL, "Font is missing STAT table"
        return

    AXES_TO_CHECK = {
        "CASL",
        "CRSV",
        "FILL",
        "FLAR",
        "MONO",
        "SOFT",
        "VOLM",
        "wdth",
        "wght",
        "WONK",
    }

    def stat_axis_values(ttFont):
        name = ttFont["name"]
        stat = ttFont["STAT"].table
        axes = [a.AxisTag for a in stat.DesignAxisRecord.Axis]
        res = {}
        if ttFont["STAT"].table.AxisValueCount == 0:
            return res
        axis_values = stat.AxisValueArray.AxisValue
        for ax in axis_values:
            # Google Fonts axis registry cannot check format 4 Axis Values
            if ax.Format == 4:
                continue
            axis_tag = axes[ax.AxisIndex]
            if axis_tag not in AXES_TO_CHECK:
                continue
            ax_name = name.getName(ax.ValueNameID, 3, 1, 0x409).toUnicode()
            if ax.Format == 2:
                value = ax.NominalValue
            else:
                value = ax.Value
            res[(axis_tag, ax_name)] = {
                "Axis": axis_tag,
                "Name": ax_name,
                "Flags": ax.Flags,
                "Value": value,
                "LinkedValue": None
                if not hasattr(ax, "LinkedValue")
                else ax.LinkedValue,
            }
        return res

    font_axis_values = stat_axis_values(ttFont)
    expected_axis_values = stat_axis_values(expected_font_names)

    table = []
    for axis, name in set(font_axis_values.keys()) | set(expected_axis_values.keys()):
        row = {}
        key = (axis, name)
        if key in font_axis_values:
            row["Name"] = name
            row["Axis"] = axis
            row["Current Value"] = font_axis_values[key]["Value"]
            row["Current Flags"] = font_axis_values[key]["Flags"]
            row["Current LinkedValue"] = font_axis_values[key]["LinkedValue"]
        else:
            row["Name"] = name
            row["Axis"] = axis
            row["Current Value"] = "N/A"
            row["Current Flags"] = "N/A"
            row["Current LinkedValue"] = "N/A"
        if key in expected_axis_values:
            row["Name"] = name
            row["Axis"] = axis
            row["Expected Value"] = expected_axis_values[key]["Value"]
            row["Expected Flags"] = expected_axis_values[key]["Flags"]
            row["Expected LinkedValue"] = expected_axis_values[key]["LinkedValue"]
        else:
            row["Name"] = name
            row["Axis"] = axis
            row["Expected Value"] = "N/A"
            row["Expected Flags"] = "N/A"
            row["Expected LinkedValue"] = "N/A"
        table.append(row)
    table.sort(key=lambda k: (k["Axis"], str(k["Expected Value"])))
    md_table = markdown_table(table)

    is_italic = any(a.axisTag in ["ital", "slnt"] for a in ttFont["fvar"].axes)
    missing_ital_av = any("Italic" in r["Name"] for r in table)
    if is_italic and missing_ital_av:
        yield FAIL, Message("missing-ital-axis-values", "Italic Axis Value missing.")

    if font_axis_values != expected_axis_values:
        yield FAIL, Message(
            "bad-axis-values",
            f"Compulsory STAT Axis Values are incorrect:\n\n{md_table}\n\n",
        )
