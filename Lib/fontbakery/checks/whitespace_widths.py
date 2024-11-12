from fontbakery.prelude import check, Message, PASS, FAIL
from fontbakery.utils import get_glyph_name


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
