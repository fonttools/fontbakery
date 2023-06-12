from fontbakery.callable import check
from fontbakery.status import FAIL, PASS
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import (  # NOQA pylint: disable=unused-import
    profile_factory,
)


@check(
    id="com.google.fonts/check/family/equal_unicode_encodings",
    proposal="legacy:check/013",
)
def com_google_fonts_check_family_equal_unicode_encodings(ttFonts):
    """Fonts have equal unicode encodings?"""
    encoding = None
    failed = False
    for ttFont in ttFonts:
        cmap = None
        for table in ttFont["cmap"].tables:
            if table.format == 4:
                cmap = table
                break
        # Could a font lack a format 4 cmap table ?
        # If we ever find one of those, it would crash the check here.
        # Then we'd have to yield a FAIL regarding the missing table entry.
        if not encoding:
            encoding = cmap.platEncID
        if encoding != cmap.platEncID:
            failed = True
    if failed:
        yield FAIL, Message("mismatch", "Fonts have different unicode encodings.")
    else:
        yield PASS, "Fonts have equal unicode encodings."
