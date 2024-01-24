import argparse
import sys
from unittest.mock import patch

import pytest

from fontbakery.constants import (
    NO_COLORS_THEME,
    DARK_THEME,
    LIGHT_THEME,
)
from fontbakery.utils import (
    apple_terminal_bg_is_white,
    bullet_list,
    exit_with_install_instructions,
    get_apple_terminal_bg_color,
    get_theme,
    html5_collapsible,
    is_negated,
    pretty_print_list,
    split_camel_case,
    unindent_and_unwrap_rationale,
)


def test_exit_with_install_instructions():
    from fontbakery.utils import set_profile_name

    profile_name = "test-profile"
    set_profile_name(profile_name)
    with patch("sys.exit") as mock_exit:
        exit_with_install_instructions()
        mock_exit.assert_called_with(
            f"\nTo run the {profile_name} profile, one needs to install\n"
            f"fontbakery with the '{profile_name}' extra, like this:\n\n"
            f"    python -m pip install -U 'fontbakery[{profile_name}]'\n\n"
        )


def test_remove_white_space():
    from fontbakery.utils import remove_white_space

    assert remove_white_space("\t  ab \n\tcd  ef ") == "abcdef"


@pytest.mark.parametrize(
    "input_str, expected_tup",
    [
        ("", (False, "")),
        (" ", (False, "")),
        ("abc", (False, "abc")),
        (" abc ", (False, "abc")),
        ("not", (False, "not")),
        ("not ", (False, "not")),
        (" not ", (False, "not")),
        ("notabc", (False, "notabc")),
        ("not abc", (True, "abc")),
        ("not  abc", (True, "abc")),
        (" not  abc ", (True, "abc")),
    ],
)
def test_is_negated(input_str, expected_tup):
    assert is_negated(input_str) == expected_tup


@patch("subprocess.run")
def test_get_apple_terminal_bg_color(mock_subproc):
    subproc_output = "6424, 6425, 6425\n"
    mock_subproc.return_value.stdout = subproc_output
    assert get_apple_terminal_bg_color() == subproc_output.strip()


@pytest.mark.parametrize(
    "rgb_str, term_prog, expected_bool",
    [
        (None, "", False),
        (None, "iTerm.app", False),
        ("", "Apple_Terminal", False),
        ("65535, 65535, 65535", "Apple_Terminal", True),
    ],
)
@patch("fontbakery.utils.get_apple_terminal_bg_color")
def test_apple_terminal_bg_is_white(
    mock_get_bg_color, rgb_str, term_prog, expected_bool, monkeypatch
):
    monkeypatch.setenv("TERM_PROGRAM", term_prog)
    mock_get_bg_color.return_value = rgb_str
    assert apple_terminal_bg_is_white() is expected_bool


@pytest.mark.parametrize(
    "args, expected_theme",
    [
        (
            # args.no_colors is True
            argparse.Namespace(no_colors=True, light_theme=False, dark_theme=False),
            NO_COLORS_THEME,
        ),
        (
            # args.light_theme is True
            argparse.Namespace(no_colors=False, light_theme=True, dark_theme=False),
            LIGHT_THEME,
        ),
        (
            # args.dark_theme is True
            argparse.Namespace(no_colors=False, light_theme=False, dark_theme=True),
            DARK_THEME,
        ),
        (
            # None of the theme flags is True
            argparse.Namespace(no_colors=False, light_theme=False, dark_theme=False),
            DARK_THEME,
        ),
        (
            # Multiple theme flags are True (Should return the first True theme)
            argparse.Namespace(no_colors=True, light_theme=True, dark_theme=True),
            NO_COLORS_THEME,
        ),
    ],
)
def test_get_theme(args, expected_theme):
    assert get_theme(args) == expected_theme


@pytest.mark.parametrize(
    "platform, bg_is_white, expected_theme",
    [
        ("", None, DARK_THEME),
        ("linux", None, DARK_THEME),
        ("win32", None, DARK_THEME),
        ("darwin", True, LIGHT_THEME),
        ("darwin", False, DARK_THEME),
    ],
)
@patch("fontbakery.utils.apple_terminal_bg_is_white")
def test_get_theme_on_macos(
    mock_bg_is_white, platform, bg_is_white, expected_theme, monkeypatch
):
    mock_bg_is_white.return_value = bg_is_white
    monkeypatch.setattr(sys, "platform", platform)
    args = argparse.Namespace(no_colors=False, light_theme=False, dark_theme=False)
    assert get_theme(args) == expected_theme


def test_unindent_and_unwrap_rationale():
    rationale = """
        This is a line that is very long, so long in fact that it must be hard wrapped
        because it is longer than 88 lines, including the two 4-space indents.

        This is a new paragraph. This paragraph is also too long to fit within the
        maximum width, so it must be hard wrapped.
        This is a new line that was NOT soft-wrapped, so it will end up appendend to
        the previous line.⏎
        This is yet another line, but this one was soft-wrapped (Shift+Return), which
        means that it will not be appendend to the end of the previous line.

        This is the last paragraph.
    """
    expected_rationale = (
        "\n"
        "This is a line that is very long, so long in fact that it must be hard wrapped"
        " because it is longer than 88 lines, including the two 4-space indents.\n"
        "\n"
        "This is a new paragraph. This paragraph is also too long to fit within the"
        " maximum width, so it must be hard wrapped."
        " This is a new line that was NOT soft-wrapped, so it will end up appendend to"
        " the previous line.\n"
        "This is yet another line, but this one was soft-wrapped (Shift+Return), which"
        " means that it will not be appendend to the end of the previous line.\n"
        "\n"
        "This is the last paragraph."
        "\n"
    )
    assert unindent_and_unwrap_rationale(rationale) == expected_rationale


def test_html5_collapsible():
    assert (
        html5_collapsible("abc", "ABC")
        == "<details><summary>abc</summary><div>ABC</div></details>"
    )


def test_split_camel_case():
    assert split_camel_case("") == ""
    assert split_camel_case("abc") == "abc"
    assert split_camel_case("Abc") == "Abc"
    assert split_camel_case("abC") == "ab C"
    assert split_camel_case("AbC") == "Ab C"
    assert split_camel_case("ABC") == "A B C"
    assert split_camel_case("Lobster") == "Lobster"
    assert split_camel_case("LibreCaslonText") == "Libre Caslon Text"


def _make_values(count: int) -> list:
    """Helper method that returns a list with 'count' number of items"""
    return [f"item {i}" for i in range(1, count + 1)]


@pytest.mark.parametrize(
    "values, expected_str",
    [
        # (_make_values(0), ""),  # causes IndexError
        (_make_values(1), "item 1"),
        (_make_values(2), "item 1 and item 2"),
        (_make_values(3), "item 1, item 2 and item 3"),
        (_make_values(4), "item 1, item 2, item 3 and item 4"),
        (
            _make_values(12),
            (
                "item 1, item 2, item 3, item 4, item 5, item 6, item 7,"
                " item 8, item 9, item 10, item 11 and item 12"
            ),
        ),
    ],
)
def test_pretty_print_list_full(values, expected_str):
    config = {"full_lists": True}
    assert pretty_print_list(config, values) == expected_str
    assert pretty_print_list(config, values, shorten=3) == expected_str
    assert pretty_print_list(config, values, sep=" + ") == expected_str.replace(
        ", ", " + "
    )
    assert pretty_print_list(config, values, glue=" & ") == expected_str.replace(
        "and", "&"
    )


MORE_MSG = "\n\nUse -F or --full-lists to disable shortening of long lists."


@pytest.mark.parametrize(
    "values, shorten, expected_str",
    [
        (_make_values(1), None, "item 1"),
        (_make_values(1), 0, "item 1"),
        (_make_values(1), 1, "item 1"),
        (_make_values(1), 2, "item 1"),
        (_make_values(2), None, "item 1 and item 2"),
        (_make_values(2), 0, "item 1 and item 2"),
        (_make_values(2), 1, "item 1 and item 2"),
        (_make_values(2), 2, "item 1 and item 2"),
        (_make_values(2), 3, "item 1 and item 2"),
        (_make_values(3), None, "item 1, item 2 and item 3"),
        (_make_values(3), 1, "item 1, item 2 and item 3"),
        (_make_values(3), 2, "item 1, item 2 and item 3"),
        (_make_values(3), 3, "item 1, item 2 and item 3"),
        (_make_values(3), 4, "item 1, item 2 and item 3"),
        (_make_values(4), None, "item 1, item 2, item 3 and item 4"),
        (_make_values(4), 0, "item 1, item 2, item 3 and item 4"),
        (_make_values(4), 1, f"item 1 and 3 more.{MORE_MSG}"),
        (_make_values(4), 2, "item 1, item 2, item 3 and item 4"),
        (_make_values(4), 3, "item 1, item 2, item 3 and item 4"),
        (_make_values(4), 4, "item 1, item 2, item 3 and item 4"),
        (_make_values(4), 5, "item 1, item 2, item 3 and item 4"),
        (_make_values(5), None, "item 1, item 2, item 3, item 4 and item 5"),
        (_make_values(5), 0, "item 1, item 2, item 3, item 4 and item 5"),
        (_make_values(5), 1, f"item 1 and 4 more.{MORE_MSG}"),
        (_make_values(5), 2, f"item 1, item 2 and 3 more.{MORE_MSG}"),
        (_make_values(5), 3, "item 1, item 2, item 3, item 4 and item 5"),
        (_make_values(5), 4, "item 1, item 2, item 3, item 4 and item 5"),
        (_make_values(5), 5, "item 1, item 2, item 3, item 4 and item 5"),
        (_make_values(5), 6, "item 1, item 2, item 3, item 4 and item 5"),
        (
            _make_values(12),
            None,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6, item 7,"
                " item 8, item 9, item 10, item 11 and item 12"
            ),
        ),
        (
            _make_values(12),
            0,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6, item 7,"
                " item 8, item 9, item 10, item 11 and item 12"
            ),
        ),
        (_make_values(12), 1, f"item 1 and 11 more.{MORE_MSG}"),
        (
            _make_values(12),
            6,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6"
                f" and 6 more.{MORE_MSG}"
            ),
        ),
        (
            _make_values(13),
            None,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6, item 7,"
                f" item 8, item 9, item 10 and 3 more.{MORE_MSG}"
            ),
        ),
        (
            _make_values(13),
            0,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6, item 7,"
                " item 8, item 9, item 10, item 11, item 12 and item 13"
            ),
        ),
        (_make_values(13), 1, f"item 1 and 12 more.{MORE_MSG}"),
        (
            _make_values(13),
            6,
            (
                "item 1, item 2, item 3, item 4, item 5, item 6"
                f" and 7 more.{MORE_MSG}"
            ),
        ),
    ],
)
def test_pretty_print_list_shorten(values, shorten, expected_str):
    config = {}
    if shorten is not None:
        assert pretty_print_list(config, values, shorten=shorten) == expected_str
    else:
        assert pretty_print_list(config, values) == expected_str


@pytest.mark.parametrize(
    "values, expected_str",
    [
        (_make_values(1), "\t- item 1"),
        (_make_values(2), "\t- item 1\n\n\t- item 2"),
        (_make_values(3), "\t- item 1\n\n\t- item 2\n\n\t- item 3"),
        (_make_values(4), "\t- item 1\n\n\t- item 2\n\n\t- item 3\n\n\t- item 4"),
    ],
)
def test_bullet_list(values, expected_str):
    config = {"full_lists": True}
    assert bullet_list(config, values) == expected_str
    assert bullet_list(config, values, bullet="*") == expected_str.replace("-", "*")
    assert bullet_list(config, values, indentation="") == expected_str.replace("\t", "")
