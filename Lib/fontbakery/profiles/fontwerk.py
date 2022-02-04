"""
Checks for Fontwerk <https://fontwerk.com/>
"""
import re

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.fontwerk_conditions import general
from fontbakery.constants import NameID
from fontbakery.utils import get_name_entry_strings

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
        'com.google.fonts/check/font_copyright',
        'com.google.fonts/check/name/line_breaks',  # can be ignored because of general fontwerk name table test.
        'com.google.fonts/check/varfont/has_HVAR',  # not needed for fontwerk fonts.
        'com.google.fonts/check/glyf_nested_components',  # it seem to be not an issue anymore. Maybe downgrade to 'WARN'. Tested it in various browsers, InDesign, exported a PDF, printed it.
        'com.google.fonts/check/transformed_components',  # it seem to be not an issue anymore. Maybe downgrade to 'WARN'.

        # The following check they may need some improvements
        # before we decide to include it:
        'com.google.fonts/check/family/italics_have_roman_counterparts',
        'com.google.fonts/check/varfont_instance_names',  # need improvements for optical size name or own test.
        'com.google.fonts/check/smart_dropout',  # improvements needed when it comes to variable fonts. No hinting for var fonts should be ok.
        'com.google.fonts/check/STAT/gf-axisregistry',  # need improvements.
        '''
        Output from report:
        --- Rationale ---
        Check that particle names and values on STAT table match the fallback names in
        each axis entry at the Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry
        🔥 FAIL On the font variation axis 'opsz', the name 'Micro' is not among the expected ones (6pt, 7pt, 8pt, 9pt, 10pt, 11pt, 12pt, 14pt, 16pt, 17pt, 18pt, 20pt, 24pt, 28pt, 36pt, 48pt, 60pt, 72pt, 96pt, 120pt, 144pt) according to the Google Fonts Axis Registry. [code: invalid-name]

        '''
    ]

    if checkid in CHECKS_NOT_TO_INCLUDE:
        return True

FONTWERK_PROFILE_CHECKS = \
    [checkid for checkid in GOOGLEFONTS_PROFILE_CHECKS
     if not leave_this_one_out(checkid)] + [
        'com.fontwerk/check/no_mac_entries',
        'com.fontwerk/check/vendor_id',
        'com.fontwerk/check/weight_class_fvar',
        'com.fontwerk/check/name_table_entries',
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
    id = 'com.fontwerk/check/name_table_entries',
    rationale="""
      Checking if name table entries meets Fontwerk requirements.
  """,
)
def com_fontwerk_check_name_table_entries(ttFont):
    """Checking if name table entries meets Fontwerk requirements.
    """

    for name_rec in ttFont["name"].names:
        name_id = name_rec.nameID
        text_pattern = general.get('name table').get(name_id)
        if not text_pattern:
            continue
        name_str = name_rec.toUnicode()
        if not re.search(text_pattern, name_str):
            yield FAIL, \
                  Message("bad-name-content",
                          f'Name Table ID {name_rec.nameID} should match:\n'
                          f' "{text_pattern}"\n'
                          f'But instead we got:\n"{name_str}"')
        else:
            yield PASS, f"Name Table ID {name_rec.nameID} entry looks good."


profile.auto_register(globals(),
                      filter_func=lambda type, id, _:
                      not (type == 'check' and leave_this_one_out(id)))
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
