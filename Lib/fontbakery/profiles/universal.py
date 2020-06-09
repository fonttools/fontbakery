import os

from fontbakery.checkrunner import Section, PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.callable import condition, check, disable
from fontbakery.constants import PriorityLevel
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.opentype import OPENTYPE_PROFILE_CHECKS

profile_imports = ('fontbakery.profiles.opentype',
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
  THIRDPARTY_CHECKS + \
  SUPERFAMILY_CHECKS + [
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
#  'com.google.fonts/check/glyphnames_max_length',
  'com.google.fonts/check/family/vertical_metrics',
  'com.google.fonts/check/STAT_strings'
]

@check(
  id = 'com.google.fonts/check/name/trailing_spaces',
)
def com_google_fonts_check_name_trailing_spaces(ttFont):
  """Name table records must not have trailing spaces."""
  failed = False
  for name_record in ttFont['name'].names:
    name_string = name_record.toUnicode()
    if name_string != name_string.strip():
      failed = True
      name_key = tuple([name_record.platformID, name_record.platEncID,
                       name_record.langID, name_record.nameID])
      shortened_str = name_record.toUnicode()
      if len(shortened_str) > 20:
        shortened_str = shortened_str[:10] + "[...]" + shortened_str[-10:]
      yield FAIL, (f"Name table record with key = {name_key} has"
                    " trailing spaces that must be removed:"
                   f" '{shortened_str}'")
  if not failed:
    yield PASS, ("No trailing spaces on name table entries.")


@check(
  id = 'com.google.fonts/check/family/win_ascent_and_descent',
  conditions = ['vmetrics'],
  rationale = """
    A font's winAscent and winDescent values should be greater than the head table's yMax, abs(yMin) values. If they are less than these values, clipping can occur on Windows platforms (https://github.com/RedHatBrand/Overpass/issues/33).

    If the font includes tall/deep writing systems such as Arabic or Devanagari, the winAscent and winDescent can be greater than the yMax and abs(yMin) to accommodate vowel marks.

    When the win Metrics are significantly greater than the upm, the linespacing can appear too loose. To counteract this, enabling the OS/2 fsSelection bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 typo values instead. This means the font developer can control the linespacing with the typo values, whilst avoiding clipping by setting the win values to values greater than the yMax and abs(yMin).
  """
)
def com_google_fonts_check_family_win_ascent_and_descent(ttFont, vmetrics):
  """Checking OS/2 usWinAscent & usWinDescent."""

  if "OS/2" not in ttFont:
    yield FAIL, Message("lacks-OS/2",
                        "Font file lacks OS/2 table")
    return

  failed = False

  # OS/2 usWinAscent:
  if ttFont['OS/2'].usWinAscent < vmetrics['ymax']:
    failed = True
    yield FAIL, Message("ascent",
                        ("OS/2.usWinAscent value"
                         " should be equal or greater than {}, but got"
                         " {} instead").format(vmetrics['ymax'],
                                               ttFont['OS/2'].usWinAscent))
  if ttFont['OS/2'].usWinAscent > vmetrics['ymax'] * 2:
    failed = True
    yield FAIL, Message(
        "ascent", ("OS/2.usWinAscent value {} is too large."
                   " It should be less than double the yMax."
                   " Current yMax value is {}").format(ttFont['OS/2'].usWinDescent,
                                                       vmetrics['ymax']))
  # OS/2 usWinDescent:
  if ttFont['OS/2'].usWinDescent < abs(vmetrics['ymin']):
    failed = True
    yield FAIL, Message(
        "descent", ("OS/2.usWinDescent value"
                    " should be equal or greater than {}, but got"
                    " {} instead").format(
                        abs(vmetrics['ymin']), ttFont['OS/2'].usWinDescent))

  if ttFont['OS/2'].usWinDescent > abs(vmetrics['ymin']) * 2:
    failed = True
    yield FAIL, Message(
        "descent", ("OS/2.usWinDescent value {} is too large."
                    " It should be less than double the yMin."
                    " Current absolute yMin value is {}").format(ttFont['OS/2'].usWinDescent,
                                                                 abs(vmetrics['ymin'])))
  if not failed:
    yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"


@check(
  id = 'com.google.fonts/check/os2_metrics_match_hhea',
  rationale = """
    When OS/2 and hhea vertical metrics match, the same linespacing results on macOS, GNU+Linux and Windows. Unfortunately as of 2018, Google Fonts has released many fonts with vertical metrics that don't match in this way. When we fix this issue in these existing families, we will create a visible change in line/paragraph layout for either Windows or macOS users, which will upset some of them.

    But we have a duty to fix broken stuff, and inconsistent paragraph layout is unacceptably broken when it is possible to avoid it.

    If users complain and prefer the old broken version, they have the freedom to take care of their own situation.
  """
)
def com_google_fonts_check_os2_metrics_match_hhea(ttFont):
  """Checking OS/2 Metrics match hhea Metrics.

  OS/2 and hhea vertical metric values should match. This will produce
  the same linespacing on Mac, GNU+Linux and Windows.

  Mac OS X uses the hhea values.
  Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.
  """

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
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
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
    yield FAIL, ("Not all fonts passed in the command line"
                 " are in the same directory. This may lead to"
                 " bad results as the tool will interpret all"
                 " font files as belonging to a single"
                 " font family. The detected directories are:"
                 " {}".format(directories))


@condition
def ftxvalidator_cmd():
  """ Test if `ftxvalidator` is a command; i.e. an executable with a path."""
  import shutil
  return shutil.which('ftxvalidator')


@check(
  id = 'com.google.fonts/check/ftxvalidator_is_available',
  rationale = """
    There's no reasonable (and legal) way to run the command `ftxvalidator` of the Apple Font Tool Suite on a non-macOS machine. I.e. on GNU+Linux or Windows etc.

    If Font Bakery is not running on an OSX machine, the machine running Font Bakery could access `ftxvalidator` on OSX, e.g. via ssh or a remote procedure call (rpc).

    There's an ssh example implementation at:
    https://github.com/googlefonts/fontbakery/blob/master/prebuilt/workarounds/ftxvalidator/ssh-implementation/ftxvalidator
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/2184'
  }
)
def com_google_fonts_check_ftxvalidator_is_available(ftxvalidator_cmd):
  """Is the command `ftxvalidator` (Apple Font Tool Suite) available?"""
  if ftxvalidator_cmd:
    yield PASS, f"ftxvalidator is available at {ftxvalidator_cmd}"
  else:
    yield WARN, "Could not find ftxvalidator."


@check(
  id = 'com.google.fonts/check/ftxvalidator',
  conditions = ['ftxvalidator_cmd']
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
    pipes = subprocess.Popen(ftx_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
  id = 'com.google.fonts/check/ots'
)
def com_google_fonts_check_ots(font):
  """Checking with ots-sanitize."""
  import ots

  try:
    process = ots.sanitize(font, check=True, capture_output=True)
  except ots.CalledProcessError as e:
    yield FAIL, (
      "ots-sanitize returned an error code ({}). Output follows:\n\n{}{}"
    ).format(e.returncode, e.stderr.decode(), e.stdout.decode())
  else:
    if process.stderr:
      yield WARN, (
        "ots-sanitize passed this file, however warnings were printed:\n\n{}"
      ).format(process.stderr.decode())
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
  id = 'com.google.fonts/check/fontbakery_version'
)
def com_google_fonts_check_fontbakery_version():
  """Do we have the latest version of FontBakery installed?"""

  try:
    import subprocess
    installed_str = None
    latest_str = None
    is_latest = False
    failed = False
    pip_cmd = ["pip", "search", "fontbakery"]
    pip_output = subprocess.check_output(pip_cmd, stderr=subprocess.STDOUT)
    for line in pip_output.decode().split('\n'):
      if 'INSTALLED' in line:
        installed_str = line.split('INSTALLED')[1].strip()
      if 'LATEST' in line:
        latest_str = line.split('LATEST')[1].strip()
      if '(latest)' in line:
        is_latest = True

    if not (is_latest or is_up_to_date(installed_str, latest_str)):
      failed = True
      yield FAIL, (f"Current Font Bakery version is {installed_str},"
                   f" while a newer {latest_str} is already available."
                    " Please upgrade it with 'pip install -U fontbakery'")
    yield INFO, pip_output.decode()
  except Exception:
    yield FAIL, ("Unable to detect what's the latest version of"
                 " FontBakery available. Maybe we're offline?"
                 " Please check Internet access and try again.")
  except subprocess.CalledProcessError as e:
    yield ERROR, ("Running 'pip search fontbakery' returned an error code."
                  " Output follows :\n\n{}\n").format(e.output.decode())

  if not failed:
    yield PASS, "Font Bakery is up-to-date"


@check(
  id = 'com.google.fonts/check/mandatory_glyphs',
  rationale = """
    The OpenType specification v1.8.2 recommends that the first glyph is the .notdef glyph without a codepoint assigned and with a drawing.

    https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph

    Pre-v1.8, it was recommended that a font should also contain a .null, CR and space glyph. This might have been relevant for applications on MacOS 9.
  """
)
def com_google_fonts_check_mandatory_glyphs(ttFont):
  """Font contains .notdef as first glyph?"""
  from fontbakery.utils import glyph_has_ink

  if (
    ttFont.getGlyphOrder()[0] == ".notdef"
    and ".notdef" not in ttFont.getBestCmap().values()
    and glyph_has_ink(ttFont, ".notdef")
  ):
    yield PASS, (
      "Font contains the .notdef glyph as the first glyph, it does "
      "not have a Unicode value assigned and contains a drawing."
    )
  else:
    yield WARN, (
      "Font should contain the .notdef glyph as the first glyph, "
      "it should not have a Unicode value assigned and should "
      "contain a drawing."
    )


@check(
  id = 'com.google.fonts/check/whitespace_glyphs'
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
  conditions = ['not missing_whitespace_chars']
)
def com_google_fonts_check_whitespace_glyphnames(ttFont):
  """Font has **proper** whitespace glyph names?"""
  from fontbakery.utils import get_glyph_name

  def getGlyphEncodings(font, names):
    result = set()
    for subtable in font['cmap'].tables:
      if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
          if name in names:
            result.add(codepoint)
    return result

  if ttFont['post'].formatType == 3.0:
    yield SKIP, "Font has version 3 post table."
  else:
    failed = False
    space_enc = getGlyphEncodings(ttFont, ["uni0020", "space"])
    nbsp_enc = getGlyphEncodings(
        ttFont, ["uni00A0", "nonbreakingspace", "nbspace", "nbsp"])
    space = get_glyph_name(ttFont, 0x0020)
    if 0x0020 not in space_enc:
      failed = True
      yield FAIL, Message("bad20", ("Glyph 0x0020 is called \"{}\":"
                                    " Change to \"space\""
                                    " or \"uni0020\"").format(space))

    nbsp = get_glyph_name(ttFont, 0x00A0)
    if 0x00A0 not in nbsp_enc:
      if 0x00A0 in space_enc:
        # This is OK.
        # Some fonts use the same glyph for both space and nbsp.
        pass
      else:
        failed = True
        yield FAIL, Message("badA0", ("Glyph 0x00A0 is called \"{}\":"
                                      " Change to \"nbsp\""
                                      " or \"uni00A0\"").format(nbsp))

    if failed is False:
      yield PASS, "Font has **proper** whitespace glyph names."


@check(
  id = 'com.google.fonts/check/whitespace_ink'
)
def com_google_fonts_check_whitespace_ink(ttFont):
  """Whitespace glyphs have ink?"""
  from fontbakery.utils import get_glyph_name, glyph_has_ink

  # code-points for all "whitespace" chars:
  WHITESPACE_CHARACTERS = [
    0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x0020, 0x0085, 0x00A0, 0x1680,
    0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
    0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000, 0x180E, 0x200B,
    0x2060, 0xFEFF
  ]
  failed = False
  for codepoint in WHITESPACE_CHARACTERS:
    g = get_glyph_name(ttFont, codepoint)
    if g is not None and glyph_has_ink(ttFont, g):
      failed = True
      yield FAIL, ("Glyph \"{}\" has ink."
                   " It needs to be replaced by"
                   " an empty glyph.").format(g)
  if not failed:
    yield PASS, "There is no whitespace glyph with ink."


@check(
  id='com.google.fonts/check/required_tables',
  conditions = ['is_ttf'],
  rationale = """
    Depending on the typeface and coverage of a font, certain tables are recommended for optimum quality. For example, the performance of a non-linear font is improved if the VDMX, LTSH, and hdmx tables are present. Non-monospaced Latin fonts should have a kern table. A gasp table is necessary if a designer wants to influence the sizes at which grayscaling is used under Windows. A DSIG table containing a digital signature helps ensure the integrity of the font file. Etc.
  """
  # FIXME:
  # The rationale description above comes from FontValidator, check W0022.
  # We may want to improve it and/or rephrase it.
)
def com_google_fonts_check_required_tables(ttFont):
  """Font contains all required tables?"""
  from .shared_conditions import is_variable_font

  REQUIRED_TABLES = {
      "cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post"}
  OPTIONAL_TABLES = {
      "cvt ", "fpgm", "loca", "prep", "VORG", "EBDT", "EBLC", "EBSC", "BASE",
      "GPOS", "GSUB", "JSTF", "DSIG", "gasp", "hdmx", "LTSH", "PCLT", "VDMX",
      "vhea", "vmtx", "kern"
  }
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
    yield INFO, ("This font contains the following"
                 " optional tables [{}]").format(", ".join(optional_tables))

  if is_variable_font(ttFont):
    # According to https://github.com/googlefonts/fontbakery/issues/1671
    # STAT table is required on WebKit on MacOS 10.12 for variable fonts.
    REQUIRED_TABLES.add("STAT")

  missing_tables = [req for req in REQUIRED_TABLES if req not in ttFont.keys()]
  if "glyf" not in ttFont.keys() and "CFF " not in ttFont.keys():
    missing_tables.append("CFF ' or 'glyf")

  if missing_tables:
    yield FAIL, ("This font is missing the following required tables:"
                 " ['{}']").format("', '".join(missing_tables))
  else:
    yield PASS, "Font contains all required tables."


@check(
  id = 'com.google.fonts/check/unwanted_tables',
  rationale = """
    Some font editors store source data in their own SFNT tables, and these can sometimes sneak into final release files, which should only have OpenType spec tables.
  """
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
    'prop': '', # FIXME: why is this one unwanted?
      # Marc Foley found that VFs containing a MVAR table have very
      # loose vertical metrics, even if the MVAR table hasn't adjusted
      # any vertical metric values.
    'MVAR': ('Produces a bug in DirectWrite which causes'
             ' https://bugzilla.mozilla.org/show_bug.cgi?id=1492477,'
             ' https://github.com/google/fonts/issues/2085')
  }
  unwanted_tables_found = []
  for table in ttFont.keys():
    if table in UNWANTED_TABLES.keys():
      info = UNWANTED_TABLES[table]
      unwanted_tables_found.append(f'Table: {table}\nReason: {info}\n')

  if len(unwanted_tables_found) > 0:
    yield FAIL, ("The following unwanted font tables were found:\n"
                 "{}\n"
                 "They can be removed with the gftools fix-unwanted-tables script."
                 ).format("\n".join(unwanted_tables_found))
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
  misc_metadata = {
    'requested': "https://github.com/googlefonts/fontbakery/issues/2863"
  }
)
def com_google_fonts_check_STAT_strings(ttFont):
  """ Check correctness of STAT table strings """
  passed = True
  ital_axis_index = None
  for index, axis in enumerate(ttFont["STAT"].table.DesignAxisRecord.Axis):
    if axis.AxisTag == 'ital':
      ital_axis_index = index
      break

  nameIDs = []
  if ttFont["STAT"].table.AxisValueArray:
    for value in ttFont["STAT"].table.AxisValueArray.AxisValue:
      if value.AxisIndex != ital_axis_index: nameIDs.append(value.ValueNameID)

  bad_values = []
  for name in ttFont['name'].names:
    if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
      passed = False
      bad_values.append(name.toUnicode())

  if bad_values:
    yield FAIL,\
          Message("bad-italic",
                  f'The following AxisValue entries on the STAT table'
                  f' should not contain "Italic":\n'
                  f' {bad_values}')

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
  misc_metadata = {
    'requested': "https://github.com/googlefonts/fontbakery/issues/2832" # increase limit to 63 chars
  }
)
def com_google_fonts_check_valid_glyphnames(ttFont):
  """Glyph names are all valid?"""
  from fontbakery.utils import pretty_print_list

  if ttFont.sfntVersion == b'\x00\x01\x00\x00' and ttFont.get(
      "post") and ttFont["post"].formatType == 3.0:
    yield SKIP, ("TrueType fonts with a format 3.0 post table contain no"
                 " glyph names.")
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
                      ("The following glyph names may be too"
                       " long for some legacy systems which may"
                       " expect a maximum 31-char length limit:\n"
                       "{}").format(pretty_print_list(warn_names)))
    else:
      yield FAIL,\
            Message('found-invalid-names',
                    ("The following glyph names do not comply"
                     " with naming conventions: {}\n\n"
                     " such as the special character \".notdef\"."
                     " The glyph names \"twocents\", \"a1\", and \"_\""
                     " are all valid, while \"2cents\""
                     " and \".twocents\" are not."
                     "").format(pretty_print_list(bad_names)))


@check(
  id = 'com.google.fonts/check/unique_glyphnames',
  rationale = """
    Duplicate glyph names prevent font installation on Mac OS X.
  """,
  misc_metadata = {
    'affects': [('Mac', 'unspecified')]
  }
)
def com_google_fonts_check_unique_glyphnames(ttFont):
  """Font contains unique glyph names?"""
  if ttFont.sfntVersion == b'\x00\x01\x00\x00' and ttFont.get(
      "post") and ttFont["post"].formatType == 3.0:
    yield SKIP, ("TrueType fonts with a format 3.0 post table contain no"
                 " glyph names.")
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
      yield FAIL, ("The following glyph names"
                   " occur twice: {}").format(duplicated_glyphIDs)


# This check was originally ported from
# Mekkablue Preflight Checks available at:
# https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Preflight%20Font.py
# Disabled until we know the rationale.
@disable
@check(
  id = 'com.google.fonts/check/glyphnames_max_length',
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  }
)
def com_google_fonts_check_glyphnames_max_length(ttFont):
  """Check that glyph names do not exceed max length."""
  if ttFont.sfntVersion == b'\x00\x01\x00\x00' and ttFont.get(
      "post") and ttFont["post"].formatType == 3.0:
    yield PASS, ("TrueType fonts with a format 3.0 post table contain no "
                 "glyph names.")
  else:
    failed = False
    for name in ttFont.getGlyphOrder():
      if len(name) > 109:
        failed = True
        yield FAIL, ("Glyph name is too long:" " '{}'").format(name)
    if not failed:
      yield PASS, "No glyph names exceed max allowed length."


@check(
  id = 'com.google.fonts/check/ttx-roundtrip',
  conditions = ["not vtt_talk_sources"]
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
    import_error_msgs = [msg for msg in logger.msgs if msg not in export_error_msgs]

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
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1487'
  }
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
                      (f"{k} is not the same across the family:\n"
                       f"{s}"))
    else:
      yield PASS, "Vertical metrics are the same across the family."


@check(
  id = 'com.google.fonts/check/superfamily/list',
  rationale = """
    This is a merely informative check that lists all sibling families detected by fontbakery.

    Only the fontfiles in these directories will be considered in superfamily-level checks.
  """
)
def com_google_fonts_check_superfamily_list(superfamily):
  """List all superfamily filepaths"""
  for family in superfamily:
    yield INFO,\
          Message("family-path", os.path.split(family[0])[0])


@check(
  id = 'com.google.fonts/check/superfamily/vertical_metrics',
  rationale = """
    We may want all fonts within a super-family (all sibling families) to have the same vertical metrics so their line spacing is consistent across the super-family.

    This is an experimental extended version of com.google.fonts/check/superfamily/vertical_metrics and for now it will only result in WARNs.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1487'
  }
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
      yield WARN, (f"{k} is not the same across the super-family:\n"
                   f"{s}")
  else:
    yield PASS, "Vertical metrics are the same across the super-family."


profile.auto_register(globals())
profile.test_expected_checks(UNIVERSAL_PROFILE_CHECKS, exclusive=True)
