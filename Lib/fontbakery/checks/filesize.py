import os

from fontbakery.prelude import check, Message, FAIL, WARN, PASS
from fontbakery.utils import filesize_formatting


@check(
    id="file_size",
    rationale="""
        Serving extremely large font files causes usability issues.
        This check ensures that file sizes are reasonable.
    """,
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3320",
    configs=["WARN_SIZE", "FAIL_SIZE"],
)
def check_file_size(font):
    """Ensure files are not too large."""
    # pytype: disable=name-error
    size = os.stat(font.file).st_size
    if size > FAIL_SIZE:  # noqa:F821 pylint:disable=E0602
        yield FAIL, Message(
            "massive-font",
            f"Font file is {filesize_formatting(size)}, larger than limit"
            f" {filesize_formatting(FAIL_SIZE)}",  # noqa:F821 pylint:disable=E0602
        )
    elif size > WARN_SIZE:  # noqa:F821 pylint:disable=E0602
        yield WARN, Message(
            "large-font",
            f"Font file is {filesize_formatting(size)}; ideally it should be less than"
            f" {filesize_formatting(WARN_SIZE)}",  # noqa:F821 pylint:disable=E0602
        )
    else:
        yield PASS, "Font had a reasonable file size"
    # pytype: enable=name-error
