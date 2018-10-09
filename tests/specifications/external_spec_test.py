from fontbakery.checkrunner import Section
from fontbakery.fonts_spec import spec_factory


def check_filter(item_type, item_id, item):
  # Filter out external tool checks for testing purposes.
  if item_type == "check" and item_id in (
      "com.google.fonts/check/035",  # ftxvalidator
      "com.google.fonts/check/036",  # ots-sanitize
      "com.google.fonts/check/037",  # Font Validator
      "com.google.fonts/check/038",  # Fontforge
      "com.google.fonts/check/039",  # Fontforge
  ):
    return False

  return True


def test_external_specification():
  """Test the creation of external specifications."""
  specification = spec_factory(default_section=Section("Dalton Maag OpenType"))
  specification.auto_register(
      globals(),
      spec_imports=["fontbakery.specifications.opentype"],
      filter_func=check_filter)

  # Probe some tests
  expected_tests = ["com.google.fonts/check/002", "com.google.fonts/check/171"]
  specification.test_expected_checks(expected_tests)

  # Probe tests we don't want
  assert "com.google.fonts/check/035" not in specification._check_registry.keys()

  assert len(specification.sections) > 1

def test_spec_imports():
  """
    When a names array in spec_imports contained sub module names, the import
    would fail.

    https://github.com/googlefonts/fontbakery/issues/1886
  """
  def _test(spec_imports, expected_tests,expected_conditions=tuple()):
    specification = spec_factory(default_section=Section("Testing"))
    specification.auto_register({}, spec_imports=spec_imports)
    specification.test_expected_checks(expected_tests)
    if expected_conditions:
      registered_conditions = specification.conditions.keys()
      for name in expected_conditions:
        assert name in registered_conditions, ('"{}" is expected to be '
                                  'registered as a condition.'.format(name))

  # this is in docs/writing specifications
  spec_imports = [
    ['fontbakery.specifications', ['cmap', 'head']]
  ]
  # Probe some tests
  expected_tests = [
      "com.google.fonts/check/076", # in cmap
      "com.google.fonts/check/043"  # in head
  ]
  _test(spec_imports, expected_tests)


  # the example from issue #1886
  spec_imports = (
    (
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
            "fvar",
            "shared_conditions",
        ),
    ),
  )
  # Probe some tests
  expected_tests = [
      "com.google.fonts/check/076", # in cmap
      "com.google.fonts/check/043"  # in head
  ]
  _test(spec_imports, expected_tests)


  # make sure the suggested workaround still works:
  # https://github.com/googlefonts/fontbakery/issues/1886#issuecomment-392535435
  spec_imports = (
      "fontbakery.specifications.general",
      "fontbakery.specifications.cmap",
      "fontbakery.specifications.head",
      "fontbakery.specifications.os2",
      "fontbakery.specifications.post",
      "fontbakery.specifications.name",
      "fontbakery.specifications.hhea",
      "fontbakery.specifications.dsig",
      "fontbakery.specifications.hmtx",
      "fontbakery.specifications.gpos",
      "fontbakery.specifications.gdef",
      "fontbakery.specifications.kern",
      "fontbakery.specifications.glyf",
      "fontbakery.specifications.fvar",
      "fontbakery.specifications.shared_conditions"
  )
  # Probe some tests
  expected_tests = [
      "com.google.fonts/check/076", # in cmap
      "com.google.fonts/check/043"  # in head
  ]
  _test(spec_imports, expected_tests)


  # cherry pick attributes from a module (instead of getting submodules)
  # also from this is in docs/writing specifications
  # Import just certain attributes from modules.
  # Also, using absolute import module names:
  spec_imports = [
      # like we do in fontbakery.specifications.fvar
      ('fontbakery.specifications.shared_conditions', ('is_variable_font',
              'regular_wght_coord', 'regular_wdth_coord', 'regular_slnt_coord',
              'regular_ital_coord', 'regular_opsz_coord', 'bold_wght_coord')),
      # just as an example: import a check and a dependency/condition of
      # that check from the googlefonts specific spec:
      ('fontbakery.specifications.googlefonts', (
          # "License URL matches License text on name table?"
          'com_google_fonts_check_030',
          # This condition is a dependency of the check above:
          'familyname',
      ))
  ]
  # Probe some tests
  expected_tests = [
      "com.google.fonts/check/030"  # in googlefonts
  ]
  expected_conditions = ('is_variable_font', 'regular_wght_coord',
        'regular_wdth_coord', 'regular_slnt_coord', 'regular_ital_coord',
        'regular_opsz_coord', 'bold_wght_coord', 'familyname')
  _test(spec_imports, expected_tests, expected_conditions)


def test_opentype_checks_load():
  spec_imports = ("fontbakery.specifications.opentype", )
  specification = spec_factory(default_section=Section("OpenType Testing"))
  specification.auto_register({}, spec_imports=spec_imports)
  specification.test_dependencies()


def test_googlefonts_checks_load():
  spec_imports = ("fontbakery.specifications.googlefonts", )
  specification = spec_factory(default_section=Section("Google Fonts Testing"))
  specification.auto_register({}, spec_imports=spec_imports)
  specification.test_dependencies()


def test_in_and_exclude_checks():
  spec_imports = ("fontbakery.specifications.opentype", )
  specification = spec_factory(default_section=Section("OpenType Testing"))
  specification.auto_register({}, spec_imports=spec_imports)
  specification.test_dependencies()
  explicit_checks = ["06", "07"]  # "06" or "07" in check ID
  exclude_checks = ["065", "079"]  # "065" or "079" in check ID
  iterargs = {"font": 1}
  check_names = {
      c[1].id for c in specification.execution_order(
          iterargs,
          explicit_checks=explicit_checks,
          exclude_checks=exclude_checks)
  }
  check_names_expected = set()
  for section in specification.sections:
    for check in section.checks:
      if any(i in check.id for i in explicit_checks) and not any(
          x in check.id for x in exclude_checks):
        check_names_expected.add(check.id)
  assert check_names == check_names_expected


def test_in_and_exclude_checks_default():
  spec_imports = ("fontbakery.specifications.opentype",)
  specification = spec_factory(default_section=Section("OpenType Testing"))
  specification.auto_register({}, spec_imports=spec_imports)
  specification.test_dependencies()
  explicit_checks = None  # "All checks aboard"
  exclude_checks = None  # "No checks left behind"
  iterargs = {"font": 1}
  check_names = {
      c[1].id for c in specification.execution_order(
          iterargs,
          explicit_checks=explicit_checks,
          exclude_checks=exclude_checks)
  }
  check_names_expected = set()
  for section in specification.sections:
    for check in section.checks:
      check_names_expected.add(check.id)
  assert check_names == check_names_expected
