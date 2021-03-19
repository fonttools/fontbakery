import pytest
from fontbakery.utils import text_flow


def test_text_flow():
    assert text_flow("") == ""

    assert text_flow("Testing") == "Testing"

    assert text_flow("One Two Three") == "One Two Three"

    assert text_flow("One Two Three",
                     width=5) == ("One\n"
                                  "Two\n"
                                  "Three")

    assert text_flow("One Two Three",
                     width=6,
                     space_padding=True) == ("One   \n"
                                             "Two   \n"
                                             "Three ")

    assert text_flow("One Two Three",
                     width=7,
                     space_padding=True) == ("One Two\n"
                                             "Three  ")

    assert text_flow("One Two Three",
                     width=9,
                     left_margin=2,
                     space_padding=True) == ("  One Two\n"
                                             "  Three  ")

    assert text_flow("One Two Three",
                     width=7,
                     left_margin=1,
                     space_padding=True) == (" One   \n"
                                             " Two   \n"
                                             " Three ")

# FIXME!
#    assert text_flow("One Two Three",
#                     width=12,
#                     left_margin=6,
#                     first_line_indent=-5,
#                     space_padding=True) == (     " One   \n"
#                                             "      Two   \n"
#                                             "      Three ")

