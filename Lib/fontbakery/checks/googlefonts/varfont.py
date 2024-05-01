import os
from collections import defaultdict

from fontbakery.checks.googlefonts.conditions import expected_font_names
from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID
from fontbakery.prelude import FAIL, PASS, SKIP, WARN, Message, check, condition
from fontbakery.testable import Font
from fontbakery.utils import exit_with_install_instructions, markdown_table


@check(
    id="com.google.fonts/check/STAT",
    conditions=["is_variable_font", "expected_font_names"],
    rationale="""
        Check a font's STAT table contains compulsory Axis Values which exist
        in the Google Fonts Axis Registry.

        We cannot determine what Axis Values the user will set for axes such as
        opsz, GRAD since these axes are unique for each font so we'll skip them.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def com_google_fonts_check_stat(ttFont, expected_font_names):
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
    id="com.google.fonts/check/fvar_instances",
    conditions=["is_variable_font"],
    rationale="""
        Check a font's fvar instance coordinates comply with our guidelines:
        https://googlefonts.github.io/gf-guide/variable.html#fvar-instances
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def com_google_fonts_check_fvar_instances(ttFont, ttFonts):
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
    id="com.google.fonts/check/fvar_name_entries",
    conditions=["is_variable_font"],
    rationale="""
        The purpose of this check is to make sure that all name entries referenced
        by variable font instances do exist in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2069",
)
def com_google_fonts_check_fvar_name_entries(ttFont):
    """All name entries referenced by fvar instances exist on the name table?"""

    for instance in ttFont["fvar"].instances:
        entries = [
            entry
            for entry in ttFont["name"].names
            if entry.nameID == instance.subfamilyNameID
        ]
        if len(entries) == 0:
            yield FAIL, Message(
                "missing-name",
                f"Named instance with coordinates {instance.coordinates}"
                f" lacks an entry on the name table"
                f" (nameID={instance.subfamilyNameID}).",
            )


@check(
    id="com.google.fonts/check/varfont/consistent_axes",
    rationale="""
        In order to facilitate the construction of intuitive and friendly user
        interfaces, all variable font files in a given family should have the same set
        of variation axes. Also, each axis must have a consistent setting of min/max
        value ranges accross all the files.
    """,
    conditions=["VFs"],
    proposal="https://github.com/fonttools/fontbakery/issues/2810",
)
def com_google_fonts_check_varfont_consistent_axes(VFs):
    """Ensure that all variable font files have the same set of axes and axis ranges."""
    ref_ranges = {}
    for vf in VFs:
        ref_ranges.update(
            {k.axisTag: (k.minValue, k.maxValue) for k in vf["fvar"].axes}
        )

    for vf in VFs:
        for axis in ref_ranges:
            if axis not in map(lambda x: x.axisTag, vf["fvar"].axes):
                yield FAIL, Message(
                    "missing-axis",
                    f"{os.path.basename(vf.reader.file.name)}:"
                    f" lacks a '{axis}' variation axis.",
                )

    expected_ranges = {
        axis: {
            (
                vf["fvar"].axes[vf["fvar"].axes.index(axis)].minValue,
                vf["fvar"].axes[vf["fvar"].axes.index(axis)].maxValue,
            )
            for vf in VFs
        }
        for axis in ref_ranges
        if axis in vf["fvar"].axes
    }

    for axis, ranges in expected_ranges:
        if len(ranges) > 1:
            yield FAIL, Message(
                "inconsistent-axis-range",
                "Axis 'axis' has diverging ranges accross the family: {ranges}.",
            )


@check(
    id="com.google.fonts/check/varfont/generate_static",
    rationale="""
        Google Fonts may serve static fonts which have been generated from variable
        fonts. This test will attempt to generate a static ttf using fontTool's
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
def com_google_fonts_check_varfont_generate_static(ttFont):
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
    id="com.google.fonts/check/varfont/has_HVAR",
    rationale="""
        Not having a HVAR table can lead to costly text-layout operations on some
        platforms, which we want to avoid.

        So, all variable fonts on the Google Fonts collection should have an HVAR
        with valid values.

        More info on the HVAR table can be found at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements
    """,  # FIX-ME: We should clarify which are these
    #         platforms in which there can be issues
    #         with costly text-layout operations
    #         when an HVAR table is missing!
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2119",
)
def com_google_fonts_check_varfont_has_HVAR(ttFont):
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
    id="com.google.fonts/check/varfont/bold_wght_coord",
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
def com_google_fonts_check_varfont_bold_wght_coord(font):
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
    id="com.google.fonts/check/varfont/duplexed_axis_reflow",
    rationale="""
        Certain axes, such as grade (GRAD) or roundness (ROND), should not
        change any advanceWidth or kerning data across the font's design space.
        This is because altering the advance width of glyphs can cause text reflow.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3187",
)
def com_google_fonts_check_varfont_duplexed_axis_reflow(font, ttFont, config):
    """Ensure VFs with duplexed axes do not vary horizontal advance."""
    from fontbakery.utils import all_kerning, pretty_print_list

    DUPLEXED_AXES = {"GRAD", "ROND"}
    relevant_axes = set(font.axes_by_tag.keys()) & DUPLEXED_AXES
    relevant_axes_display = " or ".join(relevant_axes)

    if not (relevant_axes):
        yield SKIP, Message("no-relevant-axes", "This font has no duplexed axes")
        return

    gvar = ttFont["gvar"]
    bad_glyphs_by_axis = defaultdict(set)
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            for duplexed_axis in relevant_axes:
                if duplexed_axis not in delta.axes:
                    continue
                if any(c is not None and c != (0, 0) for c in delta.coordinates[-4:]):
                    bad_glyphs_by_axis[duplexed_axis].add(glyph)

    for duplexed_axis, bad_glyphs in bad_glyphs_by_axis.items():
        bad_glyphs_list = pretty_print_list(config, sorted(bad_glyphs))
        yield FAIL, Message(
            f"{duplexed_axis.lower()}-causes-reflow",
            "The following glyphs have variation in horizontal"
            f" advance due to duplexed axis {duplexed_axis}:"
            f" {bad_glyphs_list}",
        )

    # Determine if any kerning rules vary the horizontal advance.
    # This is going to get grubby.

    if "GDEF" in ttFont and hasattr(ttFont["GDEF"].table, "VarStore"):
        effective_regions = set()
        varstore = ttFont["GDEF"].table.VarStore
        regions = varstore.VarRegionList.Region
        for axis in relevant_axes:
            axis_index = [x.axisTag == axis for x in ttFont["fvar"].axes].index(True)
            for ix, region in enumerate(regions):
                axis_tent = region.VarRegionAxis[axis_index]
                effective = (
                    axis_tent.StartCoord != axis_tent.PeakCoord
                    or axis_tent.PeakCoord != axis_tent.EndCoord
                )
                if effective:
                    effective_regions.add(ix)

        # Some regions vary *something* along the axis. But what?
        if effective_regions:
            kerning = all_kerning(ttFont)
            for left, right, v1, v2 in kerning:
                if v1 and hasattr(v1, "XAdvDevice") and v1.XAdvDevice:
                    variation = [v1.XAdvDevice.StartSize, v1.XAdvDevice.EndSize]
                    regions = varstore.VarData[variation[0]].VarRegionIndex
                    if any(region in effective_regions for region in regions):
                        deltas = varstore.VarData[variation[0]].Item[variation[1]]
                        effective_deltas = [
                            deltas[ix]
                            for ix, region in enumerate(regions)
                            if region in effective_regions
                        ]
                        if any(x for x in effective_deltas):
                            yield FAIL, Message(
                                "duplexed-kern-causes-reflow",
                                f"Kerning rules cause variation in"
                                f" horizontal advance on a duplexed axis "
                                f" ({relevant_axes_display})"
                                f" (e.g. {left}/{right})",
                            )
                            break


@check(
    id="com.google.fonts/check/varfont_duplicate_instance_names",
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
def com_google_fonts_check_varfont_duplicate_instance_names(ttFont):
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


@check(
    id="com.google.fonts/check/varfont/unsupported_axes",
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
def com_google_fonts_check_varfont_unsupported_axes(font):
    """Ensure VFs do not contain the ital axis."""
    if font.ital_axis:
        yield FAIL, Message(
            "unsupported-ital",
            'The "ital" axis is not yet well supported on Google Chrome.',
        )


@check(
    id="com.google.fonts/check/mandatory_avar_table",
    rationale="""
        Most variable fonts should include an avar table to correctly define
        axes progression rates.

        For example, a weight axis from 0% to 100% doesn't map directly to 100 to 1000,
        because a 10% progression from 0% may be too much to define the 200,
        while 90% may be too little to define the 900.

        If the progression rates of axes is linear, this check can be ignored.
        Fontmake will also skip adding an avar table if the progression rates
        are linear. However, we still recommend designers visually proof each
        instance is at the expected weight, width etc.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3100"
    # NOTE: This is a high-priority WARN.
)
def com_google_fonts_check_mandatory_avar_table(ttFont):
    """Ensure variable fonts include an avar table."""
    if "avar" not in ttFont:
        yield WARN, Message(
            "missing-avar", "This variable font does not have an avar table."
        )


@condition(Font)
def uharfbuzz_blob(font):
    try:
        import uharfbuzz as hb
    except ImportError:
        exit_with_install_instructions("googlefonts")

    return hb.Blob.from_file_path(font.file)


@check(
    id="com.google.fonts/check/slant_direction",
    conditions=["is_variable_font"],
    rationale="""
        The 'slnt' axis values are defined as negative values for a clockwise (right)
        lean, and positive values for counter-clockwise lean. This is counter-intuitive
        for many designers who are used to think of a positive slant as a lean to
        the right.

        This check ensures that the slant axis direction is consistent with the specs.

        https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3910",
)
def com_google_fonts_check_slant_direction(ttFont, uharfbuzz_blob):
    """Checking direction of slnt axis angles"""
    try:
        import uharfbuzz as hb
    except ImportError:
        exit_with_install_instructions("googlefonts")

    from fontbakery.utils import PointsPen, axis

    if not axis(ttFont, "slnt"):
        yield PASS, "Font has no slnt axis"
        return

    hb_face = hb.Face(uharfbuzz_blob)
    hb_font = hb.Font(hb_face)
    buf = hb.Buffer()
    buf.add_str("H")
    features = {"kern": True, "liga": True}
    hb.shape(hb_font, buf, features)

    def x_delta(slant):
        """
        Return the x delta (difference of x position between highest and lowest point)
        for the given slant value.
        """
        hb_font.set_variations({"slnt": slant})
        pen = PointsPen()
        hb_font.draw_glyph_with_pen(buf.glyph_infos[0].codepoint, pen)
        x_delta = pen.highestPoint()[0] - pen.lowestPoint()[0]
        return x_delta

    if x_delta(axis(ttFont, "slnt").minValue) < x_delta(axis(ttFont, "slnt").maxValue):
        yield FAIL, Message(
            "positive-value-for-clockwise-lean",
            "The right-leaning glyphs have a positive 'slnt' axis value,"
            " which is likely a mistake. It needs to be negative"
            " to lean rightwards.",
        )


@check(
    id="com.google.fonts/check/varfont/instances_in_order",
    rationale="""
        Ensure that the fvar table instances are in ascending order of weight.
        Some software, such as Canva, displays the instances in the order they
        are defined in the fvar table, which can lead to confusion if the
        instances are not in order of weight.
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3334",
    severity=2,  # It only affects a few applications
    conditions=["has_wght_axis"],
    experimental="Since 2024/Mar/27",
)
def com_google_fonts_check_varfont_instances_in_order(ttFont, config):
    """Ensure the font's instances are in the correct order."""
    from fontbakery.utils import bullet_list

    coords = [i.coordinates for i in ttFont["fvar"].instances]
    # Partition into sub-lists based on the other axes values.
    # e.g. "Thin Regular", "Bold Regular", "Thin Condensed", "Bold Condensed"
    # becomes [ ["Thin Regular", "Bold Regular"], ["Thin Condensed", "Bold Condensed"] ]
    sublists = [[]]
    last_non_wght = {}
    for coord in coords:
        non_wght = {k: v for k, v in coord.items() if k != "wght"}
        if non_wght != last_non_wght:
            sublists.append([])
            last_non_wght = non_wght
        sublists[-1].append(coord)

    for lst in sublists:
        wght_values = [i["wght"] for i in lst]
        if wght_values != sorted(wght_values):
            yield FAIL, Message(
                "instances-not-in-order",
                "The fvar table instances are not in ascending order of weight:\n"
                + bullet_list(config, lst),
            )
