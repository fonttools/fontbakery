"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Fontwerk"))

FONTWERK_PROFILE_CHECKS = \
    UNIVERSAL_PROFILE_CHECKS + [
        'com.fontwerk/check/no_mac_entries'
    ]

@check(
    id = 'com.fontwerk/check/no_mac_entries',
    rationale = """
        Check if font has Mac name table entries (platform=1).
        Mac name table entries are not needed anymore.
        For example, even Apple stopped producing name tables with platform 1.
        Please see: /System/Library/Fonts/SFCompact.ttf

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


profile.auto_register(globals())
profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
