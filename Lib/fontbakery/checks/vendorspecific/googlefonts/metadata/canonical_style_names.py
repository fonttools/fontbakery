from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="googlefonts/metadata/canonical_style_names",
    conditions=["font_metadata"],
    rationale="""
        If the style is set to 'normal' in the METADATA.pb file, we expect a
        non-italic font - i.e. the font's macStyle bit 1 should be set to 0,
        and the font's fullname should not end with "Italic"; similarly if
        the style is set to 'italic', we expect a font with the macStyle bit 1
        set to 1, and the font's fullname ending with "Italic". If this is
        not the case, it can indicate an italic font was incorrectly marked
        as 'normal' in the METADATA.pb file or vice versa.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_canonical_style_names(font, font_metadata):
    """METADATA.pb: Font styles are named canonically?"""
    if font_metadata.style not in ["italic", "normal"]:
        yield SKIP, (
            "This check only applies to font styles declared"
            ' as "italic" or "normal" on METADATA.pb.'
        )
    else:
        if font.is_italic and font_metadata.style != "italic":
            yield FAIL, Message(
                "italic",
                f'The font style is "{font_metadata.style}" but it should be "italic".',
            )
        elif not font.is_italic and font_metadata.style != "normal":
            yield FAIL, Message(
                "normal",
                f'The font style is "{font_metadata.style}" but it should be "normal".',
            )
