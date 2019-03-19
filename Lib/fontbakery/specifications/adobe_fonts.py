"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
from fontbakery.callable import check
from fontbakery.checkrunner import (PASS, FAIL, Section)
from fontbakery.fonts_spec import spec_factory

spec_imports = (
    ('.',
        ('general', 'cmap', 'head', 'os2', 'post', 'name', 'hhea', 'dsig',
         'hmtx', 'gpos', 'gdef', 'kern', 'glyf', 'fvar', 'shared_conditions',
         'loca')
    ),
    ('fontbakery.specifications.googlefonts',
        ('com_google_fonts_check_win_ascent_and_descent'
        ,'com_google_fonts_check_os2_metrics_match_hhea'
        )
    ),
)

# If you comment out the call to specification.test_expected_checks(),
# then this list can be generated from the output of:
# $ fontbakery check-specification fontbakery.specifications.adobe_fonts -L
expected_check_ids = [
    'com.google.fonts/check/single_family_directory',
    'com.google.fonts/check/underline_thickness',
    'com.google.fonts/check/panose_proportion',
    'com.google.fonts/check/panose_familytype',
    'com.google.fonts/check/equal_unicode_encodings',
    'com.google.fonts/check/equal_font_versions',
    'com.google.fonts/check/post_table_version',
    'com.google.fonts/check/name/no_copyright_on_description',
    'com.google.fonts/check/monospace',
    'com.google.fonts/check/xavgcharwidth',
    'com.adobe.fonts/check/fsselection_matches_macstyle',
    'com.adobe.fonts/check/bold_italic_unique_for_nameid1',
    'com.google.fonts/check/ftxvalidator',
    'com.google.fonts/check/ots',
    'com.google.fonts/check/fontforge_stderr',
    'com.google.fonts/check/fontforge',
    'com.google.fonts/check/win_ascent_and_descent',
    'com.google.fonts/check/linegaps',
    'com.google.fonts/check/os2_metrics_match_hhea',
    'com.google.fonts/check/043',  # Checking unitsPerEm value is reasonable.
    'com.google.fonts/check/044',  # Checking font version fields.
    'com.google.fonts/check/dsig',
    'com.google.fonts/check/046',  # Font contains the first few mandatory glyphs (.null or NULL, CR and space)?
    'com.google.fonts/check/047',  # Font contains glyphs for whitespace characters?
    'com.google.fonts/check/048',  # Font has **proper** whitespace glyph names?
    'com.google.fonts/check/049',  # Whitespace glyphs have ink?
    'com.google.fonts/check/050',  # Whitespace glyphs have coherent widths?
    'com.google.fonts/check/052',  # Font contains all required tables?
    'com.google.fonts/check/053',  # Are there unwanted tables?
    'com.google.fonts/check/057',  # Name table entries should not contain line-breaks.
    'com.google.fonts/check/058',  # Glyph names are all valid?
    'com.google.fonts/check/059',  # Font contains unique glyph names?
    'com.google.fonts/check/063',  # Does GPOS table have kerning information?
    'com.google.fonts/check/ligature_carets',
    'com.google.fonts/check/kerning_for_non_ligated_sequences',
    'com.google.fonts/check/066',  # Is there a "kern" table declared in the font?
    'com.google.fonts/check/068',  # Does full font name begin with the font family name?
    'com.google.fonts/check/069',  # Is there any unused data at the end of the glyf table?
    'com.google.fonts/check/071',  # Font follows the family naming recommendations?
    'com.google.fonts/check/073',  # MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?
    'com.google.fonts/check/075',  # Check for points out of bounds.
    # 'com.google.fonts/check/076',  # Check glyphs have unique unicode codepoints.
    'com.google.fonts/check/077',  # Check all glyphs have codepoints assigned.
    'com.google.fonts/check/079',  # Monospace font has hhea.advanceWidthMax equal to each glyph's advanceWidth?
    'com.google.fonts/check/152',  # Name table strings must not contain 'Reserved Font Name'.
    'com.google.fonts/check/family_and_style_max_length',
    'com.google.fonts/check/varfont/regular_wght_coord',
    'com.google.fonts/check/168',  # The variable font 'wdth' (Width) axis coordinate must be 100 on the 'Regular' instance.
    'com.google.fonts/check/169',  # The variable font 'slnt' (Slant) axis coordinate must be zero on the 'Regular' instance.
    'com.google.fonts/check/170',  # The variable font 'ital' (Italic) axis coordinate must be zero on the 'Regular' instance.
    'com.google.fonts/check/171',  # The variable font 'opsz' (Optical Size) axis coordinate should be between 9 and 13 on the 'Regular' instance.
    'com.google.fonts/check/172',  # The variable font 'wght' (Weight) axis coordinate must be 700 on the 'Bold'
    'com.google.fonts/check/180',  # Does the number of glyphs in the loca table match the maxp table?
    'com.google.fonts/check/ttx-roundtrip',
    'com.google.fonts/check/fontbakery_version',
    'com.google.fonts/check/ftxvalidator_is_available',
    'com.google.fonts/check/wght_valid_range',
    'com.adobe.fonts/check/postscript_name_cff_vs_name',
    'com.adobe.fonts/check/postscript_name_consistency',
    'com.adobe.fonts/check/max_4_fonts_per_family_name',
    'com.adobe.fonts/check/name_empty_records',
    'com.adobe.fonts/check/consistent_upm'
]

specification = spec_factory(default_section=Section("Adobe Fonts"))


@check(
    id='com.adobe.fonts/check/name_empty_records',
    conditions=[],
    rationale="""Check the name table for empty records,
    as this can cause problems in Adobe apps."""
)
def com_adobe_fonts_check_name_empty_records(ttFont):
    """Check name table for empty records."""
    failed = False
    for name_record in ttFont['name'].names:
        name_string = name_record.toUnicode().strip()
        if len(name_string) == 0:
            failed = True
            name_key = tuple([name_record.platformID, name_record.platEncID,
                             name_record.langID, name_record.nameID])
            yield FAIL, ("'name' table record with key={} is "
                         "empty and should be removed."
                         ).format(name_key)
    if not failed:
        yield PASS, ("No empty name table records found.")


@check(
    id='com.adobe.fonts/check/consistent_upm',
    rationale="""While not required by the OpenType spec, we (Adobe) expect
    that a group of fonts designed & produced as a family have consistent
    units per em. """
)
def com_adobe_fonts_check_consistent_upm(ttFonts):
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


specification.check_skip_filter = check_skip_filter

specification.auto_register(globals())

specification.test_expected_checks(expected_check_ids, exclusive=True)
