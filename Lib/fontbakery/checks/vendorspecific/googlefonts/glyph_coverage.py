from fontbakery.prelude import check, Message, FAIL, SKIP
from fontbakery.utils import (
    bullet_list,
    is_icon_font,
)


@check(
    id="googlefonts/glyph_coverage",
    conditions=["font_codepoints"],
    rationale="""
        Google Fonts expects that fonts in its collection support at least the minimal
        set of characters defined in the `GF-latin-core` glyph-set.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2488",
)
def check_glyph_coverage(ttFont, family_metadata, config):
    """Check Google Fonts glyph coverage."""
    import unicodedata2
    from glyphsets import get_glyphsets_fulfilled

    if is_icon_font(ttFont, config):
        yield SKIP, "This is an icon font or a symbol font."
        return

    glyphsets_fulfilled = get_glyphsets_fulfilled(ttFont)

    # If we have a primary_script set, we only need care about Kernel
    if family_metadata and family_metadata.primary_script:
        required_glyphset = "GF_Latin_Kernel"
    else:
        required_glyphset = "GF_Latin_Core"

    if glyphsets_fulfilled[required_glyphset]["missing"]:
        missing = [
            "0x%04X (%s)\n" % (c, unicodedata2.name(chr(c)))
            for c in glyphsets_fulfilled[required_glyphset]["missing"]
        ]
        yield FAIL, Message(
            "missing-codepoints",
            f"Missing required codepoints:\n\n{bullet_list(config, missing)}",
        )
