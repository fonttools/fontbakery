import os
import re
import subprocess
import tempfile

import pytest

TOOL_NAME = "fontbakery"


def test_list_subcommands_has_all_scripts():
    """Tests if the output from running `fontbakery --list-subcommands` matches
    the fontbakery scripts within the bin folder and the promoted profiles."""
    import fontbakery.commands
    from fontbakery.cli import CLI_PROFILES

    commands_dir = os.path.dirname(fontbakery.commands.__file__)

    scripts = [
        f.rstrip(".py").replace("_", "-")
        for f in os.listdir(commands_dir)
        if (f.endswith(".py") and not f.startswith("_"))
    ]
    scripts = scripts + [("check-" + i).replace("_", "-") for i in CLI_PROFILES]
    subcommands = (
        subprocess.check_output([TOOL_NAME, "--list-subcommands"]).decode().split()
    )
    assert sorted(scripts) == sorted(subcommands)


def test_list_checks_option(capfd):
    """Test if 'fontbakery <subcommand> --list-checks' can run successfully and output
    the expected content."""
    from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

    subprocess.run([TOOL_NAME, "check-universal", "--list-checks"], check=True)
    output = capfd.readouterr().out
    assert set(output.split()) == set(UNIVERSAL_PROFILE_CHECKS)


def test_command_check_googlefonts():
    """Test if 'fontbakery check-googlefonts' can run successfully."""
    subprocess.run([TOOL_NAME, "check-googlefonts", "-h"], check=True)
    subprocess.run(
        [
            TOOL_NAME,
            "check-googlefonts",
            "-c",
            "com.google.fonts/check/canonical_filename",
            os.path.join("data", "test", "nunito", "Nunito-Regular.ttf"),
        ],
        check=True,
    )
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([TOOL_NAME, "check-googlefonts"], check=True)


@pytest.mark.parametrize(
    "subcommand",
    [
        "check-profile",
        "check-opentype",
        "check-ufo-sources",
    ],
)
def test_command_check_profile(subcommand):
    """Test if 'fontbakery <subcommand>' can run successfully."""
    subprocess.run([TOOL_NAME, subcommand, "-h"], check=True)

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([TOOL_NAME, subcommand], check=True)


def test_tool_help():
    """Test if just 'fontbakery' command can run successfully."""
    assert subprocess.run([TOOL_NAME, "-h"]).returncode == 0
    assert subprocess.run([TOOL_NAME]).returncode == 0


@pytest.mark.xfail(
    strict=True
)  # This test is too much prone to failing whenever we update
# the text-output formatting or the actual log messages in that fontbakery check
# I would like to have this test refactored to be in a good state for much longer.
# Please, only remove the xfail mark once the test is more robust / future proof.
def test_status_log_is_indented():
    """Test if statuses are printed in a limited boundary."""
    result = subprocess.run(
        [
            TOOL_NAME,
            "check-googlefonts",
            "-c",
            "old_ttfautohint",
            "-c",
            "font_copyright",
            os.path.join("data", "test", "nunito", "Nunito-Regular.ttf"),
        ],
        capture_output=True,
    )

    p = re.compile("([^][a-zA-Z0-9@:,.()'\"\n ])", re.I | re.M)
    stdout = p.sub("#", result.stdout.decode()).split("\n")
    assert "\n".join(stdout[24:30]) == "\n".join(
        [
            "     #[0#31#40mFAIL#[0m Name Table entry: Copyright notices should match a      ",  # noqa:E501 pylint:disable=C0301
            '          pattern similar to: "Copyright 2019 The Familyname Project Authors    ',  # noqa:E501 pylint:disable=C0301
            '          (git url)"                                                            ',  # noqa:E501 pylint:disable=C0301
            "          But instead we have got:                                              ",  # noqa:E501 pylint:disable=C0301
            '          "Copyright 2014 The Nunito Project Authors (contact@sansoxygen.com)"  ',  # noqa:E501 pylint:disable=C0301
            "          [code: bad#notice#format]                                             ",  # noqa:E501 pylint:disable=C0301
        ]
    )
    assert "\n".join(stdout[10:15]) == "\n".join(
        [
            "     #[0#36#40mINFO#[0m Could not detect which version of ttfautohint was used  ",  # noqa:E501 pylint:disable=C0301
            "          in this font. It is typically specified as a comment in the font      ",  # noqa:E501 pylint:disable=C0301
            "          version entries of the 'name' table. Such font version strings are    ",  # noqa:E501 pylint:disable=C0301
            "          currently: ['Version 3.000', 'Version 3.000'] [code:                  ",  # noqa:E501 pylint:disable=C0301
            "          version#not#detected]                                                 ",  # noqa:E501 pylint:disable=C0301
        ]
    )


def test_command_config_file():
    """Test if we can set checks using a config file."""
    config = tempfile.NamedTemporaryFile(delete=False)
    config.write(b"explicit_checks = ['com.adobe.fonts/check/name/empty_records']")
    config.close()
    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")
    result = subprocess.run(
        [TOOL_NAME, "check-googlefonts", "--config", config.name, test_font],
        stdout=subprocess.PIPE,
    )
    stdout = result.stdout.decode()
    assert "running 1 individual check" in stdout
    os.unlink(config.name)


def test_command_config_file_injection():
    """Test if we can inject a config variable into a check."""
    config = tempfile.NamedTemporaryFile(delete=False)
    config.write(
        b"""
[a_test_profile]
OK = 123
"""
    )
    config.close()
    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")
    test_profile = os.path.join("tests", "profiles", "a_test_profile.py")
    result = subprocess.run(
        [
            TOOL_NAME,
            "check-profile",
            "-C",
            "--config",
            config.name,
            test_profile,
            test_font,
        ],
        stdout=subprocess.PIPE,
    )
    stdout = result.stdout.decode()
    assert "FAIL: 0" in stdout
    os.unlink(config.name)


def test_config_override():
    """Test we can override check statuses in the configuration file"""
    config = tempfile.NamedTemporaryFile(delete=False)
    config.write(
        b"""
overrides:
  com.google.fonts/check/file_size:
    large-font: FAIL
explicit_checks:
  - com.google.fonts/check/file_size
"""
    )
    config.close()
    test_font = os.path.join("data", "test", "varfont", "inter", "Inter[slnt,wght].ttf")
    result = subprocess.run(
        [TOOL_NAME, "check-googlefonts", "-C", "--config", config.name, test_font],
        stdout=subprocess.PIPE,
    )
    stdout = result.stdout.decode()
    # This font has a WARN here, so should now FAIL
    assert "FAIL: 1" in stdout
    os.unlink(config.name)
