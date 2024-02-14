from fontbakery.prelude import check, Message, INFO, SKIP


@check(
    id="com.google.fonts/check/STAT/axis_order",
    rationale="""
        This is (for now) a merely informative check to detect what's the axis ordering
        declared on the STAT table of fonts in the Google Fonts collection.

        We may later update this to enforce some unified axis ordering scheme,
        yet to be determined.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3049",
)
def com_google_fonts_check_STAT_axis_order(fonts):
    """Check axis ordering on the STAT table."""
    from collections import Counter
    from fontTools.ttLib import TTLibError

    no_stat = 0
    summary = []
    for font in fonts:
        try:
            ttFont = font.ttFont
            if "STAT" in ttFont:
                order = {}
                for axis in ttFont["STAT"].table.DesignAxisRecord.Axis:
                    order[axis.AxisTag] = axis.AxisOrdering

                summary.append("-".join(sorted(order.keys(), key=order.get)))
            else:
                no_stat += 1
                yield SKIP, Message(
                    "missing-STAT", f"This font does not have a STAT table: {font}"
                )
        except (TTLibError, AttributeError):
            yield INFO, Message("bad-font", f"Something wrong with {font}")

    if no_stat == 0:
        percentage = "None"
    elif no_stat == len(fonts):
        percentage = "All"
    else:
        percentage = f"{100.0*no_stat/len(fonts):.2f}%"

    msg = f"{percentage} of the fonts lack a STAT table.\n"

    if len(Counter(summary).most_common()) > 0:
        report = "\n\t".join(map(str, Counter(summary).most_common()))
        msg += (
            f"\n"
            f"\tAnd these are the most common STAT axis orderings:\n"
            f"\t{report}"
        )

    yield INFO, Message("summary", msg)
