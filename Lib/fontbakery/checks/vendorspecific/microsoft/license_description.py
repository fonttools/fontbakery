from fontbakery.prelude import check, PASS, FAIL


MS_LICENSE_DESCRIPTION = (
    "Microsoft supplied font. You may use this font to create, display, "
    "and print content as permitted by the license terms or terms of use, "
    "of the Microsoft product, service, or content in which this font was "
    "included. You may only (i) embed this font in content as permitted by "
    "the embedding restrictions included in this font; and (ii) temporarily "
    "download this font to a printer or other output device to help print "
    "content. Any other use is prohibited."
).replace(
    ",", ""
)  # ignore commas, see below


@check(
    id="microsoft/license_description",
    rationale="""
        Check whether license description is correct.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_license_description(ttFont):
    """Validate license description field in the name table."""
    name_record = ttFont["name"].getName(13, 3, 1, 0x0409)
    if name_record is None:
        yield FAIL, "Name ID 13 (license description) does not exist."
    else:
        license_description = name_record.toUnicode()
        # There are versions around with/without Oxford commas. Let's
        # ignore commas altogether.
        license_description = license_description.replace(",", "")
        if MS_LICENSE_DESCRIPTION not in license_description:
            yield FAIL, "License description does not contain required text"
        else:
            yield PASS, "License description OK"
