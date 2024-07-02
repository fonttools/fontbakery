from fontbakery.prelude import FAIL, INFO, PASS, Message, check
from fontbakery.utils import bullet_list


@check(
    id="com.google.fonts/check/required_tables",
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
    proposal="legacy:check/052",
)
def com_google_fonts_check_required_tables(ttFont, config, is_variable_font):
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
    # com.google.fonts/check/kern_table is a good example of a separate
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
    id="com.google.fonts/check/unwanted_tables",
    rationale="""
        Some font editors store source data in their own SFNT tables, and these
        can sometimes sneak into final release files, which should only have
        OpenType spec tables.
    """,
    proposal="legacy:check/053",
)
def com_google_fonts_check_unwanted_tables(ttFont):
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
