import os
from collections import Counter
from typing import List

from fontbakery.prelude import condition
from fontbakery.testable import (
    CheckRunContext,
    Designspace,
    Font,
    TTCFont,
    Ufo,
)
from fontbakery.utils import get_glyph_name


@condition(CheckRunContext)
def network(collection):
    return not collection.config["skip_network"]


@condition(CheckRunContext)
def are_ttf(collection):
    return all(f.is_ttf for f in collection.fonts)


@condition(Font)
def variable_font_filename(font):
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import MacStyle, NameID

    ttFont = font.ttFont
    familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    typo_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    if not familynames:
        return None

    familyname = typo_familynames[0] if typo_familynames else familynames[0]
    familyname = "".join(familyname.split(" "))  # remove spaces
    if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
        familyname += "-Italic"

    tags = ttFont["fvar"].axes
    tags = list(map(lambda t: t.axisTag, tags))
    tags.sort()
    tags = "[{}]".format(",".join(tags))
    return f"{familyname}{tags}.ttf"


@condition(Font)
def glyph_metrics_stats(font):
    """Returns a dict containing whether the font seems_monospaced,
    what's the maximum glyph width and what's the most common width.

    For a font to be considered monospaced, if at least 80% of ASCII
    characters have glyphs, then at least 80% of those must have the same
    width, otherwise all glyphs of printable characters must have one of
    two widths or be zero-width.
    """
    ttFont = font.ttFont
    glyph_metrics = ttFont["hmtx"].metrics
    # NOTE: `range(a, b)` includes `a` and does not include `b`.
    #       Here we don't include 0-31 as well as 127
    #       because these are control characters.
    ascii_glyph_names = [
        ttFont.getBestCmap()[c] for c in range(32, 127) if c in ttFont.getBestCmap()
    ]

    if len(ascii_glyph_names) > 0.8 * (127 - 32):
        ascii_widths = [
            adv
            for name, (adv, lsb) in glyph_metrics.items()
            if name in ascii_glyph_names and adv != 0
        ]
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
            marks = {
                name for name, c in gdef.table.GlyphClassDef.classDefs.items() if c == 3
            }
            relevant_glyph_names.difference_update(marks)

        widths = sorted(
            {
                adv
                for name, (adv, lsb) in glyph_metrics.items()
                if name in relevant_glyph_names and adv != 0
            }
        )
        seems_monospaced = len(widths) <= 2

    width_max = max(adv for k, (adv, lsb) in glyph_metrics.items())
    most_common_width = Counter(
        [g for g in glyph_metrics.values() if g[0] != 0]
    ).most_common(1)[0][0][0]
    return {
        "seems_monospaced": seems_monospaced,
        "width_max": width_max,
        "most_common_width": most_common_width,
    }


def get_instance_axis_value(ttFont, instance_name, axis_tag):
    if "fvar" not in ttFont:
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


@condition(Font)
def regular_wght_coord(font):
    ttFont = font.ttFont
    upright = get_instance_axis_value(ttFont, "Regular", "wght")
    italic = get_instance_axis_value(ttFont, "Italic", "wght")
    if upright is None and italic is None:
        italic = get_instance_axis_value(ttFont, "Regular Italic", "wght")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition(Font)
def bold_wght_coord(font):
    ttFont = font.ttFont
    upright = get_instance_axis_value(ttFont, "Bold", "wght")
    italic = get_instance_axis_value(ttFont, "Bold Italic", "wght")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition(Font)
def regular_wdth_coord(font):
    ttFont = font.ttFont
    upright = get_instance_axis_value(ttFont, "Regular", "wdth")
    italic = get_instance_axis_value(ttFont, "Italic", "wdth")
    if upright is None and italic is None:
        italic = get_instance_axis_value(ttFont, "Regular Italic", "wdth")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition(Font)
def regular_slnt_coord(font):
    ttFont = font.ttFont
    return get_instance_axis_value(ttFont, "Regular", "slnt")


@condition(Font)
def regular_ital_coord(font):
    ttFont = font.ttFont
    return get_instance_axis_value(ttFont, "Regular", "ital")


@condition(Font)
def regular_opsz_coord(font):
    ttFont = font.ttFont
    upright = get_instance_axis_value(ttFont, "Regular", "opsz")
    italic = get_instance_axis_value(ttFont, "Italic", "opsz")
    if upright is None and italic is None:
        italic = get_instance_axis_value(ttFont, "Regular Italic", "opsz")
    # Note: you cannot simply do `return upright or italic` since `0 or None`
    # will return None in Python.
    return upright if upright is not None else italic


@condition(Font)
def vtt_talk_sources(font) -> List[str]:
    """Return the tags of VTT source tables found in a font."""
    VTT_SOURCE_TABLES = {"TSI0", "TSI1", "TSI2", "TSI3", "TSI5"}
    tables_found = [tag for tag in font.ttFont.keys() if tag in VTT_SOURCE_TABLES]
    return tables_found


@condition(Font)
def is_cjk_font(font):
    """
    The `is_claiming_to_be_cjk_font` condition looks up the font's metadata to see if
    it is claiming to be a CJK font. But the metadata may be wrong, and the correctness
    of the metadata is something what we want to check!
    We also want to know if the font really is a CJK font, i.e. it contains a
    significant number of CJK characters. We say that *this* definition is met if the
    font has more than 150 CJK Unicode code points defined in the cmap table.
    """
    return len(font.get_cjk_glyphs) > 150


@condition(Font)
def get_cjk_glyphs(font):
    """Return all glyphs which belong to a CJK unicode block"""
    from fontbakery.constants import CJK_UNICODE_RANGES

    results = []
    cjk_unicodes = set()
    for start, end in CJK_UNICODE_RANGES:
        cjk_unicodes |= set(u for u in range(start, end + 1))
    for uni, glyph_name in font.ttFont.getBestCmap().items():
        if uni in cjk_unicodes:
            results.append(glyph_name)
    return results


@condition(Font)
def sibling_directories(font):
    """
    Given a directory, this function tries to figure out where else in the filesystem
    other related "sibling" families might be located.
    This is guesswork and may not be able to find font files in other folders not yet
    covered by this routine. We may improve this in the future by adding other
    smarter filesystem lookup procedures or even by letting the user feed explicit
    sibling family paths.

    This function returs a list of paths to directories where related font files were
    detected.
    """
    SIBLING_SUFFIXES = ["sans", "sc", "narrow", "text", "display", "condensed"]

    base_family_dir = font.family_directory
    for suffix in SIBLING_SUFFIXES:
        if font.family_directory.endswith(suffix):
            candidate = font.family_directory[: -len(suffix)]
            if os.path.isdir(candidate):
                base_family_dir = candidate
                break

    directories = [base_family_dir]
    for suffix in SIBLING_SUFFIXES:
        candidate = base_family_dir + suffix
        if os.path.isdir(candidate):
            directories.append(candidate)

    return directories


@condition(Font)
def superfamily(font):
    """
    Given a list of directories, this functions looks for font files
    and returs a list of lists of the detected filepaths.
    """
    result = []
    for family_dir in font.sibling_directories:
        filepaths = []
        for entry in os.listdir(family_dir):
            if entry[-4:] in [".otf", ".ttf"]:
                filepaths.append(os.path.join(family_dir, entry))
        result.append(filepaths)
    return result


@condition(Font)
def superfamily_ttFonts(font):
    from fontTools.ttLib import TTFont

    result = []
    for family in font.superfamily:
        result.append([TTFont(f) for f in family])
    return result


@condition(Font)
def is_indic_font(font):
    INDIC_FONT_DETECTION_CODEPOINTS = [
        0x0988,  # Bengali
        0x0908,  # Devanagari
        0x0A88,  # Gujarati
        0x0A08,  # Gurmukhi
        0x0D08,  # Kannada
        0x0B08,  # Malayalam
        0xABC8,  # Meetei Mayek
        0x1C58,  # OlChiki
        0x0B08,  # Oriya
        0x0B88,  # Tamil
        0x0C08,  # Telugu
    ]

    font_codepoints = font.font_codepoints
    for codepoint in INDIC_FONT_DETECTION_CODEPOINTS:
        if codepoint in font_codepoints:
            return True

    # otherwise:
    return False


@condition(Font)
def missing_whitespace_chars(font):
    ttFont = font.ttFont
    space = get_glyph_name(ttFont, 0x0020)
    nbsp = get_glyph_name(ttFont, 0x00A0)
    # tab = get_glyph_name(ttFont, 0x0009)

    missing = []
    if space is None:
        missing.append("0x0020")
    if nbsp is None:
        missing.append("0x00A0")
    # fonts probably don't need an actual tab char
    # if tab is None: missing.append("0x0009")
    return missing


class CFFAnalysis:
    def __init__(self):
        self.glyphs_dotsection = []
        self.glyphs_endchar_seac = []
        self.glyphs_exceed_max = []
        self.glyphs_recursion_errors = []
        self.string_not_ascii = []


def _get_subr_bias(count):
    if count < 1240:
        bias = 107
    elif count < 33900:
        bias = 1131
    else:
        bias = 32768
    return bias


def _traverse_subr_call_tree(info, program, depth):
    global_subrs = info["global_subrs"]
    subrs = info["subrs"]
    gsubr_bias = info["gsubr_bias"]
    subr_bias = info["subr_bias"]

    if depth > info["max_depth"]:
        info["max_depth"] = depth

    # once we exceed the max depth we can stop going deeper
    if depth > 10:
        return

    if (
        len(program) >= 5
        and program[-1] == "endchar"
        and all([isinstance(a, int) for a in program[-5:-1]])
    ):
        info["saw_endchar_seac"] = True
    if "ignore" in program:  # decompiler expresses 'dotsection' as 'ignore'
        info["saw_dotsection"] = True

    while program:
        x = program.pop()
        if x == "callgsubr":
            y = int(program.pop()) + gsubr_bias
            sub_program = global_subrs[y].program.copy()
            _traverse_subr_call_tree(info, sub_program, depth + 1)
        elif x == "callsubr":
            y = int(program.pop()) + subr_bias
            sub_program = subrs[y].program.copy()
            _traverse_subr_call_tree(info, sub_program, depth + 1)


def _analyze_cff(analysis, top_dict, private_dict, fd_index=0):
    char_strings = top_dict.CharStrings
    global_subrs = top_dict.GlobalSubrs
    gsubr_bias = _get_subr_bias(len(global_subrs))

    if hasattr(top_dict, "rawDict"):
        raw_dict = top_dict.rawDict
        for key in ["Notice", "Copyright", "FontName", "FullName", "FamilyName"]:
            for char in raw_dict.get(key, ""):
                if ord(char) > 0x7F:
                    analysis.string_not_ascii.append((key, raw_dict[key]))
                    break

    if private_dict is not None and hasattr(private_dict, "Subrs"):
        subrs = private_dict.Subrs
        subr_bias = _get_subr_bias(len(subrs))
    else:
        subrs = None
        subr_bias = None

    char_list = char_strings.keys()

    for glyph_name in char_list:
        t2_char_string, fd_select_index = char_strings.getItemAndSelector(glyph_name)
        if fd_select_index is not None and fd_select_index != fd_index:
            continue
        try:
            t2_char_string.decompile()
        except RecursionError:
            analysis.glyphs_recursion_errors.append(glyph_name)
            continue
        info = {}
        info["subrs"] = subrs
        info["global_subrs"] = global_subrs
        info["gsubr_bias"] = gsubr_bias
        info["subr_bias"] = subr_bias
        info["max_depth"] = 0
        depth = 0
        program = t2_char_string.program.copy()
        _traverse_subr_call_tree(info, program, depth)
        max_depth = info["max_depth"]

        if max_depth > 10:
            analysis.glyphs_exceed_max.append(glyph_name)
        if info.get("saw_endchar_seac"):
            analysis.glyphs_endchar_seac.append(glyph_name)
        if info.get("saw_dotsection"):
            analysis.glyphs_dotsection.append(glyph_name)


@condition(Font)
def cff_analysis(font):
    from fontTools.ttLib import TTFont

    analysis = CFFAnalysis()
    if isinstance(font, TTCFont):
        ttFont = TTFont(font.file, fontNumber=font.index)
    else:
        ttFont = TTFont(font.file)  # Use our own copy here since we are decompiling

    if "CFF " in ttFont:
        try:
            cff = ttFont["CFF "].cff
        except UnicodeDecodeError:
            analysis.string_not_ascii = None
            return analysis

        for top_dict in cff.topDictIndex:
            if hasattr(top_dict, "FDArray"):
                for fd_index, font_dict in enumerate(top_dict.FDArray):
                    if hasattr(font_dict, "Private"):
                        private_dict = font_dict.Private
                    else:
                        private_dict = None
                    _analyze_cff(analysis, top_dict, private_dict, fd_index)
            else:
                if hasattr(top_dict, "Private"):
                    private_dict = top_dict.Private
                else:
                    private_dict = None
                _analyze_cff(analysis, top_dict, private_dict)

    elif "CFF2" in ttFont:
        cff = ttFont["CFF2"].cff

        for top_dict in cff.topDictIndex:
            for fd_index, font_dict in enumerate(top_dict.FDArray):
                if hasattr(font_dict, "Private"):
                    private_dict = font_dict.Private
                else:
                    private_dict = None
                _analyze_cff(analysis, top_dict, private_dict, fd_index)

    return analysis


@condition(Font)
def licenses(font):
    """Get a list of paths for every license
    file found in a font project."""
    from fontbakery.utils import git_rootdir

    found = []
    family_directory = font.family_directory
    search_paths = [family_directory]
    gitroot = git_rootdir(family_directory)
    if gitroot and gitroot not in search_paths:
        search_paths.append(gitroot)

    for directory in search_paths:
        if directory:
            for license_filename in ["OFL.txt", "LICENSE.txt"]:
                license_path = os.path.join(directory, license_filename)
                if os.path.exists(license_path):
                    found.append(license_path)
    return found


@condition(Font)
def license_contents(font):
    if font.license_path:
        return open(font.license_path, encoding="utf-8").read().replace(" \n", "\n")


@condition(Font)
def license_path(font):
    """Get license path."""
    # This assumes that a repo can have multiple license files
    # and they're all the same.
    # FIXME: We should have a fontbakery check for that, though!
    if font.licenses and len(font.licenses) > 0:
        return font.licenses[0]


@condition(Font)
def license_filename(font):
    """Get license filename."""
    if font.license_path:
        return os.path.basename(font.license_path)


@condition(Font)
def is_ofl(font):
    return font.license_filename and "OFL" in font.license_filename


@condition(Font)
def outlines_dict(font):
    from beziers.path import BezierPath

    ttFont = font.ttFont
    reversed_cmap = {v: k for k, v in ttFont.getBestCmap().items()}

    def display_name(glyphname):
        if glyphname in reversed_cmap:
            return f"{glyphname} (U+{reversed_cmap[glyphname]:04X})"
        return glyphname

    return {
        (glyphname, display_name(glyphname)): BezierPath.fromFonttoolsGlyph(
            ttFont, glyphname
        )
        for glyphname in ttFont.getGlyphOrder()
    }


@condition(Ufo)
def ufo_font(ufo):
    from fontTools.ufoLib.errors import UFOLibError
    import defcon

    try:
        return defcon.Font(ufo.file)
    except UFOLibError:
        return None


@condition(Designspace)
def designSpace(designspace):
    """
    Given a filepath for a designspace file, parse it
    and return a DesignSpaceDocument, which is
    'an object to read, write and edit
    interpolation systems for typefaces'.
    """
    from fontTools.designspaceLib import DesignSpaceDocument
    import defcon

    if designspace:
        DS = DesignSpaceDocument.fromfile(designspace.file)
        DS.loadSourceFonts(defcon.Font)
        return DS


@condition(Designspace)
def designspace_sources(designspace):
    """
    Given a DesignSpaceDocument object,
    return a set of UFO font sources.
    """
    import defcon

    if designspace.designSpace:
        return designspace.designSpace.loadSourceFonts(defcon.Font)
