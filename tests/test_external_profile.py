from fontbakery.checkrunner import CheckRunner
from fontbakery.codetesting import TEST_FILE
from fontbakery.fonts_profile import profile_factory, setup_context
import fontbakery.profiles.opentype


def check_filter(item_type, item_id, item):
    # Filter out external tool checks for testing purposes.
    if item_type == "check" and item_id in (
        "ots",
        "fontvalidator",
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
            "include_profiles": ["universal"],
            "sections": {
                "Dalton Maag OpenType": [
                    "opentype/family/panose_familytype",
                    "opentype/fvar/regular_coords_correct",
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
    expected_tests = ["opentype/unitsperem"]  # in head
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

    checks = profile_checks(fakemodule, {"exclude_checks": ["opentype/unitsperem"]})
    assert "opentype/unitsperem" not in checks

    checks = profile_checks(fakemodule, {"explicit_checks": ["opentype/unitsperem"]})
    assert checks == ["opentype/unitsperem"]


def test_exclude_checks_old_ids():
    from fontbakery.legacy_checkids import renaming_map

    fakemodule = FakeModule()
    setattr(
        fakemodule,
        "PROFILE",
        {
            "include_profiles": ["microsoft"],
            "sections": {},
        },
    )

    old = "com.microsoft/check/vendor_url"
    new = renaming_map[old]

    checks = profile_checks(fakemodule)
    assert new in checks

    checks = profile_checks(fakemodule, {"exclude_checks": [old]})
    assert new not in checks
