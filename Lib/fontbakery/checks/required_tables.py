from fontbakery.prelude import check, Message, FAIL, INFO, PASS
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
