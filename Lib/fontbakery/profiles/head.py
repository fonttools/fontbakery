from typing import Tuple
from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
from fontbakery.constants import NameID

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/family/equal_font_versions'
)
def com_google_fonts_check_family_equal_font_versions(ttFonts):
  """Make sure all font files have the same version value."""
  all_detected_versions = []
  fontfile_versions = {}
  for ttFont in ttFonts:
    v = ttFont['head'].fontRevision
    fontfile_versions[ttFont] = v

    if v not in all_detected_versions:
      all_detected_versions.append(v)
  if len(all_detected_versions) != 1:
    versions_list = ""
    for v in fontfile_versions.keys():
      versions_list += "* {}: {}\n".format(v.reader.file.name,
                                           fontfile_versions[v])
    yield WARN,\
          Message("mismatch",
                  f"Version info differs among font"
                  f" files of the same font project.\n"
                  f"These were the version values found:\n"
                  f"{versions_list}")
  else:
    yield PASS, "All font files have the same version."


@check(
  id = 'com.google.fonts/check/unitsperem',
  rationale = """
    According to the OpenType spec:

    The value of unitsPerEm at the head table must be a value between 16 and 16384. Any value in this range is valid.

    In fonts that have TrueType outlines, a power of 2 is recommended as this allows performance optimizations in some rasterizers.

    But 1000 is a commonly used value. And 2000 may become increasingly more common on Variable Fonts.
  """
)
def com_google_fonts_check_unitsperem(ttFont):
  """Checking unitsPerEm value is reasonable."""
  upem = ttFont['head'].unitsPerEm
  target_upem = [2**i for i in range(4, 15)]
  target_upem.append(1000)
  target_upem.append(2000)
  if upem < 16 or upem > 16384:
    yield FAIL,\
          Message("out-of-range",
                  f"The value of unitsPerEm at the head table"
                  f" must be a value between 16 and 16384."
                  f" Got {upem} instead.")
  elif upem not in target_upem:
    yield WARN,\
          Message("suboptimal",
                  f"In order to optimize performance on some"
                  f" legacy renderers, the value of unitsPerEm"
                  f" at the head table should idealy be"
                  f" a power of between 16 to 16384."
                  f" And values of 1000 and 2000 are also"
                  f" common and may be just fine as well."
                  f" But we got {upem} instead.")
  else:
    yield PASS, (f"The unitsPerEm value ({upem}) on"
                 f" the 'head' table is reasonable.")


def parse_version_string(name: str) -> Tuple[str, str]:
  """Parse a version string (name ID 5) and return (major, minor) strings.

  Example of the expected format: 'Version 01.003; Comments'. Version
  strings like "Version 1.3" will be post-processed into ("1", "300").
  The parsed version numbers will therefore match in spirit, but not
  necessarily in string form.
  """
  import re

  # We assume ";" is the universal delimiter here.
  version_entry = name.split(";")[0]

  # Catch both "Version 1.234" and "1.234" but not "1x2.34". Note: search()
  # will return the first match.
  version_string = re.search(r"(?: |^)(\d+\.\d+)", version_entry)

  if version_string is None:
    raise ValueError("The version string didn't contain a number of the format"
                     " major.minor.")

  major, minor = version_string.group(1).split('.')
  major = str(int(major))  # "01.123" -> "1.123"
  minor = minor.ljust(3, '0')  # "3.0" -> "3.000", but "3.123" -> "3.123"
  return major, minor


@check(
  id = 'com.google.fonts/check/font_version'
)
def com_google_fonts_check_font_version(ttFont):
  """Checking font version fields (head and name table)."""
  from decimal import Decimal
  head_version_str = str(Decimal(ttFont["head"].fontRevision).quantize(Decimal('1.000')))
  head_version = parse_version_string(head_version_str)

  # Compare the head version against the name ID 5 strings in all name records.
  name_id_5_records = [
      record for record in ttFont["name"].names
      if record.nameID == NameID.VERSION_STRING
  ]

  failed = False
  if name_id_5_records:
    for record in name_id_5_records:
      try:
        name_version = parse_version_string(record.toUnicode())
        if name_version != head_version:
          failed = True
          yield FAIL,\
                Message("mismatch",
                        f'head version is "{head_version_str}"'
                        f' while name version string (for'
                        f' platform {record.platformID},'
                        f' encoding {record.platEncID}) is'
                        f' "{record.toUnicode()}".')
      except ValueError:
        failed = True
        yield FAIL,\
              Message("parse",
                      f'name version string for'
                      f' platform {record.platformID},'
                      f' encoding {record.platEncID}'
                      f' ("{record.toUnicode()}"),'
                      f' could not be parsed.')
  else:
    failed = True
    yield FAIL,\
          Message("missing",
                  "There is no name ID 5 (version string) in the font.")

  if not failed:
    yield PASS, "All font version fields match."
