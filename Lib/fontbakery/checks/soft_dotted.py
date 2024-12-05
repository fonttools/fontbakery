from fontbakery.prelude import check, Message, PASS, WARN, SKIP
from fontbakery.utils import exit_with_install_instructions


@check(
    id="soft_dotted",
    severity=3,
    rationale="""
        An accent placed on characters with a "soft dot", like i or j, causes
        the dot to disappear.
        An explicit dot above can be added where required.
        See "Diacritics on i and j" in Section 7.1, "Latin" in The Unicode Standard.

        Characters with the Soft_Dotted property are listed in
        https://www.unicode.org/Public/UCD/latest/ucd/PropList.txt

        See also:
        https://googlefonts.github.io/gf-guide/diacritics.html#soft-dotted-glyphs
    """,
    conditions=[
        "network"
    ],  # use Shaperglot, which uses youseedee, which downloads Unicode files
    proposal="https://github.com/fonttools/fontbakery/issues/4059",
)
def check_soft_dotted(ttFont):
    """Ensure soft_dotted characters lose their dot when combined with marks that
    replace the dot."""
    try:
        from vharfbuzz import Vharfbuzz
    except ImportError:
        exit_with_install_instructions("shaping")

    import itertools
    from beziers.path import BezierPath
    from fontTools import unicodedata

    cmap = ttFont["cmap"].getBestCmap()

    # Soft dotted strings know to be used in orthographies.
    ortho_soft_dotted_strings = set(
        "i̋ i̍ i᷆ i᷇ i̓ i̊ i̐ ɨ́ ɨ̀ ɨ̂ ɨ̋ ɨ̏ ɨ̌ ɨ̄ ɨ̃ ɨ̈ ɨ̧́ ɨ̧̀ ɨ̧̂ ɨ̧̌ ɨ̱́ ɨ̱̀ ɨ̱̈ "
        "į́ į̀ į̂ į̄ į̄́ į̄̀ į̄̂ į̄̌ į̃ į̌ ị́ ị̀ ị̂ ị̄ ị̃ ḭ́ ḭ̀ ḭ̄ j́ j̀ j̄ j̑ j̃ "
        "j̈ і́".split()
    )
    # Characters with Soft_Dotted property in Unicode.
    soft_dotted_chars = set(
        ord(c) for c in "iⅈ𝐢𝑖𝒊𝒾𝓲𝔦𝕚𝖎𝗂𝗶𝘪𝙞𝚒ⁱᵢįịḭɨᶤ𝼚ᶖjⅉ𝐣𝑗𝒋𝒿𝓳𝔧𝕛𝖏𝗃𝗷𝘫𝙟𝚓ʲⱼɉʝᶨϳіј"
    ) & set(cmap.keys())
    # Only check above marks used with Latin, Greek, Cyrillic scripts.
    mark_above_chars = set(
        (
            c
            for c in cmap.keys()
            if unicodedata.combining(chr(c)) == 230
            and unicodedata.block(chr(c)).startswith(
                ("Combining Diacritical Marks", "Cyrillic")
            )
        )
    )
    # Only check non above marks used with Latin, Grek, Cyrillic scripts
    # that are reordered before the above marks
    mark_non_above_chars = set(
        c
        for c in cmap.keys()
        if unicodedata.combining(chr(c)) < 230
        and unicodedata.block(chr(c)).startswith("Combining Diacritical Marks")
    )
    # Skip when no characters to test with
    if not soft_dotted_chars or not mark_above_chars:
        yield SKIP, "Font has no soft dotted characters or no mark above characters."
        return

    # Collect outlines to skip fonts where i and dotlessi are the same,
    # or i and I are the same.
    outlines_dict = {
        codepoint: BezierPath.fromFonttoolsGlyph(ttFont, glyphname)
        for codepoint, glyphname in cmap.items()
        if codepoint in [ord("i"), ord("I"), ord("ı")]
    }
    unclear = False
    if ord("i") in cmap.keys() and ord("I") in cmap.keys():
        if len(outlines_dict[ord("i")]) == len(outlines_dict[ord("I")]):
            unclear = True
    if not unclear and ord("i") in cmap.keys() and ord("ı") in cmap.keys():
        if len(outlines_dict[ord("i")]) == len(outlines_dict[ord("ı")]):
            unclear = True
    if unclear:
        yield SKIP, (
            "It is not clear if the soft dotted characters have glyphs with dots."
        )
        return

    # Use harfbuzz to check if soft dotted glyphs are substituted
    filename = ttFont.reader.file.name
    vharfbuzz = Vharfbuzz(filename)
    fail_unchanged_strings = []
    warn_unchanged_strings = []
    for sequence in sorted(
        itertools.product(
            soft_dotted_chars,
            # add "" to add cases without non above marks
            mark_non_above_chars.union(set((0,))),
            mark_above_chars,
        )
    ):
        soft, non_above, above = sequence
        if non_above:
            unchanged = f"{cmap[soft]}|{cmap[non_above]}|{cmap[above]}"
            text = f"{chr(soft)}{chr(non_above)}{chr(above)}"
        else:
            unchanged = f"{cmap[soft]}|{cmap[above]}"
            text = f"{chr(soft)}{chr(above)}"

        # Only check a few strings that we WARN about.
        if text not in ortho_soft_dotted_strings and len(warn_unchanged_strings) >= 20:
            continue

        buf = vharfbuzz.shape(text)
        output = vharfbuzz.serialize_buf(buf, glyphsonly=True)
        if output == unchanged:
            if text in ortho_soft_dotted_strings:
                fail_unchanged_strings.append(text)
            else:
                warn_unchanged_strings.append(text)

    message = ""
    if fail_unchanged_strings:
        fail_unchanged_strings = " ".join(fail_unchanged_strings)
        message += (
            f"The dot of soft dotted characters used in orthographies"
            f" _must_ disappear in the following strings: {fail_unchanged_strings}"
        )
    if warn_unchanged_strings:
        warn_unchanged_strings = " ".join(warn_unchanged_strings)
        if message:
            message += "\n\n"
        message += (
            f"The dot of soft dotted characters _should_ disappear in"
            f" other cases, for example: {warn_unchanged_strings}"
        )

    # Calculate font's affected languages for additional information
    if fail_unchanged_strings or warn_unchanged_strings:
        from shaperglot.checker import Checker
        from shaperglot.languages import Languages, gflangs

        languages = Languages()

        # Find all affected languages
        ortho_soft_dotted_langs = set()
        for c in ortho_soft_dotted_strings:
            for lang in gflangs:
                if (
                    c in gflangs[lang].exemplar_chars.base
                    or c in gflangs[lang].exemplar_chars.auxiliary
                ):
                    ortho_soft_dotted_langs.add(lang)
        if ortho_soft_dotted_langs:
            affected_languages = []
            unaffected_languages = []
            languages = Languages()
            checker = Checker(ttFont.reader.file.name)

            for lang in ortho_soft_dotted_langs:
                reporter = checker.check(languages[lang])
                string = (
                    f"{gflangs[lang].name} ({gflangs[lang].script}, "
                    f"{'{:,.0f}'.format(gflangs[lang].population)} speakers)"
                )
                if reporter.is_success:
                    affected_languages.append(string)
                else:
                    unaffected_languages.append(string)

            if affected_languages:
                affected_languages = ", ".join(affected_languages)
                message += (
                    f"\n\nYour font fully covers the following languages that require"
                    f" the soft-dotted feature: {affected_languages}. "
                )

            if unaffected_languages:
                unaffected_languages = ", ".join(unaffected_languages)
                message += (
                    f"\n\nYour font does *not* cover the following languages that"
                    f" require the soft-dotted feature: {unaffected_languages}."
                )

    if fail_unchanged_strings or warn_unchanged_strings:
        yield WARN, Message("soft-dotted", message)
    else:
        yield PASS, (
            "All soft dotted characters seem to lose their dot when combined with"
            " a mark above."
        )
