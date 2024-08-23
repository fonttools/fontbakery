from fontbakery.prelude import check, Message, WARN, FAIL


@check(
    id="com.google.fonts/check/aat",
    rationale="""
        Apple's TrueType reference manual [1] describes SFNT tables not in the
        Microsoft OpenType specification [2] and these can sometimes sneak into final
        release files, but Google Fonts should only have OpenType tables.

        [1] https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html
        [2] https://docs.microsoft.com/en-us/typography/opentype/spec/
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2190",
)
def com_google_fonts_check_aat(ttFont):
    """Are there unwanted Apple tables?"""
    UNWANTED_TABLES = {
        "EBSC",
        "Zaph",
        "acnt",
        "ankr",
        "bdat",
        "bhed",
        "bloc",
        "bmap",
        "bsln",
        "fdsc",
        "feat",
        "fond",
        "gcid",
        "just",
        "kerx",
        "lcar",
        "ltag",
        "mort",
        "morx",
        "opbd",
        "prop",
        "trak",
        "xref",
    }
    unwanted_tables_found = []
    for table in ttFont.keys():
        if table in UNWANTED_TABLES:
            unwanted_tables_found.append(table)

    if len(unwanted_tables_found) > 0:
        unwanted_list = "".join(f"* {tag}\n" for tag in unwanted_tables_found)
        yield FAIL, Message(
            "has-unwanted-tables",
            f"Unwanted AAT tables were found"
            f" in the font and should be removed, either by"
            f" fonttools/ttx or by editing them using the tool"
            f" they built with:\n\n"
            f" {unwanted_list}",
        )


@check(
    id="com.google.fonts/check/no_debugging_tables",
    rationale="""
        Tables such as `Debg` are useful in the pre-production stages of font
        development, but add unnecessary bloat to a production font and should
        be removed before release.
    """,
    severity=6,
    proposal="https://github.com/fonttools/fontbakery/issues/3357",
)
def com_google_fonts_check_no_debugging_tables(ttFont):
    """Ensure fonts do not contain any pre-production tables."""

    DEBUGGING_TABLES = ["Debg", "FFTM"]
    found = [t for t in DEBUGGING_TABLES if t in ttFont]
    if found:
        tables_list = ", ".join(found)
        yield WARN, Message(
            "has-debugging-tables",
            f"This font file contains the following"
            f" pre-production tables: {tables_list}",
        )
