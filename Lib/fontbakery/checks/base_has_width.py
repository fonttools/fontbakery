import unicodedata

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import bullet_list, mark_glyphs


def is_space(codepoint):
    return (
        unicodedata.category(chr(codepoint))
        in [
            "Zs",  # Space Separator
            "Zl",  # Line Separator
            "Zp",  # Paragraph Separator
            "Cf",  # Format
            "Mn",  # Nonspacing Mark
            "Cc",  # Control
        ]
        or 0xE000 <= codepoint <= 0xF8FF
        or 0xF0000 <= codepoint <= 0xFFFFD
        or 0x100000 <= codepoint <= 0x10FFFD
    )


@check(
    id="base_has_width",
    rationale="""
        Base characters should have non-zero advance width.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4906",
)
def check_base_has_width(font, config):
    """Check base characters have non-zero advance width."""

    reversed_cmap = {v: k for k, v in font.ttFont.getBestCmap().items()}

    problems = []
    for gid, metric in font.ttFont["hmtx"].metrics.items():
        advance = metric[0]

        codepoint = reversed_cmap.get(gid)
        if codepoint == 0 or codepoint is None:
            continue

        if advance == 0 and gid not in mark_glyphs(font.ttFont):
            if is_space(codepoint):
                continue

            problems.append(f"{gid} (U+{codepoint:04X})")

    if problems:
        problems = bullet_list(config, problems)
        yield FAIL, Message(
            "zero-width-bases",
            f"The following glyphs had zero advance width:\n{problems}",
        )
