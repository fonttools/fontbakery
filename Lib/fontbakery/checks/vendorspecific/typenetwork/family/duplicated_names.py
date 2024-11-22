from fontbakery.prelude import check, Message, PASS, FAIL
from fontbakery.constants import (
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)


@check(
    id="typenetwork/family/duplicated_names",
    rationale="""
        Having duplicated name records can produce several issues like not all fonts
        being listed on design apps or incorrect automatic creation of CSS classes
        and @font-face rules.
        """,
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/25", # Currently private repo.
    ],
)
def check_family_duplicated_names(ttFonts):
    """Check if font doesn’t have duplicated names within a family."""
    duplicate_subfamilyNames = set()
    seen_fullNames = set()
    duplicate_fullNames = set()
    seen_postscriptNames = set()
    duplicate_postscriptNames = set()

    PLAT_ID = PlatformID.WINDOWS
    ENC_ID = WindowsEncodingID.UNICODE_BMP
    LANG_ID = WindowsLanguageID.ENGLISH_USA

    for ttFont in list(ttFonts):
        # # Subfamily name
        # if ttFont["name"].getName(17, PLAT_ID, ENC_ID, LANG_ID):
        #     subfamName = ttFont["name"].getName(17, PLAT_ID, ENC_ID, LANG_ID)
        # else:
        #     subfamName = ttFont["name"].getName(2, PLAT_ID, ENC_ID, LANG_ID)

        # if subfamName:
        #     subfamName = subfamName.toUnicode()
        #     if subfamName in seen_subfamilyNames:
        #         duplicate_subfamilyNames.add(subfamName)
        #     else:
        #         seen_subfamilyNames.add(subfamName)

        # FullName name
        fullName = ttFont["name"].getName(4, PLAT_ID, ENC_ID, LANG_ID)

        if fullName:
            fullName = fullName.toUnicode()
            if fullName in seen_fullNames:
                duplicate_fullNames.add(fullName)
            else:
                seen_fullNames.add(fullName)

        # Postscript name
        postscriptName = ttFont["name"].getName(6, PLAT_ID, ENC_ID, LANG_ID)
        if postscriptName:
            postscriptName = postscriptName.toUnicode()
            if postscriptName in seen_postscriptNames:
                duplicate_subfamilyNames.add(postscriptName)
            else:
                seen_postscriptNames.add(postscriptName)

    # if duplicate_subfamilyNames:
    #     duplicate_subfamilyNamesString = \
    #         "".join(f"* {inst}\n" for inst in sorted(duplicate_subfamilyNames))
    #     yield FAIL, Message(
    #         "duplicate-subfamily-names",
    #         "Following subfamily names are duplicate:\n\n"
    #         f"{duplicate_subfamilyNamesString}",
    #     )

    if duplicate_fullNames:
        duplicate_fullNamesString = "".join(
            f"* {inst}\n" for inst in sorted(duplicate_fullNames)
        )
        yield FAIL, Message(
            "duplicate-full-names",
            "Following full names are duplicate:\n\n" f"{duplicate_fullNamesString}",
        )

    if duplicate_postscriptNames:
        duplicate_postscriptNamesString = "".join(
            f"* {inst}\n" for inst in sorted(duplicate_postscriptNames)
        )
        yield FAIL, Message(
            "duplicate-postscript-names",
            "Following postscript names are duplicate:\n\n"
            f"{duplicate_postscriptNamesString}",
        )

    if not duplicate_fullNames and not duplicate_postscriptNames:
        yield PASS, "All names are unique"
