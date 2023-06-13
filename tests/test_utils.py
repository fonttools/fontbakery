import pytest

from fontbakery.utils import (
    bullet_list,
    can_shape,
    pretty_print_list,
    text_flow,
    unindent_and_unwrap_rationale,
)
from fontTools.ttLib import TTFont
from fontbakery.codetesting import portable_path


def test_text_flow():
    assert text_flow("") == ""

    assert text_flow("Testing") == "Testing"

    assert text_flow("One Two Three") == "One Two Three"

    assert text_flow("One Two Three", width=5) == ("One\n" "Two\n" "Three")

    assert text_flow("One Two Three", width=6, space_padding=True) == (
        "One   \n" "Two   \n" "Three "
    )

    assert text_flow("One Two Three", width=7, space_padding=True) == (
        "One Two\n" "Three  "
    )

    assert text_flow("One Two Three", width=9, left_margin=2, space_padding=True) == (
        "  One Two\n" "  Three  "
    )

    assert text_flow("One Two Three", width=7, left_margin=1, space_padding=True) == (
        " One   \n" " Two   \n" " Three "
    )

    assert text_flow(
        "One Two Three", width=9, left_margin=1, right_margin=1, space_padding=True
    ) == (" One Two \n" " Three   ")

    assert text_flow(
        "One Two Three", width=8, left_margin=1, right_margin=1, space_padding=True
    ) == (" One    \n" " Two    \n" " Three  ")

    assert text_flow(
        "One Two Three Four", width=7, left_margin=1, right_margin=1, space_padding=True
    ) == (" One   \n" " Two   \n" " Three \n" " Four  ")

    assert text_flow(
        "One Two Three Four", width=6, left_margin=1, right_margin=1, space_padding=True
    ) == (" One  \n" " Two  \n" " Thre \n" " e    \n" " Four ")


# FIXME!
#    assert text_flow("One Two Three",
#                     width=12,
#                     left_margin=6,
#                     first_line_indent=-5,
#                     space_padding=True) == (     " One   \n"
#                                             "      Two   \n"
#                                             "      Three ")


def test_can_shape():
    font = TTFont(
        portable_path("data/test/source-sans-pro/OTF/SourceSansPro-Regular.otf")
    )
    assert can_shape(font, "ABC")
    assert not can_shape(font, "こんにちは")


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
    assert pretty_print_list(config, values, glue="&") == expected_str.replace(
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


# FIXME: The spurious extra spaces in the expected strings below seem like
#        bad formatting being enforced by the code-test
#        Or, in other words, the code-test simply documenting
#        the poor output of the code it tests.
@pytest.mark.parametrize(
    "values, expected_str",
    [
        (_make_values(1), "\t- item 1"),
        (_make_values(2), "\t- item 1 \n\n\t- item 2"),
        (_make_values(3), "\t- item 1\n\n\t- item 2 \n\n\t- item 3"),
        (_make_values(4), "\t- item 1\n\n\t- item 2\n\n\t- item 3 \n\n\t- item 4"),
    ],
)
def test_bullet_list(values, expected_str):
    config = {"full_lists": True}
    assert bullet_list(config, values) == expected_str
    assert bullet_list(config, values, bullet="*") == expected_str.replace("-", "*")
    assert bullet_list(config, values, indentation="") == expected_str.replace("\t", "")
