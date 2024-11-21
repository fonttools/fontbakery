from fontbakery.prelude import check, FAIL, Message


@check(
    id="fontwerk/vendor_id",
    rationale="""
        Vendor ID must be WERK for Fontwerk fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3579",
)
def check_vendor_id(ttFont):
    """Checking OS/2 achVendID."""

    vendor_id = ttFont["OS/2"].achVendID
    if vendor_id != "WERK":
        yield FAIL, Message(
            "bad-vendor-id", f"OS/2 VendorID is '{vendor_id}', but should be 'WERK'."
        )
