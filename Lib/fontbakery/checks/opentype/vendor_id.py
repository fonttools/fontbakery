from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="opentype/vendor_id",
    rationale="""
        When a font project's Vendor ID is specified explicitly on FontBakery's
        configuration file, all binaries must have a matching vendor identifier
        value in the OS/2 table.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3941",
)
def check_vendor_id(config, ttFont):
    """Checking OS/2 achVendID against configuration."""

    if "vendor_id" not in config:
        yield SKIP, (
            "Add the `vendor_id` key to a `fontbakery.yaml` file"
            " on your font project directory to enable this check.\n"
            "You'll also need to use the `--configuration` flag when"
            " invoking fontbakery."
        )
        return

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "The required OS/2 table is missing.")
        return

    # vendor ID is a 4-byte ASCII string, per the OpenType spec
    # so this pads the string to 4 bytes if it's shorter
    config_vendor_id = config["vendor_id"].ljust(4)

    font_vendor_id = ttFont["OS/2"].achVendID

    if config_vendor_id != font_vendor_id:
        yield FAIL, Message(
            "bad-vendor-id",
            f"OS/2 VendorID is '{font_vendor_id}',"
            f" but should be '{config_vendor_id}'.",
        )
