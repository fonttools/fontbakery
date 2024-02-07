from fontbakery.prelude import check, WARN, INFO, FAIL, Message


@check(
    id="com.google.fonts/check/meta/script_lang_tags",
    rationale="""
        The OpenType 'meta' table originated at Apple. Microsoft added it to OT with
        just two DataMap records:

        - dlng: comma-separated ScriptLangTags that indicate which scripts,
          or languages and scripts, with possible variants, the font is designed for.

        - slng: comma-separated ScriptLangTags that indicate which scripts,
          or languages and scripts, with possible variants, the font supports.


        The slng structure is intended to describe which languages and scripts the
        font overall supports. For example, a Traditional Chinese font that also
        contains Latin characters, can indicate Hant,Latn, showing that it supports
        Hant, the Traditional Chinese variant of the Hani script, and it also
        supports the Latn script.

        The dlng structure is far more interesting. A font may contain various glyphs,
        but only a particular subset of the glyphs may be truly "leading" in the design,
        while other glyphs may have been included for technical reasons. Such a
        Traditional Chinese font could only list Hant there, showing that it’s designed
        for Traditional Chinese, but the font would omit Latn, because the developers
        don’t think the font is really recommended for purely Latin-script use.

        The tags used in the structures can comprise just script, or also language
        and script. For example, if a font has Bulgarian Cyrillic alternates in the
        locl feature for the cyrl BGR OT languagesystem, it could also indicate in
        dlng explicitly that it supports bul-Cyrl. (Note that the scripts and languages
        in meta use the ISO language and script codes, not the OpenType ones).

        This check ensures that the font has the meta table containing the
        slng and dlng structures.

        All families in the Google Fonts collection should contain the 'meta' table.
        Windows 10 already uses it when deciding on which fonts to fall back to.
        The Google Fonts API and also other environments could use the data for
        smarter filtering. Most importantly, those entries should be added
        to the Noto fonts.

        In the font making process, some environments store this data in external
        files already. But the meta table provides a convenient way to store this
        inside the font file, so some tools may add the data, and unrelated tools
        may read this data. This makes the solution much more portable and universal.
    """,
    severity=3,
    proposal="https://github.com/fonttools/fontbakery/issues/3349",
)
def com_google_fonts_check_meta_script_lang_tags(ttFont):
    """Ensure fonts have ScriptLangTags declared on the 'meta' table."""

    if "meta" not in ttFont:
        yield WARN, Message(
            "lacks-meta-table", "This font file does not have a 'meta' table."
        )

    else:
        if "dlng" not in ttFont["meta"].data:
            yield FAIL, Message(
                "missing-dlng-tag",
                "Please specify which languages and scripts this font is designed for.",
            )
        else:
            yield INFO, Message("dlng-tag", f"{ttFont['meta'].data['dlng']}")

        if "slng" not in ttFont["meta"].data:
            yield FAIL, Message(
                "missing-slng-tag",
                "Please specify which languages and scripts this font supports.",
            )
        else:
            yield INFO, Message("slng-tag", f"{ttFont['meta'].data['slng']}")
