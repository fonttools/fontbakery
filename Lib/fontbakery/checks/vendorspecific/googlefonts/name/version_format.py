from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID


@check(
    id="googlefonts/name/version_format",
    rationale="""
        For Google Fonts, the version string must be in the format "Version X.Y".
        The version number must be greater than or equal to 1.000. (Additional
        information following the numeric version number is acceptable.)
        The "Version " prefix is a recommendation given by the OpenType spec.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_version_format(ttFont):
    """Version format is correct in 'name' table?"""
    from fontbakery.utils import get_name_entry_strings
    import re

    def is_valid_version_format(value):
        return re.match(r"Version\s0*[1-9][0-9]*\.\d+", value)

    version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    if len(version_entries) == 0:
        yield FAIL, Message(
            "no-version-string",
            f"Font lacks a NameID.VERSION_STRING"
            f" (nameID={NameID.VERSION_STRING}) entry",
        )
    for ventry in version_entries:
        if not is_valid_version_format(ventry):
            yield FAIL, Message(
                "bad-version-strings",
                f"The NameID.VERSION_STRING"
                f" (nameID={NameID.VERSION_STRING}) value must"
                f' follow the pattern "Version X.Y" with X.Y'
                f" greater than or equal to 1.000."
                f' The "Version " prefix is a recommendation'
                f" given by the OpenType spec."
                f' Current version string is: "{ventry}"',
            )
