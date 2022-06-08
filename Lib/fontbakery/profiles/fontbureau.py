"""
Checks for Font Bureau.
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Font Bureau"))

FONTBUREAU_PROFILE_CHECKS = \
    UNIVERSAL_PROFILE_CHECKS + [
        'io.github.abysstypeco/check/ytlc_sanity'
    ]

@check(
    id = 'io.github.abysstypeco/check/ytlc_sanity',
    rationale = """
        This check follows the values of the ytlc axis proposed by Font Bureau.
    """,
    conditions=["is_variable_font"],
    proposal = 'https://github.com/googlefonts/fontbakery/issues/3130'
)
def io_github_abysstypeco_check_ytlc_sanity(ttFont):
    """Check if ytlc values are sane in vf"""
    passed = True

    for axis in ttFont['fvar'].axes:
        if not axis.axisTag == 'ytlc': continue

        if axis.minValue < 0 or axis.maxValue > 1000:
            passed = False
            yield FAIL,\
                  Message("invalid-range",
                          f'The range of ytlc values'
                          f' ({axis.minValue} - {axis.maxValue}) does not conform'
                          f' to the expected range of ytlc which'
                          f' should be min value 0 to max value 1000')
    if passed:
        yield PASS, 'ytlc is sane'


profile.auto_register(globals())


profile.test_expected_checks(FONTBUREAU_PROFILE_CHECKS, exclusive=True)
