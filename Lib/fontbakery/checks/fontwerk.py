"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.prelude import check, FAIL, INFO, Message
from fontbakery.constants import FsSelection, MacStyle


@check(
    id="com.fontwerk/check/no_mac_entries",
    rationale="""
        Mac name table entries are not needed anymore. Even Apple stopped producing
        name tables with platform 1. Please see for example the following system font:

        /System/Library/Fonts/SFCompact.ttf

        Also, Dave Opstad, who developed Apple's TrueType specifications, told
        Olli Meier a couple years ago (as of January/2022) that these entries are
        outdated and should not be produced anymore.
    """,
    proposal="https://github.com/googlefonts/gftools/issues/469",
)
def com_fontwerk_check_name_no_mac_entries(ttFont):
    """Check if font has Mac name table entries (platform=1)"""

    for rec in ttFont["name"].names:
        if rec.platformID == 1:
            yield FAIL, Message("mac-names", f"Please remove name ID {rec.nameID}")


@check(
    id="com.fontwerk/check/vendor_id",
    rationale="""
        Vendor ID must be WERK for Fontwerk fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3579",
)
def com_fontwerk_check_vendor_id(ttFont):
    """Checking OS/2 achVendID."""

    vendor_id = ttFont["OS/2"].achVendID
    if vendor_id != "WERK":
        yield FAIL, Message(
            "bad-vendor-id", f"OS/2 VendorID is '{vendor_id}', but should be 'WERK'."
        )


@check(
    id="com.fontwerk/check/names_match_default_fvar",
    rationale="""
        Check if the font names match default fvar instance name.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3698",
)
def com_fontwerk_check_names_match_default_fvar(ttFont):
    """Checking if names match default fvar instance name."""
    from fontbakery.constants import NameID

    default_axis_values = {
        axis.axisTag: axis.defaultValue for axis in ttFont["fvar"].axes
    }
    default_name_id = None
    for instance in ttFont["fvar"].instances:
        if instance.coordinates == default_axis_values:
            default_name_id = instance.subfamilyNameID
            break

    if default_name_id is None:
        yield FAIL, Message(
            "missing-default-name-id", "fvar is missing a default instance name ID."
        )
        return

    fam_name = ttFont["name"].getBestFamilyName()
    subfam_name = ttFont["name"].getDebugName(default_name_id)

    if subfam_name is None:
        yield FAIL, Message(
            "missing-name-id",
            f"Name ID {default_name_id} stored in"
            f" fvar instance is missing in name table.",
        )
        return

    default_name = f"{fam_name} {subfam_name}"

    # check if default_name match family + subfamily name
    for fam_id, subfam_id in [
        (NameID.WWS_FAMILY_NAME, NameID.WWS_SUBFAMILY_NAME),
        (NameID.TYPOGRAPHIC_FAMILY_NAME, NameID.TYPOGRAPHIC_SUBFAMILY_NAME),
        (NameID.FONT_FAMILY_NAME, NameID.FONT_SUBFAMILY_NAME),
    ]:
        name_fam = ttFont["name"].getDebugName(fam_id)
        name_subfam = ttFont["name"].getDebugName(subfam_id)

        if (fam_id, subfam_id) in [
            (NameID.WWS_FAMILY_NAME, NameID.WWS_SUBFAMILY_NAME),
            (NameID.TYPOGRAPHIC_FAMILY_NAME, NameID.TYPOGRAPHIC_SUBFAMILY_NAME),
        ]:
            if [name_fam, name_subfam] == [None, None]:
                yield INFO, Message(
                    "missing-name-ids",
                    f"It's not a requirement that a font has "
                    f"to have these name IDs {fam_id} and {subfam_id}.",
                )
                continue

        if name_fam is None:
            yield FAIL, Message("missing-name-id", "Missing name ID {fam_id}.")
        elif name_subfam is None:
            yield FAIL, Message("missing-name-id", "Missing name ID {subfam_id}.")
        else:
            possible_names = [f"{name_fam} {name_subfam}"]
            if name_subfam.lower() == "regular":
                possible_names.append(name_fam)

            if default_name not in possible_names:
                yield FAIL, Message(
                    "bad-name",
                    f"Name {possible_names} does not match fvar"
                    f" default name '{default_name}'",
                )


@check(
    id="com.fontwerk/check/weight_class_fvar",
    rationale="""
        According to Microsoft's OT Spec the OS/2 usWeightClass
        should match the fvar default value.
    """,
    conditions=["is_variable_font", "has_wght_axis"],
    proposal="https://github.com/googlefonts/gftools/issues/477",
)
def com_fontwerk_check_weight_class_fvar(ttFont):
    """Checking if OS/2 usWeightClass matches fvar."""

    fvar = ttFont["fvar"]
    default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}

    fvar_value = default_axis_values.get("wght")
    os2_value = ttFont["OS/2"].usWeightClass

    if os2_value != int(fvar_value):
        yield FAIL, Message(
            "bad-weight-class",
            f"OS/2 usWeightClass is '{os2_value}', "
            f"but should match fvar default value '{fvar_value}'.",
        )


def is_covered_in_stat(ttFont, axis_tag, value):
    if "STAT" not in ttFont:
        return False
    stat_table = ttFont["STAT"].table
    if stat_table.AxisValueCount == 0:
        return False
    for ax_value in stat_table.AxisValueArray.AxisValue:
        ax_value_format = ax_value.Format
        stat_value = []
        if ax_value_format in (1, 2, 3):
            axis_tag_stat = stat_table.DesignAxisRecord.Axis[ax_value.AxisIndex].AxisTag
            if axis_tag != axis_tag_stat:
                continue

            if ax_value_format in (1, 3):
                stat_value.append(ax_value.Value)

            if ax_value_format == 3:
                stat_value.append(ax_value.LinkedValue)

            if ax_value_format == 2:
                stat_value.append(ax_value.NominalValue)

        if ax_value_format == 4:
            # TODO: Need to implement
            #  locations check as well
            pass

        if value in stat_value:
            return True

    return False


@check(
    id="com.fontwerk/check/inconsistencies_between_fvar_stat",
    rationale="""
        Check for inconsistencies in names and values between the fvar instances
        and STAT table. Inconsistencies may cause issues in apps like Adobe InDesign.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3636",
)
def com_fontwerk_check_inconsistencies_between_fvar_stat(ttFont):
    """Checking if STAT entries matches fvar and vice versa."""

    if "STAT" not in ttFont:
        return FAIL, Message(
            "missing-stat-table", "Missing STAT table in variable font."
        )
    fvar = ttFont["fvar"]
    name = ttFont["name"]

    for ins in fvar.instances:
        instance_name = name.getDebugName(ins.subfamilyNameID)
        if instance_name is None:
            yield FAIL, Message(
                "missing-name-id",
                f"The name ID {ins.subfamilyNameID} used in an"
                f" fvar instance is missing in the name table.",
            )
            continue

        for axis_tag, value in ins.coordinates.items():
            if not is_covered_in_stat(ttFont, axis_tag, value):
                yield FAIL, Message(
                    "missing-fvar-instance-axis-value",
                    f"{instance_name}: '{axis_tag}' axis value '{value}'"
                    f" missing in STAT table.",
                )

        # TODO: Compare fvar instance name with constructed STAT table name.


@check(
    id="com.fontwerk/check/style_linking",
    rationale="""
        Look for possible style linking issues.
    """,
    proposal="https://github.com/googlefonts/noto-fonts/issues/2269",
)
def com_fontwerk_check_style_linking(ttFont, font):
    """Checking style linking entries"""

    errs = []
    if font.is_bold:
        if not (ttFont["OS/2"].fsSelection & FsSelection.BOLD):
            errs.append("OS/2 fsSelection flag should be (most likely) 'Bold'.")
        if not (ttFont["head"].macStyle & MacStyle.BOLD):
            errs.append("head macStyle flag should be (most likely) 'Bold'.")
        if ttFont["name"].getDebugName(2) not in ("Bold", "Bold Italic"):
            name_id_2_should_be = "Bold"
            if font.is_italic:
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    if font.is_italic:
        if "post" in ttFont and not ttFont["post"].italicAngle:
            errs.append(
                "post talbe italic angle should be (most likely) different to 0."
            )
        if not (ttFont["OS/2"].fsSelection & FsSelection.ITALIC):
            errs.append("OS/2 fsSelection flag should be (most likely) 'Italic'.")
        if not (ttFont["head"].macStyle & MacStyle.ITALIC):
            errs.append("head macStyle flag should be (most likely) 'Italic'.")
        if ttFont["name"].getDebugName(2) not in ("Italic", "Bold Italic"):
            name_id_2_should_be = "Italic"
            if font.is_bold:
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    for err in errs:
        yield FAIL, Message("style-linking-issue", err)
