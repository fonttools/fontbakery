from fontbakery.checkrunner import Section
from fontbakery.fonts_spec import spec_factory


def check_filter(checkid, font=None, **iterargs):
  if checkid in (
      "com.google.fonts/check/035",  # ftxvalidator
      "com.google.fonts/check/036",  # ots-sanitize
      "com.google.fonts/check/037",  # Font Validator
      "com.google.fonts/check/038",  # Fontforge
      "com.google.fonts/check/039",  # Fontforge
  ):
    return False, "Skipping external tools."

  return True, None


def test_external_specification():
  """Test the creation of external specifications."""
  specification = spec_factory(default_section=Section("Dalton Maag OpenType"))
  specification.set_check_filter(check_filter)
  specification.auto_register(
      globals(), spec_imports=["fontbakery.specifications.opentype"])

  # Probe some tests
  expected_tests = ["com.google.fonts/check/002", "com.google.fonts/check/180"]
  specification.test_expected_checks(expected_tests)

  # Probe tests we don't want
  assert "com.google.fonts/check/035" not in specification._check_registry.keys()

  assert len(specification.sections) > 1
