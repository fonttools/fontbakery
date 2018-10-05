from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, ERROR, Section
from fontbakery.constants import (NameID,
                                  PlatformID,
                                  MacEncodingID,
                                  MacLanguageID)
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

specification = spec_factory(default_section=Section("Adobe Font Development Kit for OpenType"))


@condition
def macCompFullName(ttFont):
  from fontbakery.utils import get_name_entry_string
  return get_name_entry_string(ttFont,
                               NameID.COMPATIBLE_FULL_MACONLY,
                               PlatformID.MACINTOSH,
                               MacEncodingID.ROMAN,
                               MacLanguageID.ENGLISH)

@condition
def postScriptName(ttFont):
  from fontbakery.utils import get_name_entry_string
  return get_name_entry_string(ttFont,
                               NameID.POSTSCRIPT_NAME,
                               PlatformID.MACINTOSH,
                               MacEncodingID.ROMAN,
                               MacLanguageID.ENGLISH)
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
      between the head Table and OS/2 Table. """
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
      in blue value pairs meet the requirement. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-1'
)
def com_adobe_typetools_check_family_1(ttFonts):
  """ Verify that each group of fonts with the
      same nameID 1 has maximum of 4 fonts. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-2'
)
def com_adobe_typetools_check_family_2(ttFonts):
  """ Check that the Compatible Family group has
      same name ID's in all languages except for
      the compatible names 16, 17, 18, 20, 21 and 22. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-3'
)
def com_adobe_typetools_check_family_3(ttFonts):
  """ Check that the Compatible Family group has
      same Preferred Family name (name ID 16) in
      all languagesID 16 in all other languages. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-4'
)
def com_adobe_typetools_check_family_4(ttFonts):
  """ Family-wide 'size' feature checks. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-5'
)
def com_adobe_typetools_check_family_5(ttFonts):
  """ Check that style settings for each face is
      unique within Compatible Family group, in all languages. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-6'
)
def com_adobe_typetools_check_family_6(ttFonts):
  """ Check that the Compatible Family group has a
      base font and at least two faces, and check
      if weight class is valid. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-7'
)
def com_adobe_typetools_check_family_7(ttFonts):
  """ Check that all faces in the Preferred Family
      group have the same Copyright and Trademark string. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-8'
)
def com_adobe_typetools_check_family_8(ttFonts):
  """ Check the Compatible Family group style vs OS/2.usWeightClass settings.
      Max 2 usWeightClass allowed. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-9'
)
def com_adobe_typetools_check_family_9(ttFonts):
  """ Check that all faces in the Compatible Family
      group have the same OS/2.usWidthClass value. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-10'
)
def com_adobe_typetools_check_family_10(ttFonts):
  """ Check that if all faces in family have a Panose number
      and that CFF ISFixedPtch matches the Panose monospace setting. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-11'
)
def com_adobe_typetools_check_family_11(ttFonts):
  """ Check that Mac and Windows menu names differ for all
      but base font, and are the same for the base font. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-12'
)
def com_adobe_typetools_check_family_12(ttFonts):
  """ Check that GSUB/GPOS script and language feature lists
      are the same in all faces, and that DFLT/dflt
      and latn/dflt are present. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-13'
)
def com_adobe_typetools_check_family_13(ttFonts):
  """ Check that no two faces in a preferred group
      have the same weight/width/Italic-style values
      when the OS/2 table fsSelection bit 8
      (WEIGHT_WIDTH_SLOPE_ONLY) is set. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-14'
)
def com_adobe_typetools_check_family_14(ttFonts):
  """ Check that all faces in a preferred group
      have the same fsType embedding values. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-15'
)
def com_adobe_typetools_check_family_15(ttFonts):
  """ Check that all faces in a preferred group
      have the same underline position and width. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-16'
)
def com_adobe_typetools_check_family_16(ttFonts):
  """ Check that for all faces in a preferred family group,
      that the width of any glyph is not more than 3 times
      the width of the same glyph in any other face. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-17'
)
def com_adobe_typetools_check_family_17(ttFonts):
  """ Check that fonts have OS/2 table version 4. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-18'
)
def com_adobe_typetools_check_family_18(ttFonts):
  """ Check that all faces in a Compatible Family group
      have the same array size of BlueValues and OtherBlues
      within a Compatible Family Name Italic or Regular
      sub-group of the family. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-19'
)
def com_adobe_typetools_check_family_19(ttFonts):
  """ Check that all faces in the Preferred Family group
      have the same values of FamilyBlues and
      FamilyOtherBlues, and are valid. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-20'
)
def com_adobe_typetools_check_family_20(ttFonts):
  """ Check that all faces in the Compatible Family group
      have the same BlueScale value. """
  yield ERROR, "Implement-me!"


@check(
  id = 'com.adobe.typetools/check/implement-me/family-21'
)
def com_adobe_typetools_check_family_21(ttFonts):
  """ Check that all faces in the Compatible Family group
      have the same BlueShift value. """
  yield ERROR, "Implement-me!"


specification.auto_register(globals())
