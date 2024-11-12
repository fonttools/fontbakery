from fontbakery.prelude import check, WARN, FAIL, SKIP, Message


@check(
    id="cmap/format_12",
    rationale="""
        If a format 12 cmap table is used to address codepoints beyond the BMP,
        it should actually contain such codepoints. Additionally, it should also
        contain all characters mapped in the format 4 subtable.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_cmap_format_12(ttFont, config):
    """Check that format 12 cmap subtables are correctly constituted."""
    skipped = True
    # Find the format 4
    cmap4 = None
    for table in ttFont["cmap"].tables:
        if table.format == 4:
            cmap4 = table
            break

    if not cmap4:
        yield FAIL, Message(
            "no-cmap-4", "The font did not contain a format 4 cmap table"
        )
        return

    for subtable in ttFont["cmap"].tables:
        if subtable.format != 12:
            continue
        skipped = False
        codepoints = subtable.cmap.keys()
        if not any(cp > 0x0FFF for cp in codepoints):
            yield FAIL, Message(
                "pointless-format-12",
                "A format 12 subtable did not contain"
                " any codepoints beyond the Basic Multilingual Plane (BMP)",
            )

        unmapped_from_4 = set(cmap4.cmap.keys()) - set(codepoints)
        if unmapped_from_4:
            from fontbakery.utils import pretty_print_list

            yield WARN, Message(
                "unmapped-from-4",
                f"A format 12 subtable did not the following codepoints"
                f" mapped in the format 4 subtable:"
                f" {pretty_print_list(config, unmapped_from_4)}",
            )

    if skipped:
        yield SKIP, "No format 12 subtables found"
