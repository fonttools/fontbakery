from fontbakery.prelude import (
    check,
    Message,
    PASS,
    FAIL,
)
from fontbakery.utils import (
    get_glyph_name,
    glyph_has_ink,
)

# Note: There's also a 'whitespace_glyphs' check at Lib/fontbakery/checks/glyphset.py


@check(
    id="whitespace_widths",
    conditions=["not missing_whitespace_chars"],
    rationale="""
        If the space and nbspace glyphs have different widths, then Google Workspace
        has problems with the font.

        The nbspace is used to replace the space character in multiple situations in
        documents; such as the space before punctuation in languages that do that. It
        avoids the punctuation to be separated from the last word and go to next line.

        This is automatic substitution by the text editors, not by fonts. It's also used
        by designers in text composition practice to create nicely shaped paragraphs.
        If the space and the nbspace are not the same width, it breaks the text
        composition of documents.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3843",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_whitespace_widths(ttFont):
    """Space and non-breaking space have the same width?"""
    space_name = get_glyph_name(ttFont, 0x0020)
    nbsp_name = get_glyph_name(ttFont, 0x00A0)

    space_width = ttFont["hmtx"][space_name][0]
    nbsp_width = ttFont["hmtx"][nbsp_name][0]

    if space_width > 0 and space_width == nbsp_width:
        yield PASS, "Space and non-breaking space have the same width."
    else:
        yield FAIL, Message(
            "different-widths",
            "Space and non-breaking space have differing width:"
            f" The space glyph named {space_name} is {space_width} font units wide,"
            f" non-breaking space named ({nbsp_name}) is {nbsp_width} font units wide,"
            ' and both should be positive and the same. GlyphsApp has "Sidebearing'
            ' arithmetic" (https://glyphsapp.com/tutorials/spacing) which allows you to'
            " set the non-breaking space width to always equal the space width.",
        )


@check(
    id="whitespace_ink",
    rationale="""
           This check ensures that certain whitespace glyphs are empty.
           Certain text layout engines will assume that these glyphs are empty,
           and will not draw them; if they were in fact not designed to be
           empty, the result will be text layout that is not as expected.
       """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_whitespace_ink(ttFont):
    """Whitespace glyphs have ink?"""
    # This checks that certain glyphs are empty.
    # Some, but not all, are Unicode whitespace.

    # code-points for all Unicode whitespace chars
    # (according to Unicode 11.0 property list):
    WHITESPACE_CHARACTERS = {
        0x0009,
        0x000A,
        0x000B,
        0x000C,
        0x000D,
        0x0020,
        0x0085,
        0x00A0,
        0x1680,
        0x2000,
        0x2001,
        0x2002,
        0x2003,
        0x2004,
        0x2005,
        0x2006,
        0x2007,
        0x2008,
        0x2009,
        0x200A,
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }

    # Code-points that do not have whitespace property, but
    # should not have a drawing.
    EXTRA_NON_DRAWING = {0x180E, 0x200B, 0x2060, 0xFEFF}

    # Make the set of non drawing characters.
    # OGHAM SPACE MARK U+1680 is removed as it is
    # a whitespace that should have a drawing.
    NON_DRAWING = (WHITESPACE_CHARACTERS | EXTRA_NON_DRAWING) - {0x1680}

    passed = True
    for codepoint in sorted(NON_DRAWING):
        g = get_glyph_name(ttFont, codepoint)
        if g is not None and glyph_has_ink(ttFont, g):
            passed = False
            yield FAIL, Message(
                "has-ink",
                f"Glyph '{g}' has ink. It needs to be replaced by an empty glyph.",
            )
    if passed:
        yield PASS, "There is no whitespace glyph with ink."
