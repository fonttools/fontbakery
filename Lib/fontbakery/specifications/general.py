from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from fontbakery.callable import check, condition, disable
from fontbakery.checkrunner import ERROR, FAIL, INFO, PASS, SKIP, WARN
from fontbakery.constants import CRITICAL
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
        'status = fontforge.open("{0}").validate();'
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
      "ff_err_messages": ff_err_messages
    }
  except:
    return None


@check(
  id = 'com.google.fonts/check/002',
  misc_metadata = {
    'priority': CRITICAL
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

    ftx_data = plistlib.readPlistFromString(ftx_output)
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
      yield FAIL, "ftxvalidator output follows:\n\n{}\n".format(ftx_output)

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
  try:
    import subprocess
    ots_output = subprocess.check_output(
        ["ots-sanitize", font], stderr=subprocess.STDOUT).decode()
    if ots_output != "" and "File sanitized successfully" not in ots_output:
      yield FAIL, "ots-sanitize output follows:\n\n{}".format(ots_output)
    else:
      yield PASS, "ots-sanitize passed this file"
  except subprocess.CalledProcessError as e:
    yield FAIL, ("ots-sanitize returned an error code. Output follows :"
                 "\n\n{}").format(e.output)
  except OSError as e:
    yield ERROR, ("ots-sanitize is not available!"
                  " You really MUST check the fonts with this tool."
                  " To install it, see"
                  " https://github.com/googlefonts"
                  "/gf-docs/blob/master/ProjectChecklist.md#ots"
                  " Actual error message was: "
                  "'{}'").format(e)


@check(
  id = 'com.google.fonts/check/037'
)
def com_google_fonts_check_037(font):
  """Checking with Microsoft Font Validator."""
  try:
    import subprocess
    fval_cmd = [
        "FontValidator.exe", "-file", font, "-all-tables",
        "-report-in-font-dir", "+raster-tests"
    ]
    subprocess.check_output(fval_cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    filtered_msgs = ""
    for line in e.output.decode().split("\n"):
      if "Validating glyph with index" in line:
        continue
      if "Table Test:" in line:
        continue
      filtered_msgs += line + "\n"
    yield INFO, ("Microsoft Font Validator returned an error code."
                 " Output follows :\n\n{}\n").format(filtered_msgs)
  except (OSError, IOError) as error:
    yield ERROR, ("Mono runtime and/or "
                  "Microsoft Font Validator are not available!")
    raise error

  def report_message(msg, details):
    if details:
      return "MS-FonVal: {} DETAILS: {}".format(msg, details)
    else:
      return "MS-FonVal: {}".format(msg)

  xml_report_file = "{}.report.xml".format(font)
  html_report_file = "{}.report.html".format(font)
  fval_file = os.path.join(os.path.dirname(font), 'fval.xsl')

  with open(xml_report_file, "rb") as xml_report:
    import defusedxml.lxml
    doc = defusedxml.lxml.parse(xml_report)
    already_reported = []
    for report in doc.iter('Report'):
      msg = report.get("Message")
      details = report.get("Details")
      if [msg, details] not in already_reported:
        # avoid cluttering the output with tons of identical reports
        already_reported.append([msg, details])

        if report.get("ErrorType") == "P":
          yield PASS, report_message(msg, details)
        elif report.get("ErrorType") == "E":
          yield FAIL, report_message(msg, details)
        elif report.get("ErrorType") == "W":
          yield WARN, report_message(msg, details)
        else:
          yield INFO, report_message(msg, details)

  os.remove(xml_report_file)
  # FontVal internal detail: HTML report generated only on non-Windows due to
  # Mono or the used HTML renderer not being able to render XML with a
  # stylesheet directly. https://github.com/googlefonts/fontbakery/issues/1747
  if os.path.exists(html_report_file):
    os.remove(html_report_file)
  os.remove(fval_file)


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
    yield FAIL, ("fontforge did print these messages to stderr:\n"
                 "{}").format(filtered_err_msgs)
  else:
    yield PASS, "fontforge validation did not output any error message."


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
       0x2,
       "Contours are not closed!", "Contours are closed.")

    , ("Contours do not intersect",
       0x4,
       "There are countour intersections!",
       "Contours do not intersect.")

    , ("Contours have correct directions",
       0x8,
       "Contours have incorrect directions!",
       "Contours have correct directions.")

    , ("References in the glyph haven't been flipped",
       0x10,
       "References in the glyph have been flipped!",
       "References in the glyph haven't been flipped.")

    , ("Glyphs have points at extremas",
       0x20,
       "Glyphs do not have points at extremas!",
       "Glyphs have points at extremas.")

    , ("Glyph names referred to from glyphs present in the font",
       0x40,
       "Glyph names referred to from glyphs"
       " not present in the font!",
       "Glyph names referred to from glyphs"
       " present in the font.")

    , ("Points (or control points) are not too far apart",
       0x40000,
       "Points (or control points) are too far apart!",
       "Points (or control points) are not too far apart.")

    , ("Not more than 1,500 points in any glyph"
       " (a PostScript limit)",
       0x80,
       "There are glyphs with more than 1,500 points!"
       "Exceeds a PostScript limit.",
       "Not more than 1,500 points in any glyph"
       " (a PostScript limit).")

    , ("PostScript has a limit of 96 hints in glyphs",
       0x100,
       "Exceeds PostScript limit of 96 hints per glyph",
       "Font respects PostScript limit of 96 hints per glyph")

    , ("Font doesn't have invalid glyph names",
       0x200,
       "Font has invalid glyph names!",
       "Font doesn't have invalid glyph names.")

    , ("Glyphs have allowed numbers of points defined in maxp",
       0x400,
       "Glyphs exceed allowed numbers of points defined in maxp",
       "Glyphs have allowed numbers of points defined in maxp.")

    , ("Glyphs have allowed numbers of paths defined in maxp",
       0x800,
       "Glyphs exceed allowed numbers of paths defined in maxp!",
       "Glyphs have allowed numbers of paths defined in maxp.")

    , ("Composite glyphs have allowed numbers"
       " of points defined in maxp?",
       0x1000,
       "Composite glyphs exceed allowed numbers"
       " of points defined in maxp!",
       "Composite glyphs have allowed numbers"
       " of points defined in maxp.")

    , ("Composite glyphs have allowed numbers"
       " of paths defined in maxp",
       0x2000, "Composite glyphs exceed"
       " allowed numbers of paths defined in maxp!", "Composite glyphs have"
       " allowed numbers of paths defined in maxp.")

    , ("Glyphs instructions have valid lengths",
       0x4000,
       "Glyphs instructions have invalid lengths!",
       "Glyphs instructions have valid lengths.")

    , ("Points in glyphs are integer aligned",
       0x80000,
       "Points in glyphs are not integer aligned!",
       "Points in glyphs are integer aligned.")

    # According to the opentype spec, if a glyph contains an anchor point
    # for one anchor class in a subtable, it must contain anchor points
    # for all anchor classes in the subtable. Even it, logically,
    # they do not apply and are unnecessary.
    , ("Glyphs have all required anchors.",
       0x100000,
       "Glyphs do not have all required anchors!",
       "Glyphs have all required anchors.")

    , ("Glyph names are unique?",
       0x200000,
       "Glyph names are not unique!", "Glyph names are unique.")

    , ("Unicode code points are unique?",
       0x400000,
       "Unicode code points are not unique!",
       "Unicode code points are unique.")

    , ("Do hints overlap?",
       0x800000,
       "Hints should NOT overlap!", "Hints do not overlap.")
  )

  for description, bit, err_msg, ok_msg in fontforge_checks:
    if fontforge_skip_checks is not None and \
                          bool(fontforge_skip_checks & bit) is not False:
      yield SKIP, description
    elif bool(validation_state & bit) is not False:
      yield FAIL, "fontforge-check: {}".format(err_msg)
    else:
      yield PASS, "fontforge-check: {}".format(ok_msg)


@check(
  id = 'com.google.fonts/check/046'
)
def com_google_fonts_check_046(ttFont):
  """Font contains the first few mandatory glyphs (.null or NULL, CR and
  space)?"""
  from fontbakery.utils import get_glyph_name

  # It would be good to also check
  # for .notdef (codepoint = unspecified)
  null = get_glyph_name(ttFont, 0x0000)
  CR = get_glyph_name(ttFont, 0x000D)
  space = get_glyph_name(ttFont, 0x0020)

  missing = []
  if null is None:
    missing.append("0x0000")
  if CR is None:
    missing.append("0x000D")
  if space is None:
    missing.append("0x0020")
  if missing != []:
    yield WARN, ("Font is missing glyphs for"
                 " the following mandatory codepoints:"
                 " {}.").format(", ".join(missing))
  else:
    yield PASS, ("Font contains the first few mandatory glyphs"
                 " (.null or NULL, CR and space).")


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
  from fontbakery.utils import get_glyph_name

  def glyphHasInk(font, name):
    """Checks if specified glyph has any ink.

    That is, that it has at least one defined contour associated.
    Composites are considered to have ink if any of their components have ink.
    Args:
        font:       the font
        glyph_name: The name of the glyph to check for ink.
    Returns:
        True if the font has at least one contour associated with it.
    """
    glyph = font['glyf'].glyphs[name]
    glyph.expand(font['glyf'])
    if not glyph.isComposite():
      if glyph.numberOfContours == 0:
        return False
      (coords, _, _) = glyph.getCoordinates(font['glyf'])
      # you need at least 3 points to draw
      return len(coords) > 2

    # composite is blank if composed of blanks
    # if you setup a font with cycles you are just a bad person
    # Dave: lol, bad people exist, so put a recursion in this recursion
    for glyph_name in glyph.getComponentNames(glyph.components):
      if glyphHasInk(font, glyph_name):
        return True
    return False

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
    if g is not None and glyphHasInk(ttFont, g):
      failed = True
      yield FAIL, ("Glyph \"{}\" has ink."
                   " It needs to be replaced by"
                   " an empty glyph.").format(g)
  if not failed:
    yield PASS, "There is no whitespace glyph with ink."


@check(
    id='com.google.fonts/check/052',
    conditions=['is_ttf']
)
def com_google_fonts_check_052(ttFont):
  """Font contains all required tables?"""
  REQUIRED_TABLES = set(
      ["cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post"])
  OPTIONAL_TABLES = set([
      "cvt ", "fpgm", "loca", "prep", "VORG", "EBDT", "EBLC", "EBSC", "BASE",
      "GPOS", "GSUB", "JSTF", "DSIG", "gasp", "hdmx", "LTSH", "PCLT", "VDMX",
      "vhea", "vmtx", "kern"
  ])
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
  UNWANTED_TABLES = set(
      ['FFTM', 'TTFA', 'prop', 'TSI0', 'TSI1', 'TSI2', 'TSI3', 'TSI5'])
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
  id = 'com.google.fonts/check/058'
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
      if glyphName in [".null", ".notdef"]:
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
