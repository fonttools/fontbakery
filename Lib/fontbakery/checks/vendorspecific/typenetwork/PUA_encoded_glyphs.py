from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list


def in_PUA_range(codepoint):
    """
    Three private use areas are defined:
    one in the Basic Multilingual Plane (U+E000–U+F8FF),
    and one each in, and nearly covering, planes 15 and 16
    (U+F0000–U+FFFFD, U+100000–U+10FFFD).
    """
    return (
        (codepoint >= 0xE000 and codepoint <= 0xF8FF)
        or (codepoint >= 0xF0000 and codepoint <= 0xFFFFD)
        or (codepoint >= 0x100000 and codepoint <= 0x10FFFD)
    )


@check(
    id="typenetwork/PUA_encoded_glyphs",
    rationale="""
        Using Private Use Area (PUA) encodings is not recommended. They are
        defined by users and are not standardized. That said, PUA are font
        specific so they will break if the user tries to copy/paste,
        search/replace, or change the font. Using PUA to encode small caps,
        for example, is not recommended as small caps can and should be
        accessible via Open Type substitution instead.

        If you must encode your characters in the Private Use Area (PUA),
        do so with great caution.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_PUA_encoded_glyphs(ttFont, config):
    """Check if font has PUA encoded glyphs."""

    pua_encoded_glyphs = []

    for cp, glyphName in ttFont.getBestCmap().items():
        if in_PUA_range(cp) and cp != 0xF8FF:
            pua_encoded_glyphs.append(glyphName + f" U+{cp:02x}".upper())

    if pua_encoded_glyphs:
        yield WARN, Message(
            "pua-encoded",
            f"Glyphs with PUA codepoints:\n\n"
            f"{bullet_list(config, pua_encoded_glyphs)}",
        )
    else:
        yield PASS, "No PUA encoded glyphs."
