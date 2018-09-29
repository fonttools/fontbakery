from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, ERROR, Section
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


@check(
  id = 'com.adobe.typetools/check/implement-me/single-2'
)
def com_adobe_typetools_check_singleface_2(ttFonts):
  """ Length overrun check for name ID's 1,2, 4, 16, 17.
      Max 63 characters. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-3'
)
def com_adobe_typetools_check_singleface_3(ttFonts):
  """ Check that name ID 4 (Full Name) starts with same string as
      Preferred Family Name, and is the same as the CFF font Full Name. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-4'
)
def com_adobe_typetools_check_singleface_4(ttFonts):
  """ Version name string matches release font criteria
      and head table value. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-5'
)
def com_adobe_typetools_check_singleface_5(ttFonts):
  """ Check that CFF PostScript name is same as name table name ID 6. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-6'
)
def com_adobe_typetools_check_singleface_6(ttFonts):
  """ Check that Copyright, Trademark, Designer note,
      and foundry values are present, and match default values. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-7'
)
def com_adobe_typetools_check_singleface_7(ttFonts):
  """ Checking for deprecated CFF operators. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-8'
)
def com_adobe_typetools_check_singleface_8(ttFonts):
  """ Check SubFamily Name (name ID 2) for  Regular Style,
      Bold Style, Italic Style, and BoldItalic Style. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-9'
)
def com_adobe_typetools_check_singleface_9(ttFonts):
  """ Check that no OS/2.usWeightClass is less than 250. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-10'
)
def com_adobe_typetools_check_singleface_10(ttFonts):
  """ Check that no Bold Style face has
      OS/2.usWeightClass of less than 500. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-11',
  rationale = """
    BASE table is necessary for users who are
    editing in a different script than the font is designed for.
  """
)
def com_adobe_typetools_check_singleface_11(ttFonts):
  """ Check that BASE table exists, and has reasonable values. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-12'
)
def com_adobe_typetools_check_singleface_12(ttFonts):
  """ Check that Italic style is set when post table italic angle
      is non-zero, and that italic angle is reasonable. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-13'
)
def com_adobe_typetools_check_singleface_13(ttFonts):
  """ Warn if post.isFixedPitch is set when font is not monospaced. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-14'
)
def com_adobe_typetools_check_singleface_14(ttFonts):
  """ Warn if Bold/Italic style bits do not match
      between the head Table and OS/2 Table """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-15'
)
def com_adobe_typetools_check_singleface_15(ttFonts):
  """ Warn if Font BBox x/y coordinates are improbable,
      or differ between head table and CFF. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-16'
)
def com_adobe_typetools_check_singleface_16(ttFonts):
  """ Check values of Ascender and Descender vs em-square. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-17'
)
def com_adobe_typetools_check_singleface_17(ttFonts):
  """ Verify that all tabular glyphs have the same width. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-18'
)
def com_adobe_typetools_check_singleface_18(ttFonts):
  """ Hint Check.  Verify that there is at least one hint
      for each charstring in each font, and that no charstring
      exceeds the 32K limit for Mac OSX 10.3.x and earlier. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-19'
)
def com_adobe_typetools_check_singleface_19(ttFonts):
  """ Warn if the Unicode cmap table does not exist,
      or there are double mapped glyphs in the Unicode cmap table. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-20'
)
def com_adobe_typetools_check_singleface_20(ttFonts):
  """ Warn if there are double spaces in the name table font menu names. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-21'
)
def com_adobe_typetools_check_singleface_21(ttFonts):
  """ Warn if there trailing or leading spaces
      in the name table font menu names. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-22'
)
def com_adobe_typetools_check_singleface_22(ttFonts):
  """ Warn if any ligatures have a width which not larger
      than the width of the first glyph, or, if first glyph
      is not in font, if the RSB is negative. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-23'
)
def com_adobe_typetools_check_singleface_23(ttFonts):
  """ Warn if any accented glyphs have a width
      different than the base glyph. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-24'
)
def com_adobe_typetools_check_singleface_24(ttFonts):
  """ Warn if font has 'size' feature, and
      design size is not in specified range. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-25'
)
def com_adobe_typetools_check_singleface_25(ttFonts):
  """ Check that fonts do not have UniqueID, UID, or XUID in CFF table. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-26'
)
def com_adobe_typetools_check_singleface_26(ttFonts):
  """ Glyph name checks. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-27'
)
def com_adobe_typetools_check_singleface_27(ttFonts):
  """ Check strikeout/subscript/superscript positions. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-28'
)
def com_adobe_typetools_check_singleface_28(ttFonts):
  """ Check font OS/2 code pages for the a common set of code page bits. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-30'
)
def com_adobe_typetools_check_singleface_30(ttFonts):
  """ Check that there are no more than 7 pairs of BlueValues
      and FamilyBlues in a font, and there is an even number of values. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-31'
)
def com_adobe_typetools_check_singleface_31(ttFonts):
  """ Check that there are no more than 5 pairs of OtherBlues
      and FamilyOtherBlues in a font, and there is
      an even number of values. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-32'
)
def com_adobe_typetools_check_singleface_32(ttFonts):
  """ Check that all fonts have blue value pairs
      with first integer is less than or equal
      to the second integer in pairs. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-33'
)
def com_adobe_typetools_check_singleface_33(ttFonts):
  """ Check that Bottom Zone blue value pairs
      and Top Zone blue value pairs are at least
      (2*BlueFuzz+1) unit apart in a font. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/single-34'
)
def com_adobe_typetools_check_singleface_34(ttFonts):
  """ Check that the difference between numbers
      in blue value pairs meet the requirement."""
  yield ERROR, "Implement-me!"


specification.auto_register(globals())
