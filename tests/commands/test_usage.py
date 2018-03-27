import os
import subprocess

import pytest


def test_list_subcommands_has_all_scripts():
    """Tests if the output from running `fontbakery --list-subcommands` matches
    the fontbakery scripts within the bin folder."""
    import fontbakery.commands
    commands_dir = os.path.dirname(fontbakery.commands.__file__)

    scripts = [
        f.rstrip(".py").replace("_", "-") for f in os.listdir(commands_dir)
        if (f.endswith(".py") and not f.startswith('_'))
    ]
    subcommands = subprocess.check_output(['fontbakery',
                                           '--list-subcommands']).split()
    assert sorted(scripts) == sorted(subcommands)


def test_command_check_googlefonts():
    """Test if `fontbakery check-googlefonts` can run successfully`."""
    subprocess.check_output(["fontbakery", "check-googlefonts", "-h"])

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(["fontbakery", "check-googlefonts"])
