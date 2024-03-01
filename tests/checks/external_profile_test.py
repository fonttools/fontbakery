from fontbakery.checkrunner import CheckRunner
from fontbakery.codetesting import TEST_FILE
from fontbakery.fonts_profile import profile_factory, setup_context
import fontbakery.profiles.opentype


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
                    "com.google.fonts/check/family/panose_familytype",
                    "com.google.fonts/check/varfont/regular_opsz_coord",
                ]
            },
        },
    )
    profile = profile_factory(fakemodule)

    assert len(profile.sections) > 1


def profile_checks(module, config=None):
    if not config:
        config = {}
    context = setup_context([TEST_FILE("nunito/Nunito-Regular.ttf")])
    opentypeprofile = profile_factory(module)
    expected_order = CheckRunner(opentypeprofile, context, config).order
    return [identity.check.id for identity in expected_order]


def test_profile_imports():
    """
    When a names array in profile_imports contained sub module names, the import
    would fail.

    https://github.com/fonttools/fontbakery/issues/1886
    """

    def _test(profile_imports, expected_checks, expected_conditions=tuple()):
        fakemodule = FakeModule()
        setattr(
            fakemodule,
            "PROFILE",
            {"sections": {"Testing": []}, "include_profiles": profile_imports},
        )

        checks = profile_checks(fakemodule)
        for check in expected_checks:
            assert check in checks

    # this is in docs/writing profiles
    profile_imports = ["universal"]
    # Probe some tests
    expected_tests = ["com.google.fonts/check/unitsperem"]  # in head
    _test(profile_imports, expected_tests)


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
    opentype_checks = profile_checks(fontbakery.profiles.opentype)
    checks = profile_checks(fakemodule)

    assert checks == opentype_checks

    checks = profile_checks(
        fakemodule, {"exclude_checks": ["com.google.fonts/check/unitsperem"]}
    )
    assert "com.google.fonts/check/unitsperem" not in checks

    checks = profile_checks(
        fakemodule, {"explicit_checks": ["com.google.fonts/check/unitsperem"]}
    )
    assert checks == ["com.google.fonts/check/unitsperem"]
