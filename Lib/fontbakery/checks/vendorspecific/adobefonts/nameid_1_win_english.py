from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="adobefonts/nameid_1_win_english",
    rationale="""
        While not required by the OpenType spec, Adobe Fonts' pipeline requires
        every font to support at least nameID 1 (Font Family name) for platformID 3
        (Windows), encodingID 1 (Unicode), and languageID 1033/0x409 (US-English).
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3714",
)
def check_nameid_1_win_english(ttFont, has_name_table):
    """Font has a good nameID 1, Windows/Unicode/US-English `name` table record?"""
    if not has_name_table:
        return FAIL, Message("name-table-not-found", "Font has no 'name' table.")

    nameid_1 = ttFont["name"].getName(1, 3, 1, 0x409)

    if nameid_1 is None:
        return FAIL, Message(
            "nameid-1-not-found",
            "Windows nameID 1 US-English record not found.",
        )

    try:
        nameid_1_unistr = nameid_1.toUnicode()
    except UnicodeDecodeError:
        return FAIL, Message(
            "nameid-1-decoding-error",
            "Windows nameID 1 US-English record could not be decoded.",
        )

    if not nameid_1_unistr.strip():
        return FAIL, Message(
            "nameid-1-empty",
            "Windows nameID 1 US-English record is empty.",
        )

    return PASS, "Font contains a good Windows nameID 1 US-English record."
