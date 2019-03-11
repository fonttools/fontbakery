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
         'loca')),
    ('fontbakery.specifications.googlefonts',
        ('com_google_fonts_check_040', 'com_google_fonts_check_042')),
)

# If you comment out the call to specification.test_expected_checks(),
# then this list can be generated from the output of:
# $ fontbakery check-specification fontbakery.specifications.adobe_fonts -L
expected_check_ids = [
    'com.google.fonts/check/002',  # Checking all files are in the same directory.
    'com.google.fonts/check/008',  # Fonts have consistent underline thickness?
    'com.google.fonts/check/009',  # Fonts have consistent PANOSE proportion?
    'com.google.fonts/check/010',  # Fonts have consistent PANOSE family type?
    'com.google.fonts/check/013',  # Fonts have equal unicode encodings?
    'com.google.fonts/check/014',  # Make sure all font files have the same version value.
    'com.google.fonts/check/015',  # Font has post table version 2?
    'com.google.fonts/check/031',  # Description strings in the name table must not contain copyright info.
    'com.google.fonts/check/033',  # Checking correctness of monospaced metadata.
    'com.google.fonts/check/034',  # Check if OS/2 xAvgCharWidth is correct.
    'com.adobe.fonts/check/fsselection_matches_macstyle',  # Check if OS/2 fsSelection matches head macStyle bold and italic bits.
    'com.adobe.fonts/check/bold_italic_unique_for_nameid1', # Check that OS/2.fsSelection bold & italic settings are unique for each NameID1
    'com.google.fonts/check/035',  # Checking with ftxvalidator.
    'com.google.fonts/check/036',  # Checking with ots-sanitize.
    'com.google.fonts/check/038',  # FontForge validation outputs error messages?
    'com.google.fonts/check/039',  # FontForge checks.
    'com.google.fonts/check/040',  # Checking OS/2 usWinAscent & usWinDescent.
    'com.google.fonts/check/041',  # Checking Vertical Metric Linegaps.
    'com.google.fonts/check/042',  # Checking OS/2 Metrics match hhea Metrics.
    'com.google.fonts/check/043',  # Checking unitsPerEm value is reasonable.
    'com.google.fonts/check/044',  # Checking font version fields.
    'com.google.fonts/check/045',  # Does the font have a DSIG table?
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
    'com.google.fonts/check/064',  # Is there a caret position declared for every ligature?
    'com.google.fonts/check/065',  # Is there kerning info for non-ligated sequences?
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
    'com.google.fonts/check/163',  # Combined length of family and style must not exceed 20 characters.
    'com.google.fonts/check/167',  # The variable font 'wght' (Weight) axis coordinate must be 400 on the 'Regular' instance.
    'com.google.fonts/check/168',  # The variable font 'wdth' (Width) axis coordinate must be 100 on the 'Regular' instance.
    'com.google.fonts/check/169',  # The variable font 'slnt' (Slant) axis coordinate must be zero on the 'Regular' instance.
    'com.google.fonts/check/170',  # The variable font 'ital' (Italic) axis coordinate must be zero on the 'Regular' instance.
    'com.google.fonts/check/171',  # The variable font 'opsz' (Optical Size) axis coordinate should be between 9 and 13 on the 'Regular' instance.
    'com.google.fonts/check/172',  # The variable font 'wght' (Weight) axis coordinate must be 700 on the 'Bold'
    'com.google.fonts/check/180',  # Does the number of glyphs in the loca table match the maxp table?
    'com.google.fonts/check/ttx-roundtrip',  # Checking with fontTools.ttx
    'com.google.fonts/check/fontbakery_version',  # Do we have the latest version of FontBakery installed?
    'com.google.fonts/check/ftxvalidator_is_available',  # Is the command "ftxvalidator" (Apple Font Tool Suite) available?
    'com.google.fonts/check/wght_valid_range',  # Weight axis coordinate must be within spec range of 1 to 1000 on all instances.
    'com.adobe.fonts/check/postscript_name_cff_vs_name',  # CFF table FontName must match name table ID 6 (PostScript name).
    'com.adobe.fonts/check/max_4_fonts_per_family_name',  # Verify that each group of fonts with the same nameID 1 has maximum of 4 fonts
    'com.adobe.fonts/check/name_empty_records',  # check 'name' table for empty records
    'com.adobe.fonts/check/consistent_upm'  # fonts have consistent Units Per Em?
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
        # ToDo: revisit the FontForge checks -- can we filter just some out?
        'com.google.fonts/check/038',  # FontForge #1 of 2
        'com.google.fonts/check/039',  # FontForge #2 of 2
        'com.google.fonts/check/064',  # Is there a caret position declared for every ligature?
        'com.google.fonts/check/065',  # Is there kerning info for non-ligated sequences?
        'com.google.fonts/check/163'   # Combined length of family and style must not exceed 20 characters.
    ):
        return False, None
    return True, None


# ToDo: add many more checks...


specification.check_skip_filter = check_skip_filter

specification.auto_register(globals())

specification.test_expected_checks(expected_check_ids, exclusive=True)
