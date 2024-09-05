"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="adobefonts/family/consistent_upm",
    rationale="""
        While not required by the OpenType spec, we (Adobe) expect that a group
        of fonts designed & produced as a family have consistent units per em.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2372",
)
def check_family_consistent_upm(ttFonts):
    """Fonts have consistent Units Per Em?"""
    upm_set = set()
    for ttFont in ttFonts:
        upm_set.add(ttFont["head"].unitsPerEm)
    if len(upm_set) > 1:
        yield FAIL, Message(
            "inconsistent-upem",
            f"Fonts have different units per em: {sorted(upm_set)}.",
        )


@check(
    id="adobefonts/nameid_1_win_english",
    rationale="""
        While not required by the OpenType spec, Adobe Fonts' pipeline requires
        every font to support at least nameID 1 (Font Family name) for platformID 3
        (Windows), encodingID 1 (Unicode), and languageID 1033/0x409 (US-English).
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3714",
)
def check_nameid_1_win_english(ttFont, has_name_table):
    """Font has a good nameID 1, Windows/Unicode/US-English `name` table record?"""
    if not has_name_table:
        return FAIL, Message("name-table-not-found", "Font has no 'name' table.")

    nameid_1 = ttFont["name"].getName(1, 3, 1, 0x409)

    if nameid_1 is None:
        return FAIL, Message(
            "nameid-1-not-found",
            "Windows nameID 1 US-English record not found.",
        )

    try:
        nameid_1_unistr = nameid_1.toUnicode()
    except UnicodeDecodeError:
        return FAIL, Message(
            "nameid-1-decoding-error",
            "Windows nameID 1 US-English record could not be decoded.",
        )

    if not nameid_1_unistr.strip():
        return FAIL, Message(
            "nameid-1-empty",
            "Windows nameID 1 US-English record is empty.",
        )

    return PASS, "Font contains a good Windows nameID 1 US-English record."


@check(
    id="adobefonts/unsupported_tables",
    rationale="""
        Adobe Fonts' font-processing pipeline does not support all kinds of tables
        that can be included in OpenType font files.⏎
        Fonts that do not pass this check are guaranteed to be rejected by the pipeline.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3870",
)
def check_unsupported_tables(ttFont):
    """Does the font have any unsupported tables?"""
    SUPPORTED_TABLES = {
        "avar",
        "BASE",
        "CFF ",
        "CFF2",
        "cmap",
        "cvar",
        "cvt ",
        "DSIG",
        "feat",
        "fpgm",
        "fvar",
        "gasp",
        "GDEF",
        "glyf",
        "GPOS",
        "GSUB",
        "gvar",
        "hdmx",
        "head",
        "hhea",
        "hmtx",
        "HVAR",
        "kern",
        "loca",
        "LTSH",
        "maxp",
        "meta",
        "morx",
        "MVAR",
        "name",
        "OS/2",
        "PCLT",
        "post",
        "prep",
        "STAT",
        "SVG ",
        "VDMX",
        "vhea",
        "vmtx",
        "VORG",
        "VVAR",
    }
    font_tables = set(ttFont.keys())
    font_tables.discard("GlyphOrder")  # pseudo-table created by FontTools
    unsupported_tables = sorted(font_tables - SUPPORTED_TABLES)

    if unsupported_tables:
        unsupported_list = "".join(f"* {tag}\n" for tag in unsupported_tables)
        yield FAIL, Message(
            "unsupported-tables",
            f"The following unsupported font tables were found:\n\n{unsupported_list}",
        )


@check(
    id="adobefonts/STAT_strings",
    conditions=["has_STAT_table"],
    rationale="""
        In the STAT table, the "Italic" keyword must not be used on AxisValues
        for variation axes other than 'ital' or 'slnt'. This is a more lenient
        implementation of googlefonts/STAT_strings which allows "Italic"
        only for the 'ital' axis.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2863",
)
def check_STAT_strings(ttFont):
    """Check correctness of STAT table strings"""
    stat_table = ttFont["STAT"].table
    ital_slnt_axis_indices = []
    for index, axis in enumerate(stat_table.DesignAxisRecord.Axis):
        if axis.AxisTag in ("ital", "slnt"):
            ital_slnt_axis_indices.append(index)

    nameIDs = set()
    if ttFont["STAT"].table.AxisValueArray:
        for value in stat_table.AxisValueArray.AxisValue:
            if hasattr(value, "AxisIndex"):
                if value.AxisIndex not in ital_slnt_axis_indices:
                    nameIDs.add(value.ValueNameID)

            if hasattr(value, "AxisValueRecord"):
                for record in value.AxisValueRecord:
                    if record.AxisIndex not in ital_slnt_axis_indices:
                        nameIDs.add(value.ValueNameID)

    bad_values = set()
    for name in ttFont["name"].names:
        if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            f"The following AxisValue entries in the STAT table"
            f' should not contain "Italic":\n'
            f" {sorted(bad_values)}",
        )
