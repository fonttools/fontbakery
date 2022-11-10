from fontbakery.section import Section
from fontbakery.fonts_profile import profile_factory


def check_filter(item_type, item_id, item):
    # Filter out external tool checks for testing purposes.
    if item_type == "check" and item_id in (
        "com.google.fonts/check/ots",
        "com.google.fonts/check/fontvalidator",
    ):
        return False

    return True


def test_external_profile():
    """Test the creation of external profiles."""
    profile = profile_factory(default_section=Section("Dalton Maag OpenType"))
    profile.auto_register(
        globals(),
        profile_imports=["fontbakery.profiles.opentype"],
        filter_func=check_filter)

    # Probe some tests
    expected_tests = ["com.google.fonts/check/family/panose_proportion",
                      "com.google.fonts/check/varfont/regular_opsz_coord"]
    profile.test_expected_checks(expected_tests)

    # Probe tests we don't want
    assert "com.google.fonts/check/fontvalidator" not in profile._check_registry.keys()

    assert len(profile.sections) > 1

def test_profile_imports():
    """
      When a names array in profile_imports contained sub module names, the import
      would fail.

      https://github.com/googlefonts/fontbakery/issues/1886
    """
    def _test(profile_imports, expected_tests,expected_conditions=tuple()):
        profile = profile_factory(default_section=Section("Testing"))
        profile.auto_register({}, profile_imports=profile_imports)
        profile.test_expected_checks(expected_tests)
        if expected_conditions:
            registered_conditions = profile.conditions.keys()
            for name in expected_conditions:
                assert name in registered_conditions, \
                       f'"{name}" is expected to be registered as a condition.'

    # this is in docs/writing profiles
    profile_imports = [
        ['fontbakery.profiles', ['cmap', 'head']]
    ]
    # Probe some tests
    expected_tests = [
        "com.google.fonts/check/unitsperem"  # in head
    ]
    _test(profile_imports, expected_tests)


    # the example from issue #1886
    profile_imports = (
        (
            "fontbakery.profiles",
            (
                "cmap",
                "head",
                "os2",
                "post",
                "name",
                "hhea",
                "dsig",
                "gpos",
                "kern",
                "glyf",
                "fvar",
                "shared_conditions",
            ),
        ),
    )
    # Probe some tests
    expected_tests = [
        "com.google.fonts/check/unitsperem"  # in head
    ]
    _test(profile_imports, expected_tests)


    # make sure the suggested workaround still works:
    # https://github.com/googlefonts/fontbakery/issues/1886#issuecomment-392535435
    profile_imports = (
        "fontbakery.profiles.cmap",
        "fontbakery.profiles.head",
        "fontbakery.profiles.os2",
        "fontbakery.profiles.post",
        "fontbakery.profiles.name",
        "fontbakery.profiles.hhea",
        "fontbakery.profiles.dsig",
        "fontbakery.profiles.gpos",
        "fontbakery.profiles.kern",
        "fontbakery.profiles.glyf",
        "fontbakery.profiles.fvar",
        "fontbakery.profiles.shared_conditions"
    )
    # Probe some tests
    expected_tests = [
        "com.google.fonts/check/unitsperem"  # in head
    ]
    _test(profile_imports, expected_tests)


    # cherry pick attributes from a module (instead of getting submodules)
    # also from this is in docs/writing profiles
    # Import just certain attributes from modules.
    # Also, using absolute import module names:
    profile_imports = [
        # like we do in fontbakery.profiles.fvar
        ('fontbakery.profiles.shared_conditions', ('is_variable_font',
            'regular_wght_coord', 'regular_wdth_coord', 'regular_slnt_coord',
            'regular_ital_coord', 'regular_opsz_coord', 'bold_wght_coord')),
        # just as an example: import a check and a dependency/condition of
        # that check from the googlefonts specific profile:
        ('fontbakery.profiles.googlefonts', (
            # "License URL matches License text on name table?"
            'com_google_fonts_check_name_license_url',
            # This condition is a dependency of the check above:
            'familyname',
        ))
    ]
    # Probe some tests
    expected_tests = [
        "com.google.fonts/check/name/license_url"  # in googlefonts
    ]
    expected_conditions = ('is_variable_font', 'regular_wght_coord',
        'regular_wdth_coord', 'regular_slnt_coord', 'regular_ital_coord',
        'regular_opsz_coord', 'bold_wght_coord', 'familyname')
    _test(profile_imports, expected_tests, expected_conditions)


def test_opentype_checks_load():
    profile_imports = ("fontbakery.profiles.opentype", )
    profile = profile_factory(default_section=Section("OpenType Testing"))
    profile.auto_register({}, profile_imports=profile_imports)
    profile.test_dependencies()


def test_googlefonts_checks_load():
    profile_imports = ("fontbakery.profiles.googlefonts", )
    profile = profile_factory(default_section=Section("Google Fonts Testing"))
    profile.auto_register({}, profile_imports=profile_imports)
    profile.test_dependencies()


def test_in_and_exclude_checks():
    profile_imports = ("fontbakery.profiles.opentype", )
    profile = profile_factory(default_section=Section("OpenType Testing"))
    profile.auto_register({}, profile_imports=profile_imports)
    profile.test_dependencies()
    explicit_checks = ["06", "07"]  # "06" or "07" in check ID
    exclude_checks = ["065", "079"]  # "065" or "079" in check ID
    iterargs = {"font": 1}
    check_names = {
        c[1].id for c in \
            profile.execution_order(iterargs,
                                    explicit_checks=explicit_checks,
                                    exclude_checks=exclude_checks)
    }
    check_names_expected = set()
    for section in profile.sections:
        for check in section.checks:
            if any(i in check.id
                   for i in explicit_checks) and \
               not any(x in check.id
                       for x in exclude_checks):
                check_names_expected.add(check.id)
    assert check_names == check_names_expected


def test_in_and_exclude_checks_default():
    profile_imports = ("fontbakery.profiles.opentype",)
    profile = profile_factory(default_section=Section("OpenType Testing"))
    profile.auto_register({}, profile_imports=profile_imports)
    profile.test_dependencies()
    explicit_checks = None  # "All checks aboard"
    exclude_checks = None  # "No checks left behind"
    iterargs = {"font": 1}
    check_names = {
        c[1].id for c in \
            profile.execution_order(iterargs,
                                    explicit_checks=explicit_checks,
                                    exclude_checks=exclude_checks)
    }
    check_names_expected = set()
    for section in profile.sections:
        for check in section.checks:
            check_names_expected.add(check.id)
    assert check_names == check_names_expected
