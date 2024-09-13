from fontbakery.prelude import check, Message, WARN, FAIL, INFO, PASS
from fontbakery.utils import bullet_list


@check(
    id="required_tables",
    conditions=["ttFont"],
    rationale="""
        According to the OpenType spec
        https://docs.microsoft.com/en-us/typography/opentype/spec/otff#required-tables

        Whether TrueType or CFF outlines are used in an OpenType font, the following
        tables are required for the font to function correctly:

        - cmap (Character to glyph mapping)⏎
        - head (Font header)⏎
        - hhea (Horizontal header)⏎
        - hmtx (Horizontal metrics)⏎
        - maxp (Maximum profile)⏎
        - name (Naming table)⏎
        - OS/2 (OS/2 and Windows specific metrics)⏎
        - post (PostScript information)

        The spec also documents that variable fonts require the following table:

        - STAT (Style attributes)

        Depending on the typeface and coverage of a font, certain tables are
        recommended for optimum quality.

        For example:⏎
        - the performance of a non-linear font is improved if the VDMX, LTSH,
          and hdmx tables are present.⏎
        - Non-monospaced Latin fonts should have a kern table.⏎
        - A gasp table is necessary if a designer wants to influence the sizes
          at which grayscaling is used under Windows. Etc.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_required_tables(ttFont, config, is_variable_font):
    """Font contains all required tables?"""
    REQUIRED_TABLES = ["cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post"]

    OPTIONAL_TABLES = [
        "cvt ",
        "fpgm",
        "loca",
        "prep",
        "VORG",
        "EBDT",
        "EBLC",
        "EBSC",
        "BASE",
        "GPOS",
        "GSUB",
        "JSTF",
        "gasp",
        "hdmx",
        "LTSH",
        "PCLT",
        "VDMX",
        "vhea",
        "vmtx",
        "kern",
    ]

    # See https://github.com/fonttools/fontbakery/issues/617
    #
    # We should collect the rationale behind the need for each of the
    # required tables above. Perhaps split it into individual checks
    # with the correspondent rationales for each subset of required tables.
    #
    # The `opentype/kern_table` check is a good example of a separate
    # check for a specific table providing a detailed description of
    # the rationale behind it.

    font_tables = ttFont.keys()

    optional_tables = [opt for opt in OPTIONAL_TABLES if opt in font_tables]
    if optional_tables:
        yield INFO, Message(
            "optional-tables",
            "This font contains the following optional tables:\n\n"
            f"{bullet_list(config, optional_tables)}",
        )

    if is_variable_font:
        # According to https://github.com/fonttools/fontbakery/issues/1671
        # STAT table is required on WebKit on MacOS 10.12 for variable fonts.
        REQUIRED_TABLES.append("STAT")

    missing_tables = [req for req in REQUIRED_TABLES if req not in font_tables]

    # Note (from the OpenType spec):
    # OpenType fonts that contain TrueType outlines should use the value of 0x00010000
    # for sfntVersion. OpenType fonts containing CFF data (version 1 or 2) should use
    # 0x4F54544F ('OTTO', when re-interpreted as a Tag) for sfntVersion.
    if ttFont.sfntVersion == "OTTO" and (
        "CFF " not in font_tables and "CFF2" not in font_tables
    ):
        if "fvar" in font_tables:
            missing_tables.append("CFF2")
        else:
            missing_tables.append("CFF ")

    elif ttFont.sfntVersion == "\x00\x01\x00\x00" and "glyf" not in font_tables:
        missing_tables.append("glyf")

    if missing_tables:
        yield FAIL, Message(
            "required-tables",
            "This font is missing the following required tables:\n\n"
            f"{bullet_list(config, missing_tables)}",
        )
    else:
        yield PASS, "Font contains all required tables."


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
        "FFTM": "Table contains redundant FontForge timestamp info",
        "TTFA": "Redundant TTFAutohint table",
        "TSI0": "Table contains data only used in VTT",
        "TSI1": "Table contains data only used in VTT",
        "TSI2": "Table contains data only used in VTT",
        "TSI3": "Table contains data only used in VTT",
        "TSI5": "Table contains data only used in VTT",
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
def check_aat(ttFont):
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


@check(
    id="no_debugging_tables",
    rationale="""
        Tables such as `Debg` are useful in the pre-production stages of font
        development, but add unnecessary bloat to a production font and should
        be removed before release.
    """,
    severity=6,
    proposal="https://github.com/fonttools/fontbakery/issues/3357",
)
def check_no_debugging_tables(ttFont):
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
