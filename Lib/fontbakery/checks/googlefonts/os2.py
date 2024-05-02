from functools import lru_cache
import re

from fontbakery.checks.googlefonts.conditions import expected_font_names
from fontbakery.prelude import check, Message, WARN, FAIL, SKIP
from fontbakery.utils import exit_with_install_instructions


@lru_cache(maxsize=1)
def registered_vendor_ids():
    """Get a list of vendor IDs from Microsoft's website."""
    from pkg_resources import resource_filename

    try:
        from bs4 import BeautifulSoup, NavigableString
    except ImportError:
        exit_with_install_instructions("googlefonts")

    registered_vendor_ids = {}
    CACHED = resource_filename(
        "fontbakery", "data/fontbakery-microsoft-vendorlist.cache"
    )
    content = open(CACHED, encoding="utf-8").read()
    # Strip all <A> HTML tags from the raw HTML. The current page contains a
    # closing </A> for which no opening <A> is present, which causes
    # beautifulsoup to silently stop processing that section from the error
    # onwards. We're not using the href's anyway.
    content = re.sub("<a[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub("</a>", "", content, flags=re.IGNORECASE)
    soup = BeautifulSoup(content, "html.parser")

    IDs = [chr(c + ord("a")) for c in range(ord("z") - ord("a") + 1)]
    IDs.append("0-9-")

    for section_id in IDs:
        section = soup.find("h2", {"id": section_id})
        if not section:
            continue

        table = section.find_next_sibling("table")
        if not table or isinstance(table, NavigableString):
            continue

        # print ("table: '{}'".format(table))
        for row in table.findAll("tr"):
            # print("ROW: '{}'".format(row))
            cells = row.findAll("td")
            if not cells:
                continue

            labels = list(cells[1].stripped_strings)

            # pad the code to make sure it is a 4 char string,
            # otherwise eg "CF  " will not be matched to "CF"
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * " "
            registered_vendor_ids[code] = labels[0]

            # Do the same with NULL-padding:
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * chr(0)
            registered_vendor_ids[code] = labels[0]

    return registered_vendor_ids


@check(
    id="com.google.fonts/check/vendor_id",
    rationale="""
        Microsoft keeps a list of font vendors and their respective contact info. This
        list is updated regularly and is indexed by a 4-char "Vendor ID" which is
        stored in the achVendID field of the OS/2 table.

        Registering your ID is not mandatory, but it is a good practice since some
        applications may display the type designer / type foundry contact info on some
        dialog and also because that info will be visible on Microsoft's website:

        https://docs.microsoft.com/en-us/typography/vendors/

        This check verifies whether or not a given font's vendor ID is registered in
        that list or if it has some of the default values used by the most common
        font editors.

        Each new FontBakery release includes a cached copy of that list of vendor IDs.
        If you registered recently, you're safe to ignore warnings emitted by this
        check, since your ID will soon be included in one of our upcoming releases.
    """,
    proposal=[
        "legacy:check/018",
        "https://github.com/fonttools/fontbakery/issues/3943",
    ],
)
def com_google_fonts_check_vendor_id(ttFont):
    """Checking OS/2 achVendID."""

    SUGGEST_MICROSOFT_VENDORLIST_WEBSITE = (
        "If you registered it recently, then it's safe to ignore this warning message."
        " Otherwise, you should set it to your own unique 4 character code,"
        " and register it with Microsoft at"
        " https://www.microsoft.com/typography/links/vendorlist.aspx\n"
    )

    vid = ttFont["OS/2"].achVendID
    bad_vids = ["UKWN", "ukwn", "PfEd", "PYRS"]
    if vid is None:
        yield WARN, Message(
            "not-set",
            f"OS/2 VendorID is not set." f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}",
        )
    elif vid in bad_vids:
        yield WARN, Message(
            "bad",
            f"OS/2 VendorID is '{vid}', a font editor default."
            f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}",
        )
    elif vid not in registered_vendor_ids().keys():
        yield WARN, Message(
            "unknown",
            f"OS/2 VendorID value '{vid}' is not yet recognized."
            f" {SUGGEST_MICROSOFT_VENDORLIST_WEBSITE}",
        )


@check(
    id="com.google.fonts/check/os2/use_typo_metrics",
    rationale="""
        All fonts on the Google Fonts collection should have OS/2.fsSelection bit 7
        (USE_TYPO_METRICS) set. This requirement is part of the vertical metrics scheme
        established as a Google Fonts policy aiming at a common ground supported by
        all major font rendering environments.

        For more details, read:
        https://github.com/googlefonts/gf-docs/blob/main/VerticalMetrics/README.md

        Below is the portion of that document that is most relevant to this check:

        Use_Typo_Metrics must be enabled. This will force MS Applications to use the
        OS/2 Typo values instead of the Win values. By doing this, we can freely set
        the Win values to avoid clipping and control the line height with the typo
        values. It has the added benefit of future line height compatibility. When
        a new script is added, we simply change the Win values to the new yMin
        and yMax, without needing to worry if the line height have changed.
    """,
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3241",
)
def com_google_fonts_check_os2_fsselectionbit7(fonts):
    """OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts."""
    if any(font.is_cjk_font for font in fonts):
        yield SKIP, Message("cjk", "This check does not apply to CJK fonts.")
        return

    bad_fonts = []
    for font in fonts:
        if not font.ttFont["OS/2"].fsSelection & (1 << 7):
            bad_fonts.append(font.file)

    if bad_fonts:
        yield FAIL, Message(
            "missing-os2-fsselection-bit7",
            f"OS/2.fsSelection bit 7 (USE_TYPO_METRICS) was"
            f"NOT set in the following fonts: {bad_fonts}.",
        )


@check(
    id="com.google.fonts/check/fstype",
    rationale="""
        The fsType in the OS/2 table is a legacy DRM-related field. Fonts in the
        Google Fonts collection must have it set to zero (also known as
        "Installable Embedding"). This setting indicates that the fonts can be
        embedded in documents and permanently installed by applications on
        remote systems.

        More detailed info is available at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype
    """,
    proposal="legacy:check/016",
)
def com_google_fonts_check_fstype(ttFont):
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


@check(
    id="com.google.fonts/check/usweightclass",
    rationale="""
        Google Fonts expects variable fonts, static ttfs and static otfs to have
        differing OS/2 usWeightClass values.

        - For Variable Fonts, Thin-Black must be 100-900

        - For static ttfs, Thin-Black can be 100-900 or 250-900

        - For static otfs, Thin-Black must be 250-900

        If static otfs are set lower than 250, text may appear blurry in
        legacy Windows applications.

        Glyphsapp users can change the usWeightClass value of an instance by adding
        a 'weightClass' customParameter.
    """,
    proposal="legacy:check/020",
)
def com_google_fonts_check_usweightclass(font, ttFonts):
    """
    Check the OS/2 usWeightClass is appropriate for the font's best SubFamily name.
    """
    value = font.ttFont["OS/2"].usWeightClass
    expected_names = expected_font_names(font.ttFont, ttFonts)
    expected_value = expected_names["OS/2"].usWeightClass
    style_name = font.ttFont["name"].getBestSubFamilyName()
    has_expected_value = value == expected_value
    fail_message = (
        "Best SubFamily name is '{}'. Expected OS/2 usWeightClass is {}, got {}."
    )
    if font.is_variable_font:
        if not has_expected_value:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
    # overrides for static Thin and ExtaLight fonts
    # for static ttfs, we don't mind if Thin is 250 and ExtraLight is 275.
    # However, if the values are incorrect we will recommend they set Thin
    # to 100 and ExtraLight to 250.
    # for static otfs, Thin must be 250 and ExtraLight must be 275
    elif "Thin" in style_name:
        if font.is_ttf and value not in [100, 250]:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
        if font.is_cff and value != 250:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, 250, value)
            )

    elif "ExtraLight" in style_name:
        if font.is_ttf and value not in [200, 275]:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
        if font.is_cff and value != 275:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, 275, value)
            )

    elif not has_expected_value:
        yield FAIL, Message(
            "bad-value", fail_message.format(style_name, expected_value, value)
        )
