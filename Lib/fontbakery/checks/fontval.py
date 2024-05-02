from pathlib import Path
import tempfile

from fontbakery.prelude import check, ERROR, FAIL, INFO, PASS, WARN, Message
from fontbakery.utils import exit_with_install_instructions


@check(
    id="com.google.fonts/check/fontvalidator",
    proposal="legacy:check/037",
    rationale="""
        Microsoft Font Validator is a tool that can be used to check for
        various problems with a font file. Fonts which report errors in
        Microsoft Font Validator are likely to have problems in Microsoft
        Windows applications. This check runs Microsoft Font Validator
        on the font and reports any errors or warnings that it finds.
    """,
)
def com_google_fonts_check_fontvalidator(font, config):
    """Checking with Microsoft Font Validator."""

    try:
        import lxml.etree
    except ImportError:
        exit_with_install_instructions("fontval")

    check_config = config.get("com.google.fonts/check/fontvalidator", {})
    enabled_checks = check_config.get("enabled_checks")
    disabled_checks = check_config.get("disabled_checks")
    if enabled_checks is not None and disabled_checks is not None:
        raise Exception(
            "The check config must contain either enabled_checks or "
            "disabled_checks, but not both."
        )

    # In some cases we want to override the severity level of
    # certain checks in FontValidator:
    downgrade_to_warn = [
        # FIX-ME: Why did we downgrade this one to WARN?
        "Misoriented contour"
    ]

    # Some other checks we want to completely disable:
    disabled_fval_checks = [
        # FontVal E4012 thinks that
        # "Versions 0x00010000 and 0x0001002 are currently
        #  the only defined versions of the GDEF table."
        # but the GDEF chapter of the OpenType specification at
        # https://docs.microsoft.com/en-us/typography/opentype/spec/gdef
        # describes GDEF header version 1.3, which is not yet recognized
        # by FontVal, thus resulting in this spurious false-FAIL:
        "The version number is neither 0x00010000 nor 0x0001002",
        # No software is affected by Mac strings nowadays.
        # More info at: googlei18n/fontmake#414
        "The table doesn't contain strings for Mac platform",
        "The PostScript string is not present for both required platforms",
        # FontBakery has got a native check for the xAvgCharWidth field
        # which is: com.google.fonts/check/xavgcharwidth
        "The xAvgCharWidth field does not equal the calculated value",
        # The optimal ordering suggested by FVal check W0020 seems to only be
        # relevant to performance optimizations on old versions of Windows
        # running on old hardware. Since such performance considerations
        # are most likely negligible, we're not going to bother users with
        # this check's table ordering requirements.
        # More info at:
        # https://github.com/fonttools/fontbakery/issues/2105
        "Tables are not in optimal order",
        # FontBakery has its own check for required/optional tables:
        # com.google.fonts/check/required_tables
        "Recommended table is missing",
        # Check W5300 does not recognise some tags in use, e.g. stylistic sets
        # tagged `ssXX` (where XX is the number). This warning has been reported
        # to HinTak here: https://github.com/HinTak/Font-Validator/issues/41
        "The FeatureRecord tag is valid, but unregistered",
        # Check E5400: field now called featureParamsOffset and can be null.
        # This error has been reported to HinTak by Khaled Hosny here:
        # https://github.com/HinTak/Font-Validator/issues/34.
        "The FeatureParams field is not null",
        # Check E5700: Lookup flags more recently used by the pipeline are not
        # recognized by Font Validator and therefore it flags that they are in a
        # reserved bit. This error has been reported to HinTak by Khaled Hosny
        # here: https://github.com/HinTak/Font-Validator/issues/34.
        "The LookupFlag reserved bits are not all set to zero.",
        # Check E4100: We expect this error due to the new way fontmake compiles
        # anchors. See this bug report on the FontValidator side:
        # https://github.com/HinTak/Font-Validator/issues/59
        "The AnchorFormat field is invalid",
        # Check E2101: Complains about the USE_TYPO_METRICS bit. See
        # https://github.com/HinTak/Font-Validator/issues/34.
        "There are undefined bits set in fsSelection field",
        # Unless there is a Microsoft Symbol subtable in the CMAP table, Font
        # Validator will check Microsoft Unicode/Apple subtables for the
        # presence of the euro character. This does not consider the glyph set
        # of the font, and so will raise a warning in fonts that purposely do
        # not contain the euro.
        "Character code U+20AC, the euro character, is not mapped in cmap 3,1",
        # FontBakery has its own check for this.
        "The unitsPerEm value is not a power of two",
        # Actually not a problem, and being produced by ufo2ft for years.
        "Intersecting components of composite glyph",
        # OS/2 table version: Yeah, and?
        "The version number is valid, but less than 5",
        # W1900: FontVal computes maxp.maxSizeOfInstructions and
        # maxComponentDepth differently from fontTools
        "maxSizeOfInstructions computation not via either approved method",
        # E1900: FontValidator calculates the wrong maxp.maxComponentDepth. This
        # issue has been reported on the FontValidator side:
        # https://github.com/microsoft/Font-Validator/issues/62
        "The value doesn't match the calculated value",
    ]

    # There are also some checks that do not make
    # sense when we're dealing with variable fonts:
    VARFONT_disabled_fval_checks = [
        # Variable fonts typically do have lots of self-intersecting
        # contours because they are used to draw each portion
        # of variable glyph features.
        "Intersecting contours",
        # DeltaFormat = 32768 (same as 0x8000) means VARIATION_INDEX, according to
        # https://docs.microsoft.com/en-us/typography/opentype/spec/chapter2
        # The FontVal problem description for this check (E5200) only mentions
        # the other values as possible valid ones. So apparently this means FontVal
        # implementation is not up-to-date with more recent versions of the OpenType
        # spec and that's why these spurious FAILs are being emitted.
        # That's good enough reason to mute it.
        # More info at:
        # https://github.com/fonttools/fontbakery/issues/2109
        "The device table's DeltaFormat value is invalid",
    ]

    CFF_disabled_fval_checks = [
        # We expect this warning for static OTFs, since they store glyph names in
        # the CFF table instead of the post table.
        "Apple recommends against using post table format 3 under most circumstances",
    ]

    ttFont = font.ttFont
    if "fvar" in ttFont:
        disabled_fval_checks.extend(VARFONT_disabled_fval_checks)

    if "CFF" in ttFont:
        disabled_fval_checks.extend(CFF_disabled_fval_checks)

    if disabled_checks is not None:
        disabled_fval_checks = disabled_checks

    report_dir = tempfile.TemporaryDirectory(prefix="fontval-")
    import subprocess

    try:
        fval_cmd = [
            "FontValidator",
            "-file",
            font.file,
            "-all-tables",
            "-report-dir",
            report_dir.name,
            "-no-raster-tests",
        ]
        subprocess.check_output(fval_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # Filter uninteresting progress reports.
        filtered_output = [
            msg
            for msg in e.output.decode().splitlines()
            if not msg.startswith(
                ("Table Test:", "Progress: Validating glyph with index")
            )
        ]
        yield INFO, Message(
            "fontval-returned-error",
            (
                "Microsoft Font Validator returned an error code."
                " Output follows :\n\n{}\n"
            ).format("\n".join(filtered_output)),
        )
    except (OSError, IOError) as error:
        yield ERROR, Message(
            "fontval-not-available",
            "Mono runtime and/or Microsoft Font Validator are not available!",
        )
        raise error

    def report_message(msg, details):
        if details:
            if isinstance(details, list) and len(details) > 1:
                # We'll print lists with one item per line for
                # improved readability.
                if None in details:
                    details.remove(None)

                # A designer will likely not need the full list
                # in order to fix a problem.
                # Showing only the 10 first ones is more than enough
                # and helps avoid flooding the report.
                if len(details) > 25:
                    num_similar = len(details) - 10
                    details = details[:10]
                    details.append(
                        f"NOTE: {num_similar} other similar" " results were hidden!"
                    )
                details = "\n\t- " + "\n\t- ".join(details)
            return f"MS-FonVal: {msg} DETAILS: {details}"
        else:
            return f"MS-FonVal: {msg}"

    report_file = Path(report_dir.name) / f"{Path(font.file).name}.report.xml"

    grouped_msgs = {}
    with open(report_file, "rb") as xml_report:
        doc = lxml.etree.fromstring(xml_report.read())
        for report in doc.iterfind(".//Report"):
            msg = report.get("Message")
            details = report.get("Details")

            disable_it = False
            if enabled_checks is not None:
                if not any(substring in msg for substring in enabled_checks):
                    disable_it = True
            else:
                if any(substring in msg for substring in disabled_fval_checks):
                    disable_it = True
            if disable_it:
                continue

            if msg not in grouped_msgs:
                grouped_msgs[msg] = {
                    "errortype": report.get("ErrorType"),
                    "details": [details],
                }
            else:
                if details not in grouped_msgs[msg]["details"]:
                    # avoid cluttering the output with tons of identical reports
                    # yield INFO, 'grouped_msgs[msg]["details"]: {}'.format(
                    # grouped_msgs[msg]["details"])
                    grouped_msgs[msg]["details"].append(details)

    # ---------------------------
    # Here we start emitting the grouped log messages
    for msg, data in grouped_msgs.items():
        # But before printing we try to make the "details" more
        # readable. Otherwise the user would get the text terminal
        # flooded with messy data.

        # No need to print is as a list if wereally only
        # got one log message of this kind:
        if len(data["details"]) == 1:
            data["details"] = data["details"][0]

        # Simplify the list of glyph indices by only displaying
        # their numerical values in a list:
        for glyph_index in ["Glyph index ", "glyph# "]:
            if (
                data["details"]
                and data["details"][0]
                and glyph_index in data["details"][0]
            ):
                try:
                    data["details"] = {
                        "Glyph index": [
                            int(x.split(glyph_index)[1]) for x in data["details"]
                        ]
                    }
                    break
                except ValueError:
                    pass

        # And, finally, the log messages are emitted:
        if data["errortype"] == "P":
            yield PASS, report_message(msg, data["details"])

        elif data["errortype"] == "E":
            status = FAIL
            for substring in downgrade_to_warn:
                if substring in msg:
                    status = WARN
            yield status, Message("fontval-error", report_message(msg, data["details"]))

        elif data["errortype"] == "W":
            yield WARN, Message("fontval-warn", report_message(msg, data["details"]))

        else:
            yield INFO, Message("fontval-info", report_message(msg, data["details"]))
