from fontbakery.checks.vendorspecific.googlefonts.utils import registered_vendor_ids
from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/vendor_id",
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
        "https://github.com/fonttools/fontbakery/issues/3943",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_vendor_id(ttFont):
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
