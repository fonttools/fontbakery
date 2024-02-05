from fontbakery.fonts_profile import profile_factory


def check_filter(item_type, item_id, item):
    # Filter out external tool checks for testing purposes.
    if item_type == "check" and item_id in (
        "com.google.fonts/check/ots",
        "com.google.fonts/check/fontvalidator",
    ):
        return False

    return True


class FakeModule:
    PROFILE = None


def test_external_profile():
    """Test the creation of external profiles."""
    fakemodule = FakeModule()
    setattr(
        fakemodule,
        "PROFILE",
        {
            "include_profiles": ["opentype"],
            "sections": {
                "Dalton Maag OpenType": [
                    "com.google.fonts/check/family/panose_proportion",
                    "com.google.fonts/check/varfont/regular_opsz_coord",
                ]
            },
        },
    )
    profile = profile_factory(fakemodule)

    # Probe some tests
    expected_tests = [
        "com.google.fonts/check/family/panose_proportion",
        "com.google.fonts/check/varfont/regular_opsz_coord",
    ]
    profile.test_expected_checks(expected_tests)

    # Probe tests we don't want
    assert "com.google.fonts/check/fontvalidator" not in profile._check_registry.keys()

    assert len(profile.sections) > 1


def test_profile_imports():
    """
    When a names array in profile_imports contained sub module names, the import
    would fail.

    https://github.com/fonttools/fontbakery/issues/1886
    """

    def _test(profile_imports, expected_tests, expected_conditions=tuple()):
        fakemodule = FakeModule()
        setattr(
            fakemodule,
            "PROFILE",
            {"sections": {"Testing": []}, "include_profiles": profile_imports},
        )

        profile = profile_factory(fakemodule)
        profile.test_expected_checks(expected_tests)
        if expected_conditions:
            registered_conditions = profile.conditions.keys()
            for name in expected_conditions:
                assert (
                    name in registered_conditions
                ), f'"{name}" is expected to be registered as a condition.'

    # this is in docs/writing profiles
    profile_imports = ["universal"]
    # Probe some tests
    expected_tests = ["com.google.fonts/check/unitsperem"]  # in head
    _test(profile_imports, expected_tests)


def test_in_and_exclude_checks():
    fakemodule = FakeModule()
    setattr(
        fakemodule,
        "PROFILE",
        {
            "include_profiles": ["opentype"],
            "exclude_checks": ["065", "079"],
            "sections": {},
        },
    )

    profile = profile_factory(fakemodule)
    explicit_checks = ["06", "07"]  # "06" or "07" in check ID
    exclude_checks = ["065", "079"]  # "065" or "079" in check ID
    iterargs = {"font": 1}
    check_names = {
        c[1].id
        for c in profile.execution_order(
            iterargs, explicit_checks=explicit_checks, exclude_checks=exclude_checks
        )
    }
    check_names_expected = set()
    for section in profile.sections:
        for check in section.checks:
            if any(i in check.id for i in explicit_checks) and not any(
                x in check.id for x in exclude_checks
            ):
                check_names_expected.add(check.id)
    assert check_names == check_names_expected


def test_in_and_exclude_checks_default():
    fakemodule = FakeModule()
    setattr(
        fakemodule,
        "PROFILE",
        {
            "include_profiles": ["opentype"],
            "sections": {},
        },
    )
    profile = profile_factory(fakemodule)
    explicit_checks = None  # "All checks aboard"
    exclude_checks = None  # "No checks left behind"
    iterargs = {"font": 1}
    check_names = {
        c.check.id
        for c in profile.execution_order(
            iterargs, explicit_checks=explicit_checks, exclude_checks=exclude_checks
        )
    }
    check_names_expected = set()
    for section in profile.sections:
        for check in section.checks:
            check_names_expected.add(check.id)
    assert check_names == check_names_expected
