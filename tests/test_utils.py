from fontbakery.utils import (
    can_shape,
    text_flow,
    unindent_and_unwrap_rationale,
)
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

    assert text_flow("One Two Three",
                     width=9,
                     left_margin=1,
                     right_margin=1,
                     space_padding=True) == (" One Two \n"
                                             " Three   ")

    assert text_flow("One Two Three",
                     width=8,
                     left_margin=1,
                     right_margin=1,
                     space_padding=True) == (" One    \n"
                                             " Two    \n"
                                             " Three  ")

    assert text_flow("One Two Three Four",
                     width=7,
                     left_margin=1,
                     right_margin=1,
                     space_padding=True) == (" One   \n"
                                             " Two   \n"
                                             " Three \n"
                                             " Four  ")

    assert text_flow("One Two Three Four",
                     width=6,
                     left_margin=1,
                     right_margin=1,
                     space_padding=True) == (" One  \n"
                                             " Two  \n"
                                             " Thre \n"
                                             " e    \n"
                                             " Four ")

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


def test_unindent_and_unwrap_rationale():
    rationale = """
        This is a line that is very long, so long in fact that it must be hard wrapped
        because it is longer than 88 lines, including the two 4-space indents.

        This is a new paragraph. This paragraph is also too long to fit within the
        maximum width, so it must be hard wrapped.
        This is a new line that was NOT soft-wrapped, so it will end up appendend to
        the previous line. 
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
