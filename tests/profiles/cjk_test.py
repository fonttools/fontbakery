import pytest
from fontTools.ttLib import TTFont

from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


@pytest.fixture
def montserrat_ttFonts():
  paths = [
    TEST_FILE("montserrat/Montserrat-Black.ttf"),
    TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Bold.ttf"),
    TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Italic.ttf"),
    TEST_FILE("montserrat/Montserrat-Light.ttf"),
    TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Medium.ttf"),
    TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Regular.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Thin.ttf"),
    TEST_FILE("montserrat/Montserrat-ThinItalic.ttf")
  ]
  return [TTFont(path) for path in paths]


def test_check_cjk_example():
  """ check docstring """
  from fontbakery.profiles.cjk import com_google_fonts_check_cjk_example as check
  something = [
    TEST_FILE("cabin/Cabin-Thin.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]
  something_else = [
    TEST_FILE("mada/Mada-Regular.ttf"),
    TEST_FILE("cabin/Cabin-ExtraLight.ttf")
  ]
  print(f'Test PASS with something: {something}')
  status, message = list(check(something))[-1]
  assert status == PASS

  print(f'Test FAIL with something else: {something_else}')
  status, message = list(check(something_else))[-1]
  assert status == FAIL
