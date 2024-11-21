from fontbakery.prelude import check, PASS, FAIL


@check(
    id="microsoft/fstype",
    rationale="""
        The value of the OS/2.fstype field must be 8 (Editable embedding), meaning,
        according to the OpenType spec:
        
        "Editable embedding: the font may be embedded, and may be temporarily loaded
        on other systems. As with Preview & Print embedding, documents containing
        Editable fonts may be opened for reading. In addition, editing is permitted,
        including ability to format new text using the embedded font, and changes
        may be saved." 
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_fstype(ttFont):
    """Checking OS/2 fsType."""
    required_value = 8
    value = ttFont["OS/2"].fsType
    if value != required_value:
        yield FAIL, (
            f"OS/2 fsType must be set to {required_value}, found {value} instead."
        )
    else:
        yield PASS, "OS/2 fsType is properly set."
