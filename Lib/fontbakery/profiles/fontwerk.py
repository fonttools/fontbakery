"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, SKIP
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
        'com.fontwerk/check/names_match_default_fvar',
    ]

def _familyname(font_obj):
    '''
    Function to get the the fonts family name.
    '''
    for name_id in [21, 16, 1]:
        name_str = font_obj["name"].getDebugName(name_id)
        if name_str is not None:
            return name_str

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
            yield FAIL, \
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
    proposal='https://github.com/googlefonts/fontbakery/pull/3579'
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
    conditions=["is_variable_font"],
    proposal='https://github.com/googlefonts/gftools/issues/477'
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
        yield FAIL, \
              Message("bad-weight-class",
                      f"OS/2 usWeightClass is '{os2_value}', "
                      f"but should match fvar default value '{fvar_value}'.")

    else:
        yield PASS, f"OS/2 usWeightClass '{os2_value}' matches fvar default value."

@check(
    id = 'com.fontwerk/check/names_match_default_fvar',
    rationale = """
        Check if the font names names_match_default_fvar
    """,
    conditions=["is_variable_font"],
)
def com_fontwerk_check_names_match_default_fvar(ttFont):
    """Checking if names match default fvar."""

    def _check_font_names(font_obj, default_name, fam_id, subfam_id):
        # check if default_name match family + subfamily name
        name_fam = font_obj["name"].getDebugName(fam_id)
        name_subfam = font_obj["name"].getDebugName(subfam_id)

        if (fam_id, subfam_id) in [(16, 17), (21, 22)]:
            if [name_fam, name_subfam] == [None, None]:
                return SKIP, \
                       Message("missing-name-ids",
                               f"It's not a requirement that a font has "
                               f"to have these name IDs {fam_id} and {subfam_id}.")

        if None in [name_fam, name_subfam]:
            return FAIL, \
                   Message("missing-name-id",
                           "Missing name ID.")
        else:
            possibel_names = [f"{name_fam} {name_subfam}"]
            if name_subfam.lower() == 'regular':
                possibel_names.append(name_fam)

            if default_name in possibel_names:
                return PASS, f"Name matches fvar default name '{default_name}'."
            else:
              return FAIL, \
                     Message("bad-name",
                              f"Name {possibel_names} does not match fvar default name '{default_name}'")


    fvar = ttFont['fvar']
    default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}

    default_name_id = None
    for instance in fvar.instances:
        if instance.coordinates == default_axis_values:
            default_name_id = instance.subfamilyNameID
            break

    if default_name_id is None:
        return FAIL, \
              Message("missing-default-name-id",
                      "fvar is missing a default instance name ID.")

    fam_name = _familyname(ttFont)
    subfam_name = ttFont["name"].getDebugName(default_name_id)

    if subfam_name is None:
        return FAIL, \
              Message("missing-name-id",
                      f"Name ID {default_name_id} stored in fvar instance is missing in name table.")

    default_name = f"{fam_name} {subfam_name}"

    # check if default_name match name ID 1 + 2
    for pair in [(21, 22), (16, 17), (1, 2)]:
        yield _check_font_names(ttFont, default_name, pair[0], pair[1])



profile.auto_register(globals(),
                      filter_func=lambda type, id, _:
                      not (type == 'check' and leave_this_one_out(id)))
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
