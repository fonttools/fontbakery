from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str
from builtins import range

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/014'
)
def com_google_fonts_check_014(ttFonts):
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
    yield WARN, ("version info differs among font"
                 " files of the same font project.\n"
                 "These were the version values found:\n"
                 "{}").format(versions_list)
  else:
    yield PASS, "All font files have the same version."


@check(
  id = 'com.google.fonts/check/043'
)
def com_google_fonts_check_043(ttFont):
  """Checking unitsPerEm value is reasonable."""
  upem = ttFont['head'].unitsPerEm
  target_upem = [2**i for i in range(4, 15)]
  target_upem.insert(0, 1000)
  if upem not in target_upem:
    yield FAIL, ("The value of unitsPerEm at the head table"
                 " must be either 1000 or a power of"
                 " 2 between 16 to 16384."
                 " Got '{}' instead.").format(upem)
  else:
    yield PASS, "unitsPerEm value on the 'head' table is reasonable."


def parse_version_string(name):
  # type: (str) -> Tuple[str, str]
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
  id = 'com.google.fonts/check/044'
)
def com_google_fonts_check_044(ttFont):
  """Checking font version fields (head and name table)."""
  head_version = parse_version_string(str(ttFont["head"].fontRevision))

  # Compare the head version against the name ID 5 strings in all name records.
  from fontbakery.constants import NAMEID_VERSION_STRING
  name_id_5_records = [
      record for record in ttFont["name"].names
      if record.nameID == NAMEID_VERSION_STRING
  ]

  failed = False
  if name_id_5_records:
    for record in name_id_5_records:
      try:
        name_version = parse_version_string(record.toUnicode())
        if name_version != head_version:
          failed = True
          yield FAIL, Message(
              "mismatch",
              "head version is {}, name version string for platform {},"
              " encoding {}, is {}".format(head_version, record.platformID,
                                           record.platEncID, name_version))
      except ValueError:
        failed = True
        yield FAIL, Message("parse", "name version string for platform {},"
                            " encoding {}, could not be parsed".format(
                                record.platformID, record.platEncID))
  else:
    failed = True
    yield FAIL, Message("missing",
                        "There is no name ID 5 (version string) in the font.")

  if not failed:
    yield PASS, "All font version fields match."
