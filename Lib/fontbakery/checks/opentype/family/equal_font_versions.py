from fontbakery.prelude import check, Message, WARN


@check(
    id="opentype/family/equal_font_versions",
    rationale="""
        Within a family released at the same time, all members of the family
        should have the same version number in the head table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_equal_font_versions(ttFonts):
    """Make sure all font files have the same version value."""
    all_detected_versions = []
    fontfile_versions = {}
    for ttFont in ttFonts:
        v = ttFont["head"].fontRevision
        fontfile_versions[ttFont] = v

        if v not in all_detected_versions:
            all_detected_versions.append(v)
    if len(all_detected_versions) != 1:
        versions_list = ""
        for v in fontfile_versions.keys():
            versions_list += "* {}: {}\n".format(
                v.reader.file.name, fontfile_versions[v]
            )
        yield WARN, Message(
            "mismatch",
            f"Version info differs among font"
            f" files of the same font project.\n"
            f"These were the version values found:\n"
            f"{versions_list}",
        )
