"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.googlefonts',)
profile = profile_factory(default_section=Section("Fontwerk"))

# FIXME: It would be much better to refactor this as described at:
#        https://github.com/googlefonts/fontbakery/issues/3585
profile.configuration_defaults = {
    "com.google.fonts/check/file_size": {
        "WARN_SIZE": 1 * 1024 * 1024,
        "FAIL_SIZE": 9 * 1024 * 1024
    }
}

# Note: I had to use a function here in order to display it
# in the auto-generated Sphinx docs due to this bug:
# https://stackoverflow.com/questions/31561895/literalinclude-how-to-include-only-a-variable-using-pyobject
def leave_this_one_out(checkid):
    CHECKS_NOT_TO_INCLUDE = [
        # don't run these checks on the Fontwerk profile:
        'com.google.fonts/check/canonical_filename',
        'com.google.fonts/check/vendor_id',
        'com.google.fonts/check/fstype',
        'com.google.fonts/check/gasp',

        # The following check they may need some improvements
        # before we decide to include it:
        'com.google.fonts/check/family/italics_have_roman_counterparts',
    ]

    if checkid in CHECKS_NOT_TO_INCLUDE:
        return True


FONTWERK_PROFILE_CHECKS = \
    [checkid for checkid in GOOGLEFONTS_PROFILE_CHECKS
     if not leave_this_one_out(checkid)] + [
        'com.fontwerk/check/no_mac_entries',
        'com.fontwerk/check/vendor_id',
        'com.fontwerk/check/weight_class_fvar',
        'com.fontwerk/check/inconsistencies_between_fvar_stat',
    ]


@check(
    id = 'com.fontwerk/check/no_mac_entries',
    rationale = """
        Mac name table entries are not needed anymore.
        Even Apple stopped producing name tables with platform 1.
        Please see for example the following system font:
        /System/Library/Fonts/SFCompact.ttf

        Also, Dave Opstad, who developed Apple's TrueType specifications, told Olli Meier a couple years ago (as of January/2022) that these entries are outdated and should not be produced anymore.
    """,
    proposal = 'https://github.com/googlefonts/gftools/issues/469'
)
def com_fontwerk_check_name_no_mac_entries(ttFont):
    """Check if font has Mac name table entries (platform=1)"""

    passed = True
    for rec in ttFont["name"].names:
        if rec.platformID == 1:
            yield FAIL,\
                  Message("mac-names",
                          f'Please remove name ID {rec.nameID}')
            passed = False

    if passed:
        yield PASS, 'No Mac name table entries.'


@check(
    id = 'com.fontwerk/check/vendor_id',
    rationale = """
        Vendor ID must be WERK for Fontwerk fonts.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3579'
)
def com_fontwerk_check_vendor_id(ttFont):
    """Checking OS/2 achVendID."""

    vendor_id = ttFont['OS/2'].achVendID
    if vendor_id != 'WERK':
        yield FAIL,\
              Message("bad-vendor-id",
                      f"OS/2 VendorID is '{vendor_id}', but should be 'WERK'.")
    else:
        yield PASS, f"OS/2 VendorID '{vendor_id}' is correct."


@check(
    id = 'com.fontwerk/check/weight_class_fvar',
    rationale = """
        According to Microsoft's OT Spec the OS/2 usWeightClass should match the fvar default value.
    """,
    conditions = ["is_variable_font"],
    proposal = 'https://github.com/googlefonts/gftools/issues/477'
)
def com_fontwerk_check_weight_class_fvar(ttFont):
    """Checking if OS/2 usWeightClass matches fvar."""

    fvar = ttFont['fvar']
    default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}

    fvar_value = default_axis_values.get('wght', None)
    os2_value = ttFont["OS/2"].usWeightClass

    if fvar_value is None:
        return

    if os2_value != int(fvar_value):
        yield FAIL,\
              Message("bad-weight-class",
                      f"OS/2 usWeightClass is '{os2_value}', "
                      f"but should match fvar default value '{fvar_value}'.")

    else:
        yield PASS, f"OS/2 usWeightClass '{os2_value}' matches fvar default value."


def is_covered_in_stat(ttFont, axis_tag, value):
    stat_table = ttFont['STAT'].table
    for ax_value in stat_table.AxisValueArray.AxisValue:
        axis_tag_stat = stat_table.DesignAxisRecord.Axis[ax_value.AxisIndex].AxisTag
        if axis_tag != axis_tag_stat:
            continue

        stat_value = []
        if ax_value.Format in (1, 3):
            stat_value.append(ax_value.Value)

        if ax_value.Format == 3:
            stat_value.append(ax_value.LinkedValue)

        if ax_value.Format == 2:
            stat_value.append(ax_value.NominalValue)

        if ax_value.Format == 4:
            # TODO: Need to implement
            #  locations check as well
            pass

        if value in stat_value:
            return True

    return False


@check(
    id = 'com.fontwerk/check/inconsistencies_between_fvar_stat',
    rationale = """
        Check for inconsistencies in names and values between the fvar instances and STAT table.
        Inconsistencies may cause issues in apps like Adobe InDesign.
    """,
    conditions = ["is_variable_font"],
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3636'
)
def com_fontwerk_check_inconsistencies_between_fvar_stat(ttFont):
    """Checking if STAT entries matches fvar and vice versa."""

    if 'STAT' not in ttFont:
        return FAIL,\
               Message("missing-stat-table",
                       "Missing STAT table in variable font.")

    fvar = ttFont['fvar']
    name = ttFont['name']

    for ins in fvar.instances:
        instance_name = name.getDebugName(ins.subfamilyNameID)
        if instance_name is None:
            yield FAIL,\
                  Message("missing-name-id",
                          f"The name ID {ins.subfamilyNameID} used in an "
                          f"fvar instance is missing in the name table.")
            continue

        for axis_tag, value in ins.coordinates.items():
            if not is_covered_in_stat(ttFont, axis_tag, value):
                yield FAIL,\
                      Message("missing-fvar-instance-axis-value",
                              f"{instance_name}: '{axis_tag}' axis value '{value}' "
                              f"missing in STAT table.")

        # TODO: Compare fvar instance name with constructed STAT table name.


profile.auto_register(globals(),
                      filter_func=lambda type, id, _:
                      not (type == 'check' and leave_this_one_out(id)))
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
