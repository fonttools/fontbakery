import pytest
import os

from fontbakery.checkrunner import (
              INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO)

from fontTools.ttLib import TTFont

  ##################################################
  # Suggested template for implementing code-tests #
  ##################################################
 
  ## Start with a font known to be good:
  #good_font = TTFont(os.path.join("data", "test", "mada", "Mada-Regular.ttf"))
  #print(""Test PASS with a good font...")
  #status, _ = list(check(good_font))[-1]
  #assert status == PASS
  #
  ## Introduce the problem
  #bad_font = ...
  #
  # And make sure the check FAILs:
  #print(""Test FAIL with a bad font...")
  #status, _ = list(check(bad_font))[-1]
  #assert status == FAIL


def IMPLEMENT_ME_test_check_singleface_1():
  """ Length overrun check for name ID 18.
  
      Max 63 characters.
      Must be unique within 31 chars. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_1 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_2():
  """ Length overrun check for name ID's 1,2, 4, 16, 17.
      Max 63 characters. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_2 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_3():
  """ Check that name ID 4 (Full Name) starts with same string as
      Preferred Family Name, and is the same as the CFF font Full Name."""
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_3 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_4():
  """ Version name string matches release font criteria
      and head table value. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_4 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_5():
  """ Check that CFF PostScript name is same as name table name ID 6. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_5 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_6():
  """ Check that Copyright, Trademark, Designer note,
      and foundry values are present, and match default values. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_6 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_7():
  """ Checking for deprecated CFF operators. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_7 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_8():
  """ Check SubFamily Name (name ID 2) for  Regular Style,
      Bold Style, Italic Style, and BoldItalic Style. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_8 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_9():
  """ Check that no OS/2.usWeightClass is less than 250. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_9 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_10():
  """ Check that no Bold Style face has
      OS/2.usWeightClass of less than 500. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_10 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_11():
  """ Check that BASE table exists, and has reasonable values. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_11 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_12():
  """ Check that Italic style is set when post table italic angle
      is non-zero, and that italic angle is reasonable. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_12 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_13():
  """ Warn if post.isFixedPitch is set when font is not monospaced. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_13 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_14():
  """ Warn if Bold/Italic style bits do not match
      between the head Table and OS/2 Table. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_14 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_15():
  """ Warn if Font BBox x/y coordinates are improbable,
      or differ between head table and CFF. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_15 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_16():
  """ Check values of Ascender and Descender vs em-square. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_16 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_17():
  """ Verify that all tabular glyphs have the same width. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_17 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_18():
  """ Hint Check.  Verify that there is at least one hint
      for each charstring in each font, and that no charstring
      exceeds the 32K limit for Mac OSX 10.3.x and earlier. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_18 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_19():
  """ Warn if the Unicode cmap table does not exist,
      or there are double mapped glyphs in the Unicode cmap table. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_19 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_20():
  """ Warn if there are double spaces in the name table font menu names. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_20 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_21():
  """ Warn if there trailing or leading spaces
      in the name table font menu names. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_21 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_22():
  """ Warn if any ligatures have a width which not larger
      than the width of the first glyph, or, if first glyph
      is not in font, if the RSB is negative. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_22 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_23():
  """ Warn if any accented glyphs have a width
      different than the base glyph. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_23 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_24():
  """ Warn if font has 'size' feature, and
      design size is not in specified range. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_24 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_25():
  """ Check that fonts do not have UniqueID, UID, or XUID in CFF table. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_25 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_26():
  """ Glyph name checks. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_26 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_27():
  """ Check strikeout/subscript/superscript positions. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_27 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_28():
  """ Check font OS/2 code pages for the a common set of code page bits. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_28 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_30():
  """ Check that there are no more than 7 pairs of BlueValues
      and FamilyBlues in a font, and there is an even number of values. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_30 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_31():
  """ Check that there are no more than 5 pairs of OtherBlues
      and FamilyOtherBlues in a font, and there is
      an even number of values. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_31 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_32():
  """ Check that all fonts have blue value pairs
      with first integer is less than or equal
      to the second integer in pairs. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_32 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_33():
  """ Check that Bottom Zone blue value pairs
      and Top Zone blue value pairs are at least
      (2*BlueFuzz+1) unit apart in a font. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_33 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_singleface_34():
  """ Check that the difference between numbers
      in blue value pairs meet the requirement. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_singleface_34 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_1():
  """ Verify that each group of fonts with the
      same nameID 1 has maximum of 4 fonts. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_1 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_2():
  """ Check that the Compatible Family group has
      same name ID's in all languages except for
      the compatible names 16, 17, 18, 20, 21 and 22. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_2 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_3():
  """ Check that the Compatible Family group has
      same Preferred Family name (name ID 16) in
      all languagesID 16 in all other languages. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_3 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_4():
  """ Family-wide 'size' feature checks. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_4 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_5():
  """ Check that style settings for each face is
      unique within Compatible Family group, in all languages. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_5 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_6():
  """ Check that the Compatible Family group has a
      base font and at least two faces, and check
      if weight class is valid. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_6 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_7():
  """ Check that all faces in the Preferred Family
      group have the same Copyright and Trademark string. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_7 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_8():
  """ Check the Compatible Family group style vs OS/2.usWeightClass settings.
      Max 2 usWeightClass allowed. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_8 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_9():
  """ Check that all faces in the Compatible Family
      group have the same OS/2.usWidthClass value. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_9 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_10():
  """ Check that if all faces in family have a Panose number
      and that CFF ISFixedPtch matches the Panose monospace setting. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_10 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_11():
  """ Check that Mac and Windows menu names differ for all
      but base font, and are the same for the base font. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_11 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_12():
  """ Check that GSUB/GPOS script and language feature lists
      are the same in all faces, and that DFLT/dflt
      and latn/dflt are present. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_12 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_13():
  """ Check that no two faces in a preferred group
      have the same weight/width/Italic-style values
      when the OS/2 table fsSelection bit 8
      (WEIGHT_WIDTH_SLOPE_ONLY) is set. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_13 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_14():
  """ Check that all faces in a preferred group
      have the same fsType embedding values. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_14 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_15():
  """ Check that all faces in a preferred group
      have the same underline position and width. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_15 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_16():
  """ Check that for all faces in a preferred family group,
      that the width of any glyph is not more than 3 times
      the width of the same glyph in any other face. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_16 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_17():
  """ Check that fonts have OS/2 table version 4. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_17 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_18():
  """ Check that all faces in a Compatible Family group
      have the same array size of BlueValues and OtherBlues
      within a Compatible Family Name Italic or Regular
      sub-group of the family. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_18 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_19():
  """ Check that all faces in the Preferred Family group
      have the same values of FamilyBlues and
      FamilyOtherBlues, and are valid. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_19 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_20():
  """ Check that all faces in the Compatible Family group
      have the same BlueScale value. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_20 as check
  # TODO: Implement-me!


def IMPLEMENT_ME_test_check_family_21():
  """ Check that all faces in the Compatible Family group
      have the same BlueShift value. """
  #from fontbakery.specifications.afdko import com_adobe_typetools_check_family_21 as check
  # TODO: Implement-me!
