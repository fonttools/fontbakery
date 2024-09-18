from fontbakery.checks.vendorspecific.googlefonts.conditions import expected_font_names
from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID
from fontbakery.prelude import FAIL, PASS, SKIP, WARN, Message, check
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/axes_match",
    conditions=["remote_style"],
    rationale="""
        An updated font family must include the same axes found in the Google "
        Fonts version, with the same axis ranges.
    """,
)
def check_axes_match(ttFont, remote_style):
    """Check if the axes match between the font and the Google Fonts version."""
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
        yield FAIL, Message(
            "missing-axes",
            f"Missing axes: {', '.join(missing_axes)}",
        )
    else:
        yield PASS, "Axes match Google Fonts version."


@check(
    id="googlefonts/STAT",
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


@check(
    id="googlefonts/fvar_instances",
    conditions=["is_variable_font"],
    rationale="""
        Check a font's fvar instance coordinates comply with our guidelines:
        https://googlefonts.github.io/gf-guide/variable.html#fvar-instances
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def check_fvar_instances(ttFont, ttFonts):
    """Check variable font instances"""
    expected_names = expected_font_names(ttFont, ttFonts)

    def get_instances(ttFont):
        name = ttFont["name"]
        fvar = ttFont["fvar"]
        res = {}
        for inst in fvar.instances:
            inst_name = name.getName(inst.subfamilyNameID, 3, 1, 0x409)
            if not inst_name:
                continue
            res[inst_name.toUnicode()] = inst.coordinates
        return res

    font_instances = get_instances(ttFont)
    expected_instances = get_instances(expected_names)
    table = []
    for name in set(font_instances.keys()) | set(expected_instances.keys()):
        row = {"Name": name}
        if name in font_instances:
            row["current"] = ", ".join(
                [f"{k}={v}" for k, v in font_instances[name].items()]
            )
        else:
            row["current"] = "N/A"
        if name in expected_instances:
            row["expected"] = ", ".join(
                [f"{k}={v}" for k, v in expected_instances[name].items()]
            )
        else:
            row["expected"] = "N/A"
        table.append(row)
    table = sorted(table, key=lambda k: str(k["expected"]))

    missing = set(expected_instances.keys()) - set(font_instances.keys())
    new = set(font_instances.keys()) - set(expected_instances.keys())
    same = set(font_instances.keys()) & set(expected_instances.keys())
    # check if instances have correct weight.
    if all("wght" in expected_instances[i] for i in expected_instances):
        wght_wrong = any(
            font_instances[i]["wght"] != expected_instances[i]["wght"] for i in same
        )
    else:
        wght_wrong = False

    md_table = markdown_table(table)
    if any([wght_wrong, missing, new]):
        hints = ""
        if missing:
            hints += "- Add missing instances\n"
        if new:
            hints += "- Delete additional instances\n"
        if wght_wrong:
            hints += "- wght coordinates are wrong for some instances"
        yield FAIL, Message(
            "bad-fvar-instances",
            f"fvar instances are incorrect:\n\n" f"{hints}\n\n{md_table}\n\n",
        )
    elif any(font_instances[i] != expected_instances[i] for i in same):
        yield WARN, Message(
            "suspicious-fvar-coords",
            f"fvar instance coordinates for non-wght axes are not the same as"
            f" the fvar defaults. This may be intentional so please check with"
            f" the font author:\n\n"
            f"{md_table}\n\n",
        )


@check(
    id="googlefonts/varfont/generate_static",
    rationale="""
        Google Fonts may serve static fonts which have been generated from variable
        fonts. This check will attempt to generate a static ttf using fontTool's
        varLib mutator.

        The target font will be the mean of each axis e.g:

        **VF font axes**

        - min weight, max weight = 400, 800

        - min width, max width = 50, 100

        **Target Instance**

        - weight = 600

        - width = 75
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/1727",
)
def check_varfont_generate_static(ttFont):
    """Check a static ttf can be generated from a variable font."""
    import tempfile

    from fontTools.varLib import mutator

    try:
        loc = {
            k.axisTag: float((k.maxValue + k.minValue) / 2) for k in ttFont["fvar"].axes
        }
        with tempfile.TemporaryFile() as instance:
            font = mutator.instantiateVariableFont(ttFont, loc)
            font.save(instance)
            yield PASS, "fontTools.varLib.mutator generated a static font instance"
    except Exception as e:
        yield FAIL, Message(
            "varlib-mutator",
            f"fontTools.varLib.mutator failed"
            f" to generated a static font instance\n"
            f"{repr(e)}",
        )


@check(
    id="googlefonts/varfont/has_HVAR",
    rationale="""
        Not having a HVAR table can lead to costly text-layout operations on some
        platforms, which we want to avoid.

        So, all variable fonts on the Google Fonts collection should have an HVAR
        with valid values.

        More info on the HVAR table can be found at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements
    """,
    # FIX-ME: We should clarify which are these platforms in which there can be issues
    #         with costly text-layout operations when an HVAR table is missing!
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2119",
)
def check_varfont_has_HVAR(ttFont):
    """Check that variable fonts have an HVAR table."""
    if "HVAR" not in ttFont.keys():
        yield FAIL, Message(
            "lacks-HVAR",
            "All variable fonts on the Google Fonts collection"
            " must have a properly set HVAR table in order"
            " to avoid costly text-layout operations on"
            " certain platforms.",
        )


@check(
    id="googlefonts/varfont/bold_wght_coord",
    rationale="""
        The Open-Type spec's registered
        design-variation tag 'wght' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght
        does not specify a required value for the 'Bold' instance of a variable font.

        But Dave Crossland suggested that we should enforce
        a required value of 700 in this case (NOTE: a distinction
        is made between "no bold instance present" vs "bold instance is present
        but its wght coordinate is not == 700").
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
            f'The "wght" axis coordinate of'
            f' the "Bold" instance must be 700.'
            f" Got {font.bold_wght_coord} instead.",
        )


@check(
    id="googlefonts/varfont/duplicate_instance_names",
    rationale="""
        This check's purpose is to detect duplicate named instances names in a
        given variable font.
        Repeating instance names may be the result of instances for several VF axes
        defined in `fvar`, but since currently only weight+italic tokens are allowed
        in instance names as per GF specs, they ended up repeating.
        Instead, only a base set of fonts for the most default representation of the
        family can be defined through instances in the `fvar` table, all other
        instances will have to be left to access through the `STAT` table.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2986",
)
def check_varfont_duplicate_instance_names(ttFont):
    """Check variable font instances don't have duplicate names"""
    seen = set()
    duplicate = set()
    PLAT_ID = PlatformID.WINDOWS
    ENC_ID = WindowsEncodingID.UNICODE_BMP
    LANG_ID = WindowsLanguageID.ENGLISH_USA

    for instance in ttFont["fvar"].instances:
        name_id = instance.subfamilyNameID
        name = ttFont["name"].getName(name_id, PLAT_ID, ENC_ID, LANG_ID)

        if name:
            name = name.toUnicode()

            if name in seen:
                duplicate.add(name)
            else:
                seen.add(name)
        else:
            yield FAIL, Message(
                "name-record-not-found",
                f"A 'name' table record for platformID {PLAT_ID},"
                f" encodingID {ENC_ID}, languageID {LANG_ID}({LANG_ID:04X}),"
                f" and nameID {name_id} was not found.",
            )

    if duplicate:
        duplicate_instances = "".join(f"* {inst}\n" for inst in sorted(duplicate))
        yield FAIL, Message(
            "duplicate-instance-names",
            "Following instances names are duplicate:\n\n" f"{duplicate_instances}",
        )
