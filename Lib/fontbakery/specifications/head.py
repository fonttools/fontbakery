from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str
from builtins import range

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

@check(id='com.google.fonts/check/014')
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


@check(id='com.google.fonts/check/043')
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


def get_version_from_name_entry(name):
  string = name.string.decode(name.getEncoding())
  # we ignore any comments that
  # may be present in the version name entries
  if ";" in string:
    string = string.split(";")[0]
  # and we also ignore
  # the 'Version ' prefix
  if "Version " in string:
    string = string.split("Version ")[1]
  return string.split('.')


def parse_version_string(s):
  """Tries to parse a version string as used in ttf versioning metadata fields.

  Example of expected format is: 'Version 01.003; Comments'
  """
  suffix = ''
  # DC: I think this may be wrong, the ; isnt the only separator,
  # anything not an int is ok
  if ';' in s:
    fields = s.split(';')
    s = fields[0]
    fields.pop(0)
    suffix = ';'.join(fields)

  substrings = s.split('.')
  minor = substrings[-1]
  if ' ' in substrings[-2]:
    major = substrings[-2].split(' ')[-1]
  else:
    major = substrings[-2]

  if suffix:
    return major, minor, suffix
  else:
    return major, minor


def get_expected_version(f):
  from fontbakery.constants import NAMEID_VERSION_STRING
  expected_version = parse_version_string(str(f["head"].fontRevision))
  for name in f["name"].names:
    if name.nameID == NAMEID_VERSION_STRING:
      name_version = get_version_from_name_entry(name)
      if expected_version is None:
        expected_version = name_version
      elif name_version > expected_version:
        expected_version = name_version
      # else what?
  return expected_version

# FIXME: This check has got too many FAIL code-paths.
#        It may be possible to simplify this check code.
@check(id='com.google.fonts/check/044')
def com_google_fonts_check_044(ttFont):
  """Checking font version fields."""
  import re
  from fontbakery.constants import NAMEID_VERSION_STRING
  failed = False
  try:
    expected = get_expected_version(ttFont)
  except:
    expected = None
    yield FAIL, Message("parse",
                        ("Failed to parse font version"
                         " entries in the name table."))
  if expected is None:
    failed = True
    yield FAIL, Message("missing",
                        ("Could not find any font versioning info on the"
                         " head table or in the name table entries."))
  else:
    font_revision = str(ttFont['head'].fontRevision)
    expected_str = "{}.{}".format(expected[0], expected[1])
    if font_revision != expected_str:
      failed = True
      yield FAIL, Message("differs",
                          ("Font revision on the head table ({})"
                           " differs from the expected value ({})."
                           "").format(font_revision, expected))

    expected_str = "Version {}.{}".format(expected[0], expected[1])
    for name in ttFont["name"].names:
      if name.nameID == NAMEID_VERSION_STRING:
        name_version = name.string.decode(name.getEncoding())
        try:
          # change "Version 1.007" to "1.007"
          # (stripping out the "Version " prefix, if any)
          version_stripped = r'(?<=[V|v]ersion )?([0-9]{1,4}\.[0-9]{1,5})'
          version_without_comments = re.search(version_stripped,
                                               name_version).group(0)
        except:
          failed = True
          yield FAIL, Message("bad-entry",
                              ("Unable to parse font version info"
                               " from this name table entry:"
                               " '{}'").format(name))
          continue

        comments = re.split(r'(?<=[0-9]{1})[;\s]', name_version)[-1]
        if version_without_comments != expected_str:
          # maybe the version strings differ only
          # on floating-point error, so let's
          # also give it a change by rounding and re-checking...

          try:
            rounded_string = round(float(version_without_comments), 3)
            version = round(float(".".join(expected)), 3)
            if rounded_string != version:
              failed = True
              if comments:
                fix = "{};{}".format(expected_str, comments)
              else:
                fix = expected_str
              yield FAIL, Message("mismatch",
                                  ("NAMEID_VERSION_STRING value '{}'"
                                   " does not match expected '{}'"
                                   "").format(name_version, fix))
          except:
            failed = True  # give up. it's definitely bad :(
            yield FAIL, Message("bad",
                                ("Unable to parse font version info"
                                 " from name table entries."))
  if not failed:
    yield PASS, "All font version fields look good."
