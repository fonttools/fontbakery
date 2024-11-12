from fontbakery.prelude import check, Message, FAIL


@check(
    id="no_mac_entries",
    rationale="""
        Mac name table entries are not needed anymore. Even Apple stopped producing
        name tables with platform 1. Please see for example the following system font:

        /System/Library/Fonts/SFCompact.ttf

        Also, Dave Opstad, who developed Apple's TrueType specifications, told
        Olli Meier a couple years ago (as of January/2022) that these entries are
        outdated and should not be produced anymore.
    """,
    proposal="https://github.com/googlefonts/gftools/issues/469",
)
def check_name_no_mac_entries(ttFont):
    """Ensure font doesn't have Mac name table entries (platform=1)."""

    for rec in ttFont["name"].names:
        if rec.platformID == 1:
            yield FAIL, Message("mac-names", f"Please remove name ID {rec.nameID}")
