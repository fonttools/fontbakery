import math

from fontbakery.prelude import check, FAIL, SKIP, Message
from fontbakery.utils import get_advance_width_for_char


@check(
    id="notofonts/hmtx/whitespace_advances",
    rationale="""
        Encoded whitespace in Noto fonts should have well-defined advance widths.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_htmx_whitespace_advances(ttFont, config, glyph_metrics_stats):
    """Check all whitespace glyphs have correct advances"""

    problems = []
    if glyph_metrics_stats["seems_monospaced"]:
        yield SKIP, "Monospace glyph widths handled in other checks"
        return

    space_width = get_advance_width_for_char(ttFont, " ")
    period_width = get_advance_width_for_char(ttFont, ".")
    digit_width = get_advance_width_for_char(ttFont, "0")
    em_width = ttFont["head"].unitsPerEm
    expectations = {
        0x0009: space_width,  # tab
        0x00A0: space_width,  # nbsp
        0x2000: em_width / 2,
        0x2001: em_width,
        0x2002: em_width / 2,
        0x2003: em_width,
        0x2004: em_width / 3,
        0x2005: em_width / 4,
        0x2006: em_width / 6,
        0x2007: digit_width,
        0x2008: period_width,
        0x2009: (em_width / 6, em_width / 5),
        0x200A: (em_width / 16, em_width / 10),
        0x200B: 0,
    }
    for cp, expected_width in expectations.items():
        got_width = get_advance_width_for_char(ttFont, chr(cp))
        if got_width is None:
            continue
        if isinstance(expected_width, tuple):
            if got_width < math.floor(expected_width[0]) or got_width > math.ceil(
                expected_width[1]
            ):
                problems.append(
                    f"0x{cp:02x} (got={got_width},"
                    f" expected={expected_width[0]}...{expected_width[1]}"
                )
        else:
            if got_width != round(expected_width):
                problems.append(
                    f"0x{cp:02x} (got={got_width}, expected={expected_width}"
                )

    if problems:
        from fontbakery.utils import pretty_print_list

        formatted_list = "\t* " + pretty_print_list(config, problems, sep="\n\t* ")
        yield FAIL, Message(
            "bad-whitespace-advances",
            f"The following glyphs had wrong advance widths:\n{formatted_list}",
        )
