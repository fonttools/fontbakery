from fontbakery.checkrunner import Section
from fontbakery.fonts_spec import spec_factory

spec_imports = ((
    "fontbakery.specifications",
    (
        "general",
        "cmap",
        "head",
        "os2",
        "post",
        "name",
        "hhea",
        "dsig",
        "hmtx",
        "gpos",
        "gdef",
        "kern",
        "glyf",
        "prep",
        "fvar",
        "shared_conditions",
    ),
),)


def check_filter(checkid, font=None, **iterargs):
  if checkid in (
      "com.google.fonts/check/035",
      "com.google.fonts/check/036",
      "com.google.fonts/check/037",
      "com.google.fonts/check/038",
      "com.google.fonts/check/039",
  ):
    return False, ("Skipping external tools.")
  return True, None


specification = spec_factory(default_section=Section("Dalton Maag OpenType"))
specification.auto_register(globals(), filter_func=check_filter)


def test_external_specification():
  """Test the creation of external specifications."""
  assert specification
