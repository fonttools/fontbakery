import os

from fontTools.ttLib import TTFont

from fontbakery.prelude import check, Message, INFO, PASS, FAIL, WARN, SKIP
from fontbakery.constants import LATEST_TTFAUTOHINT_VERSION, NameID
from fontbakery.utils import filesize_formatting
from fontbakery.testable import Font


def hinting_stats(font: Font):
    """
    Return file size differences for a hinted font compared to an dehinted version
    of same file
    """
    from io import BytesIO
    from dehinter.font import dehint
    from fontTools.subset import main as pyftsubset

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
    id="com.google.fonts/check/gasp",
    conditions=["is_ttf"],
    rationale="""
        Traditionally version 0 'gasp' tables were set so that font sizes below 8 ppem
        had no grid fitting but did have antialiasing. From 9-16 ppem, just grid
        fitting.
        And fonts above 17ppem had both antialiasing and grid fitting toggled on.
        The use of accelerated graphics cards and higher resolution screens make this
        approach obsolete. Microsoft's DirectWrite pushed this even further with much
        improved rendering built into the OS and apps.

        In this scenario it makes sense to simply toggle all 4 flags ON for all font
        sizes.
    """,
    proposal="legacy:check/062",
)
def com_google_fonts_check_gasp(ttFont):
    """Is the Grid-fitting and Scan-conversion Procedure ('gasp') table
    set to optimize rendering?"""

    NON_HINTING_MESSAGE = (
        "If you are dealing with an unhinted font,"
        " it can be fixed by running the fonts through"
        " the command 'gftools fix-nonhinting'\n"
        "GFTools is available at"
        " https://pypi.org/project/gftools/"
    )

    if "gasp" not in ttFont.keys():
        yield FAIL, Message(
            "lacks-gasp",
            "Font is missing the 'gasp' table."
            " Try exporting the font with autohinting enabled.\n" + NON_HINTING_MESSAGE,
        )
    else:
        if not isinstance(ttFont["gasp"].gaspRange, dict):
            yield FAIL, Message(
                "empty", "The 'gasp' table has no values.\n" + NON_HINTING_MESSAGE
            )
        else:
            if 0xFFFF not in ttFont["gasp"].gaspRange:
                yield WARN, Message(
                    "lacks-ffff-range",
                    "The 'gasp' table does not have an entry"
                    " that applies for all font sizes."
                    " The gaspRange value for such entry should"
                    " be set to 0xFFFF.",
                )
            else:
                gasp_meaning = {
                    0x01: "- Use grid-fitting",
                    0x02: "- Use grayscale rendering",
                    0x04: "- Use gridfitting with ClearType symmetric smoothing",
                    0x08: "- Use smoothing along multiple axes with ClearType®",
                }
                table = []
                for key in ttFont["gasp"].gaspRange.keys():
                    value = ttFont["gasp"].gaspRange[key]
                    meaning = []
                    for flag, info in gasp_meaning.items():
                        if value & flag:
                            meaning.append(info)

                    meaning = "\n\t".join(meaning)
                    table.append(f"PPM <= {key}:\n\tflag = 0x{value:02X}\n\t{meaning}")

                table = "\n".join(table)
                yield INFO, Message(
                    "ranges",
                    f"These are the ppm ranges declared on"
                    f" the gasp table:\n\n{table}\n",
                )

                for key in ttFont["gasp"].gaspRange.keys():
                    if key != 0xFFFF:
                        yield WARN, Message(
                            "non-ffff-range",
                            f"The gasp table has a range of {key}"
                            f" that may be unneccessary.",
                        )
                    else:
                        value = ttFont["gasp"].gaspRange[0xFFFF]
                        if value != 0x0F:
                            yield WARN, Message(
                                "unset-flags",
                                f"The gasp range 0xFFFF value 0x{value:02X}"
                                f" should be set to 0x0F.",
                            )


@check(
    id="com.google.fonts/check/hinting_impact",
    rationale="""
        This check is merely informative, displaying and useful comparison of filesizes
        of hinted versus unhinted font files.
    """,
    proposal="legacy:check/054",
)
def com_google_fonts_check_hinting_impact(font):
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
    id="com.google.fonts/check/has_ttfautohint_params",
    proposal="https://github.com/fonttools/fontbakery/issues/1773",
    rationale="""
        It is critically important that all static TTFs in the API which
        were autohinted with ttfautohint store their TTFAutohint args in
        the 'name' table, so that an automated solution can be made to
        replicate the hinting on subsets, etc.
    """,
)
def com_google_fonts_check_has_ttfautohint_params(ttFont):
    """Font has ttfautohint params?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(value):
        # example string:
        # 'Version 1.000; ttfautohint (v0.93) -l 8 -r 50 -G 200 -x 14 -w "G"
        import re

        results = re.search(r"ttfautohint \(v(.*)\) ([^;]*)", value)
        if results:
            return results.group(1), results.group(2)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    passed = False
    for vstring in version_strings:
        values = ttfautohint_version(vstring)
        if values:
            ttfa_version, params = values
            if params:
                passed = True
                yield PASS, Message("ok", f"Font has ttfautohint params ({params})")
        else:
            passed = True
            yield SKIP, Message(
                "not-hinted",
                "Font appears to our heuristic as not hinted using ttfautohint.",
            )

    if not passed:
        yield FAIL, Message(
            "lacks-ttfa-params",
            "Font is lacking ttfautohint params on its"
            " version strings on the name table.",
        )


@check(
    id="com.google.fonts/check/old_ttfautohint",
    conditions=["is_ttf"],
    rationale="""
        Check if font has been hinted with an outdated version of ttfautohint.
    """,
    proposal="legacy:check/056",
)
def com_google_fonts_check_old_ttfautohint(ttFont):
    """Font has old ttfautohint applied?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(values):
        import re

        for value in values:
            results = re.search(r"ttfautohint \(v(.*)\)", value)
            if results:
                return results.group(1)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    ttfa_version = ttfautohint_version(version_strings)
    if len(version_strings) == 0:
        yield FAIL, Message(
            "lacks-version-strings",
            "This font file lacks mandatory version strings in its name table.",
        )
    elif ttfa_version is None:
        yield INFO, Message(
            "version-not-detected",
            f"Could not detect which version of"
            f" ttfautohint was used in this font."
            f" It is typically specified as a comment"
            f" in the font version entries of the 'name' table."
            f" Such font version strings are currently:"
            f" {version_strings}",
        )
    else:
        try:
            if LATEST_TTFAUTOHINT_VERSION > ttfa_version:
                yield WARN, Message(
                    "old-ttfa",
                    f"ttfautohint used in font = {ttfa_version};"
                    f" latest = {LATEST_TTFAUTOHINT_VERSION};"
                    f" Need to re-run with the newer version!",
                )
        except ValueError:
            yield FAIL, Message(
                "parse-error",
                f"Failed to parse ttfautohint version values:"
                f" latest = '{LATEST_TTFAUTOHINT_VERSION}';"
                f" used_in_font = '{ttfa_version}'",
            )


@check(
    id="com.google.fonts/check/smart_dropout",
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
    proposal="legacy:check/072",
)
def com_google_fonts_check_smart_dropout(ttFont):
    """Font enables smart dropout control in "prep" table instructions?"""
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
    id="com.google.fonts/check/vttclean",
    rationale="""
        The goal here is to reduce filesizes and improve pageloading when dealing
        with webfonts.

        The VTT Talk sources are not necessary at runtime and endup being just dead
        weight when left embedded in the font binaries. The sources should be kept on
        the project files but stripped out when building release binaries.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2059",
)
def com_google_fonts_check_vtt_clean(ttFont, vtt_talk_sources):
    """There must not be VTT Talk sources in the font."""

    if vtt_talk_sources:
        yield FAIL, Message(
            "has-vtt-sources",
            f"Some tables containing VTT Talk (hinting) sources"
            f" were found in the font and should be removed in order"
            f" to reduce total filesize:"
            f" {', '.join(vtt_talk_sources)}",
        )


@check(
    id="com.google.fonts/check/integer_ppem_if_hinted",
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
def com_google_fonts_check_integer_ppem_if_hinted(ttFont):
    """PPEM must be an integer on hinted fonts."""

    if not ttFont["head"].flags & (1 << 3):
        yield FAIL, Message(
            "bad-flags",
            (
                "This is a hinted font, so it must have bit 3 set"
                " on the flags of the head table, so that"
                " PPEM values will be rounded into an integer"
                " value.\n"
                "\n"
                "This can be accomplished by using the"
                " 'gftools fix-hinting' command:\n"
                "\n"
                "```\n"
                "# create virtualenv\n"
                "python3 -m venv venv"
                "\n"
                "# activate virtualenv\n"
                "source venv/bin/activate"
                "\n"
                "# install gftools\n"
                "pip install git+https://www.github.com"
                "/googlefonts/tools\n"
                "```\n"
            ),
        )
