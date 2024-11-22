import unicodedata

from fontbakery.prelude import check, Message, PASS, FAIL
from fontbakery.utils import bullet_list


@check(
    id="typenetwork/marks_width",
    rationale="""
        To avoid incorrect overlappings when typing, glyphs that are spacing marks
        must have width, on the other hand, combining marks should be 0 width.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_marks_width(ttFont, config):
    """Check if marks glyphs have the correct width."""

    def _is_non_spacing_mark_char(charcode):
        category = unicodedata.category(chr(charcode))
        if category in ("Mn", "Me"):
            return True

    def _is_spacing_mark_char(charcode):
        category = unicodedata.category(chr(charcode))
        if category in ("Sk", "Lm"):
            return True

    cmap = ttFont["cmap"].getBestCmap()
    glyphSet = ttFont.getGlyphSet()

    failed_non_spacing_mark_chars = []
    failed_spacing_mark_chars = []

    for charcode, glypname in cmap.items():
        if _is_non_spacing_mark_char(charcode):
            if glyphSet[glypname].width != 0:
                failed_non_spacing_mark_chars.append(glypname)

        if _is_spacing_mark_char(charcode):
            if glyphSet[glypname].width == 0:
                failed_spacing_mark_chars.append(glypname)

    if failed_non_spacing_mark_chars:
        yield FAIL, Message(
            "non-spacing-not-zero",
            f"Combining accents with width advance width:\n\n"
            f"{bullet_list(config, failed_non_spacing_mark_chars)}",
        )

    if failed_spacing_mark_chars:
        yield FAIL, Message(
            "non-spacing-not-zero",
            f"Spacing marks without advance width:\n\n"
            f"{bullet_list(config, failed_spacing_mark_chars)}",
        )

    if not failed_non_spacing_mark_chars and not failed_spacing_mark_chars:
        yield PASS, "Marks have correct widths."
