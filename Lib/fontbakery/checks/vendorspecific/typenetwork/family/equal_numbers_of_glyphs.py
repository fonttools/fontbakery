from fontbakery.testable import CheckRunContext
from fontbakery.prelude import check, condition, Message, PASS, WARN


@condition(CheckRunContext)
def roman_ttFonts(context):
    return [font.ttFont for font in context.fonts if not font.is_italic]


@condition(CheckRunContext)
def italic_ttFonts(context):
    return [font.ttFont for font in context.fonts if font.is_italic]


@check(
    id="typenetwork/family/equal_numbers_of_glyphs",
    rationale="""
        Check if all fonts in a family have the same number of glyphs.
    """,
    conditions=["roman_ttFonts", "italic_ttFonts"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def equal_numbers_of_glyphs(roman_ttFonts, italic_ttFonts):
    """Equal number of glyphs"""
    max_roman_count = 0
    max_roman_font = None
    roman_failed_fonts = {}

    # Checks roman
    for ttFont in list(roman_ttFonts):
        fontname = ttFont.reader.file.name
        this_count = ttFont["maxp"].numGlyphs
        if this_count > max_roman_count:
            max_roman_count = this_count
            max_roman_font = fontname

    for ttFont in list(roman_ttFonts):
        this_count = ttFont["maxp"].numGlyphs
        fontname = ttFont.reader.file.name
        if this_count != max_roman_count:
            roman_failed_fonts[fontname] = this_count

    max_italic_count = 0
    max_italic_font = None
    italic_failed_fonts = {}

    # Checks Italics
    for ttFont in list(italic_ttFonts):
        fontname = ttFont.reader.file.name
        this_count = ttFont["maxp"].numGlyphs
        if this_count > max_italic_count:
            max_italic_count = this_count
            max_italic_font = fontname

    for ttFont in list(italic_ttFonts):
        this_count = ttFont["maxp"].numGlyphs
        fontname = ttFont.reader.file.name
        if this_count != max_italic_count:
            italic_failed_fonts[fontname] = this_count

    if len(roman_failed_fonts) > 0:
        yield WARN, Message(
            "roman-different-number-of-glyphs",
            f"Romans doesn’t have the same number of glyphs"
            f"{max_roman_font} has {max_roman_count} and \n\t{roman_failed_fonts}",
        )
    else:
        yield PASS, (
            "All roman files in this family have an equal total ammount of glyphs."
        )

    if len(italic_failed_fonts) > 0:
        yield WARN, Message(
            "italic-different-number-of-glyphs",
            f"Italics doesn’t have the same number of glyphs"
            f"{max_italic_font} has {max_italic_count} and \n\t{italic_failed_fonts}",
        )
    else:
        yield PASS, (
            "All italics files in this family have an equal total ammount of glyphs."
        )
