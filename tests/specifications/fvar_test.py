from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_167():
  """ The variable font 'wght' (Weight) axis coordinate
      must be 400 on the 'Regular' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_167 as check
  from fontbakery.specifications.shared_conditions import regular_wght_coord

  # Our reference varfont, CabinVFBeta.ttf, has
  # a bad Regular:wght coordinate
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
  regular_weight_coord = regular_wght_coord(ttFont)

  # So it must FAIL the test
  print('Test FAIL with a bad Regular:wght coordinate...')
  status, message = list(check(ttFont, regular_weight_coord))[-1]
  assert status == FAIL

  # We then fix the value:
  ttFont["fvar"].instances[0].coordinates["wght"] = 400
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # Then re-read the coord:
  regular_weight_coord = regular_wght_coord(ttFont)

  # and now this should PASS the test:
  print('Test PASS with a good Regular:wght coordinate (400)...')
  status, message = list(check(ttFont, regular_weight_coord))[-1]
  assert status == PASS


def test_check_168():
  """ The variable font 'wdth' (Width) axis coordinate
      must be 100 on the 'Regular' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_168 as check
  from fontbakery.specifications.shared_conditions import regular_wdth_coord

  # Our reference varfont, CabinVFBeta.ttf, has
  # a bad Regular:wdth coordinate
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
  regular_width_coord = regular_wdth_coord(ttFont)

  # So it must FAIL the test
  print('Test FAIL with a bad Regular:wdth coordinate...')
  status, message = list(check(ttFont, regular_width_coord))[-1]
  assert status == FAIL

  # We then fix the value:
  ttFont["fvar"].instances[0].coordinates["wdth"] = 100
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # Then re-read the coord:
  regular_width_coord = regular_wdth_coord(ttFont)

  # and now this should PASS the test:
  print('Test PASS with a good Regular:wdth coordinate (100)...')
  status, message = list(check(ttFont, regular_width_coord))[-1]
  assert status == PASS


def test_check_169():
  """ The variable font 'slnt' (Slant) axis coordinate
      must be zero on the 'Regular' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_169 as check
  from fontbakery.specifications.shared_conditions import regular_slnt_coord
  from fontTools.ttLib.tables._f_v_a_r import Axis

  # Our reference varfont, CabinVFBeta.ttf, lacks a 'slnt' variation axis.
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

  # So we add one:
  new_axis = Axis()
  new_axis.axisTag = "slnt"
  ttFont["fvar"].axes.append(new_axis)

  # and specify a bad coordinate for the Regular:
  ttFont["fvar"].instances[0].coordinates["slnt"] = 123
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # then we test the code of the regular_slnt_coord condition:
  regular_slant_coord = regular_slnt_coord(ttFont)

  # And with this the test must FAIL
  print('Test FAIL with a bad Regular:slnt coordinate (123)...')
  status, message = list(check(ttFont, regular_slant_coord))[-1]
  assert status == FAIL

  # We then fix the Regular:slnt coordinate value value:
  regular_slant_coord = 0

  # and now this should PASS the test:
  print('Test PASS with a good Regular:slnt coordinate (zero)...')
  status, message = list(check(ttFont, regular_slant_coord))[-1]
  assert status == PASS


def test_check_170():
  """ The variable font 'ital' (Italic) axis coordinate
      must be zero on the 'Regular' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_170 as check
  from fontbakery.specifications.shared_conditions import regular_ital_coord
  from fontTools.ttLib.tables._f_v_a_r import Axis

  # Our reference varfont, CabinVFBeta.ttf, lacks an 'ital' variation axis.
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

  # So we add one:
  new_axis = Axis()
  new_axis.axisTag = "ital"
  ttFont["fvar"].axes.append(new_axis)

  # and specify a bad coordinate for the Regular:
  ttFont["fvar"].instances[0].coordinates["ital"] = 123
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # then we test the code of the regular_ital_coord condition:
  regular_italic_coord = regular_ital_coord(ttFont)

  # So it must FAIL the test
  print('Test FAIL with a bad Regular:ital coordinate (123)...')
  status, message = list(check(ttFont, regular_italic_coord))[-1]
  assert status == FAIL

  # We then fix the Regular:ital coordinate:
  regular_italic_coord = 0

  # and now this should PASS the test:
  print('Test PASS with a good Regular:ital coordinate (zero)...')
  status, message = list(check(ttFont, regular_italic_coord))[-1]
  assert status == PASS

def test_check_171():
  """ The variable font 'opsz' (Optical Size) axis coordinate
      should be between 9 and 13 on the 'Regular' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_171 as check
  from fontbakery.specifications.shared_conditions import regular_opsz_coord
  from fontTools.ttLib.tables._f_v_a_r import Axis

  # Our reference varfont, CabinVFBeta.ttf, lacks an 'opsz' variation axis.
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")

  # So we add one:
  new_axis = Axis()
  new_axis.axisTag = "opsz"
  ttFont["fvar"].axes.append(new_axis)

  # and specify a bad coordinate for the Regular:
  ttFont["fvar"].instances[0].coordinates["opsz"] = 8
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # then we test the regular_opsz_coord condition:
  regular_opticalsize_coord = regular_opsz_coord(ttFont)

  # And it must WARN the test
  print('Test WARN with a bad Regular:opsz coordinate (8)...')
  status, message = list(check(ttFont, regular_opticalsize_coord))[-1]
  assert status == WARN

  # We try yet another bad value
  regualr_opticalsize_coord = 14

  # And it must also WARN the test
  print('Test WARN with another bad Regular:opsz value (14)...')
  status, message = list(check(ttFont, regular_opticalsize_coord))[-1]
  assert status == WARN

  # We then test with good default opsz values:
  for value in [9, 10, 11, 12, 13]:
    regular_opticalsize_coord = value

    # and now this should PASS the test:
    print(f'Test PASS with a good Regular:opsz coordinate ({value})...')
    status, message = list(check(ttFont, regular_opticalsize_coord))[-1]
    assert status == PASS


def test_check_172():
  """ The variable font 'wght' (Weight) axis coordinate
      must be 700 on the 'Bold' instance. """
  from fontbakery.specifications.fvar import com_google_fonts_check_172 as check
  from fontbakery.specifications.shared_conditions import bold_wght_coord

  # Our reference varfont, CabinVFBeta.ttf, has
  # a bad Bold:wght coordinate
  ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
  bold_weight_coord = bold_wght_coord(ttFont)

  # So it must FAIL the test
  print('Test FAIL with a bad Bold:wght coordinate...')
  status, message = list(check(ttFont, bold_weight_coord))[-1]
  assert status == FAIL

  # We then fix the value:
  ttFont["fvar"].instances[3].coordinates["wght"] = 700
  # Note: I know the correct instance index for this hotfix because
  # I inspected the our reference CabinVF using ttx

  # Then re-read the coord:
  bold_weight_coord = bold_wght_coord(ttFont)

  # and now this should PASS the test:
  print('Test PASS with a good Bold:wght coordinage (700)...')
  status, message = list(check(ttFont, bold_weight_coord))[-1]
  assert status == PASS
