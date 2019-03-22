"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
from fontbakery.callable import check
from fontbakery.checkrunner import (PASS, FAIL, Section)
from fontbakery.fonts_profile import profile_factory

profile_imports = (
    ('.',
        ('general', 'cmap', 'head', 'os2', 'post', 'name', 'hhea', 'dsig',
         'hmtx', 'gpos', 'gdef', 'kern', 'glyf', 'fvar', 'shared_conditions',
         'loca')
    ),
    ('fontbakery.profiles.googlefonts',
        ('com_google_fonts_check_family_win_ascent_and_descent'
        ,'com_google_fonts_check_os2_metrics_match_hhea'
        )
    ),
)

# If you comment out the call to profile.test_expected_checks(),
# then this list can be generated from the output of:
# $ fontbakery check-profile fontbakery.profiles.adobefonts -L
expected_check_ids = [
    'com.google.fonts/check/family/single_directory',
    'com.google.fonts/check/family/underline_thickness',
    'com.google.fonts/check/family/panose_proportion',
    'com.google.fonts/check/family/panose_familytype',
    'com.google.fonts/check/family/equal_unicode_encodings',
    'com.google.fonts/check/family/equal_font_versions',
    'com.google.fonts/check/font_version',
    'com.google.fonts/check/post_table_version',
    'com.google.fonts/check/name/no_copyright_on_description',
    'com.google.fonts/check/monospace',
    'com.google.fonts/check/xavgcharwidth',
    'com.adobe.fonts/check/fsselection_matches_macstyle',
    'com.adobe.fonts/check/family/bold_italic_unique_for_nameid1',
    'com.google.fonts/check/ftxvalidator',
    'com.google.fonts/check/ots',
    'com.google.fonts/check/fontforge_stderr',
    'com.google.fonts/check/fontforge',
    'com.google.fonts/check/family/win_ascent_and_descent',
    'com.google.fonts/check/linegaps',
    'com.google.fonts/check/os2_metrics_match_hhea',
    'com.google.fonts/check/unitsperem',
    'com.google.fonts/check/dsig',
    'com.google.fonts/check/mandatory_glyphs',
    'com.google.fonts/check/whitespace_glyphs',
    'com.google.fonts/check/whitespace_glyphnames',
    'com.google.fonts/check/whitespace_ink',
    'com.google.fonts/check/whitespace_widths',
    'com.google.fonts/check/required_tables',
    'com.google.fonts/check/unwanted_tables',
    'com.google.fonts/check/name/line_breaks',
    'com.google.fonts/check/valid_glyphnames',
    'com.google.fonts/check/unique_glyphnames',
    'com.google.fonts/check/gpos_kerning_info',
    'com.google.fonts/check/ligature_carets',
    'com.google.fonts/check/kerning_for_non_ligated_sequences',
    'com.google.fonts/check/kern_table',
    'com.google.fonts/check/name/match_familyname_fullfont',
    'com.google.fonts/check/glyf_unused_data',
    'com.google.fonts/check/family_naming_recommendations',
    'com.google.fonts/check/maxadvancewidth',
    'com.google.fonts/check/points_out_of_bounds',
    'com.google.fonts/check/all_glyphs_have_codepoints',
    'com.google.fonts/check/monospace_max_advancewidth',
    'com.google.fonts/check/name/rfn',
    'com.google.fonts/check/name/family_and_style_max_length',
    'com.google.fonts/check/varfont/regular_wght_coord',
    'com.google.fonts/check/varfont/regular_wdth_coord',
    'com.google.fonts/check/varfont/regular_slnt_coord',
    'com.google.fonts/check/varfont/regular_ital_coord',
    'com.google.fonts/check/varfont/regular_opsz_coord',
    'com.google.fonts/check/varfont/bold_wght_coord',
    'com.google.fonts/check/loca/maxp_num_glyphs',
    'com.google.fonts/check/ttx-roundtrip',
    'com.google.fonts/check/fontbakery_version',
    'com.google.fonts/check/ftxvalidator_is_available',
    'com.google.fonts/check/wght_valid_range',
    'com.adobe.fonts/check/name/postscript_vs_cff',
    'com.adobe.fonts/check/name/postscript_name_consistency',
    'com.adobe.fonts/check/family/max_4_fonts_per_family_name',
    'com.adobe.fonts/check/name/empty_records',
    'com.adobe.fonts/check/family/consistent_upm'
]

profile = profile_factory(default_section=Section("Adobe Fonts"))

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


def check_skip_filter(checkid, font=None, **iterargs):
    if font and checkid in (
        'com.google.fonts/check/ligature_carets',
        'com.google.fonts/check/kerning_for_non_ligated_sequences',
        'com.google.fonts/check/family_and_style_max_length'
    ):
        return False, None
    return True, None


# ToDo: add many more checks...


profile.check_skip_filter = check_skip_filter

profile.auto_register(globals())

profile.test_expected_checks(expected_check_ids, exclusive=True)
