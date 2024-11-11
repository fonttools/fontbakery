from fontbakery.prelude import check, Message, FAIL, PASS


@check(
    id="unwanted_tables",
    rationale="""
        Some font editors store source data in their own SFNT tables, and these
        can sometimes sneak into final release files, which should only have
        OpenType spec tables.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_unwanted_tables(ttFont):
    """Are there unwanted tables?"""
    UNWANTED_TABLES = {
        "DSIG": (
            "This font has a digital signature (DSIG table) which is only required"
            " - even if only a placeholder - on old programs like MS Office 2013"
            " in order to work properly.\n"
            "The current recommendation is to completely remove the DSIG table."
        ),
        "FFTM": "Table contains redundant FontForge timestamp info",
        "TTFA": "Redundant TTFAutohint table",
        "TSI0": "Table contains data only used in VTT",
        "TSI1": "Table contains data only used in VTT",
        "TSI2": "Table contains data only used in VTT",
        "TSI3": "Table contains data only used in VTT",
        "TSI5": "Table contains data only used in VTT",
        "TSIC": "Table contains data only used in VTT",
        "TSIV": "Table contains data only used in VOLT",
        "TSIP": "Table contains data only used in VOLT",
        "TSIS": "Table contains data only used in VOLT",
        "TSID": "Table contains data only used in VOLT",
        "TSIJ": "Table contains data only used in VOLT",
        "TSIB": "Table contains data only used in VOLT",
        "prop": (
            "Table used on AAT, Apple's OS X specific technology."
            " Although Harfbuzz now has optional AAT support,"
            " new fonts should not be using that."
        ),
    }
    unwanted_tables_found = []
    unwanted_tables_tags = set(UNWANTED_TABLES)
    for table in ttFont.keys():
        if table in unwanted_tables_tags:
            info = UNWANTED_TABLES[table]
            unwanted_tables_found.append(f"* {table} - {info}\n")

    if unwanted_tables_found:
        yield FAIL, Message(
            "unwanted-tables",
            "The following unwanted font tables were found:\n\n"
            f"{''.join(unwanted_tables_found)}\nThey can be removed with"
            " the 'fix-unwanted-tables' script provided by gftools.",
        )
    else:
        yield PASS, "There are no unwanted tables."
