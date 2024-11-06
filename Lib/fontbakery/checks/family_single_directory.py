import os

from fontbakery.prelude import (
    check,
    Message,
    PASS,
    FAIL,
)


@check(
    id="family/single_directory",
    rationale="""
        If the set of font files passed in the command line is not all in the
        same directory, then we warn the user since the tool will interpret the
        set of files as belonging to a single family (and it is unlikely that
        the user would store the files from a single family spreaded
        in several separate directories).
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_single_directory(fonts):
    """Checking all files are in the same directory."""

    directories = []
    for font in fonts:
        directory = os.path.dirname(font.file)
        if directory not in directories:
            directories.append(directory)

    if len(directories) == 1:
        yield PASS, "All files are in the same directory."
    else:
        yield FAIL, Message(
            "single-directory",
            "Not all fonts passed in the command line are in the"
            " same directory. This may lead to bad results as the tool"
            " will interpret all font files as belonging to a single"
            f" font family. The detected directories are: {directories}",
        )
