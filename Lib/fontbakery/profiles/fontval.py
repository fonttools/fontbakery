import os
from fontbakery.callable import check
from fontbakery.checkrunner import ERROR, FAIL, INFO, PASS, WARN, Section
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import
from .shared_conditions import is_variable_font

profile_imports = ['.shared_conditions']
profile = profile_factory(default_section=Section("Checks inherited from Microsoft Font Validator"))

@check(
  id = 'com.google.fonts/check/fontvalidator'
)
def com_google_fonts_check_fontvalidator(font):
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
    # FontVal E4012 thinks that
    # "Versions 0x00010000 and 0x0001002 are currently
    #  the only defined versions of the GDEF table."
    # but the GDEF chapter of the OpenType specification at
    # https://docs.microsoft.com/en-us/typography/opentype/spec/gdef
    # describes GDEF header version 1.3, which is not yet recognized
    # by FontVal, thus resulting in this spurious false-FAIL:
    "The version number is neither 0x00010000 nor 0x0001002",

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
    # which is: com.google.fonts/check/xavgcharwidth
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
    # com.google.fonts/check/required_tables
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
    from lxml import etree
    doc = etree.fromstring(xml_report.read())
    for report in doc.iterfind('.//Report'):
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

profile.auto_register(globals())
