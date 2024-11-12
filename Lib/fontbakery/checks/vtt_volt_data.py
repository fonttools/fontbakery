from fontbakery.prelude import check, FAIL, PASS


# FIXME: I think these two checks ('vtt_volt_data' and 'vttclean') are very similar
#        so we may consider merging them into a single one.
@check(
    id="vtt_volt_data",
    rationale="""
        Check to make sure all the VTT source (TSI* tables) and
        VOLT stuff (TSIV and zz features & langsys records) are gone.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_vtt_volt_data(ttFont):
    """VTT or Volt Source Data must not be present."""

    VTT_HINT_TABLES = [
        "TSI0",
        "TSI1",
        "TSI2",
        "TSI3",
        "TSI5",
        "TSIC",  # cvar
    ]

    OTL_SOURCE_TABLES = [
        "TSIV",  # Volt
        "TSIP",  # GPOS
        "TSIS",  # GSUB
        "TSID",  # GDEF
        "TSIJ",  # JSTF
        "TSIB",  # BASE
    ]

    failure_found = False
    for table in VTT_HINT_TABLES + OTL_SOURCE_TABLES:
        if table in ttFont:
            failure_found = True
            yield FAIL, f"{table} table found"
        else:
            yield PASS, f"{table} table not found"

    for otlTableTag in ["GPOS", "GSUB"]:
        if otlTableTag not in ttFont:
            continue
        table = ttFont[otlTableTag].table
        for feature in table.FeatureList.FeatureRecord:
            if feature.FeatureTag[:2] == "zz":
                failure_found = True
                yield FAIL, "Volt zz feature found"
        for script in table.ScriptList.ScriptRecord:
            for langSysRec in script.Script.LangSysRecord:
                if langSysRec.LangSysTag[:2] == "zz":
                    failure_found = True
                    yield FAIL, "Volt zz langsys found"

    if not failure_found:
        yield PASS, "No VTT or Volt Source Data Found"
