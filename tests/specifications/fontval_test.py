import os
import pytest

from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import ERROR


def test_check_037():
  """ MS Font Validator checks """
  from fontbakery.specifications.fontval import com_google_fonts_check_037 as check

  font = TEST_FILE("mada/Mada-Regular.ttf")
  # we want to run all FValidator checks only once,
  # so here we cache all results:
  fval_results = list(check(font))

  # Then we make sure that there wasn't an ERROR
  # which would mean FontValidator is not properly installed:
  for status, message in fval_results:
    assert status != ERROR

  # Simulate FontVal missing.
  old_path = os.environ["PATH"]
  os.environ["PATH"] = ""
  with pytest.raises(OSError) as _:
    status, message = list(check(font))[-1]
    assert status == ERROR
  os.environ["PATH"] = old_path
