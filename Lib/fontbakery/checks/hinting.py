from fontbakery.prelude import check, Message, FAIL, INFO, PASS
from fontbakery.testable import Font
from fontbakery.utils import filesize_formatting


def hinting_stats(font: Font):
    """
    Return file size differences for a hinted font compared to an dehinted version
    of same file
    """
    import os
    from io import BytesIO
    from dehinter.font import dehint
    from fontTools.subset import main as pyftsubset
    from fontTools.ttLib import TTFont

    hinted_size = os.stat(font.file).st_size
    ttFont = TTFont(font.file)  # Use our own copy since we will dehint it

    if font.is_ttf:
        dehinted_buffer = BytesIO()
        dehint(ttFont, verbose=False)
        ttFont.save(dehinted_buffer)
        dehinted_buffer.seek(0)
        dehinted_size = len(dehinted_buffer.read())
    elif font.is_cff or font.is_cff2:
        ext = os.path.splitext(font.file)[1]
        tmp = font.file.replace(ext, "-tmp-dehinted%s" % ext)
        args = [
            font.file,
            "--no-hinting",
            "--glyphs=*",
            "--ignore-missing-glyphs",
            "--no-notdef-glyph",
            "--no-recommended-glyphs",
            "--no-layout-closure",
            "--layout-features=*",
            "--no-desubroutinize",
            "--name-languages=*",
            "--glyph-names",
            "--no-prune-unicode-ranges",
            "--output-file=%s" % tmp,
        ]
        pyftsubset(args)

        dehinted_size = os.stat(tmp).st_size
        os.remove(tmp)

    else:
        return None

    return {
        "dehinted_size": dehinted_size,
        "hinted_size": hinted_size,
    }


@check(
    id="hinting_impact",
    rationale="""
        This check is merely informative, displaying an useful comparison of filesizes
        of hinted versus unhinted font files.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_hinting_impact(font):
    """Show hinting filesize impact."""
    stats = hinting_stats(font)
    hinted = stats["hinted_size"]
    dehinted = stats["dehinted_size"]
    increase = hinted - dehinted
    change = (float(hinted) / dehinted - 1) * 100

    hinted_size = filesize_formatting(hinted)
    dehinted_size = filesize_formatting(dehinted)
    increase = filesize_formatting(increase)

    yield INFO, Message(
        "size-impact",
        f"Hinting filesize impact:\n"
        f"\n"
        f" |               | {font.file}     |\n"
        f" |:------------- | ---------------:|\n"
        f" | Dehinted Size | {dehinted_size} |\n"
        f" | Hinted Size   | {hinted_size}   |\n"
        f" | Increase      | {increase}      |\n"
        f" | Change        | {change:.1f} %  |\n",
    )


@check(
    id="smart_dropout",
    conditions=["is_ttf", "not VTT_hinted"],
    rationale="""
        This setup is meant to ensure consistent rendering quality for fonts across
        all devices (with different rendering/hinting capabilities).

        Below is the snippet of instructions we expect to see in the fonts:
        B8 01 FF    PUSHW 0x01FF
        85          SCANCTRL (unconditinally turn on
                              dropout control mode)
        B0 04       PUSHB 0x04
        8D          SCANTYPE (enable smart dropout control)

        "Smart dropout control" means activating rules 1, 2 and 5:
        Rule 1: If a pixel's center falls within the glyph outline,
                that pixel is turned on.
        Rule 2: If a contour falls exactly on a pixel's center,
                that pixel is turned on.
        Rule 5: If a scan line between two adjacent pixel centers
                (either vertical or horizontal) is intersected
                by both an on-Transition contour and an off-Transition
                contour and neither of the pixels was already turned on
                by rules 1 and 2, turn on the pixel which is closer to
                the midpoint between the on-Transition contour and
                off-Transition contour. This is "Smart" dropout control.

        For more detailed info (such as other rules not enabled in this snippet),
        please refer to the TrueType Instruction Set documentation.

        Generally this occurs with unhinted fonts; if you are not using autohinting,
        use gftools-fix-nonhinting (or just gftools-fix-font) to fix this issue.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_smart_dropout(ttFont):
    """Ensure smart dropout control is enabled in "prep" table instructions."""
    INSTRUCTIONS = b"\xb8\x01\xff\x85\xb0\x04\x8d"

    if not ("prep" in ttFont and INSTRUCTIONS in ttFont["prep"].program.getBytecode()):
        yield FAIL, Message(
            "lacks-smart-dropout",
            "The 'prep' table does not contain TrueType"
            " instructions enabling smart dropout control."
            " To fix, export the font with autohinting enabled,"
            " or run ttfautohint on the font, or run the"
            " `gftools fix-nonhinting` script.",
        )


@check(
    id="vttclean",
    rationale="""
        The goal here is to reduce filesizes and improve pageloading when dealing
        with webfonts.

        The VTT Talk sources are not necessary at runtime and endup being just dead
        weight when left embedded in the font binaries. The sources should be kept on
        the project files but stripped out when building release binaries.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2059",
)
def check_vtt_clean(ttFont, vtt_talk_sources):
    """There must not be VTT Talk sources in the font."""

    if vtt_talk_sources:
        yield FAIL, Message(
            "has-vtt-sources",
            f"Some tables containing VTT Talk (hinting) sources"
            f" were found in the font and should be removed in order"
            f" to reduce total filesize:"
            f" {', '.join(vtt_talk_sources)}",
        )


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


@check(
    id="integer_ppem_if_hinted",
    conditions=["is_hinted"],
    rationale="""
        Hinted fonts must have head table flag bit 3 set.

        Per https://docs.microsoft.com/en-us/typography/opentype/spec/head,
        bit 3 of Head::flags decides whether PPEM should be rounded. This bit should
        always be set for hinted fonts.

        Note:
        Bit 3 = Force ppem to integer values for all internal scaler math;
                May use fractional ppem sizes if this bit is clear;
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2338",
)
def check_integer_ppem_if_hinted(ttFont):
    """PPEM must be an integer on hinted fonts."""

    if not ttFont["head"].flags & (1 << 3):
        yield FAIL, Message(
            "bad-flags",
            (
                "This is a hinted font, so it must have bit 3 set on the flags of"
                " the head table, so that PPEM values will be rounded into an"
                " integer value.\n"
                "\n"
                "This can be accomplished by using the 'gftools fix-hinting' command:\n"
                "\n"
                "```\n"
                "# create virtualenv\n"
                "python3 -m venv venv"
                "\n"
                "# activate virtualenv\n"
                "source venv/bin/activate"
                "\n"
                "# install gftools\n"
                "pip install git+https://www.github.com/googlefonts/gftools\n"
                "```\n"
            ),
        )
