from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, Section
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

specification = spec_factory(default_section=Section("Adobe Font Development Kit for OpenType"))

from fontbakery.constants import (NAMEID_COMPATIBLE_FULL_MACONLY,
                                  NAMEID_POSTSCRIPT_NAME,
                                  PLATFORM_ID__MACINTOSH,
                                  PLAT_ENC_ID__MAC_ROMAN,
                                  MAC_LANG_ID__ENGLISH)

@condition
def macCompFullName(ttFont):
  from fontbakery.utils import get_name_entry_string
  return get_name_entry_string(ttFont,
                               NAMEID_COMPATIBLE_FULL_MACONLY,
                               PLATFORM_ID__MACINTOSH,
                               PLAT_ENC_ID__MAC_ROMAN,
                               MAC_LANG_ID__ENGLISH)

@condition
def postScriptName(ttFont):
  from fontbakery.utils import get_name_entry_string
  return get_name_entry_string(ttFont,
                               NAMEID_POSTSCRIPT_NAME,
                               PLATFORM_ID__MACINTOSH,
                               PLAT_ENC_ID__MAC_ROMAN,
                               MAC_LANG_ID__ENGLISH)
@check(
  id = 'com.adobe.typetools/check/name/id18/length',
  conditions = ["macCompFullName",
                "postScriptName"]
)
def com_adobe_typetools_check_singleface_1(ttFonts,
                                           macCompFullName,
                                           postScriptName
):
  """ Length overrun check for name ID 18.

      Max 63 characters.
      Must be unique within 31 chars. """
  failed = False
  nameDict = {}
  for ttFont in ttFonts:
    if macCompFullName:
      key = macCompFullName[:32]
      if key in nameDict:
        failed = True
        nameDict[key].append(postScriptName)
        yield FAIL, ("The first 32 chars of the Mac platform name ID 18"
                     " Compatible Full Name must be unique within"
                     " Preferred Family Name group.\nname: '%s'."
                     "\nConflicting fonts: %s.").format(macCompFullName,
                                                        nameDict[key])
      else:
        nameDict[key] = [postScriptName]

      if len(macCompFullName) > 63:
        failed = True
        yield FAIL, ("Name ID 18, Mac-compatible full name, is {} characters,"
                     " but should not be longer than 63 chars."
                     "").format(len(macCompFullName))
  if not failed:
    yield PASS, "Name ID 18 looks good!"

specification.auto_register(globals())
