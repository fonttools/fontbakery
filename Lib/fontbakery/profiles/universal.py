import os

from fontbakery.status import PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.section import Section
from fontbakery.callable import condition, check, disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.opentype import OPENTYPE_PROFILE_CHECKS
from fontbakery.profiles.outline import OUTLINE_PROFILE_CHECKS
from fontbakery.profiles.shaping import SHAPING_PROFILE_CHECKS
from fontbakery.profiles.ufo_sources import UFO_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.opentype',
                   'fontbakery.profiles.outline',
                   'fontbakery.profiles.shaping',
                   'fontbakery.profiles.ufo_sources',
                   '.shared_conditions')
profile = profile_factory(default_section=Section("Universal"))

THIRDPARTY_CHECKS = [
    'com.google.fonts/check/ots',
    'com.google.fonts/check/ftxvalidator',
    'com.google.fonts/check/ftxvalidator_is_available'
]

SUPERFAMILY_CHECKS = [
    'com.google.fonts/check/superfamily/list',
    'com.google.fonts/check/superfamily/vertical_metrics',
]

UNIVERSAL_PROFILE_CHECKS = \
    OPENTYPE_PROFILE_CHECKS + \
    OUTLINE_PROFILE_CHECKS + \
    SHAPING_PROFILE_CHECKS + \
    SUPERFAMILY_CHECKS + \
    THIRDPARTY_CHECKS + \
    UFO_PROFILE_CHECKS + [
        'com.google.fonts/check/name/trailing_spaces',
        'com.google.fonts/check/family/win_ascent_and_descent',
        'com.google.fonts/check/os2_metrics_match_hhea',
        'com.google.fonts/check/fontbakery_version',
        'com.google.fonts/check/ttx-roundtrip',
        'com.google.fonts/check/family/single_directory',
        'com.google.fonts/check/mandatory_glyphs',
        'com.google.fonts/check/whitespace_glyphs',
        'com.google.fonts/check/whitespace_glyphnames',
        'com.google.fonts/check/whitespace_ink',
        'com.google.fonts/check/required_tables',
        'com.google.fonts/check/unwanted_tables',
        'com.google.fonts/check/valid_glyphnames',
        'com.google.fonts/check/unique_glyphnames',
#       'com.google.fonts/check/glyphnames_max_length',
        'com.google.fonts/check/family/vertical_metrics',
        'com.google.fonts/check/STAT_strings',
        'com.google.fonts/check/rupee'
    ]

@check(
    id = 'com.google.fonts/check/name/trailing_spaces',
    proposal = 'https://github.com/googlefonts/fontbakery/issues/2417'
)
def com_google_fonts_check_name_trailing_spaces(ttFont):
    """Name table records must not have trailing spaces."""
    failed = False
    for name_record in ttFont['name'].names:
        name_string = name_record.toUnicode()
        if name_string != name_string.strip():
            failed = True
            name_key = tuple([name_record.platformID,
                              name_record.platEncID,
                              name_record.langID,
                              name_record.nameID])
            shortened_str = name_record.toUnicode()
            if len(shortened_str) > 20:
                shortened_str = shortened_str[:10] + "[...]" + shortened_str[-10:]
            yield FAIL, \
                  Message("trailing-space",
                          f"Name table record with key = {name_key} has"
                          f" trailing spaces that must be removed:"
                          f" '{shortened_str}'")
    if not failed:
        yield PASS, ("No trailing spaces on name table entries.")


@check(
    id = 'com.google.fonts/check/family/win_ascent_and_descent',
    conditions = ['vmetrics',
                  'not is_cjk_font'],
    rationale = """
        A font's winAscent and winDescent values should be greater than the head table's yMax, abs(yMin) values. If they are less than these values, clipping can occur on Windows platforms (https://github.com/RedHatBrand/Overpass/issues/33).

        If the font includes tall/deep writing systems such as Arabic or Devanagari, the winAscent and winDescent can be greater than the yMax and abs(yMin) to accommodate vowel marks.

        When the win Metrics are significantly greater than the upm, the linespacing can appear too loose. To counteract this, enabling the OS/2 fsSelection bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 typo values instead. This means the font developer can control the linespacing with the typo values, whilst avoiding clipping by setting the win values to values greater than the yMax and abs(yMin).
    """,
    proposal = 'legacy:check/040'
)
def com_google_fonts_check_family_win_ascent_and_descent(ttFont, vmetrics):
    """Checking OS/2 usWinAscent & usWinDescent."""

    if "OS/2" not in ttFont:
        yield FAIL,\
              Message("lacks-OS/2",
                      "Font file lacks OS/2 table")
        return

    failed = False

    # OS/2 usWinAscent:
    if ttFont['OS/2'].usWinAscent < vmetrics['ymax']:
        failed = True
        yield FAIL,\
              Message("ascent",
                      f"OS/2.usWinAscent value should be"
                      f" equal or greater than {vmetrics['ymax']},"
                      f" but got {ttFont['OS/2'].usWinAscent} instead")
    if ttFont['OS/2'].usWinAscent > vmetrics['ymax'] * 2:
        failed = True
        yield FAIL,\
              Message("ascent",
                      f"OS/2.usWinAscent value"
                      f" {ttFont['OS/2'].usWinDescent} is too large."
                      f" It should be less than double the yMax."
                      f" Current yMax value is {vmetrics['ymax']}")
    # OS/2 usWinDescent:
    if ttFont['OS/2'].usWinDescent < abs(vmetrics['ymin']):
        failed = True
        yield FAIL,\
              Message("descent",
                      f"OS/2.usWinDescent value should be equal or"
                      f" greater than {abs(vmetrics['ymin'])}, but got"
                      f" {ttFont['OS/2'].usWinDescent} instead.")

    if ttFont['OS/2'].usWinDescent > abs(vmetrics['ymin']) * 2:
        failed = True
        yield FAIL,\
              Message("descent",
                      f"OS/2.usWinDescent value"
                      f" {ttFont['OS/2'].usWinDescent} is too large."
                      f" It should be less than double the yMin."
                      f" Current absolute yMin value is {abs(vmetrics['ymin'])}")
    if not failed:
        yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"


@check(
    id = 'com.google.fonts/check/os2_metrics_match_hhea',
    conditions = ['not is_cjk_font'],
    rationale = """
        OS/2 and hhea vertical metric values should match. This will produce the same linespacing on Mac, GNU+Linux and Windows.

        - Mac OS X uses the hhea values.
        - Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.

        When OS/2 and hhea vertical metrics match, the same linespacing results on macOS, GNU+Linux and Windows. Unfortunately as of 2018, Google Fonts has released many fonts with vertical metrics that don't match in this way. When we fix this issue in these existing families, we will create a visible change in line/paragraph layout for either Windows or macOS users, which will upset some of them.

        But we have a duty to fix broken stuff, and inconsistent paragraph layout is unacceptably broken when it is possible to avoid it.

        If users complain and prefer the old broken version, they have the freedom to take care of their own situation.
    """,
    proposal = 'legacy:check/042'
)
def com_google_fonts_check_os2_metrics_match_hhea(ttFont):
    """Checking OS/2 Metrics match hhea Metrics."""

    filename = os.path.basename(ttFont.reader.file.name)

    # Check both OS/2 and hhea are present.
    missing_tables = False

    required = ["OS/2", "hhea"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL,\
                  Message(f'lacks-{key}',
                          f"{filename} lacks a '{key}' table.")

    if missing_tables:
        return

    # OS/2 sTypoAscender and sTypoDescender match hhea ascent and descent
    if ttFont["OS/2"].sTypoAscender != ttFont["hhea"].ascent:
        yield FAIL,\
              Message("ascender",
                      f"OS/2 sTypoAscender ({ttFont['OS/2'].sTypoAscender})"
                      f" and hhea ascent ({ttFont['hhea'].ascent})"
                      f" must be equal.")
    elif ttFont["OS/2"].sTypoDescender != ttFont["hhea"].descent:
        yield FAIL,\
              Message("descender",
                      f"OS/2 sTypoDescender ({ttFont['OS/2'].sTypoDescender})"
                      f" and hhea descent ({ttFont['hhea'].descent})"
                      f" must be equal.")
    else:
        yield PASS, ("OS/2.sTypoAscender/Descender values"
                     " match hhea.ascent/descent.")


@check(
    id = 'com.google.fonts/check/family/single_directory',
    rationale = """
        If the set of font files passed in the command line is not all in the same directory, then we warn the user since the tool will interpret the set of files as belonging to a single family (and it is unlikely that the user would store the files from a single family spreaded in several separate directories).
    """,
    proposal = 'legacy:check/002'
)
def com_google_fonts_check_family_single_directory(fonts):
    """Checking all files are in the same directory."""

    directories = []
    for target_file in fonts:
        directory = os.path.dirname(target_file)
        if directory not in directories:
            directories.append(directory)

    if len(directories) == 1:
        yield PASS, "All files are in the same directory."
    else:
        yield FAIL, \
              Message("single-directory",
                      f"Not all fonts passed in the command line"
                      f" are in the same directory. This may lead to"
                      f" bad results as the tool will interpret all"
                      f" font files as belonging to a single"
                      f" font family. The detected directories are:"
                      f" {directories}")


@condition
def ftxvalidator_cmd():
    """ Test if `ftxvalidator` is a command; i.e. an executable with a path."""
    import shutil
    return shutil.which('ftxvalidator')


@check(
    id = 'com.google.fonts/check/ftxvalidator_is_available',
    conditions = ["fonts"],
    rationale = """
        There's no reasonable (and legal) way to run the command `ftxvalidator` of the Apple Font Tool Suite on a non-macOS machine. I.e. on GNU+Linux or Windows etc.

        If Font Bakery is not running on an OSX machine, the machine running Font Bakery could access `ftxvalidator` on OSX, e.g. via ssh or a remote procedure call (rpc).

        There's an ssh example implementation at:
        https://github.com/googlefonts/fontbakery/blob/main/prebuilt/workarounds/ftxvalidator/ssh-implementation/ftxvalidator
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/2184'
)
def com_google_fonts_check_ftxvalidator_is_available(ftxvalidator_cmd):
    """Is the command `ftxvalidator` (Apple Font Tool Suite) available?"""
    if ftxvalidator_cmd:
        yield PASS, f"ftxvalidator is available at {ftxvalidator_cmd}"
    else:
        yield WARN, \
              Message("ftxvalidator-available",
                      "Could not find ftxvalidator.")


@check(
    id = 'com.google.fonts/check/ftxvalidator',
    conditions = ['ftxvalidator_cmd'],
    proposal = 'legacy:check/035'
)
def com_google_fonts_check_ftxvalidator(font, ftxvalidator_cmd):
    """Checking with ftxvalidator."""
    import plistlib
    try:
        import subprocess
        ftx_cmd = [
            ftxvalidator_cmd,
            "-t",
            "all",  # execute all checks
            font
        ]
        # here we capture stdout and stderr separately to avoid
        # corrupting the plist data to be parsed a bit later:
        with subprocess.Popen(
            ftx_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as pipes:
            ftx_output, ftx_err = pipes.communicate()

        if len(ftx_err):
            yield WARN, \
                  Message('stderr',
                          f"stderr output from ftxvalidator:\n{ftx_err}")

        ftx_data = plistlib.loads(ftx_output)
        # we accept kATSFontTestSeverityInformation
        # and kATSFontTestSeverityMinorError
        if 'kATSFontTestSeverityFatalError' \
           not in ftx_data['kATSFontTestResultKey']:
            yield PASS, "ftxvalidator passed this file"
        else:
            ftx_cmd = [
                ftxvalidator_cmd,
                "-T",  # Human-readable output
                "-r",  # Generate a full report
                "-t",
                "all",  # execute all checks
                font
            ]
            # Here, stdout and stderr are mixed:
            ftx_output = subprocess.check_output(ftx_cmd, stderr=subprocess.STDOUT)
            yield FAIL, f"ftxvalidator output follows:\n\n{ftx_output}\n"

    except subprocess.CalledProcessError as e:
        yield ERROR, ("ftxvalidator returned an error code. Output follows:"
                      "\n\n{}\n").format(e.output.decode('utf-8'))


@check(
    id = 'com.google.fonts/check/ots',
    proposal = 'legacy:check/036'
)
def com_google_fonts_check_ots(font):
    """Checking with ots-sanitize."""
    import ots

    try:
        process = ots.sanitize(font, check=True, capture_output=True)
    except ots.CalledProcessError as e:
        yield FAIL, \
              Message("ots-sanitize-error",
                ("ots-sanitize returned an error code ({}). Output follows:\n\n{}{}"
                ).format(e.returncode, e.stderr.decode(), e.stdout.decode())
              )
    else:
        if process.stderr:
            yield WARN, \
                  Message("ots-sanitize-warn",
                          ("ots-sanitize passed this file, "
                          "however warnings were printed:\n\n{}"
                          ).format(process.stderr.decode())
                  )
        else:
            yield PASS, "ots-sanitize passed this file"


def is_up_to_date(installed, latest):
    # ignoring the development version suffix is ok
    # and is necessary for the string comparison
    # below to always yield valid results
    has_githash = ".dev" in installed
    installed = installed.split(".dev")[0]

    # Maybe the installed version is even newer than the
    # released one (such as during development on git).
    # That's what we're trying to detect here:
    installed = installed.split('.')
    latest = latest.split('.')
    for i in range(len(installed)):
        if installed[i] > latest[i]:
            return True
        if installed[i] < latest[i]:
            return False

    # Otherwise it should be identical
    # to the latest released version.
    return not has_githash


@check(
    id = 'com.google.fonts/check/fontbakery_version',
    rationale = """
        Running old versions of FontBakery can lead to a poor report which may include false WARNs and FAILs due do bugs, as well as outdated quality assurance criteria.

        Older versions will also not report problems that are detected by new checks added to the tool in more recent updates.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/2093'
)
def com_google_fonts_check_fontbakery_version():
    """Do we have the latest version of FontBakery installed?"""
    import json
    import requests
    import pip_api

    pypi_data = requests.get('https://pypi.org/pypi/fontbakery/json')
    latest = json.loads(pypi_data.content)["info"]["version"]
    installed = str(pip_api.installed_distributions()["fontbakery"].version)

    if not is_up_to_date(installed, latest):
        yield FAIL, (f"Current Font Bakery version is {installed},"
                     f" while a newer {latest} is already available."
                     f" Please upgrade it with 'pip install -U fontbakery'")
    else:
        yield PASS, "Font Bakery is up-to-date"


@check(
    id = 'com.google.fonts/check/mandatory_glyphs',
    rationale = """
        The OpenType specification v1.8.2 recommends that the first glyph is the '.notdef' glyph without a codepoint assigned and with a drawing.

        https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph

        Pre-v1.8, it was recommended that fonts should also contain 'space', 'CR' and '.null' glyphs. This might have been relevant for MacOS 9 applications.
    """,
    proposal = 'legacy:check/046'
)
def com_google_fonts_check_mandatory_glyphs(ttFont):
    """Font contains '.notdef' as its first glyph?"""
    from fontbakery.utils import glyph_has_ink

    passed = True
    if ttFont.getGlyphOrder()[0] != ".notdef":
        passed = False
        yield WARN,\
              Message('first-glyph',
                      "Font should contain the .notdef glyph as the first glyph.")

    if ".notdef" in ttFont.getBestCmap().values():
        passed = False
        yield WARN,\
              Message('codepoint',
                      f"Glyph '.notdef' should not have a Unicode codepoint value assigned,"
                      f" but got 0x{ttFont.getBestCmap().values()['.notdef']:04X}.")

    if not glyph_has_ink(ttFont, ".notdef"):
        passed = False
        yield WARN,\
              Message('empty',
                      "Glyph '.notdef' should contain a drawing, but it is empty.")

    if passed:
        yield PASS, "OK"


@check(
    id = 'com.google.fonts/check/whitespace_glyphs',
    proposal = 'legacy:check/047'
)
def com_google_fonts_check_whitespace_glyphs(ttFont, missing_whitespace_chars):
    """Font contains glyphs for whitespace characters?"""
    failed = False
    for wsc in missing_whitespace_chars:
        failed = True
        yield FAIL, Message(f"missing-whitespace-glyph-{wsc}",
                            (f"Whitespace glyph missing for codepoint {wsc}."))

    if not failed:
        yield PASS, "Font contains glyphs for whitespace characters."


@check(
    id = 'com.google.fonts/check/whitespace_glyphnames',
    conditions = ['not missing_whitespace_chars'],
    rationale = """
        This check enforces adherence to recommended whitespace (codepoints 0020 and 00A0) glyph names according to the Adobe Glyph List.
    """,
    proposal = 'legacy:check/048'
)
def com_google_fonts_check_whitespace_glyphnames(ttFont):
    """Font has **proper** whitespace glyph names?"""
    from fontbakery.utils import get_glyph_name

    # AGL recommended names, according to Adobe Glyph List for new fonts:
    AGL_RECOMMENDED_0020 = {'space'}
    AGL_RECOMMENDED_00A0 = {"uni00A0", "space"}  # "space" is in this set because some fonts
                                                 # use the same glyph for U+0020 and U+00A0
                                                 # Including it here also removes a warning
                                                 # when U+0020 is wrong, but U+00A0 is okay.

    # AGL compliant names, but not recommended for new fonts:
    AGL_COMPLIANT_BUT_NOT_RECOMMENDED_0020 = {'uni0020',
                                              'u0020',
                                              'u00020',
                                              'u000020'}
    AGL_COMPLIANT_BUT_NOT_RECOMMENDED_00A0 = {'nonbreakingspace',
                                              'nbspace',
                                              'u00A0',
                                              'u000A0',
                                              'u0000A0'}

    if ttFont['post'].formatType == 3.0:
        yield SKIP, "Font has version 3 post table."
    else:
        passed = True

        space = get_glyph_name(ttFont, 0x0020)
        if not space:
            passed = False
            yield FAIL,\
                  Message('missing-0020',
                          'Glyph 0x0020 is missing a glyph name!')

        elif space in AGL_RECOMMENDED_0020:
            pass

        elif space in AGL_COMPLIANT_BUT_NOT_RECOMMENDED_0020:
            passed = False
            yield WARN,\
                  Message('not-recommended-0020',
                          f'Glyph 0x0020 is called "{space}":'
                          f' Change to "space"')
        else:
            passed = False
            yield FAIL,\
                  Message('non-compliant-0020',
                          f'Glyph 0x0020 is called "{space}":'
                          f' Change to "space"')


        nbsp = get_glyph_name(ttFont, 0x00A0)
        if not nbsp:
            yield FAIL,\
                  Message('missing-00a0',
                          'Glyph 0x00A0 is missing a glyph name!')

        elif nbsp == space:
            # This is OK.
            # Some fonts use the same glyph for both space and nbsp.
            pass

        elif nbsp in AGL_RECOMMENDED_00A0:
            pass

        elif nbsp in AGL_COMPLIANT_BUT_NOT_RECOMMENDED_00A0:
            passed = False
            yield WARN,\
                  Message('not-recommended-00a0',
                          f'Glyph 0x00A0 is called "{nbsp}":'
                          f' Change to "uni00A0"')
        else:
            passed = False
            yield FAIL,\
                  Message('non-compliant-00a0',
                          f'Glyph 0x00A0 is called "{nbsp}":'
                          f' Change to "uni00A0"')

        if passed:
            yield PASS, "Font has **AGL recommended** names for whitespace glyphs."


@check(
    id = 'com.google.fonts/check/whitespace_ink',
    proposal = 'legacy:check/049'
)
def com_google_fonts_check_whitespace_ink(ttFont):
    """Whitespace glyphs have ink?"""
    from fontbakery.utils import (get_glyph_name,
                                  glyph_has_ink)

    # This checks that certain glyphs are empty.
    # Some, but not all, are Unicode whitespace.

    # code-points for all Unicode whitespace chars
    # (according to Unicode 11.0 property list):
    WHITESPACE_CHARACTERS = {
        0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x0020, 0x0085, 0x00A0, 0x1680,
        0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
        0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000
    }

    # Code-points that do not have whitespace property, but
    # should not have a drawing.
    EXTRA_NON_DRAWING = {
        0x180E, 0x200B, 0x2060, 0xFEFF
    }

    # Make the set of non drawing characters.
    # OGHAM SPACE MARK U+1680 is removed as it is
    # a whitespace that should have a drawing.
    NON_DRAWING = (WHITESPACE_CHARACTERS | EXTRA_NON_DRAWING) - {0x1680}

    passed = True
    for codepoint in sorted(NON_DRAWING):
        g = get_glyph_name(ttFont, codepoint)
        if g is not None and glyph_has_ink(ttFont, g):
            passed = False
            yield FAIL,\
                  Message('has-ink',
                          f'Glyph "{g}" has ink.'
                          f' It needs to be replaced by an empty glyph.')
    if passed:
        yield PASS, "There is no whitespace glyph with ink."


@check(
    id='com.google.fonts/check/required_tables',
    conditions = ['is_ttf'],
    rationale = """
        Depending on the typeface and coverage of a font, certain tables are recommended for optimum quality. For example, the performance of a non-linear font is improved if the VDMX, LTSH, and hdmx tables are present. Non-monospaced Latin fonts should have a kern table. A gasp table is necessary if a designer wants to influence the sizes at which grayscaling is used under Windows. Etc.
    """,
    # FIXME:
    # The rationale description above comes from FontValidator, check W0022.
    # We may want to improve it and/or rephrase it.
    proposal = 'legacy:check/052'
)
def com_google_fonts_check_required_tables(ttFont):
    """Font contains all required tables?"""
    from .shared_conditions import is_variable_font
    from fontbakery.utils import bullet_list

    REQUIRED_TABLES = ["cmap", "head", "hhea", "hmtx",
                       "maxp", "name", "OS/2", "post"]

    OPTIONAL_TABLES = ["cvt ", "fpgm", "loca", "prep",
                       "VORG", "EBDT", "EBLC", "EBSC",
                       "BASE", "GPOS", "GSUB", "JSTF",
                       "gasp", "hdmx", "LTSH", "PCLT",
                       "VDMX", "vhea", "vmtx", "kern"]
    # See https://github.com/googlefonts/fontbakery/issues/617
    #
    # We should collect the rationale behind the need for each of the
    # required tables above. Perhaps split it into individual checks
    # with the correspondent rationales for each subset of required tables.
    #
    # com.google.fonts/check/kern_table is a good example of a separate
    # check for a specific table providing a detailed description of
    # the rationale behind it.

    optional_tables = [opt for opt in OPTIONAL_TABLES if opt in ttFont.keys()]
    if optional_tables:
        yield INFO, \
              Message("optional-tables",
                      f"This font contains the following optional tables:\n"
                      f"{bullet_list(optional_tables)}")

    if is_variable_font(ttFont):
        # According to https://github.com/googlefonts/fontbakery/issues/1671
        # STAT table is required on WebKit on MacOS 10.12 for variable fonts.
        REQUIRED_TABLES.append("STAT")

    missing_tables = [req for req in REQUIRED_TABLES
                      if req not in ttFont.keys()]
    if "glyf" not in ttFont.keys() and "CFF " not in ttFont.keys():
        missing_tables.append("CFF ' or 'glyf")

    if missing_tables:
        yield FAIL, \
              Message("required-tables",
                      f"This font is missing the following required tables:\n"
                      f"{bullet_list(missing_tables)}")
    else:
        yield PASS, "Font contains all required tables."


@check(
    id = 'com.google.fonts/check/unwanted_tables',
    rationale = """
        Some font editors store source data in their own SFNT tables, and these can sometimes sneak into final release files, which should only have OpenType spec tables.
    """,
    proposal = 'legacy:check/053'
)
def com_google_fonts_check_unwanted_tables(ttFont):
    """Are there unwanted tables?"""
    UNWANTED_TABLES = {
        'FFTM': 'Table contains redundant FontForge timestamp info',
        'TTFA': 'Redundant TTFAutohint table',
        'TSI0': 'Table contains data only used in VTT',
        'TSI1': 'Table contains data only used in VTT',
        'TSI2': 'Table contains data only used in VTT',
        'TSI3': 'Table contains data only used in VTT',
        'TSI5': 'Table contains data only used in VTT',
        'prop': ('Table used on AAT, Apple\'s OS X specific technology.'
                 ' Although Harfbuzz now has optional AAT support,'
                 ' new fonts should not be using that.'),
    }
    unwanted_tables_found = []
    for table in ttFont.keys():
        if table in UNWANTED_TABLES.keys():
            info = UNWANTED_TABLES[table]
            unwanted_tables_found.append(f'Table: {table}\nReason: {info}\n')

    if unwanted_tables_found:
        tables = "\n".join(unwanted_tables_found)
        yield FAIL, \
              Message("unwanted-tables",
                      f"The following unwanted font tables were found:\n"
                      f"{tables}\n"
                      f"They can be removed with the fix-unwanted-tables"
                      f" script provided by gftools.")
    else:
        yield PASS, "There are no unwanted tables."


@condition
def STAT_table(ttFont):
    return "STAT" in ttFont


@check(
    id = 'com.google.fonts/check/STAT_strings',
    conditions = ["STAT_table"],
    rationale = """
        On the STAT table, the "Italic" keyword must not be used on AxisValues for variation axes other than 'ital'.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/2863'
)
def com_google_fonts_check_STAT_strings(ttFont):
    """ Check correctness of STAT table strings """
    passed = True
    ital_axis_index = None
    for index, axis in enumerate(ttFont["STAT"].table.DesignAxisRecord.Axis):
        if axis.AxisTag == 'ital':
            ital_axis_index = index
            break

    nameIDs = set()
    if ttFont["STAT"].table.AxisValueArray:
        for value in ttFont["STAT"].table.AxisValueArray.AxisValue:
            if hasattr(value, "AxisIndex"):
                if value.AxisIndex != ital_axis_index:
                    nameIDs.add(value.ValueNameID)

            if hasattr(value, "AxisValueRecord"):
                for record in value.AxisValueRecord:
                    if record.AxisIndex != ital_axis_index:
                        nameIDs.add(value.ValueNameID)

    bad_values = set()
    for name in ttFont['name'].names:
        if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
            passed = False
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL,\
              Message("bad-italic",
                      f'The following AxisValue entries on the STAT table'
                      f' should not contain "Italic":\n'
                      f' {list(sorted(bad_values))}')

    if passed:
        yield PASS, "Looks good!"


@check(
    id = 'com.google.fonts/check/valid_glyphnames',
    rationale = """
        Microsoft's recommendations for OpenType Fonts states the following:

        'NOTE: The PostScript glyph name must be no longer than 31 characters, include only uppercase or lowercase English letters, European digits, the period or the underscore, i.e. from the set [A-Za-z0-9_.] and should start with a letter, except the special glyph name ".notdef" which starts with a period.'

        https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table


        In practice, though, particularly in modern environments, glyph names can be as long as 63 characters.
        According to the "Adobe Glyph List Specification" available at:

        https://github.com/adobe-type-tools/agl-specification
    """,
    proposal = ['legacy:check/058',
                'https://github.com/googlefonts/fontbakery/issues/2832'] # increase limit
                                                                         # to 63 chars
)
def com_google_fonts_check_valid_glyphnames(ttFont):
    """Glyph names are all valid?"""
    from fontbakery.utils import pretty_print_list

    if (ttFont.sfntVersion == b'\x00\x01\x00\x00'
        and ttFont.get("post")
        and ttFont["post"].formatType == 3.0):
        yield SKIP, ("TrueType fonts with a format 3.0 post table"
                     " contain no glyph names.")
    else:
        import re
        bad_names = []
        warn_names = []
        for _, glyphName in enumerate(ttFont.getGlyphOrder()):
            if glyphName in [".null", ".notdef", ".ttfautohint"]:
                # These 2 names are explicit exceptions
                # in the glyph naming rules
                continue
            if not re.match(r'^(?![.0-9])[a-zA-Z._0-9]{1,63}$', glyphName):
                bad_names.append(glyphName)
            if len(glyphName) > 31 and len(glyphName) <= 63:
                warn_names.append(glyphName)

        if len(bad_names) == 0:
            if len(warn_names) == 0:
                yield PASS, "Glyph names are all valid."
            else:
                yield WARN,\
                      Message('legacy-long-names',
                              f"The following glyph names may be too"
                              f" long for some legacy systems which may"
                              f" expect a maximum 31-char length limit:\n"
                              f"{pretty_print_list(warn_names)}")
        else:
            yield FAIL,\
                  Message('found-invalid-names',
                          ("The following glyph names do not comply"
                           " with naming conventions: {}\n\n"
                           " A glyph name"
                           " must be entirely comprised of characters from"
                           " the following set:"
                           " A-Z a-z 0-9 .(period) _(underscore)."
                           " A glyph name must not start with a digit or period."
                           " There are a few exceptions"
                           " such as the special glyph \".notdef\"."
                           " The glyph names \"twocents\", \"a1\", and \"_\""
                           " are all valid, while \"2cents\""
                           " and \".twocents\" are not."
                           "").format(pretty_print_list(bad_names)))


@check(
    id = 'com.google.fonts/check/unique_glyphnames',
    rationale = """
        Duplicate glyph names prevent font installation on Mac OS X.
    """,
    proposal = 'legacy:check/059',
    misc_metadata = {
        'affects': [('Mac', 'unspecified')]
    }
)
def com_google_fonts_check_unique_glyphnames(ttFont):
    """Font contains unique glyph names?"""
    if (ttFont.sfntVersion == b'\x00\x01\x00\x00'
        and ttFont.get("post")
        and ttFont["post"].formatType == 3.0):
        yield SKIP, ("TrueType fonts with a format 3.0 post table"
                     " contain no glyph names.")
    else:
        import re
        glyphs = []
        duplicated_glyphIDs = []
        for _, g in enumerate(ttFont.getGlyphOrder()):
            glyphID = re.sub(r'#\w+', '', g)
            if glyphID in glyphs:
                duplicated_glyphIDs.append(glyphID)
            else:
                glyphs.append(glyphID)

        if len(duplicated_glyphIDs) == 0:
            yield PASS, "Font contains unique glyph names."
        else:
            yield FAIL, \
                  Message("duplicated-glyph-names",
                          "The following glyph names occur twice: "
                          f"{duplicated_glyphIDs}")


@disable # until we know the rationale.
@check(
    id = 'com.google.fonts/check/glyphnames_max_length',
    proposal = 'https://github.com/googlefonts/fontbakery/issues/735'
)
def com_google_fonts_check_glyphnames_max_length(ttFont):
    """Check that glyph names do not exceed max length."""
    if (ttFont.sfntVersion == b'\x00\x01\x00\x00'
        and ttFont.get("post")
        and ttFont["post"].formatType == 3.0):
        yield PASS, ("TrueType fonts with a format 3.0 post table"
                     " contain no glyph names.")
    else:
        failed = False
        for name in ttFont.getGlyphOrder():
            if len(name) > 109:
                failed = True
                yield FAIL, \
                    Message("glyphname-too-long",
                            f"Glyph name is too long: '{name}'")
        if not failed:
            yield PASS, "No glyph names exceed max allowed length."


@check(
    id = 'com.google.fonts/check/ttx-roundtrip',
    conditions = ["not vtt_talk_sources"],
    proposal = 'https://github.com/googlefonts/fontbakery/issues/1763'
)
def com_google_fonts_check_ttx_roundtrip(font):
    """Checking with fontTools.ttx"""
    from fontTools import ttx
    import sys
    ttFont = ttx.TTFont(font)
    failed = False

    class TTXLogger:
        msgs = []

        def __init__(self):
            self.original_stderr = sys.stderr
            self.original_stdout = sys.stdout
            sys.stderr = self
            sys.stdout = self

        def write(self, data):
            if data not in self.msgs:
                self.msgs.append(data)

        def restore(self):
            sys.stderr = self.original_stderr
            sys.stdout = self.original_stdout

    from xml.parsers.expat import ExpatError
    try:
        logger = TTXLogger()
        xml_file = font + ".xml"
        ttFont.saveXML(xml_file)
        export_error_msgs = logger.msgs

        if len(export_error_msgs):
            failed = True
            yield INFO, ("While converting TTF into an XML file,"
                         " ttx emited the messages listed below.")
            for msg in export_error_msgs:
                yield FAIL, msg.strip()

        f = ttx.TTFont()
        f.importXML(font + ".xml")
        import_error_msgs = [msg for msg in logger.msgs
                             if msg not in export_error_msgs]

        if len(import_error_msgs):
            failed = True
            yield INFO, ("While importing an XML file and converting"
                         " it back to TTF, ttx emited the messages"
                         " listed below.")
            for msg in import_error_msgs:
                yield FAIL, msg.strip()
        logger.restore()
    except ExpatError as e:
        failed = True
        yield FAIL, ("TTX had some problem parsing the generated XML file."
                     " This most likely mean there's some problem in the font."
                     " Please inspect the output of ttx in order to find more"
                     " on what went wrong. A common problem is the presence of"
                     " control characteres outside the accepted character range"
                     " as defined in the XML spec. FontTools has got a bug which"
                     " causes TTX to generate corrupt XML files in those cases."
                     " So, check the entries of the name table and remove any"
                     " control chars that you find there."
                     " The full ttx error message was:\n"
                     "======\n{}\n======".format(e))

    if not failed:
        yield PASS, "Hey! It all looks good!"

    # and then we need to cleanup our mess...
    if os.path.exists(xml_file):
        os.remove(xml_file)


@check(
    id = 'com.google.fonts/check/family/vertical_metrics',
    rationale = """
        We want all fonts within a family to have the same vertical metrics so their line spacing is consistent across the family.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/1487'
)
def com_google_fonts_check_family_vertical_metrics(ttFonts):
    """Each font in a family must have the same set of vertical metrics values."""
    failed = []
    vmetrics = {
        "sTypoAscender": {},
        "sTypoDescender": {},
        "sTypoLineGap": {},
        "usWinAscent": {},
        "usWinDescent": {},
        "ascent": {},
        "descent": {}
    }

    missing_tables = False
    for ttFont in ttFonts:
        filename = os.path.basename(ttFont.reader.file.name)
        if 'OS/2' not in ttFont:
            missing_tables = True
            yield FAIL, \
                  Message('lacks-OS/2',
                          f"{filename} lacks an 'OS/2' table.")
            continue

        if 'hhea' not in ttFont:
            missing_tables = True
            yield FAIL, \
                  Message('lacks-hhea',
                          f"{filename} lacks a 'hhea' table.")
            continue

        full_font_name = ttFont['name'].getName(4, 3, 1, 1033).toUnicode()
        vmetrics['sTypoAscender'][full_font_name] = ttFont['OS/2'].sTypoAscender
        vmetrics['sTypoDescender'][full_font_name] = ttFont['OS/2'].sTypoDescender
        vmetrics['sTypoLineGap'][full_font_name] = ttFont['OS/2'].sTypoLineGap
        vmetrics['usWinAscent'][full_font_name] = ttFont['OS/2'].usWinAscent
        vmetrics['usWinDescent'][full_font_name] = ttFont['OS/2'].usWinDescent
        vmetrics['ascent'][full_font_name] = ttFont['hhea'].ascent
        vmetrics['descent'][full_font_name] = ttFont['hhea'].descent


    if not missing_tables:
        # It is important to first ensure all font files have OS/2 and hhea tables
        # before performing the rest of the check routine.

        for k, v in vmetrics.items():
            metric_vals = set(vmetrics[k].values())
            if len(metric_vals) != 1:
                failed.append(k)

        if failed:
            for k in failed:
                s = ["{}: {}".format(k, v) for k, v in vmetrics[k].items()]
                s = "\n".join(s)
                yield FAIL, \
                      Message(f'{k}-mismatch',
                              f"{k} is not the same across the family:\n"
                              f"{s}")
        else:
            yield PASS, "Vertical metrics are the same across the family."


@check(
    id = 'com.google.fonts/check/superfamily/list',
    rationale = """
        This is a merely informative check that lists all sibling families detected by fontbakery.

        Only the fontfiles in these directories will be considered in superfamily-level checks.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/1487'
)
def com_google_fonts_check_superfamily_list(superfamily):
    """List all superfamily filepaths"""
    for family in superfamily:
        yield INFO,\
              Message("family-path",
                      os.path.split(family[0])[0])


@check(
    id = 'com.google.fonts/check/superfamily/vertical_metrics',
    rationale = """
        We may want all fonts within a super-family (all sibling families) to have the same vertical metrics so their line spacing is consistent across the super-family.

        This is an experimental extended version of com.google.fonts/check/family/vertical_metrics and for now it will only result in WARNs.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/1487'
)
def com_google_fonts_check_superfamily_vertical_metrics(superfamily_ttFonts):
    """Each font in set of sibling families must have the same set of vertical metrics values."""
    if len(superfamily_ttFonts) < 2:
        yield SKIP, "Sibling families were not detected."
        return

    warn = []
    vmetrics = {
        "sTypoAscender": {},
        "sTypoDescender": {},
        "sTypoLineGap": {},
        "usWinAscent": {},
        "usWinDescent": {},
        "ascent": {},
        "descent": {}
    }

    for family_ttFonts in superfamily_ttFonts:
        for ttFont in family_ttFonts:
            full_font_name = ttFont['name'].getName(4, 3, 1, 1033).toUnicode()
            vmetrics['sTypoAscender'][full_font_name] = ttFont['OS/2'].sTypoAscender
            vmetrics['sTypoDescender'][full_font_name] = ttFont['OS/2'].sTypoDescender
            vmetrics['sTypoLineGap'][full_font_name] = ttFont['OS/2'].sTypoLineGap
            vmetrics['usWinAscent'][full_font_name] = ttFont['OS/2'].usWinAscent
            vmetrics['usWinDescent'][full_font_name] = ttFont['OS/2'].usWinDescent
            vmetrics['ascent'][full_font_name] = ttFont['hhea'].ascent
            vmetrics['descent'][full_font_name] = ttFont['hhea'].descent

    for k, v in vmetrics.items():
        metric_vals = set(vmetrics[k].values())
        if len(metric_vals) != 1:
            warn.append(k)

    if warn:
        for k in warn:
            s = ["{}: {}".format(k, v) for k, v in vmetrics[k].items()]
            s = "\n".join(s)
            yield WARN, \
                  Message("superfamily-vertical-metrics",
                          f"{k} is not the same across the super-family:\n"
                          f"{s}")
    else:
        yield PASS, "Vertical metrics are the same across the super-family."


@check(
    id = 'com.google.fonts/check/rupee',
    rationale = """
        Per Bureau of Indian Standards every font supporting one of the official Indian languages needs to include Unicode Character “₹” (U+20B9) Indian Rupee Sign.
    """,
    conditions = ['is_indic_font'],
    proposal = 'https://github.com/googlefonts/fontbakery/issues/2967'
)
def com_google_fonts_check_rupee(ttFont):
    """ Ensure indic fonts have the Indian Rupee Sign glyph. """
    if 0x20B9 not in ttFont['cmap'].getBestCmap().keys():
        yield FAIL,\
              Message("missing-rupee",
                      'Please add a glyph for Indian Rupee Sign “₹” at codepoint U+20B9.')
    else:
        yield PASS, "Looks good!"


profile.auto_register(globals())
profile.test_expected_checks(UNIVERSAL_PROFILE_CHECKS, exclusive=True)
