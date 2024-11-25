from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/fstype",
    rationale="""
        The fsType in the OS/2 table is a legacy DRM-related field. Fonts in the
        Google Fonts collection must have it set to zero (also known as
        "Installable Embedding"). This setting indicates that the fonts can be
        embedded in documents and permanently installed by applications on
        remote systems.

        More detailed info is available at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_fstype(ttFont):
    """Checking OS/2 fsType does not impose restrictions."""
    value = ttFont["OS/2"].fsType
    if value != 0:
        FSTYPE_RESTRICTIONS = {
            0x0002: (
                "* The font must not be modified, embedded or exchanged in"
                " any manner without first obtaining permission of"
                " the legal owner."
            ),
            0x0004: (
                "The font may be embedded, and temporarily loaded on the"
                " remote system, but documents that use it must"
                " not be editable."
            ),
            0x0008: (
                "The font may be embedded but must only be installed"
                " temporarily on other systems."
            ),
            0x0100: ("The font may not be subsetted prior to embedding."),
            0x0200: (
                "Only bitmaps contained in the font may be embedded."
                " No outline data may be embedded."
            ),
        }
        restrictions = ""
        for bit_mask in FSTYPE_RESTRICTIONS.keys():
            if value & bit_mask:
                restrictions += FSTYPE_RESTRICTIONS[bit_mask]

        if value & 0b1111110011110001:
            restrictions += (
                "* There are reserved bits set, which indicates an invalid setting."
            )

        yield FAIL, Message(
            "drm",
            f"In this font fsType is set to {value} meaning that:\n"
            f"{restrictions}\n"
            f"\n"
            f"No such DRM restrictions can be enabled on the"
            f" Google Fonts collection, so the fsType field"
            f" must be set to zero (Installable Embedding) instead.",
        )
