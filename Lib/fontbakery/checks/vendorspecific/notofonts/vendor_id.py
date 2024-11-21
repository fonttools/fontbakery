from fontbakery.prelude import check, FAIL, Message


@check(
    id="notofonts/vendor_id",
    rationale="""
        Vendor ID must be 'GOOG'
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_os2_vendor(ttFont):
    """Check OS/2 achVendID is set to GOOG."""

    vendor_id = ttFont["OS/2"].achVendID
    if vendor_id != "GOOG":
        yield FAIL, Message(
            "bad-vendor-id", f"OS/2 VendorID is '{vendor_id}', but should be 'GOOG'."
        )
