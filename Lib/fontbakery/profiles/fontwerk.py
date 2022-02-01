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

# not sure how I can exclude tests I don't want to run.
CHECKS_DONT_DO = [
    'com.google.fonts/check/canonical_filename',
    'com.google.fonts/check/vendor_id',
    'com.google.fonts/check/family/italics_have_roman_counterparts',
    'com.google.fonts/check/fstype',
    'com.google.fonts/check/gasp',
]

FONTWERK_PROFILE_CHECKS = \
    [check for check in GOOGLEFONTS_PROFILE_CHECKS
     if check not in CHECKS_DONT_DO] + [
        'com.fontwerk/check/no_mac_entries',
        'com.fontwerk/check/vendor_id',
        'com.fontwerk/check/weight_class_fvar',
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

profile.auto_register(globals())
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
