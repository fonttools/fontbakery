from fontbakery.prelude import check, PASS, FAIL, Message


@check(
    id="notofonts/cmap/alien_codepoints",
    rationale="""
        Private Use Area codepoints and Surrogate Pairs should not be encoded.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_cmap_alien_codepoints(ttFont, config):
    """Check no PUA or Surrogate Pair codepoints encoded"""
    pua = []
    surrogate = []
    for cp in ttFont.getBestCmap().keys():
        if (
            (0xE000 <= cp <= 0xF8FF)
            or (0xF0000 <= cp <= 0xFFFFD)
            or (0x100000 <= cp <= 0x10FFFD)
        ):
            pua.append(f"0x{cp:02x}")
        if 0xD800 <= cp <= 0xDFFF:
            surrogate.append(f"0x{cp:02x}")
    if not pua and not surrogate:
        yield PASS, "No alien codepoints were encoded"
        return

    from fontbakery.utils import pretty_print_list

    if pua:
        yield FAIL, Message(
            "pua-encoded",
            "The following private use area codepoints were"
            " encoded in the font: " + pretty_print_list(config, pua),
        )
    if surrogate:
        yield FAIL, Message(
            "surrogate-encoded",
            "The following surrogate pair codepoints were"
            " encoded in the font: " + pretty_print_list(config, surrogate),
        )
