"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
from fontbakery.callable import check
from fontbakery.checkrunner import Section, PASS, FAIL
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Adobe Fonts"))

ADOBEFONTS_PROFILE_CHECKS = \
    UNIVERSAL_PROFILE_CHECKS + [
    'com.adobe.fonts/check/family/consistent_upm'
]

@check(
    id='com.adobe.fonts/check/family/consistent_upm',
    rationale="""While not required by the OpenType spec, we (Adobe) expect
    that a group of fonts designed & produced as a family have consistent
    units per em. """
)
def com_adobe_fonts_check_family_consistent_upm(ttFonts):
    """Fonts have consistent Units Per Em?"""
    upm_set = set()
    for ttFont in ttFonts:
        upm_set.add(ttFont['head'].unitsPerEm)
    if len(upm_set) > 1:
        yield FAIL, ("Fonts have different units per em: {}."
                     ).format(sorted(upm_set))
    else:
        yield PASS, "Fonts have consistent units per em."

# ToDo: add many more checks...

profile.auto_register(globals())
profile.test_expected_checks(ADOBEFONTS_PROFILE_CHECKS, exclusive=True)
