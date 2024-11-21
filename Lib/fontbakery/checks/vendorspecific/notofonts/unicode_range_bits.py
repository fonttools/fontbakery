from fontbakery.prelude import check, WARN, Message
from fontbakery.constants import UNICODERANGE_DATA
from fontbakery.utils import (
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange,
    unicoderange_bit_name,
)


@check(
    id="notofonts/unicode_range_bits",
    rationale="""
        When the UnicodeRange bits on the OS/2 table are not properly set,
        some programs running on Windows may not recognize the font and use a
        system fallback font instead. For that reason, this check calculates the
        proper settings by inspecting the glyphs declared on the cmap table and
        then ensures that their corresponding ranges are enabled.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2676",
)
def check_unicode_range_bits(ttFont):
    """Ensure UnicodeRange bits are properly set."""

    expected_unicoderange = compute_unicoderange_bits(ttFont)
    difference = unicoderange(ttFont) ^ expected_unicoderange
    if difference:
        for bit in range(128):
            if difference & (1 << bit):
                range_name = unicoderange_bit_name(bit)
                num_chars = len(chars_in_range(ttFont, bit))
                range_size = sum(
                    entry[3] - entry[2] + 1 for entry in UNICODERANGE_DATA[bit]
                )
                set_unset = "1"
                if num_chars == 0:
                    set_unset = "0"
                    num_chars = "none"
                yield WARN, Message(
                    "bad-range-bit",
                    f'UnicodeRange bit {bit} "{range_name}" should be'
                    f" {set_unset} because cmap has {num_chars} of"
                    f" the {range_size} codepoints in this range.",
                )
