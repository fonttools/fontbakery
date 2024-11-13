from fontbakery.prelude import check, Message, FAIL, PASS, WARN


@check(
    id="opentype/post_table_version",
    rationale="""
        Format 2.5 of the 'post' table was deprecated in OpenType 1.3 and
        should not be used.

        According to Thomas Phinney, the possible problem with post format 3
        is that under the right combination of circumstances, one can generate
        PDF from a font with a post format 3 table, and not have accurate backing
        store for any text that has non-default glyphs for a given codepoint.

        It will look fine but not be searchable. This can affect Latin text with
        high-end typography, and some complex script writing systems, especially
        with higher-quality fonts. Those circumstances generally involve creating
        a PDF by first printing a PostScript stream to disk, and then creating a
        PDF from that stream without reference to the original source document.
        There are some workflows where this applies,but these are not common
        use cases.

        Apple recommends against use of post format version 4 as "no longer
        necessary and should be avoided". Please see the Apple TrueType reference
        documentation for additional details.

        https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html

        Acceptable post format versions are 2 and 3 for TTF and OTF CFF2 builds,
        and post format 3 for CFF builds.
    """,
    proposal=[
        "https://github.com/google/fonts/issues/215",
        "https://github.com/fonttools/fontbakery/issues/2638",
        "https://github.com/fonttools/fontbakery/issues/3635",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def opentype_post_table_version(ttFont):
    """Font has correct post table version?"""
    formatType = ttFont["post"].formatType
    is_cff = "CFF " in ttFont

    if is_cff and formatType != 3:
        yield FAIL, Message(
            "post-table-version", "CFF fonts must contain post format 3 table."
        )
    elif not is_cff and formatType == 3:
        yield WARN, Message(
            "post-table-version",
            "Post table format 3 use has niche use case problems."
            "Please review the check rationale for additional details.",
        )
    elif formatType == 2.5:
        yield FAIL, Message(
            "post-table-version",
            "Post format 2.5 was deprecated in OpenType 1.3 and should not be used.",
        )
    elif formatType == 4:
        yield FAIL, Message(
            "post-table-version",
            "According to Apple documentation, post format 4 tables are"
            "no longer necessary and should not be used.",
        )
    else:
        yield PASS, f"Font has an acceptable post format {formatType} table version."
