import pytest
from fontbakery.utils import text_flow, can_shape
from fontTools.ttLib import TTFont
from fontbakery.codetesting import portable_path


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

def test_can_shape():
    font = TTFont(portable_path(
        "data/test/source-sans-pro/OTF/SourceSansPro-Regular.otf"
    ))
    assert can_shape(font, "ABC")
    assert not can_shape(font, "こんにちは")
