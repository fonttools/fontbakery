"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.constants import FsSelection, MacStyle

profile_imports = ("fontbakery.profiles.googlefonts",)
profile = profile_factory(default_section=Section("Fontwerk"))

# FIXME: It would be much better to refactor this as described at:
#        https://github.com/fonttools/fontbakery/issues/3585
profile.configuration_defaults = {
    "com.google.fonts/check/file_size": {
        "WARN_SIZE": 1 * 1024 * 1024,
        "FAIL_SIZE": 9 * 1024 * 1024,
    }
}


# Note: I had to use a function here in order to display it
# in the auto-generated Sphinx docs due to this bug:
# https://stackoverflow.com/questions/31561895/literalinclude-how-to-include-only-a-variable-using-pyobject
def leave_this_one_out(checkid):
    CHECKS_NOT_TO_INCLUDE = [
        # don't run these checks on the Fontwerk profile:
        "com.google.fonts/check/canonical_filename",
        "com.google.fonts/check/vendor_id",
        "com.google.fonts/check/fstype",
        "com.google.fonts/check/gasp",
        "com.google.fonts/check/name/description_max_length",
        "com.google.fonts/check/metadata/includes_production_subsets",
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/version_bump",
        "com.google.fonts/check/production_glyphs_similarity",
        "com.google.fonts/check/name/line_breaks",
        "com.google.fonts/check/fontdata_namecheck",
        "com.google.fonts/check/meta/script_lang_tags",
        # The following check they may need some improvements
        # before we decide to include it:
        "com.google.fonts/check/family/italics_have_roman_counterparts",
    ]

    if checkid in CHECKS_NOT_TO_INCLUDE:
        return True


FONTWERK_PROFILE_CHECKS = [
    checkid for checkid in GOOGLEFONTS_PROFILE_CHECKS if not leave_this_one_out(checkid)
] + [
    "com.fontwerk/check/no_mac_entries",
    "com.fontwerk/check/vendor_id",
    "com.fontwerk/check/weight_class_fvar",
    "com.fontwerk/check/inconsistencies_between_fvar_stat",
    "com.fontwerk/check/style_linking",
]


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

    passed = True
    for rec in ttFont["name"].names:
        if rec.platformID == 1:
            yield FAIL, Message("mac-names", f"Please remove name ID {rec.nameID}")
            passed = False

    if passed:
        yield PASS, "No Mac name table entries."


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
    else:
        yield PASS, f"OS/2 VendorID '{vendor_id}' is correct."


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

    else:
        yield PASS, f"OS/2 usWeightClass '{os2_value}' matches fvar default value."


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
    passed = True
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
            passed = False
            continue

        for axis_tag, value in ins.coordinates.items():
            if not is_covered_in_stat(ttFont, axis_tag, value):
                yield FAIL, Message(
                    "missing-fvar-instance-axis-value",
                    f"{instance_name}: '{axis_tag}' axis value '{value}'"
                    f" missing in STAT table.",
                )
                passed = False

        # TODO: Compare fvar instance name with constructed STAT table name.

    if passed:
        yield PASS, "STAT and fvar axis records are consistent."


@check(
    id="com.fontwerk/check/style_linking",
    rationale="""
        Look for possible style linking issues.
    """,
    proposal="https://github.com/googlefonts/noto-fonts/issues/2269",
)
def com_fontwerk_check_style_linking(ttFont):
    """Checking style linking entries"""
    from .shared_conditions import is_italic, is_bold

    errs = []
    if is_bold(ttFont):
        if not (ttFont["OS/2"].fsSelection & FsSelection.BOLD):
            errs.append("OS/2 fsSelection flag should be (most likely) 'Bold'.")
        if not (ttFont["head"].macStyle & MacStyle.BOLD):
            errs.append("head macStyle flag should be (most likely) 'Bold'.")
        if ttFont["name"].getDebugName(2) not in ("Bold", "Bold Italic"):
            name_id_2_should_be = "Bold"
            if is_italic(ttFont):
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    if is_italic(ttFont):
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
            if is_bold(ttFont):
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    if not errs:
        yield PASS, "Style linking looks good."

    for err in errs:
        yield FAIL, Message("style-linking-issue", err)


profile.auto_register(
    globals(),
    filter_func=lambda type, id, _: not (type == "check" and leave_this_one_out(id)),
)
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
