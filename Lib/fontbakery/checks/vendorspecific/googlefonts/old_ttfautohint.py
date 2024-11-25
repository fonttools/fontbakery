from fontbakery.prelude import check, Message, INFO, FAIL, WARN
from fontbakery.constants import LATEST_TTFAUTOHINT_VERSION, NameID


@check(
    id="googlefonts/old_ttfautohint",
    conditions=["is_ttf"],
    rationale="""
        Check if font has been hinted with an outdated version of ttfautohint.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_old_ttfautohint(ttFont):
    """Font has old ttfautohint applied?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(values):
        import re

        for value in values:
            results = re.search(r"ttfautohint \(v(.*)\)", value)
            if results:
                return results.group(1)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    ttfa_version = ttfautohint_version(version_strings)
    if len(version_strings) == 0:
        yield FAIL, Message(
            "lacks-version-strings",
            "This font file lacks mandatory version strings in its name table.",
        )
    elif ttfa_version is None:
        yield INFO, Message(
            "version-not-detected",
            f"Could not detect which version of"
            f" ttfautohint was used in this font."
            f" It is typically specified as a comment"
            f" in the font version entries of the 'name' table."
            f" Such font version strings are currently:"
            f" {version_strings}",
        )
    else:
        try:
            if LATEST_TTFAUTOHINT_VERSION > ttfa_version:
                yield WARN, Message(
                    "old-ttfa",
                    f"ttfautohint used in font = {ttfa_version};"
                    f" latest = {LATEST_TTFAUTOHINT_VERSION};"
                    f" Need to re-run with the newer version!",
                )
        except ValueError:
            yield FAIL, Message(
                "parse-error",
                f"Failed to parse ttfautohint version values:"
                f" latest = '{LATEST_TTFAUTOHINT_VERSION}';"
                f" used_in_font = '{ttfa_version}'",
            )
