import unicodedata

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import bullet_list, mark_glyphs


def is_space(codepoint):
    return unicodedata.category(chr(codepoint)) in [
        "Zs",  # Space Separator
        "Zl",  # Line Separator
        "Zp",  # Paragraph Separator
        "Cf",  # Format
        "Mn",  # Nonspacing Mark
        "Cc",  # Control
    ]


@check(
    id="base_has_width",
    rationale="""
        Base characters should have non-zero advance width.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4906",
    experimental="Since 2024/12/28",
)
def check_base_has_width(font, context):
    """Check base characters have non-zero advance width."""

    reversed_cmap = {v: k for k, v in font.ttFont.getBestCmap().items()}

    problems = []
    for gid, metric in font.ttFont["hmtx"].metrics.items():
        advance = metric[0]

        codepoint = reversed_cmap.get(gid)
        if codepoint == 0 or codepoint is None:
            continue

        if advance == 0 and not gid not in mark_glyphs(font.ttFont):
            if is_space(codepoint):
                continue

            problems.append(f"{gid} (U+{codepoint:04X})")

    if problems:
        problems = bullet_list(context, problems)
        yield FAIL, Message(
            "zero-width-bases",
            f"The following glyphs had zero advance width:\n{problems}",
        )
