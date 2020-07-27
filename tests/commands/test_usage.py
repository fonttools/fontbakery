import os
import subprocess

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
