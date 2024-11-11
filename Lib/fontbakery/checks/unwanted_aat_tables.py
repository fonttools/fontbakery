from fontbakery.prelude import check, Message, FAIL


@check(
    id="unwanted_aat_tables",
    rationale="""
        Apple's TrueType reference manual [1] describes SFNT tables not in the
        Microsoft OpenType specification [2] and these can sometimes sneak into final
        release files.

        This check ensures fonts only have OpenType tables.

        [1] https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html
        [2] https://docs.microsoft.com/en-us/typography/opentype/spec/
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2190",
)
def check_unwanted_aat_tables(ttFont):
    """Are there unwanted Apple tables?"""
    UNWANTED_TABLES = {
        "acnt",
        "ankr",
        "bdat",
        "bhed",
        "bloc",
        "bmap",
        "bsln",
        "EBSC",
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
        "Zaph",
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
            f" they're built with:\n\n"
            f" {unwanted_list}",
        )
