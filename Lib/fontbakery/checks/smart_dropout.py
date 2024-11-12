from fontbakery.prelude import check, Message, FAIL


@check(
    id="smart_dropout",
    conditions=["is_ttf", "not VTT_hinted"],
    rationale="""
        This setup is meant to ensure consistent rendering quality for fonts across
        all devices (with different rendering/hinting capabilities).

        Below is the snippet of instructions we expect to see in the fonts:
        B8 01 FF    PUSHW 0x01FF
        85          SCANCTRL (unconditinally turn on
                              dropout control mode)
        B0 04       PUSHB 0x04
        8D          SCANTYPE (enable smart dropout control)

        "Smart dropout control" means activating rules 1, 2 and 5:
        Rule 1: If a pixel's center falls within the glyph outline,
                that pixel is turned on.
        Rule 2: If a contour falls exactly on a pixel's center,
                that pixel is turned on.
        Rule 5: If a scan line between two adjacent pixel centers
                (either vertical or horizontal) is intersected
                by both an on-Transition contour and an off-Transition
                contour and neither of the pixels was already turned on
                by rules 1 and 2, turn on the pixel which is closer to
                the midpoint between the on-Transition contour and
                off-Transition contour. This is "Smart" dropout control.

        For more detailed info (such as other rules not enabled in this snippet),
        please refer to the TrueType Instruction Set documentation.

        Generally this occurs with unhinted fonts; if you are not using autohinting,
        use gftools-fix-nonhinting (or just gftools-fix-font) to fix this issue.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_smart_dropout(ttFont):
    """Ensure smart dropout control is enabled in "prep" table instructions."""
    INSTRUCTIONS = b"\xb8\x01\xff\x85\xb0\x04\x8d"

    if not ("prep" in ttFont and INSTRUCTIONS in ttFont["prep"].program.getBytecode()):
        yield FAIL, Message(
            "lacks-smart-dropout",
            "The 'prep' table does not contain TrueType"
            " instructions enabling smart dropout control."
            " To fix, export the font with autohinting enabled,"
            " or run ttfautohint on the font, or run the"
            " `gftools fix-nonhinting` script.",
        )
