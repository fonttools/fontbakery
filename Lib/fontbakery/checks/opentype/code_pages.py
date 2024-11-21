from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/code_pages",
    rationale="""
        At least some programs (such as Word and Sublime Text) under Windows 7
        do not recognize fonts unless code page bits are properly set on the
        ulCodePageRange1 (and/or ulCodePageRange2) fields of the OS/2 table.

        More specifically, the fonts are selectable in the font menu, but whichever
        Windows API these applications use considers them unsuitable for any
        character set, so anything set in these fonts is rendered with Arial as a
        fallback font.

        This check currently does not identify which code pages should be set.
        Auto-detecting coverage is not trivial since the OpenType specification
        leaves the interpretation of whether a given code page is "functional"
        or not open to the font developer to decide.

        So here we simply detect as a FAIL when a given font has no code page
        declared at all.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2474",
)
def check_code_pages(ttFont):
    """Check code page character ranges"""

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "The required OS/2 table is missing.")
        return

    if (
        not hasattr(ttFont["OS/2"], "ulCodePageRange1")
        or not hasattr(ttFont["OS/2"], "ulCodePageRange2")
        or (
            ttFont["OS/2"].ulCodePageRange1 == 0
            and ttFont["OS/2"].ulCodePageRange2 == 0
        )
    ):
        yield FAIL, Message(
            "no-code-pages",
            "No code pages defined in the OS/2 table"
            " ulCodePageRange1 and CodePageRange2 fields.",
        )
