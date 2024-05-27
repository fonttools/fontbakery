import os

from fontbakery.prelude import condition
from fontbakery.testable import Font
from fontbakery.utils import get_glyph_name


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
