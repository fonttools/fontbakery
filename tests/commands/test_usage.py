import os
import subprocess
import re
import pytest


def test_list_subcommands_has_all_scripts():
    """Tests if the output from running `fontbakery --list-subcommands` matches
      the fontbakery scripts within the bin folder."""
    import fontbakery.commands
    commands_dir = os.path.dirname(fontbakery.commands.__file__)

    scripts = [
        f.rstrip(".py").replace("_", "-")
        for f in os.listdir(commands_dir)
        if (f.endswith(".py") and not f.startswith('_'))
    ]
    subcommands = subprocess.check_output(
        ['fontbakery', '--list-subcommands']).decode().split()
    assert sorted(scripts) == sorted(subcommands)


def test_command_check_googlefonts():
    """Test if `fontbakery check-googlefonts` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-googlefonts", "-h"])

    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

    subprocess.check_output([
        "fontbakery", "check-googlefonts", "-c", "com.google.fonts/check/canonical_filename",
        test_font
    ])

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-googlefonts"])


def test_status_log_is_indented():
    """Test if statuses are printed in a limited boundary."""
    test_font = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

    result = subprocess.run(["fontbakery", "check-googlefonts",
        "-c", "old_ttfautohint", "-c", "font_copyright",
        test_font], capture_output=True)

    p = re.compile('([^][a-zA-Z0-9@:,.()\'"\n ])', re.I | re.M)
    stdout = p.sub('#', result.stdout.decode()).split('\n')
    assert '\n'.join(stdout[24:30]) == '\n'.join([
    '     #[0#31#40mFAIL#[0m Name Table entry: Copyright notices should match a      ',
    '          pattern similar to: "Copyright 2019 The Familyname Project Authors    ',
    '          (git url)"                                                            ',
    '          But instead we have got:                                              ',
    '          "Copyright 2014 The Nunito Project Authors (contact@sansoxygen.com)"  ',
    '          [code: bad#notice#format]                                             '
    ])
    assert '\n'.join(stdout[10:15]) == '\n'.join([
    '     #[0#36#40mINFO#[0m Could not detect which version of ttfautohint was used  ',
    '          in this font. It is typically specified as a comment in the font      ',
    "          version entries of the 'name' table. Such font version strings are    ",
    "          currently: ['Version 3.000', 'Version 3.000'] [code:                  ",
    '          version#not#detected]                                                 '
    ])


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
