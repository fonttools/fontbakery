from collections import defaultdict
from fontbakery.prelude import check, Message, FAIL
from fontbakery.checks.vendorspecific.googlefonts.constants import (
    DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    EXPECTED_COPYRIGHT_PATTERN,
)
from fontbakery.constants import NameID
from fontbakery.utils import show_inconsistencies


@check(
    id="googlefonts/font_copyright",
    rationale="""
        This check aims at ensuring a uniform and legally accurate copyright statement
        on the name table entries and METADATA.pb files of font files across the Google
        Fonts library.

        We also check that the copyright field in METADATA.pb matches the
        contents of the name table nameID 0 (Copyright), and that the copyright
        notice within the METADATA.pb file is not too long; if it is more than 500
        characters, this may be an indication that either a full license or the
        font's description has been included in this field by mistake.

    """
    + DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/2383",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_font_copyright(ttFont, font_metadata, config):
    """Copyright notices match canonical pattern in fonts"""
    import re
    from fontbakery.utils import get_name_entry_strings

    copyrights = [
        ("Name Table entry", string)
        for string in get_name_entry_strings(ttFont, NameID.COPYRIGHT_NOTICE)
    ]
    if font_metadata:
        copyrights.append(("METADATA.pb", font_metadata.copyright))

    sources_of_copyrights = defaultdict(list)

    for source, string in copyrights:
        sources_of_copyrights[string].append(source)
        if not re.search(EXPECTED_COPYRIGHT_PATTERN, string.lower()):
            yield FAIL, Message(
                "bad-notice-format",
                f"{source}: Copyright notices should match a pattern similar to:\n\n"
                f' "Copyright 2020 The Familyname Project Authors (git url)"\n\n'
                f'But instead we have got:\n\n"{string}"',
            )

        if len(string) > 500:
            yield FAIL, Message(
                "max-length",
                f"{source}: The length of the following copyright"
                f" notice ({len(string)}) exceeds 500 chars:"
                f' "{string}"',
            )

    if len(sources_of_copyrights) > 1:
        yield FAIL, Message(
            "mismatch",
            "Copyright notices differ between name table entries and METADATA.pb."
            "The following copyright values were found:\n\n"
            + show_inconsistencies(sources_of_copyrights, config),
        )
