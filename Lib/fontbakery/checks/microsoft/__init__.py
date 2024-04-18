import re

from fontbakery.prelude import check, PASS, WARN, FAIL


def get_family_name(ttFont):
    """
    Get the family name from the name table.

    TODO: For now, this is just name ID 1. It should be expanded to at least
    check IDs 16 & 21, and ideally do the whole font differentiator heuristic.
    """
    family_name = ttFont["name"].getName(1, 3, 1, 0x0409)
    if family_name is None:
        return None
    return family_name.toUnicode()


def get_subfamily_name(ttFont):
    """
    Get the subfamily name from the name table.

    TODO: For now, this is just name ID 2. It should be expanded to at least
    check IDs 17 & 22, and ideally do the whole font differentiator heuristic.
    """
    subfamily_name = ttFont["name"].getName(2, 3, 1, 0x0409)
    if subfamily_name is None:
        return None
    return subfamily_name.toUnicode()


@check(id="com.microsoft/check/copyright", rationale="")
def com_microsoft_check_copyright(ttFont):
    """Check whether the copyright string exists and is not empty."""
    yield from _ensure_name_id_exists(ttFont, 0, "copyright")


@check(id="com.microsoft/check/version", rationale="")
def com_microsoft_check_version(ttFont):
    """Check whether Name ID 5 starts with 'Version X.YY' where X and Y
    are digits."""
    version = ttFont["name"].getName(5, 3, 1, 0x0409).toUnicode()
    version_pattern = r"Version \d\.\d\d"
    m = re.match(version_pattern, version)
    if m is None:
        yield FAIL, f"Name ID 5 does not start with 'Version X.YY': '{version}'"
    else:
        yield PASS, "Name ID 5 starts with 'Version X.YY'"


@check(id="com.microsoft/check/trademark", rationale="")
def com_microsoft_check_trademark(ttFont):
    """Check whether Name ID 7 (trademark) exists and is not empty."""
    yield from _ensure_name_id_exists(ttFont, 7, "trademark", WARN)


@check(id="com.microsoft/check/manufacturer", rationale="")
def com_microsoft_check_manufacturer(ttFont):
    """Check whether Name ID 8 (manufacturer) exists and is not empty."""
    yield from _ensure_name_id_exists(ttFont, 8, "manufacturer")


def _ensure_name_id_exists(ttFont, name_id, name_name, negative_status=FAIL):
    name_record = ttFont["name"].getName(name_id, 3, 1, 0x0409)
    if name_record is None:
        yield negative_status, f"Name ID {name_id} ({name_name}) does not exist."
    elif not name_record.toUnicode():
        yield negative_status, f"Name ID {name_id} ({name_name}) exists but is empty."
    else:
        yield PASS, f"Name ID {name_id} ({name_name}) exists and is not empty."


@check(id="com.microsoft/check/vendor_url", rationale="")
def com_microsoft_check_vendor_url(ttFont):
    """Check whether vendor URL is pointing at microsoft.com"""
    name_record = ttFont["name"].getName(11, 3, 1, 0x0409)
    if name_record is None:
        yield FAIL, "Name ID 11 (vendor URL) does not exists."
    else:
        vendor_url = name_record.toUnicode()
        vendor_pattern = r"https?://(\w+\.)?microsoft.com/?"
        m = re.match(vendor_pattern, vendor_url)
        if m is None:
            yield FAIL, (
                f"vendor URL does not point at microsoft.com: " f"'{vendor_url}'"
            )
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


@check(id="com.microsoft/check/license_description", rationale="")
def com_microsoft_check_license_description(ttFont):
    """Check whether license description is correct."""
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


@check(id="com.microsoft/check/typographic_family_name", rationale="")
def com_microsoft_check_typographic_family_name(ttFonts):
    """Check whether Name ID 16 (Typographic Family name) is consistent
    across the set of fonts."""
    values = set()
    for ttFont in ttFonts:
        name_record = ttFont["name"].getName(16, 3, 1, 0x0409)
        if name_record is None:
            values.add("<no value>")
        else:
            values.add(name_record.toUnicode())
    if len(values) != 1:
        yield FAIL, (
            f"Name ID 16 (Typographic Family name) is not consistent "
            f"across fonts. Values found: {sorted(values)}"
        )
    else:
        yield PASS, "Name ID 16 (Typographic Family name) is consistent"


@check(id="com.microsoft/check/fstype", rationale="")
def com_microsoft_check_fstype(ttFont):
    """Checking OS/2 fsType."""
    required_value = 8
    value = ttFont["OS/2"].fsType
    if value != required_value:
        yield FAIL, f"OS/2 fsType must be set to {required_value}, found {value} instead."
    else:
        yield PASS, "OS/2 fsType is properly set."


@check(id="com.microsoft/check/vertical_metrics", rationale="")
def com_microsoft_check_vertical_metrics(ttFont):
    """Checking hhea OS/2 vertical_metrics:
    If OS/2.fsSelection.useTypoMetrics is not set, then
        hhea.ascender == OS/2.winAscent
        hhea.descender == OS/2.winDescent
        hhea.lineGap == 0
    """
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
    id="com.microsoft/check/STAT_axis_values",
    conditions=["has_STAT_table"],
    rationale="",
)
def com_microsoft_check_STAT_axis_values(ttFont):
    """Check whether STAT axis values are unique."""
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
    id="com.microsoft/check/fvar_STAT_axis_ranges",
    conditions=["has_STAT_table", "is_variable_font"],
    rationale="",
)
def com_microsoft_check_fvar_STAT_axis_ranges(ttFont):
    """Check fvar named instance axis values lie within a *single* STAT axis range."""
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
    id="com.microsoft/check/STAT_table_eliding_bit",
    conditions=["has_STAT_table"],
    rationale="",
)
def com_microsoft_check_STAT_table_eliding_bit(ttFont):
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


# Reversed axis order for STAT table - note ital and slnt are rarely in same
# font but if they are, ital should be last.
AXIS_ORDER_REVERSED = ["ital", "slnt", "wdth", "wght", "opsz"]


@check(
    id="com.microsoft/check/STAT_table_axis_order",
    conditions=["has_STAT_table"],
    rationale="",
)
def com_microsoft_check_STAT_table_axis_order(ttFont):
    """Validate STAT table axisOrder"""
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


@check(id="com.microsoft/check/name_id_1", rationale="")
def com_microsoft_check_name_id_1(ttFont):
    """Font has a name with ID 1."""
    if not ttFont["name"].getName(1, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 1."
    else:
        yield PASS, "Font has a name with ID 1."


@check(id="com.microsoft/check/name_id_2", rationale="")
def com_microsoft_check_name_id_2(ttFont):
    """Font has a name with ID 2."""
    if not ttFont["name"].getName(2, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 2."
    else:
        yield PASS, "Font has a name with ID 2."


@check(id="com.microsoft/check/office_ribz_req", rationale="")
def com_microsoft_check_office_ribz_req(ttFont):
    """Office fonts: Name IDs 1 & 2 must be set for an RBIZ family model.
    I.e. ID 2 can only be one of “Regular”, “Italic”, “Bold”, or
    “Bold Italic”. All other style designators (including “Light” or
    “Semilight”) must be in ID 1.
    """
    # family_name = get_family_name(ttFont)
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


@check(id="com.microsoft/check/name_length_req", rationale="")
def com_microsoft_check_name_length_req(ttFont):
    """
    For Office, family and subfamily names must be 31 characters or less total
    to fit in a LOGFONT.
    """
    family_name = get_family_name(ttFont)
    subfamily_name = get_subfamily_name(ttFont)
    if family_name is None:
        yield FAIL, "Name ID 1 (family) missing"
    if subfamily_name is None:
        yield FAIL, "Name ID 2 (sub family) missing"

    logfont = (
        family_name
        if subfamily_name in ("Regular", "Bold", "Italic", "Bold Italic")
        else " ".join([family_name, subfamily_name])
    )

    if len(logfont) > 31:
        yield FAIL, (
            f"Family + subfamily name, '{logfont}', is too long: "
            f"{len(logfont)} characters; must be 31 or less"
        )
    else:
        yield PASS, (
            f"Family + subfamily name has good length: {len(logfont)} characters"
        )


VTT_HINT_TABLES = [
    "TSI0",
    "TSI1",
    "TSI2",
    "TSI3",
    "TSI5",
    "TSIC",  # cvar
]

OTL_SOURCE_TABLES = [
    "TSIV",  # Volt
    "TSIP",  # GPOS
    "TSIS",  # GSUB
    "TSID",  # GDEF
    "TSIJ",  # JSTF
    "TSIB",  # BASE
]


@check(id="com.microsoft/check/vtt_volt_data", rationale="")
def com_microsoft_check_vtt_volt_data_gone(ttFont):
    """
    Check to make sure all the VTT source (TSI* tables) and
    VOLT stuff (TSIV and zz features & langsys records) are gone.
    """

    failure_found = False
    for table in VTT_HINT_TABLES + OTL_SOURCE_TABLES:
        if table in ttFont:
            failure_found = True
            yield FAIL, f"{table} table found"
        else:
            yield PASS, f"{table} table not found"

    for otlTableTag in ["GPOS", "GSUB"]:
        if otlTableTag not in ttFont:
            continue
        table = ttFont[otlTableTag].table
        for feature in table.FeatureList.FeatureRecord:
            if feature.FeatureTag[:2] == "zz":
                failure_found = True
                yield FAIL, "Volt zz feature found"
        for script in table.ScriptList.ScriptRecord:
            for langSysRec in script.Script.LangSysRecord:
                if langSysRec.LangSysTag[:2] == "zz":
                    failure_found = True
                    yield FAIL, "Volt zz langsys found"
    if not failure_found:
        yield PASS, "No VTT or Volt Source Data Found"


def verify_widths(ttFont, buffer):
    """Verify all shaped glyphs are the same width"""
    glyphs_by_width = {}
    glyphOrder = ttFont.getGlyphOrder()
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        width = pos.x_advance
        # width to glyph name mapping
        glyph_name = glyphOrder[info.codepoint]
        if width in glyphs_by_width:
            glyphs_by_width[width].append(glyph_name)
        else:
            glyphs_by_width[width] = [glyph_name]

    return glyphs_by_width


def format_glyphs_by_width(glyphs_by_width):
    """
    Format glyphs_by_width as a string for output. Lists glyph groups sorted
    by the number of glyphs in each group.
    """
    output = ""
    lengths = {w: len(g) for w, g in glyphs_by_width.items()}
    output = "\n".join([f"{w}: {glyphs_by_width[w]}" for w in sorted(lengths.keys())])
    return output


def parse_unicode_escape(s):
    import ast

    s = s.replace('"', r"\"")
    return ast.literal_eval(f'"{s}"')


@check(
    id="com.microsoft/check/tnum_glyphs_equal_widths",
    configs={"TEST_STR"},
    rationale="",
)
def com_microsoft_check_tnum_glyphs_equal_widths(ttFont):
    """
    Check to make sure all the tnum glyphs are the same width.
    """
    import uharfbuzz as hb

    filename = ttFont.reader.file.name
    hbBlob = hb.Blob.from_file_path(filename)
    hbFace = hb.Face(hbBlob)
    hbFont = hb.Font(hbFace)

    check_text = "0123456789"
    if TEST_STR is not None:  # type: ignore # noqa:F821 pylint:disable=E0602
        check_text = TEST_STR  # type: ignore # noqa:F821 pylint:disable=E0602

    # Evaluate any unicode escape sequences, e.g. \N{PLUS SIGN}
    check_text = "".join([parse_unicode_escape(l) for l in check_text.splitlines()])

    # Check for existence of tnum opentype feature
    if "GSUB" not in ttFont:
        yield PASS, "Font does not contain GSUB table"
        return

    gsub = ttFont["GSUB"].table
    if not any(
        feature.FeatureTag == "tnum" for feature in gsub.FeatureList.FeatureRecord
    ):
        yield PASS, "Font does not contain tnum opentype feature"
        return

    hbBuffer = hb.Buffer()
    hbBuffer.add_str(check_text)

    # variable or static font
    if "fvar" in ttFont:
        fvar_table = ttFont["fvar"]

        # for each named instance in fvar
        for fvar_instance in fvar_table.instances:
            instance_coord_dict = fvar_instance.coordinates
            hbFont.set_variations(instance_coord_dict)

            # Shape set of characters and verify glyphs have same width
            hb.shape(hbFont, hbBuffer, features={"tnum": True})

            # Verify all shaped glyphs are the same width
            glyphs_with_widths = verify_widths(ttFont, hbBuffer)
            if len(glyphs_with_widths) > 1:
                yield FAIL, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"do not align:\n{format_glyphs_by_width(glyphs_with_widths)}"
                )
            else:
                yield PASS, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
                )

    else:
        hb.shape(hbFont, hbBuffer, features={"tnum": True})

        # Verify all shaped glyphs are the same width
        glyphs_with_widths = verify_widths(ttFont, hbBuffer)
        if len(glyphs_with_widths) > 1:
            yield FAIL, (
                f"tnum glyphs appear not to align:\n{format_glyphs_by_width(glyphs_with_widths)}"
            )
        else:
            yield PASS, (
                f"tnum glyphs are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
            )


# Optional checks


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


@check(id="com.microsoft/check/wgl4", rationale="")
def com_microsoft_check_office_wgl4(ttFont):
    """Check whether the font complies with WGL4."""
    from .character_repertoires import WGL4_OPTIONAL, WGL4_REQUIRED

    yield from check_repertoire(ttFont, WGL4_REQUIRED, "WGL4")
    yield from check_repertoire(
        ttFont, WGL4_OPTIONAL, "WGL4_OPTIONAL", error_status=WARN
    )


@check(id="com.microsoft/check/ogl2", rationale="")
def com_microsoft_check_office_ogl2(ttFont):
    """Check whether the font complies with OGL2."""
    from .character_repertoires import OGL2

    yield from check_repertoire(ttFont, OGL2, "OGL2")
