"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
import unicodedata

from fontbakery.callable import check
from fontbakery.checkrunner import Section, PASS, FAIL, WARN
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Adobe Fonts"))

ADOBEFONTS_PROFILE_CHECKS = \
    UNIVERSAL_PROFILE_CHECKS + [
        'com.adobe.fonts/check/family/consistent_upm',
        'com.adobe.fonts/check/find_empty_letters'
    ]

OVERRIDDEN_CHECKS = [
        'com.google.fonts/check/dsig',
        'com.google.fonts/check/whitespace_glyphs',
        'com.google.fonts/check/valid_glyphnames',
        ]
ADOBEFONTS_PROFILE_CHECKS += [f'{cid}:{profile.profile_tag}' for cid in OVERRIDDEN_CHECKS]

ADOBEFONTS_PROFILE_CHECKS[:] = [cid for cid in ADOBEFONTS_PROFILE_CHECKS
                                            if cid not in OVERRIDDEN_CHECKS]


@check(
  id = 'com.adobe.fonts/check/family/consistent_upm',
  rationale = """
    While not required by the OpenType spec, we (Adobe) expect that a group of fonts designed & produced as a family have consistent units per em.
  """
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


def _quick_and_dirty_glyph_is_empty(font, glyph_name):
    """
    This is meant to be a quick-and-dirty test to see if a glyph is empty.
    Ideally we'd use the glyph_has_ink() method for this, but for a family of
    large CJK CFF fonts with tens of thousands of glyphs each, it's too slow.

    Caveat Utilitor:
    If this method returns True, the glyph is definitely empty.
    If this method returns False, the glyph *might* still be empty.
    """
    if 'glyf' in font:
        glyph = font['glyf'][glyph_name]
        if not glyph.isComposite():
            if glyph.numberOfContours == 0:
                return True
        return False
    elif 'CFF2' in font:
        top_dict = font['CFF2'].cff.topDictIndex[0]
    else:
        top_dict = font['CFF '].cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    char_string = char_strings[glyph_name]
    if len(char_string.bytecode) <= 1:
        return True
    return False


@check(
  id = 'com.adobe.fonts/check/find_empty_letters',
  rationale = """
    Font language, script, and character set tagging approaches typically have an underlying assumption that letters (i.e. characters with Unicode general category 'Ll', 'Lm', 'Lo', 'Lt', or 'Lu', which includes CJK ideographs and Hangul syllables) with entries in the 'cmap' table have glyphs with ink (with a few exceptions, notably the Hangul "filler" characters).

    This check is intended to identify fonts in which such letters have been mapped to empty glyphs (typically done as a form of subsetting). Letters with empty glyphs should have their entries removed from the 'cmap' table, even if the empty glyphs are left in place (e.g. for CID consistency).
  """
)
def com_adobe_fonts_check_find_empty_letters(ttFont):
    """Letters in font have glyphs that are not empty?"""
    cmap = ttFont.getBestCmap()
    passed = True

    # http://unicode.org/reports/tr44/#General_Category_Values
    letter_categories = {
        'Ll', 'Lm', 'Lo', 'Lt', 'Lu',
    }
    invisible_letters = {
        0x115F, 0x1160, 0x3164, 0xFFA0,  # Hangul filler chars (category='Lo')
    }
    for unicode_val, glyph_name in cmap.items():
        category = unicodedata.category(chr(unicode_val))
        if (_quick_and_dirty_glyph_is_empty(ttFont, glyph_name)) \
                and (category in letter_categories) \
                and (unicode_val not in invisible_letters):
            yield FAIL, \
                ("U+%04X should be visible, but its glyph ('%s') is empty."
                 % (unicode_val, glyph_name))
            passed = False
    if passed:
        yield PASS, "No empty glyphs for letters found."


# ToDo: add many more checks...

profile.auto_register(globals())

com_google_fonts_check_dsig_adobefonts = profile.check_log_override(
    'com.google.fonts/check/dsig'
  , reason='For Adobe this issue is not as severe '\
            + 'as assessed in the original check.'
  , overrides = (
        (   'lacks-signature' # override_target -> a specific Message.code (string)
          , WARN # new_status -> None: keep old status
          , None # new_message_string -> None: keep old message
          )
    ,)
)

com_google_fonts_check_whitespace_glyph_nbsp = profile.check_log_override(
    'com.google.fonts/check/whitespace_glyphs',
    reason='For Adobe, this is not as severe '\
           + 'as assessed in the original check for 0x00A0.',
    overrides = (('missing-whitespace-glyph-0x00A0', WARN, None),)
)

com_google_fonts_check_valid_glyphnames_adobefonts = profile.check_log_override(
    'com.google.fonts/check/valid_glyphnames'
  , overrides = (('found-invalid-names', WARN, None),)
)

profile.test_expected_checks(ADOBEFONTS_PROFILE_CHECKS, exclusive=True)
