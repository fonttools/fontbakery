import os
from fontbakery.callable import check, condition, disable
from fontbakery.checkrunner import ERROR, FAIL, INFO, PASS, SKIP, WARN
from fontbakery.constants import PriorityLevel
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import
from .shared_conditions import is_variable_font

spec_imports = [
    ('.shared_conditions', ('missing_whitespace_chars', ))
]

@condition
def fontforge_check_results(font):
  if "adobeblank" in font:
    return SKIP, ("Skipping AdobeBlank since"
                  " this font is a very peculiar hack.")

  import subprocess
  cmd = (
        'import fontforge, sys;'
        'status = fontforge.open("{}").validate();'
        'sys.stdout.write(status.__str__());'.format
        )

  p = subprocess.Popen(['python', '-c', cmd(font)],
                       stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE
                      )
  ret_val, ff_err_messages = p.communicate()
  try:
    return {
      "validation_state": int(ret_val),
      "ff_err_messages": ff_err_messages.decode("utf-8")
    }
  except:
    return None


@check(
  id = 'com.google.fonts/check/002',
  misc_metadata = {
    'priority': PriorityLevel.CRITICAL
  }
)
def com_google_fonts_check_002(fonts):
  """Checking all files are in the same directory.

  If the set of font files passed in the command line is not all in the
  same directory, then we warn the user since the tool will interpret
  the set of files as belonging to a single family (and it is unlikely
  that the user would store the files from a single family spreaded in
  several separate directories).
  """

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


@check(
  id = 'com.google.fonts/check/035'
)
def com_google_fonts_check_035(font):
  """Checking with ftxvalidator."""
  import plistlib
  try:
    import subprocess
    ftx_cmd = [
        "ftxvalidator",
        "-t",
        "all",  # execute all checks
        font
    ]
    ftx_output = subprocess.check_output(ftx_cmd, stderr=subprocess.STDOUT)
    ftx_data = plistlib.loads(ftx_output)
    # we accept kATSFontTestSeverityInformation
    # and kATSFontTestSeverityMinorError
    if 'kATSFontTestSeverityFatalError' \
       not in ftx_data['kATSFontTestResultKey']:
      yield PASS, "ftxvalidator passed this file"
    else:
      ftx_cmd = [
          "ftxvalidator",
          "-T",  # Human-readable output
          "-r",  # Generate a full report
          "-t",
          "all",  # execute all checks
          font
      ]
      ftx_output = subprocess.check_output(ftx_cmd, stderr=subprocess.STDOUT)
      yield FAIL, f"ftxvalidator output follows:\n\n{ftx_output}\n"

  except subprocess.CalledProcessError as e:
    yield WARN, ("ftxvalidator returned an error code. Output follows :"
                 "\n\n{}\n").format(e.output)
  except OSError:
    yield ERROR, "ftxvalidator is not available!"


@check(
  id = 'com.google.fonts/check/036'
)
def com_google_fonts_check_036(font):
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


@check(
  id = 'com.google.fonts/check/037'
)
def com_google_fonts_check_037(font):
  """Checking with Microsoft Font Validator."""

  # In some cases we want to override the severity level of
  # certain checks in FontValidator:
  downgrade_to_warn = [
    # There are reports that this fontval check has an out-of-date
    # understanding of valid bits in fsSelection.
    # More info at:
    # https://github.com/googlei18n/fontmake/issues/414#issuecomment-379408127
    "There are undefined bits set in fsSelection field",

    # FIX-ME: Why did we downgrade this one to WARN?
    "Misoriented contour"
  ]

  # Some other checks we want to completely disable:
  disabled_fval_checks = [
    # These messages below are simply fontval given user feedback
    # on the progress of runnint it. It has nothing to do with
    # actual issues on the font files:
    "Validating glyph with index",
    "Table Test:",

    # No software is affected by Mac strings nowadays.
    # More info at: googlei18n/fontmake#414
    "The table doesn't contain strings for Mac platform",
    "The PostScript string is not present for both required platforms",

    # Font Bakery has got a native check for the xAvgCharWidth field
    # which is: com.google.fonts/check/034
    "The xAvgCharWidth field does not equal the calculated value",

    # The optimal ordering suggested by FVal check W0020 seems to only be
    # relevant to performance optimizations on old versions of Windows
    # running on old hardware. Since such performance considerations
    # are most likely negligible, we're not going to bother users with
    # this check's table ordering requirements.
    # More info at:
    # https://github.com/googlefonts/fontbakery/issues/2105
    "Tables are not in optimal order",

    # Font Bakery has its own check for required/optional tables:
    # com.google.fonts/check/052 - "Font contains all required tables?"
    "Recommended table is missing"
  ]

  # There are also some checks that do not make
  # sense when we're dealing with variable fonts:
  VARFONT_disabled_fval_checks = [
    # Variable fonts typically do have lots of self-intersecting
    # contours because they are used to draw each portion
    # of variable glyph features.
    "Intersecting contours",
    "Intersecting components of composite glyph",

    # DeltaFormat = 32768 (same as 0x8000) means VARIATION_INDEX,
    # according to https://docs.microsoft.com/en-us/typography/opentype/spec/chapter2
    # The FontVal problem description for this check (E5200) only mentions
    # the other values as possible valid ones. So apparently this means FontVal
    # implementation is not up-to-date with more recent versions of the OpenType spec
    # and that's why these spurious FAILs are being emitted.
    # That's good enough reason to mute it.
    # More info at:
    # https://github.com/googlefonts/fontbakery/issues/2109
    "The device table's DeltaFormat value is invalid"
  ]

  from fontTools.ttLib import TTFont
  if is_variable_font(TTFont(font)):
    disabled_fval_checks.extend(VARFONT_disabled_fval_checks)

  try:
    import subprocess
    fval_cmd = [
        "FontValidator", "-file", font, "-all-tables",
        "-report-in-font-dir", "-no-raster-tests"
    ]
    subprocess.check_output(fval_cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    filtered_msgs = ""
    for line in e.output.decode().split("\n"):
      disable_it = False
      for substring in disabled_fval_checks:
        if substring in line:
          disable_it = True
      if not disable_it:
        filtered_msgs += line + "\n"
    yield INFO, ("Microsoft Font Validator returned an error code."
                 " Output follows :\n\n{}\n").format(filtered_msgs)
  except (OSError, IOError) as error:
    yield ERROR, ("Mono runtime and/or "
                  "Microsoft Font Validator are not available!")
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
          details.append(f"NOTE: {num_similar} other similar"
                          " results were hidden!")
        details = '\n\t- ' + '\n\t- '.join(details)
      return f"MS-FonVal: {msg} DETAILS: {details}"
    else:
      return f"MS-FonVal: {msg}"

  xml_report_file = f"{font}.report.xml"
  html_report_file = f"{font}.report.html"
  fval_file = os.path.join(os.path.dirname(font), 'fval.xsl')

  grouped_msgs = {}
  with open(xml_report_file, "rb") as xml_report:
    import defusedxml.lxml
    doc = defusedxml.lxml.parse(xml_report)

    for report in doc.iter('Report'):
      msg = report.get("Message")
      details = report.get("Details")

      disable_it = False
      for substring in disabled_fval_checks:
        if substring in msg:
          disable_it = True
      if disable_it:
        continue

      if msg not in grouped_msgs:
        grouped_msgs[msg] = {"errortype": report.get("ErrorType"),
                             "details": [details]}
      else:
        if details not in grouped_msgs[msg]["details"]:
          # avoid cluttering the output with tons of identical reports
          # yield INFO, 'grouped_msgs[msg]["details"]: {}'.format(grouped_msgs[msg]["details"])
          grouped_msgs[msg]["details"].append(details)

  # ---------------------------
  # Clean-up generated files...
  os.remove(xml_report_file)
  # FontVal internal detail: HTML report generated only on non-Windows due to
  # Mono or the used HTML renderer not being able to render XML with a
  # stylesheet directly. https://github.com/googlefonts/fontbakery/issues/1747
  if os.path.exists(html_report_file):
    os.remove(html_report_file)
  os.remove(fval_file)

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
      if data["details"] and \
         data["details"][0] and \
         glyph_index in data["details"][0]:
        try:
          data["details"] = {'Glyph index': [int(x.split(glyph_index)[1])
                                             for x in data["details"]]}
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
      yield status, report_message(msg, data["details"])

    elif data["errortype"] == "W":
      yield WARN, report_message(msg, data["details"])

    else:
      yield INFO, report_message(msg, data["details"])


@check(
  id = 'com.google.fonts/check/038',
  conditions = ['fontforge_check_results']
)
def com_google_fonts_check_038(font, fontforge_check_results):
  """FontForge validation outputs error messages?"""

  filtered_err_msgs = ""
  for line in fontforge_check_results["ff_err_messages"].split('\n'):
    if ('The following table(s) in the font'
        ' have been ignored by FontForge') in line:
      continue
    if "Ignoring 'DSIG' digital signature table" in line:
      continue
    filtered_err_msgs += line + '\n'

  if len(filtered_err_msgs.strip()) > 0:
    yield WARN, ("FontForge seems to dislike certain aspects of this font file."
                 " The actual meaning of the log messages below is not always"
                 " clear and may require further investigation.\n\n"
                 "{}").format(filtered_err_msgs)
  else:
    yield PASS, "FontForge validation did not output any error message."


@condition
def fontforge_skip_checks():
  """ return a bitmask of the checks to skip

  E.g. to skip:
    0x2: Contours are closed?
    0x40: Glyph names referred to from glyphs present in the font
    0x200: Font doesn't have invalid glyph names
  do:
    return 0x2 + 0x40 + 0x200

  override with @condition(force=True) to customize this
  """
  return None

@check(
  id = 'com.google.fonts/check/039',
  conditions = ['fontforge_check_results']
)
def com_google_fonts_check_039(fontforge_check_results, fontforge_skip_checks):
  """FontForge checks."""

  validation_state = fontforge_check_results["validation_state"]
  fontforge_checks = (
      ("Contours are closed?",
       0x2, FAIL,
       "Contours are not closed!", "Contours are closed.")

    , ("Contours do not intersect",
       0x4, WARN,
       "There are countour intersections!",
       "Contours do not intersect.")

    , ("Contours have correct directions",
       0x8, WARN,
       "Contours have incorrect directions!",
       "Contours have correct directions.")

    , ("References in the glyph haven't been flipped",
       0x10, FAIL,
       "References in the glyph have been flipped!",
       "References in the glyph haven't been flipped.")

    , ("Glyphs have points at extremas",
       0x20, WARN,
       "Glyphs do not have points at extremas!",
       "Glyphs have points at extremas.")

    , ("Glyph names referred to from glyphs present in the font",
       0x40, FAIL,
       "Glyph names referred to from glyphs"
       " not present in the font!",
       "Glyph names referred to from glyphs"
       " present in the font.")

    , ("Points (or control points) are not too far apart",
       0x40000, FAIL,
       "Points (or control points) are too far apart!",
       "Points (or control points) are not too far apart.")

    , ("Not more than 1,500 points in any glyph"
       " (a PostScript limit)",
       0x80, FAIL,
       "There are glyphs with more than 1,500 points!"
       "Exceeds a PostScript limit.",
       "Not more than 1,500 points in any glyph"
       " (a PostScript limit).")

    , ("PostScript has a limit of 96 hints in glyphs",
       0x100, FAIL,
       "Exceeds PostScript limit of 96 hints per glyph",
       "Font respects PostScript limit of 96 hints per glyph")

    , ("Font doesn't have invalid glyph names",
       0x200, FAIL,
       "Font has invalid glyph names!",
       "Font doesn't have invalid glyph names.")

    , ("Glyphs have allowed numbers of points defined in maxp",
       0x400, FAIL,
       "Glyphs exceed allowed numbers of points defined in maxp",
       "Glyphs have allowed numbers of points defined in maxp.")

    , ("Glyphs have allowed numbers of paths defined in maxp",
       0x800, FAIL,
       "Glyphs exceed allowed numbers of paths defined in maxp!",
       "Glyphs have allowed numbers of paths defined in maxp.")

    , ("Composite glyphs have allowed numbers"
       " of points defined in maxp?",
       0x1000, FAIL,
       "Composite glyphs exceed allowed numbers"
       " of points defined in maxp!",
       "Composite glyphs have allowed numbers"
       " of points defined in maxp.")

    , ("Composite glyphs have allowed numbers"
       " of paths defined in maxp",
       0x2000, FAIL,
       "Composite glyphs exceed"
       " allowed numbers of paths defined in maxp!",
       "Composite glyphs have"
       " allowed numbers of paths defined in maxp.")

    , ("Glyphs instructions have valid lengths",
       0x4000, FAIL,
       "Glyphs instructions have invalid lengths!",
       "Glyphs instructions have valid lengths.")

    , ("Points in glyphs are integer aligned",
       0x80000, FAIL,
       "Points in glyphs are not integer aligned!",
       "Points in glyphs are integer aligned.")

    # According to the opentype spec, if a glyph contains an anchor point
    # for one anchor class in a subtable, it must contain anchor points
    # for all anchor classes in the subtable. Even it, logically,
    # they do not apply and are unnecessary.
    , ("Glyphs have all required anchors.",
       0x100000, FAIL,
       "Glyphs do not have all required anchors!",
       "Glyphs have all required anchors.")

    , ("Glyph names are unique?",
       0x200000, FAIL,
       "Glyph names are not unique!",
       "Glyph names are unique.")

    , ("Unicode code points are unique?",
       0x400000, FAIL,
       "Unicode code points are not unique!",
       "Unicode code points are unique.")

    , ("Do hints overlap?",
       0x800000, FAIL,
       "Hints should NOT overlap!",
       "Hints do not overlap.")
  )

  for description, bit, failure_status_override, fail_msg, ok_msg in fontforge_checks:
    if fontforge_skip_checks is not None and \
       bool(fontforge_skip_checks & bit) is not False:
      yield SKIP, description
    elif bool(validation_state & bit) is not False:
      yield failure_status_override, f"fontforge-check: {fail_msg}"
    else:
      yield PASS, f"fontforge-check: {ok_msg}"


@check(
  id = 'com.google.fonts/check/046'
)
def com_google_fonts_check_046(ttFont):
  """Font contains .notdef as first glyph?

  The OpenType specification v1.8.2 recommends that the first glyph is the
  .notdef glyph without a codepoint assigned and with a drawing.

  https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph

  Pre-v1.8, it was recommended that a font should also contain a .null, CR and
  space glyph. This might have been relevant for applications on MacOS 9.
  """
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
  id = 'com.google.fonts/check/047'
)
def com_google_fonts_check_047(ttFont, missing_whitespace_chars):
  """Font contains glyphs for whitespace characters?"""
  if missing_whitespace_chars != []:
    yield FAIL, ("Whitespace glyphs missing for"
                 " the following codepoints:"
                 " {}.").format(", ".join(missing_whitespace_chars))
  else:
    yield PASS, "Font contains glyphs for whitespace characters."


@check(
  id = 'com.google.fonts/check/048',
  conditions = ['not missing_whitespace_chars']
)
def com_google_fonts_check_048(ttFont):
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
  id = 'com.google.fonts/check/049',
  conditions = ['is_ttf']
)
def com_google_fonts_check_049(ttFont):
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
  id='com.google.fonts/check/052',
  conditions=['is_ttf'],
  rationale="""Depending on the typeface and coverage of a font, certain
  tables are recommended for optimum quality. For example, the performance
  of a non-linear font is improved if the VDMX, LTSH, and hdmx tables are
  present. Non-monospaced Latin fonts should have a kern table. A gasp table
  is necessary if a designer wants to influence the sizes at which grayscaling
  is used under Windows. A DSIG table containing a digital signature helps
  ensure the integrity of the font file. Etc.
  """
  # TODO: The rationale description above comes from FontValidator, check W0022.
  #       We may want to improve it and/or rephrase it.
)
def com_google_fonts_check_052(ttFont):
  """Font contains all required tables?"""
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
  # check/066 (kern table) is a good example of a separate check for
  # a specific table providing a detailed description of the rationale
  # behind it.

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
  id = 'com.google.fonts/check/053'
)
def com_google_fonts_check_053(ttFont):
  """Are there unwanted tables?"""
  UNWANTED_TABLES = {
      'FFTM', 'TTFA', 'prop', 'TSI0', 'TSI1', 'TSI2', 'TSI3', 'TSI5'}
  unwanted_tables_found = []
  for table in ttFont.keys():
    if table in UNWANTED_TABLES:
      unwanted_tables_found.append(table)

  if len(unwanted_tables_found) > 0:
    yield FAIL, ("Unwanted tables were found"
                 " in the font and should be removed:"
                 " {}").format(", ".join(unwanted_tables_found))
  else:
    yield PASS, "There are no unwanted tables."


@check(
  id = 'com.google.fonts/check/058',
  rationale = """Microsoft's recommendations for OpenType Fonts states the
  following, 'NOTE: The PostScript glyph name must be no longer than 31
  characters, include only uppercase or lowercase English letters, European
  digits, the period or the underscore, i.e. from the set [A-Za-z0-9_.] and
  should start with a letter, except the special glyph name ".notdef" which
  starts with a period.'

  https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table
  """
)
def com_google_fonts_check_058(ttFont):
  """Glyph names are all valid?"""
  if ttFont.sfntVersion == b'\x00\x01\x00\x00' and ttFont.get(
      "post") and ttFont["post"].formatType == 3.0:
    yield SKIP, ("TrueType fonts with a format 3.0 post table contain no"
                 " glyph names.")
  else:
    import re
    bad_names = []
    for _, glyphName in enumerate(ttFont.getGlyphOrder()):
      if glyphName in [".null", ".notdef", ".ttfautohint"]:
        # These 2 names are explicit exceptions
        # in the glyph naming rules
        continue
      if not re.match(r'^(?![.0-9])[a-zA-Z._0-9]{1,31}$', glyphName):
        bad_names.append(glyphName)

    if len(bad_names) == 0:
      yield PASS, "Glyph names are all valid."
    else:
      yield FAIL, ("The following glyph names do not comply"
                   " with naming conventions: {}"
                   " A glyph name may be up to 31 characters in length,"
                   " must be entirely comprised of characters from"
                   " the following set:"
                   " A-Z a-z 0-9 .(period) _(underscore). and must not"
                   " start with a digit or period."
                   " There are a few exceptions"
                   " such as the special character \".notdef\"."
                   " The glyph names \"twocents\", \"a1\", and \"_\""
                   " are all valid, while \"2cents\""
                   " and \".twocents\" are not.").format(bad_names)


@check(
  id = 'com.google.fonts/check/059',
  rationale = """
    Duplicate glyph names prevent font installation on Mac OS X.
  """,
  misc_metadata={
    'affects': [('Mac', 'unspecified')]
  }
)
def com_google_fonts_check_059(ttFont):
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
  id = 'com.google.fonts/check/078',
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  }
)
def com_google_fonts_check_078(ttFont):
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

  logger = TTXLogger()
  ttFont.saveXML(font + ".xml")
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
    yield INFO, ("While importing an XML file and converting it back to TTF,"
                 " ttx emited the messages listed below.")
    for msg in import_error_msgs:
      yield FAIL, msg.strip()
  logger.restore()

  if not failed:
    yield PASS, "Hey! It all looks good!"
