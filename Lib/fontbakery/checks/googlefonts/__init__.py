import os

from fontbakery.prelude import check, Message, INFO, WARN, ERROR, PASS, FAIL
from fontbakery.utils import filesize_formatting
from fontbakery.utils import exit_with_install_instructions


@check(
    id="com.google.fonts/check/canonical_filename",
    rationale="""
        A font's filename must be composed as "<familyname>-<stylename>.ttf":

        - Nunito-Regular.ttf

        - Oswald-BoldItalic.ttf


        Variable fonts must list the axis tags in alphabetical order in
        square brackets and separated by commas:

        - Roboto[wdth,wght].ttf

        - Familyname-Italic[wght].ttf
    """,
    proposal="legacy:check/001",
)
def com_google_fonts_check_canonical_filename(ttFont):
    """Checking file is named canonically."""

    try:
        import axisregistry
    except ImportError:
        exit_with_install_instructions("googlefonts")

    current_filename = os.path.basename(ttFont.reader.file.name)
    expected_filename = axisregistry.build_filename(ttFont)

    if current_filename != expected_filename:
        yield FAIL, Message(
            "bad-filename", f'Expected "{expected_filename}. Got {current_filename}.'
        )
    else:
        yield PASS, f'Font filename is correct, "{current_filename}".'


@check(
    id="com.google.fonts/check/file_size",
    rationale="""
        Serving extremely large font files on Google Fonts causes usability issues.
        This check ensures that file sizes are reasonable.
    """,
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3320",
    configs=["WARN_SIZE", "FAIL_SIZE"],
)
def com_google_fonts_check_file_size(font):
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


@check(
    id="com.google.fonts/check/fontdata_namecheck",
    rationale="""
        We need to check names are not already used, and today the best place to check
        that is http://namecheck.fontdata.com
    """,
    conditions=["network", "familyname"],
    proposal="https://github.com/fonttools/fontbakery/issues/494",
)
def com_google_fonts_check_fontdata_namecheck(ttFont, familyname):
    """Familyname must be unique according to namecheck.fontdata.com"""
    import requests

    FB_ISSUE_TRACKER = "https://github.com/fonttools/fontbakery/issues"
    NAMECHECK_URL = "http://namecheck.fontdata.com"
    try:
        # Since October 2019, it seems that we need to fake our user-agent
        # in order to get correct query results
        FAKE = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)"
        response = requests.post(
            NAMECHECK_URL,
            params={"q": familyname},
            headers={"User-Agent": FAKE},
            timeout=10,
        )
        data = response.content.decode("utf-8")
        if "fonts by that exact name" in data:
            yield INFO, Message(
                "name-collision",
                f'The family name "{familyname}" seems'
                f" to be already in use.\n"
                f"Please visit {NAMECHECK_URL} for more info.",
            )
        else:
            yield PASS, "Font familyname seems to be unique."
    except requests.exceptions.RequestException:
        import sys

        yield ERROR, Message(
            "namecheck-service",
            f"Failed to access: {NAMECHECK_URL}.\n"
            f"\t\tThis check relies on the external service"
            f" http://namecheck.fontdata.com via the internet."
            f" While the service cannot be reached or does not"
            f" respond this check is broken.\n"
            f"\n"
            f"\t\tYou can exclude this check with the command line"
            f" option:\n"
            f"\t\t-x com.google.fonts/check/fontdata_namecheck\n"
            f"\n"
            f"\t\tOr you can wait until the service is available again.\n"
            f"\t\tIf the problem persists please report this issue"
            f" at: {FB_ISSUE_TRACKER}\n"
            f"\n"
            f"\t\tOriginal error message:\n"
            f"\t\t{sys.exc_info()[0]}",
        )
