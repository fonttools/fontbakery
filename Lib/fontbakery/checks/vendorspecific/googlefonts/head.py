from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/unitsperem",
    rationale="""
        Even though the OpenType spec allows unitsPerEm to be any value between 16
        and 16384, the Google Fonts project aims at a narrower set of reasonable values.

        Values above 4000 would likely result in unreasonable filesize increases.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_unitsperem(ttFont):
    """Stricter unitsPerEm criteria for Google Fonts."""
    upm_height = ttFont["head"].unitsPerEm
    RECOMMENDED = [16, 32, 64, 128, 256, 500, 512, 1000, 1024, 2000, 2048]
    if upm_height > 4000:
        yield FAIL, Message(
            "large-value",
            f"Font em size (unitsPerEm) is {upm_height}"
            f" which may be too large (causing filesize bloat),"
            f" unless you are sure that the detail level"
            f" in this font requires that much precision.",
        )
    elif upm_height < 16:
        yield FAIL, Message(
            "bad-value",
            f"Font em size (unitsPerEm) is {upm_height}."
            f" If possible, please consider using 1000."
            f" Good values for unitsPerEm,"
            f" though, are typically these: {RECOMMENDED}.",
        )
