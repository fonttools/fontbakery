import os
from typing import List
from collections import Counter

from fontbakery.callable import condition
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import,cyclic-import


@condition
def ttFont(font):
    from fontTools.ttLib import TTFont
    return TTFont(font)


@condition
def is_ttf(ttFont):
    return 'glyf' in ttFont


@condition
def are_ttf(ttFonts):
    for f in ttFonts:
        if not is_ttf(f):
            return False
    # otherwise:
    return True


@condition
def is_cff(ttFont):
    return 'CFF ' in ttFont


@condition
def is_cff2(ttFont):
    return 'CFF2' in ttFont


@condition
def has_name_table(ttFont):
    return "name" in ttFont.keys()


@condition
def has_os2_table(ttFont):
    return "OS/2" in ttFont.keys()


@condition
def has_STAT_table(ttFont):
    return "STAT" in ttFont


@condition
def variable_font_filename(ttFont):
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import (MacStyle,
                                      NameID)
    familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    typo_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    if familynames == []:
        return None

    familyname = typo_familynames[0] if typo_familynames else familynames[0]
    familyname = "".join(familyname.split(' ')) #remove spaces
    if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
        familyname+="-Italic"

    tags = ttFont["fvar"].axes
    tags = list(map(lambda t: t.axisTag, tags))
    tags.sort()
    tags = "[{}]".format(",".join(tags))
    return f"{familyname}{tags}.ttf"


@condition
def designSpace(designspace):
    """
    Given a filepath for a designspace file, parse it
    and return a DesignSpaceDocument, which is
    'an object to read, write and edit
    interpolation systems for typefaces'.
    """
    if designspace:
        from fontTools.designspaceLib import DesignSpaceDocument
        import defcon
        DS = DesignSpaceDocument.fromfile(designspace)
        DS.loadSourceFonts(defcon.Font)
        return DS


@condition
def designspace_sources(designSpace):
    """
    Given a DesignSpaceDocument object,
    return a set of UFO font sources.
    """
    if designSpace:
        import defcon
        return designSpace.loadSourceFonts(defcon.Font)


@condition
def family_directory(font):
    """Get the path of font project directory."""
    if font:
        dirname = os.path.dirname(font)
        if dirname == '':
            dirname = '.'
        return dirname


@condition
def sibling_directories(family_directory):
    """
    Given a directory, this function tries to figure out where else in the filesystem
    other related "sibling" families might be located.
    This is guesswork and may not be able to find font files in other folders not yet
    covered by this routine. We may improve this in the future by adding other
    smarter filesystem lookup procedures or even by letting the user feed explicit
    sibling family paths.

    This function returs a list of paths to directories where related font files were detected.
    """
    SIBLING_SUFFIXES = ["sans",
                        "sc",
                        "narrow",
                        "text",
                        "display",
                        "condensed"]

    base_family_dir = family_directory
    for suffix in SIBLING_SUFFIXES:
        if family_directory.endswith(suffix):
            candidate = family_directory[:-len(suffix)]
            if os.path.isdir(candidate):
                base_family_dir = candidate
                break

    directories = [base_family_dir]
    for suffix in SIBLING_SUFFIXES:
        candidate = base_family_dir + suffix
        if os.path.isdir(candidate):
            directories.append(candidate)

    return directories


@condition
def superfamily(sibling_directories):
    """
    Given a list of directories, this functions looks for font files
    and returs a list of lists of the detected filepaths.
    """
    result = []
    for family_dir in sibling_directories:
        filepaths = []
        for entry in os.listdir(family_dir):
            if entry[-4:] in [".otf", ".ttf"]:
                filepaths.append(os.path.join(family_dir, entry))
        result.append(filepaths)
    return result


@condition
def superfamily_ttFonts(superfamily):
    from fontTools.ttLib import TTFont
    result = []
    for family in superfamily:
        result.append([TTFont(f) for f in family])
    return result


@condition
def ligatures(ttFont):
    from fontTools.ttLib.tables.otTables import LigatureSubst

    all_ligatures = {}
    try:
        if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
            for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if record.FeatureTag == 'liga':
                    for index in record.Feature.LookupListIndex:
                        lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
                        for subtable in lookup.SubTable:
                            if isinstance(subtable, LigatureSubst):
                                for firstGlyph in subtable.ligatures.keys():
                                    all_ligatures[firstGlyph] = []
                                    for lig in subtable.ligatures[firstGlyph]:
                                        if lig.Component not in all_ligatures[firstGlyph]:
                                            all_ligatures[firstGlyph].append(lig.Component)
        return all_ligatures
    except:
        return -1 # Indicate fontTools-related crash...


@condition
def ligature_glyphs(ttFont):
    from fontTools.ttLib.tables.otTables import LigatureSubst

    all_ligature_glyphs = []
    try:
        if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
            for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if record.FeatureTag == 'liga':
                    for index in record.Feature.LookupListIndex:
                        lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
                        for subtable in lookup.SubTable:
                            if isinstance(subtable, LigatureSubst):
                                for firstGlyph in subtable.ligatures.keys():
                                    for lig in subtable.ligatures[firstGlyph]:
                                        if lig.LigGlyph not in all_ligature_glyphs:
                                            all_ligature_glyphs.append(lig.LigGlyph)
        return all_ligature_glyphs
    except:
        return -1  # Indicate fontTools-related crash...


@condition
def glyph_metrics_stats(ttFont):
    """Returns a dict containing whether the font seems_monospaced,
    what's the maximum glyph width and what's the most common width.

    For a font to be considered monospaced, if at least 80% of ASCII
    characters have glyphs, then at least 80% of those must have the same
    width, otherwise all glyphs of printable characters must have one of
    two widths or be zero-width.
    """
    glyph_metrics = ttFont['hmtx'].metrics
    # NOTE: `range(a, b)` includes `a` and does not include `b`.
    #       Here we don't include 0-31 as well as 127
    #       because these are control characters.
    ascii_glyph_names = [ttFont.getBestCmap()[c] for c in range(32, 127)
                         if c in ttFont.getBestCmap()]

    if len(ascii_glyph_names) > 0.8 * (127 - 32):
        ascii_widths = [adv for name, (adv, lsb) in glyph_metrics.items()
                        if name in ascii_glyph_names and adv != 0]
        ascii_width_count = Counter(ascii_widths)
        ascii_most_common_width = ascii_width_count.most_common(1)[0][1]
        seems_monospaced = ascii_most_common_width >= len(ascii_widths) * 0.8
    else:
        from fontTools import unicodedata
        # Collect relevant glyphs.
        relevant_glyph_names = set()
        # Add character glyphs that are in one of these categories:
        # Letter, Mark, Number, Punctuation, Symbol, Space_Separator.
        # This excludes Line_Separator, Paragraph_Separator and Control.
        for value, name in ttFont.getBestCmap().items():
            if unicodedata.category(chr(value)).startswith(
                ("L", "M", "N", "P", "S", "Zs")
            ):
                relevant_glyph_names.add(name)
        # Remove character glyphs that are mark glyphs.
        gdef = ttFont.get("GDEF")
        if gdef and gdef.table.GlyphClassDef:
            marks = {name
                     for name, c in gdef.table.GlyphClassDef.classDefs.items()
                     if c == 3
                    }
            relevant_glyph_names.difference_update(marks)

        widths = sorted({adv for name, (adv, lsb) in glyph_metrics.items()
                         if name in relevant_glyph_names and adv != 0})
        seems_monospaced = len(widths) <= 2

    width_max = max(adv for k, (adv, lsb) in glyph_metrics.items())
    most_common_width = Counter([g for g in glyph_metrics.values()
                                 if g[0] != 0]).most_common(1)[0][0][0]
    return {
        "seems_monospaced": seems_monospaced,
        "width_max": width_max,
        "most_common_width": most_common_width,
    }


@condition
def missing_whitespace_chars(ttFont):
    from fontbakery.utils import get_glyph_name
    space = get_glyph_name(ttFont, 0x0020)
    nbsp = get_glyph_name(ttFont, 0x00A0)
    # tab = get_glyph_name(ttFont, 0x0009)

    missing = []
    if space is None: missing.append("0x0020")
    if nbsp is None: missing.append("0x00A0")
    # fonts probably don't need an actual tab char
    # if tab is None: missing.append("0x0009")
    return missing


@condition
def vmetrics(ttFonts):
    from fontbakery.utils import get_bounding_box
    v_metrics = {"ymin": 0, "ymax": 0}
    for ttFont in ttFonts:
        font_ymin, font_ymax = get_bounding_box(ttFont)
        v_metrics["ymin"] = min(font_ymin, v_metrics["ymin"])
        v_metrics["ymax"] = max(font_ymax, v_metrics["ymax"])
    return v_metrics


@condition
def is_hinted(ttFont):
    return "fpgm" in ttFont

@condition
def is_variable_font(ttFont):
    return "fvar" in ttFont.keys()


@condition
def is_not_variable_font(ttFont):
    return "fvar" not in ttFont.keys()


@condition
def VFs(ttFonts):
    """Returns a list of font files which are recognized as variable fonts"""
    return [ttFont for ttFont in ttFonts
            if is_variable_font(ttFont)]


@condition
def slnt_axis(ttFont):
    if "fvar" in ttFont:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == "slnt":
                return axis


@condition
def opsz_axis(ttFont):
    if "fvar" in ttFont:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == "opsz":
                return axis


@condition
def ital_axis(ttFont):
    if "fvar" in ttFont:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == "ital":
                return axis


@condition
def grad_axis(ttFont):
    if "fvar" in ttFont:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == "GRAD":
                return axis


def get_axis_tags_set(ttFont):
    return set(axis.axisTag for axis in ttFont["fvar"].axes)


@condition
def has_wght_axis(ttFont):
    if is_variable_font(ttFont) and "wght" in get_axis_tags_set(ttFont):
        return True


@condition
def has_wdth_axis(ttFont):
    if is_variable_font(ttFont) and "wdth" in get_axis_tags_set(ttFont):
        return True


@condition
def has_slnt_axis(ttFont):
    if is_variable_font(ttFont) and "slnt" in get_axis_tags_set(ttFont):
        return True


@condition
def has_ital_axis(ttFont):
    if is_variable_font(ttFont) and "ital" in get_axis_tags_set(ttFont):
        return True


def get_instance_axis_value(ttFont, instance_name, axis_tag):
    if not is_variable_font(ttFont):
        return None

    instance = None
    for i in ttFont["fvar"].instances:
        name = ttFont["name"].getDebugName(i.subfamilyNameID)
        if name == instance_name:
            instance = i
            break

    if instance:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == axis_tag:
                return instance.coordinates[axis_tag]


@condition
def regular_wght_coord(ttFont):
    upright = get_instance_axis_value(ttFont, "Regular", "wght")
    italic = get_instance_axis_value(ttFont, "Italic", "wght")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition
def bold_wght_coord(ttFont):
    upright = get_instance_axis_value(ttFont, "Bold", "wght")
    italic = get_instance_axis_value(ttFont, "Bold Italic", "wght")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition
def regular_wdth_coord(ttFont):
    upright = get_instance_axis_value(ttFont, "Regular", "wdth")
    italic = get_instance_axis_value(ttFont, "Italic", "wdth")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition
def regular_slnt_coord(ttFont):
    return get_instance_axis_value(ttFont, "Regular", "slnt")


@condition
def regular_ital_coord(ttFont):
    return get_instance_axis_value(ttFont, "Regular", "ital")


@condition
def regular_opsz_coord(ttFont):
    upright = get_instance_axis_value(ttFont, "Regular", "opsz")
    italic = get_instance_axis_value(ttFont, "Italic", "opsz")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition
def vtt_talk_sources(ttFont) -> List[str]:
    """Return the tags of VTT source tables found in a font."""
    VTT_SOURCE_TABLES = {'TSI0', 'TSI1', 'TSI2', 'TSI3', 'TSI5'}
    tables_found = [tag for tag in ttFont.keys() if tag in VTT_SOURCE_TABLES]
    return tables_found


@condition
def preferred_cmap(ttFont):
    from fontbakery.utils import get_preferred_cmap
    return get_preferred_cmap(ttFont)


@condition
def unicoderange(ttFont):
    """Get an integer bitmap representing the UnicodeRange fields in the os/2 table."""
    os2 = ttFont['OS/2']
    return (os2.ulUnicodeRange1 |
            os2.ulUnicodeRange2 << 32 |
            os2.ulUnicodeRange3 << 64 |
            os2.ulUnicodeRange4 << 96)

@condition
def is_cjk_font(ttFont):
    """Test font object to confirm that it meets our definition of a CJK font file.

    The definition is met if any of the following conditions are True:
      1. The font has a CJK code page bit set in the OS/2 table
      2. The font has a CJK Unicode range bit set in the OS/2 table
      3. The font has any CJK Unicode code points defined in the cmap table
    """
    from fontbakery.constants import (CJK_CODEPAGE_BITS,
                                      CJK_UNICODE_RANGE_BITS,
                                      CJK_UNICODE_RANGES)
    if not has_os2_table(ttFont):
        return

    os2 = ttFont["OS/2"]

    # OS/2 code page checks
    for _, bit in CJK_CODEPAGE_BITS.items():
        if os2.ulCodePageRange1 & (1 << bit):
            return True

    # OS/2 Unicode range checks
    for _, bit in CJK_UNICODE_RANGE_BITS.items():
        if bit in range(0, 32):
            if os2.ulUnicodeRange1 & (1 << bit):
                return True

        elif bit in range(32, 64):
            if os2.ulUnicodeRange2 & (1 << (bit-32)):
                return True

        elif bit in range(64, 96):
            if os2.ulUnicodeRange3 & (1 << (bit-64)):
                return True

    # defined CJK Unicode code point in cmap table checks
    cmap = ttFont.getBestCmap()
    for unicode_range in CJK_UNICODE_RANGES:
        for x in range(unicode_range[0], unicode_range[1]+1):
            if int(x) in cmap:
                return True

    # default, return False if the above checks did not identify a CJK font
    return False


@condition
def get_cjk_glyphs(ttFont):
    """Return all glyphs which belong to a CJK unicode block"""
    from fontbakery.constants import CJK_UNICODE_RANGES
    results = []
    cjk_unicodes = set()
    for start, end in CJK_UNICODE_RANGES:
        cjk_unicodes |= set(u for u in range(start, end+1))
    for uni, glyph_name in ttFont.getBestCmap().items():
        if uni in cjk_unicodes:
            results.append(glyph_name)
    return results


@condition
def typo_metrics_enabled(ttFont):
    return ttFont['OS/2'].fsSelection & 0b10000000 > 0


@condition
def is_indic_font(ttFont):
    INDIC_FONT_DETECTION_CODEPOINTS = [
        0x0988, # Bengali
        0x0908, # Devanagari
        0x0A88, # Gujarati
        0x0A08, # Gurmukhi
        0x0D08, # Kannada
        0x0B08, # Malayalam
        0xABC8, # Meetei Mayek
        0x1C58, # OlChiki
        0x0B08, # Oriya
        0x0B88, # Tamil
        0x0C08, # Telugu
    ]

    font_codepoints = ttFont['cmap'].getBestCmap().keys()
    for codepoint in INDIC_FONT_DETECTION_CODEPOINTS:
        if codepoint in font_codepoints:
            return True

    #otherwise:
    return False


def keyword_in_full_font_name(ttFont, keyword):
    from fontbakery.constants import (MacStyle,
                                      NameID)
    for entry in ttFont["name"].names:
        if entry.nameID == NameID.FULL_FONT_NAME and \
           keyword in entry.string.decode(entry.getEncoding()).lower().split():
            return True
    return False


@condition
def is_italic(ttFont):
    from fontbakery.constants import (FsSelection,
                                      MacStyle)
    return (
        ("OS/2" in ttFont and ttFont["OS/2"].fsSelection & FsSelection.ITALIC)
        or ("head" in ttFont and ttFont["head"].macStyle & MacStyle.ITALIC)
        or keyword_in_full_font_name(ttFont, "italic")
        or ("post" in ttFont and ttFont["post"].italicAngle)
    )


@condition
def is_bold(ttFont):
    from fontbakery.constants import (FsSelection,
                                      MacStyle)
    return (
        ("OS/2" in ttFont and ttFont["OS/2"].fsSelection & FsSelection.BOLD)
        or ("head" in ttFont and ttFont["head"].macStyle & MacStyle.BOLD)
        or keyword_in_full_font_name(ttFont, "bold")
    )


@condition
def is_not_italic(ttFont):
    return not is_italic(ttFont)


@condition
def is_not_bold(ttFont):
    return not is_bold(ttFont)
