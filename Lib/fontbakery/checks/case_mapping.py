import unicodedata

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import markdown_table


@check(
    id="case_mapping",
    rationale="""
        Ensure that no glyph lacks its corresponding upper or lower counterpart
        (but only when unicode supports case-mapping).
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3230",
    severity=10,  # if a font shows tofu in caps but not in lowercase
    #               then it can be considered broken.
)
def check_case_mapping(ttFont):
    """Ensure the font supports case swapping for all its glyphs."""

    # These are a selection of codepoints for which the corresponding case-swap
    # glyphs are missing way too often on the Google Fonts library,
    # so we'll ignore for now:
    EXCEPTIONS = [
        0x0192,  # ƒ - Latin Small Letter F with Hook
        0x00B5,  # µ - Micro Sign
        0x03C0,  # π - Greek Small Letter Pi
        0x2126,  # Ω - Ohm Sign
        0x03BC,  # μ - Greek Small Letter Mu
        0x03A9,  # Ω - Greek Capital Letter Omega
        0x0394,  # Δ - Greek Capital Letter Delta
        0x0251,  # ɑ - Latin Small Letter Alpha
        0x0261,  # ɡ - Latin Small Letter Script G
        0x00FF,  # ÿ - Latin Small Letter Y with Diaeresis
        0x0250,  # ɐ - Latin Small Letter Turned A
        0x025C,  # ɜ - Latin Small Letter Reversed Open E
        0x0252,  # ɒ - Latin Small Letter Turned Alpha
        0x0271,  # ɱ - Latin Small Letter M with Hook
        0x0282,  # ʂ - Latin Small Letter S with Hook
        0x029E,  # ʞ - Latin Small Letter Turned K
        0x0287,  # ʇ - Latin Small Letter Turned T
        0x0127,  # ħ - Latin Small Letter H with Stroke
        0x0140,  # ŀ - Latin Small Letter L with Middle Dot
        0x023F,  # ȿ - Latin Small Letter S with Swash Tail
        0x0240,  # ɀ - Latin Small Letter Z with Swash Tail
        0x026B,  # ɫ - Latin Small Letter L with Middle Tilde
    ]

    missing_counterparts_table = []
    cmap = ttFont["cmap"].getBestCmap()
    for codepoint in cmap:
        if codepoint in EXCEPTIONS:
            continue

        # Only check letters
        if unicodedata.category(chr(codepoint))[0] != "L":
            continue

        the_char = chr(codepoint)
        swapped = the_char.swapcase()

        # skip cases like 'ß' => 'SS'
        if len(swapped) > 1:
            continue

        if the_char != swapped and ord(swapped) not in cmap:
            name = unicodedata.name(the_char)
            swapped_name = unicodedata.name(swapped)
            row = {
                "Glyph present in the font": f"U+{codepoint:04X}: {name}",
                "Missing case-swapping counterpart": (
                    f"U+{ord(swapped):04X}: {swapped_name}"
                ),
            }
            missing_counterparts_table.append(row)

    if missing_counterparts_table:
        yield FAIL, Message(
            "missing-case-counterparts",
            f"The following glyphs lack their case-swapping counterparts:\n\n"
            f"{markdown_table(missing_counterparts_table)}\n\n",
        )
