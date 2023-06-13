import os
import subprocess
import sys
import re
import pytest
import tempfile


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
        subprocess.check_output(["fontbakery", "--list-subcommands"]).decode().split()
    )
    assert sorted(scripts) == sorted(subcommands)


def test_command_check_googlefonts():
    """Test if `fontbakery check-googlefonts` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-googlefonts", "-h"])

    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

    subprocess.check_output(
        [
            "fontbakery",
            "check-googlefonts",
            "-c",
            "com.google.fonts/check/canonical_filename",
            test_font,
        ]
    )

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-googlefonts"])


@pytest.mark.xfail(
    strict=True
)  # This test is too much prone to failing whenever we update
# the text-output formatting or the actual log messages in that fontbakery check
# I would like to have this test refactored to be in a good state for much longer.
# Please, only remove the xfail mark once the test is more robust / future proof.
def test_status_log_is_indented():
    """Test if statuses are printed in a limited boundary."""
    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

    result = subprocess.run(
        [
            "fontbakery",
            "check-googlefonts",
            "-c",
            "old_ttfautohint",
            "-c",
            "font_copyright",
            test_font,
        ],
        capture_output=True,
    )

    p = re.compile("([^][a-zA-Z0-9@:,.()'\"\n ])", re.I | re.M)
    stdout = p.sub("#", result.stdout.decode()).split("\n")
    assert "\n".join(stdout[24:30]) == "\n".join(
        [
            "     #[0#31#40mFAIL#[0m Name Table entry: Copyright notices should match a      ",
            '          pattern similar to: "Copyright 2019 The Familyname Project Authors    ',
            '          (git url)"                                                            ',
            "          But instead we have got:                                              ",
            '          "Copyright 2014 The Nunito Project Authors (contact@sansoxygen.com)"  ',
            "          [code: bad#notice#format]                                             ",
        ]
    )
    assert "\n".join(stdout[10:15]) == "\n".join(
        [
            "     #[0#36#40mINFO#[0m Could not detect which version of ttfautohint was used  ",
            "          in this font. It is typically specified as a comment in the font      ",
            "          version entries of the 'name' table. Such font version strings are    ",
            "          currently: ['Version 3.000', 'Version 3.000'] [code:                  ",
            "          version#not#detected]                                                 ",
        ]
    )


def test_command_check_profile():
    """Test if `fontbakery check-profile` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-profile", "-h"])

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-profile"])


def test_command_check_opentype():
    """Test if `fontbakery check-opentype` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-opentype", "-h"])

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-opentype"])


def test_command_check_ufo_sources():
    """Test if `fontbakery check-ufo-sources` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-ufo-sources", "-h"])

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-ufo-sources"])


def test_command_config_file():
    """Test if we can set checks using a config file."""
    config = tempfile.NamedTemporaryFile(delete=False)
    config.write(b"explicit_checks = ['com.adobe.fonts/check/name/empty_records']")
    config.close()
    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")
    result = subprocess.run(
        ["fontbakery", "check-googlefonts", "--config", config.name, test_font],
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
            "fontbakery",
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
        ["fontbakery", "check-googlefonts", "-C", "--config", config.name, test_font],
        stdout=subprocess.PIPE,
    )
    stdout = result.stdout.decode()
    # This font has a WARN here, so should now FAIL
    assert "FAIL: 1" in stdout
    os.unlink(config.name)
