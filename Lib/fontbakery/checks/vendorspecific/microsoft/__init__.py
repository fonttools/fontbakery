import re

from fontbakery.prelude import check, PASS, WARN, FAIL
from fontbakery.checks.name import get_family_name, get_subfamily_name


@check(
    id="microsoft/copyright",
    rationale="""
        Check whether the copyright string exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_copyright(ttFont):
    """Validate copyright string in name table."""
    yield from _ensure_name_id_exists(ttFont, 0, "copyright")


@check(
    id="microsoft/version",
    rationale="""
        Check whether Name ID 5 starts with 'Version X.YY'
        where X and Y are digits.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_version(ttFont):
    """Version string formating requirements."""
    version = ttFont["name"].getName(5, 3, 1, 0x0409).toUnicode()
    version_pattern = r"Version \d\.\d\d"
    m = re.match(version_pattern, version)
    if m is None:
        yield FAIL, f"Name ID 5 does not start with 'Version X.YY': '{version}'"
    else:
        yield PASS, "Name ID 5 starts with 'Version X.YY'"


@check(
    id="microsoft/trademark",
    rationale="""
        Check whether Name ID 7 (trademark) exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_trademark(ttFont):
    """Validate trademark field in name table."""
    yield from _ensure_name_id_exists(ttFont, 7, "trademark", WARN)


@check(
    id="microsoft/manufacturer",
    rationale="""
        Check whether Name ID 8 (manufacturer) exists and is not empty.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_manufacturer(ttFont):
    """Validate manufacturer field in name table."""
    yield from _ensure_name_id_exists(ttFont, 8, "manufacturer")


def _ensure_name_id_exists(ttFont, name_id, name_name, negative_status=FAIL):
    name_record = ttFont["name"].getName(name_id, 3, 1, 0x0409)
    if name_record is None:
        yield negative_status, f"Name ID {name_id} ({name_name}) does not exist."
    elif not name_record.toUnicode():
        yield negative_status, f"Name ID {name_id} ({name_name}) exists but is empty."
    else:
        yield PASS, f"Name ID {name_id} ({name_name}) exists and is not empty."


@check(
    id="microsoft/vendor_url",
    rationale="""
        Check whether vendor URL is pointing at microsoft.com
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_vendor_url(ttFont):
    """Validate vendor URL."""
    name_record = ttFont["name"].getName(11, 3, 1, 0x0409)
    if name_record is None:
        yield FAIL, "Name ID 11 (vendor URL) does not exists."
    else:
        vendor_url = name_record.toUnicode()
        vendor_pattern = r"https?://(\w+\.)?microsoft.com/?"
        m = re.match(vendor_pattern, vendor_url)
        if m is None:
            yield FAIL, (f"vendor URL does not point at microsoft.com: '{vendor_url}'")
        else:
            yield PASS, "vendor URL OK"


ms_license_description = (
    "Microsoft supplied font. You may use this font to create, display, "
    "and print content as permitted by the license terms or terms of use, "
    "of the Microsoft product, service, or content in which this font was "
    "included. You may only (i) embed this font in content as permitted by "
    "the embedding restrictions included in this font; and (ii) temporarily "
    "download this font to a printer or other output device to help print "
    "content. Any other use is prohibited."
).replace(
    ",", ""
)  # ignore commas, see below


@check(
    id="microsoft/license_description",
    rationale="""
        Check whether license description is correct.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_license_description(ttFont):
    """Validate license description field in the name table."""
    name_record = ttFont["name"].getName(13, 3, 1, 0x0409)
    if name_record is None:
        yield FAIL, "Name ID 13 (license description) does not exists."
    else:
        license_description = name_record.toUnicode()
        # There are versions around with/without Oxford commas. Let's
        # ignore commas altogether.
        license_description = license_description.replace(",", "")
        if ms_license_description not in license_description:
            yield FAIL, "License description does not contain required text"
        else:
            yield PASS, "License description OK"


@check(
    id="microsoft/fstype",
    rationale="""
        The value of the OS/2.fstype field must be 8 (Editable embedding), meaning,
        according to the OpenType spec:
        
        "Editable embedding: the font may be embedded, and may be temporarily loaded
        on other systems. As with Preview & Print embedding, documents containing
        Editable fonts may be opened for reading. In addition, editing is permitted,
        including ability to format new text using the embedded font, and changes
        may be saved." 
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_fstype(ttFont):
    """Checking OS/2 fsType."""
    required_value = 8
    value = ttFont["OS/2"].fsType
    if value != required_value:
        yield FAIL, (
            f"OS/2 fsType must be set to {required_value}, found {value} instead."
        )
    else:
        yield PASS, "OS/2 fsType is properly set."


@check(
    id="microsoft/vertical_metrics",
    rationale="""
        If OS/2.fsSelection.useTypoMetrics is not set, then
            hhea.ascender == OS/2.winAscent
            hhea.descender == OS/2.winDescent
            hhea.lineGap == 0
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_vertical_metrics(ttFont):
    """Checking hhea OS/2 vertical_metrics."""
    os2_table = ttFont["OS/2"]
    hhea_table = ttFont["hhea"]
    failed = False
    if os2_table.fsSelection & 1 << 7:
        # useTypoMetrics is set
        if hhea_table.ascender != os2_table.sTypoAscender:
            failed = True
            yield FAIL, (
                "hhea.ascent != OS/2.sTypoAscender: "
                f"{hhea_table.ascender} != {os2_table.sTypoAscender}"
            )
        if hhea_table.descender != os2_table.sTypoDescender:
            failed = True
            yield FAIL, (
                "hhea.descent != OS/2.sTypoDescender: "
                f"{abs(hhea_table.descender)} != {os2_table.sTypoDescender}"
            )
        if hhea_table.lineGap != os2_table.sTypoLineGap:
            failed = True
            yield FAIL, (
                "hhea.lineGap != OS/2.sTypoLineGap: "
                f"{abs(hhea_table.lineGap)} != {os2_table.sTypoLineGap}"
            )
    else:
        # useTypoMetrics is clear
        if hhea_table.ascender != os2_table.usWinAscent:
            failed = True
            yield FAIL, (
                "hhea.ascent != OS/2.usWinAscent: "
                f"{hhea_table.ascender} != {os2_table.usWinAscent}"
            )
        if abs(hhea_table.descender) != os2_table.usWinDescent:
            failed = True
            yield FAIL, (
                "hhea.descent != OS/2.usWinDescent: "
                f"{abs(hhea_table.descender)} != {os2_table.usWinDescent}"
            )
    if not failed:
        yield PASS, "Vertical metrics OK"


@check(
    id="microsoft/STAT_axis_values",
    conditions=["has_STAT_table"],
    rationale="""
        Check whether STAT axis values are unique.
    """,  # FIXME: Expand this rationale detailing why the values must be unique.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_axis_values(ttFont):
    """STAT axis values must be unique."""
    stat_table = ttFont["STAT"].table
    axis_values_format1 = set()  # set of (axisIndex, axisValue) tuples
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    for axis_value_record in stat_table.AxisValueArray.AxisValue:
        if axis_value_record.Format == 1:
            axis_index = axis_value_record.AxisIndex
            axis_value = axis_value_record.Value
            key = (axis_index, axis_value)
            if key in axis_values_format1:
                failed = True
                yield FAIL, (
                    f"axis value {axis_value} (format 1) "
                    f"for axis #{axis_index} is not unique"
                )
            axis_values_format1.add(key)
    if not failed:
        yield PASS, "STAT axis values (format 1) are unique"


@check(
    id="microsoft/fvar_STAT_axis_ranges",
    conditions=["has_STAT_table", "is_variable_font"],
    rationale="""
        Check fvar named instance axis values lie within a *single* STAT axis range.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_fvar_STAT_axis_ranges(ttFont):
    """Requirements for named instances and STAT axis ranges."""
    stat_table = ttFont["STAT"].table
    stat_design_axis = stat_table.DesignAxisRecord.Axis
    stat_design_axis_count = len(stat_design_axis)
    fvar_table = ttFont["fvar"]
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    # for each named instance in fvar
    for fvar_instance in fvar_table.instances:
        # for each axis of the named instance
        # first look for an exact match format 4
        format4_match = False
        instance_coord_set = set(fvar_instance.coordinates.items())
        for stat_axis_value_record in stat_table.AxisValueArray.AxisValue:
            if stat_axis_value_record.Format == 4:
                stat_coord_set = set()
                for axis_index, axis_value in stat_axis_value_record.AxisValue.items():
                    if axis_index >= stat_design_axis_count:
                        failed = True
                        yield FAIL, (
                            f"axis index {axis_index} (format 4) "
                            f"is greater than STAT axis count {stat_design_axis_count}"
                        )
                    stat_axis = stat_design_axis[axis_index].AxisTag
                    stat_coord_set.add((stat_axis, axis_value))
                if instance_coord_set == stat_coord_set:
                    format4_match = True
                    break
        # if no exact match for format 4, look for matches by axis in formats 1, 2 and 3
        if not format4_match:
            for instance_axis, instance_value in fvar_instance.coordinates.items():
                found_instance_axis = False
                # for each axis value record in STAT
                for stat_axis_value_record in stat_table.AxisValueArray.AxisValue:
                    # format 1, format 3
                    if stat_axis_value_record.Format in {1, 3}:
                        axis_index = stat_axis_value_record.AxisIndex
                        axis_value = stat_axis_value_record.Value
                        if axis_index >= stat_design_axis_count:
                            failed = True
                            yield FAIL, (
                                f"axis index {axis_index} (format {stat_axis_value_record.Format}) "
                                f"is greater than STAT axis count {stat_design_axis_count}"
                            )
                        stat_axis = stat_design_axis[axis_index].AxisTag
                        if instance_axis == stat_axis and instance_value == axis_value:
                            if found_instance_axis:
                                failed = True
                                yield FAIL, (
                                    f"axis value {instance_value} "
                                    f"(format {stat_axis_value_record.Format}) "
                                    f"for axis {instance_axis} is not unique"
                                )
                            found_instance_axis = True
                    # format 2
                    elif stat_axis_value_record.Format == 2:
                        axis_index = stat_axis_value_record.AxisIndex
                        axis_min_value = stat_axis_value_record.RangeMinValue
                        axis_max_value = stat_axis_value_record.RangeMaxValue
                        # axis_nominal_value = stat_axis_value_record.NominalValue
                        if axis_index >= stat_design_axis_count:
                            failed = True
                            yield FAIL, (
                                f"axis index {axis_index} (format 2) "
                                f"is greater than STAT axis count {stat_design_axis_count}"
                            )
                        stat_axis = stat_design_axis[axis_index].AxisTag
                        if (
                            instance_axis == stat_axis
                            and axis_min_value <= instance_value <= axis_max_value
                        ):
                            if found_instance_axis:
                                failed = True
                                yield FAIL, (
                                    f"axis value {instance_value} (format 2) "
                                    f"for axis {instance_axis} is not unique"
                                )
                            found_instance_axis = True
                if not found_instance_axis:
                    failed = True
                    yield FAIL, (
                        f"axis value {instance_value} "
                        f"for axis {instance_axis} not found in STAT table"
                    )
    if not failed:
        yield PASS, "fvar axis ranges found in STAT table"


@check(
    id="microsoft/STAT_table_eliding_bit",
    conditions=["has_STAT_table"],
    rationale="""
        Validate STAT table eliding bit.
    """,  # FIXME: Expand this rationale text.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_table_eliding_bit(ttFont):
    """Validate STAT table eliding bit"""
    stat_table = ttFont["STAT"].table
    name_table = ttFont["name"]
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    for axis_value_record in stat_table.AxisValueArray.AxisValue:
        if axis_value_record.Format in [1, 2, 3, 4]:
            axis_index = axis_value_record.AxisIndex
            # axis_value = axis_value_record.Value
            value_name_id = axis_value_record.ValueNameID
            axis_value_flags = axis_value_record.Flags
            value_name = name_table.getName(value_name_id, 3, 1, 0x409).toUnicode()
            if value_name == "Regular" and axis_value_flags & 0x0002 == 0:
                failed = True
                yield FAIL, (
                    f"axis value {value_name} "
                    f"(format {axis_value_record.Format}) is not elided"
                )
    if not failed:
        yield PASS, "STAT table eliding bit is valid"


@check(
    id="microsoft/STAT_table_axis_order",
    conditions=["has_STAT_table"],
    rationale="""
        Validate STAT table axisOrder.
    """,
    # FIXME: Expanding this rationale detailing the reasons why
    #        this ordeging is necessary.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_table_axis_order(ttFont):
    """STAT table axis order."""

    # Reversed axis order for STAT table - note ital and slnt are rarely in same
    # font but if they are, ital should be last.
    AXIS_ORDER_REVERSED = ["ital", "slnt", "wdth", "wght", "opsz"]

    failed = False
    stat_table = ttFont["STAT"].table
    stat_design_axis = stat_table.DesignAxisRecord.Axis
    stat_design_axis_count = len(stat_design_axis)
    axis_record_list = []
    axis_set = set()
    for stat_axis in stat_design_axis:
        axis_record = {
            "AxisTag": stat_axis.AxisTag,
            "AxisOrdering": stat_axis.AxisOrdering,
        }
        tag = stat_axis.AxisTag
        axis_set.add(tag)
        axis_record_list.append(axis_record)
    sorted_list = sorted(axis_record_list, key=lambda k: k["AxisOrdering"])
    index = stat_design_axis_count - 1
    for axis in AXIS_ORDER_REVERSED:
        if axis in axis_set:
            if sorted_list[index]["AxisTag"] == axis:
                index -= 1
            else:
                failed = True
                yield FAIL, f"STAT table axisOrder for {axis} is not valid"
    if not failed:
        yield PASS, "STAT table axisOrder is valid"


@check(
    id="microsoft/office_ribz_req",
    rationale="""
        Office fonts:
        Name IDs 1 & 2 must be set for an RBIZ family model.
        I.e. ID 2 can only be one of “Regular”, “Italic”, “Bold”, or
        “Bold Italic”.
        
        All other style designators (including “Light” or
        “Semilight”) must be in ID 1.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_ribz_req(ttFont):
    """MS Office RBIZ requirements."""

    subfamily_name = get_subfamily_name(ttFont)
    if subfamily_name is None:
        yield FAIL, "Name ID 2 (sub family) missing"

    if subfamily_name not in {"Regular", "Italic", "Bold", "Bold Italic"}:
        yield FAIL, (
            f"Name ID 2 (subfamily) invalid: {subfamily_name}; "
            f"must be one of 'Regular', 'Italic', 'Bold' or 'Bold Italic'"
        )
    else:
        yield PASS, "Name ID 2 (subfamily) OK"


# Optional checks
# FIXME: There's no way to run these checks, as they are not included in any profile!


def check_repertoire(ttFont, character_repertoire, name, error_status=FAIL):
    charset = set(ttFont["cmap"].getBestCmap())
    missing = character_repertoire - charset
    if missing:
        missing_formatted = ", ".join(f"0x{v:04X}" for v in sorted(missing))
        yield error_status, (
            f"character repertoire not complete for {name}; missing: {missing_formatted}"
        )
    else:
        yield PASS, f"character repertoire complete for {name}"


@check(
    id="microsoft/wgl4",
    rationale="""
        Check whether the font complies with WGL4.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_wgl4(ttFont):
    """WGL4 compliance."""
    from .character_repertoires import WGL4_OPTIONAL, WGL4_REQUIRED

    yield from check_repertoire(ttFont, WGL4_REQUIRED, "WGL4")
    yield from check_repertoire(
        ttFont, WGL4_OPTIONAL, "WGL4_OPTIONAL", error_status=WARN
    )


@check(
    id="microsoft/ogl2",
    rationale="""
        Check whether the font complies with OGL2.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_office_ogl2(ttFont):
    """OGL2 compliance."""
    from .character_repertoires import OGL2

    yield from check_repertoire(ttFont, OGL2, "OGL2")
