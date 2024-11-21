from fontbakery.constants import MacStyle
from fontbakery.prelude import check
from fontbakery.utils import check_bit_entry


@check(
    id="opentype/mac_style",
    rationale="""
        The values of the flags on the macStyle entry on the 'head' OpenType table
        that describe whether a font is bold and/or italic must be coherent with the
        actual style of the font as inferred by its filename.
    """,
    conditions=["style"],
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_mac_style(font):
    """Checking head.macStyle value."""

    # Checking macStyle ITALIC bit:
    expected = "Italic" in font.style
    yield check_bit_entry(
        font.ttFont,
        "head",
        "macStyle",
        expected,
        bitmask=MacStyle.ITALIC,
        bitname="ITALIC",
    )

    # Checking macStyle BOLD bit:
    expected = font.style in ["Bold", "BoldItalic"]
    yield check_bit_entry(
        font.ttFont, "head", "macStyle", expected, bitmask=MacStyle.BOLD, bitname="BOLD"
    )
