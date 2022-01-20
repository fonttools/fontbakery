"""
Checks for Fontwerk.
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
    """,
    proposal = 'https://github.com/googlefonts/gftools/issues/469'
)
def com_fontwerk_check_name_no_mac_entries(ttFont):
    """
    Check if font has Mac name table entries (platform=1)
    Report as warning, because Mac name table entries are not needed anymore.

    Further reading:
    Proof: Even Apple stopped producing name tables with platform 1.
    Please see for example the following system font: /System/Library/Fonts/SFCompact.ttf
    Also, Dave Opstad, who developed Apple's TrueType specifications, told me (Olli Meier)
    a couple years ago that these entries are outdated and should not be produced anymore.
    """

    name_table = ttFont["name"]
    passed = True

    for rec in name_table.names:
        if rec.platformID == 1:
            yield FAIL, Message("Mac Names", f'Please remove name ID {rec.nameID}')
            passed = False

    if passed:
        yield PASS, 'No Mac name table entries.'


profile.auto_register(globals())

profile.test_expected_checks(FONTWERK_PROFILE_CHECKS, exclusive=True)
