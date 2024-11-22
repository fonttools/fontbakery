from fontbakery.prelude import check, Message, FAIL


@check(
    id="adobefonts/unsupported_tables",
    rationale="""
        Adobe Fonts' font-processing pipeline does not support all kinds of tables
        that can be included in OpenType font files.⏎
        Fonts that do not pass this check are guaranteed to be rejected by the pipeline.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3870",
)
def check_unsupported_tables(ttFont):
    """Does the font have any unsupported tables?"""
    SUPPORTED_TABLES = {
        "avar",
        "BASE",
        "CFF ",
        "CFF2",
        "cmap",
        "cvar",
        "cvt ",
        "DSIG",
        "feat",
        "fpgm",
        "fvar",
        "gasp",
        "GDEF",
        "glyf",
        "GPOS",
        "GSUB",
        "gvar",
        "hdmx",
        "head",
        "hhea",
        "hmtx",
        "HVAR",
        "kern",
        "loca",
        "LTSH",
        "maxp",
        "meta",
        "morx",
        "MVAR",
        "name",
        "OS/2",
        "PCLT",
        "post",
        "prep",
        "STAT",
        "SVG ",
        "VDMX",
        "vhea",
        "vmtx",
        "VORG",
        "VVAR",
    }
    font_tables = set(ttFont.keys())
    font_tables.discard("GlyphOrder")  # pseudo-table created by FontTools
    unsupported_tables = sorted(font_tables - SUPPORTED_TABLES)

    if unsupported_tables:
        unsupported_list = "".join(f"* {tag}\n" for tag in unsupported_tables)
        yield FAIL, Message(
            "unsupported-tables",
            f"The following unsupported font tables were found:\n\n{unsupported_list}",
        )
