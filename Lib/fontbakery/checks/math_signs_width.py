from fontbakery.prelude import PASS, WARN, Message, check
from fontbakery.utils import get_glyph_name


@check(
    id="math_signs_width",
    rationale="""
        It is a common practice to have math signs sharing the same width
        (preferably the same width as tabular figures accross the entire font family).

        This probably comes from the will to avoid additional tabular math signs
        knowing that their design can easily share the same width.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3832",
)
def check_math_signs_width(ttFont):
    """Check math signs have the same width."""
    # Ironically, the block of text below may not have
    # uniform widths for these glyphs depending on
    # which font your text editor is using while you
    # read the source code of this check:
    COMMON_WIDTH_MATH_GLYPHS = (
        "+ < = > ¬ ± × ÷ ∈ ∉ ∋ ∌ − ∓ ∔ ∝ ∟ ∠ ∡ ∢ ∷ ∸ ∹ ∺ ∻ "
        "∼ ∽ ∾ ∿ ≁ ≂ ≃ ≄ ≅ ≆ ≇ ≈ ≉ ≊ ≋ ≌ ≍ ≎ ≏ ≐ ≑ ≒ ≓ ≖ ≗ "
        "≘ ≙ ≚ ≛ ≜ ≝ ≞ ≟ ≠ ≡ ≢ ≣ ≤ ≥ ≦ ≧ ≨ ≩ ≭ ≮ ≯ ≰ ≱ ≲ ≳ "
        "≴ ≵ ≶ ≷ ≸ ≹ ≺ ≻ ≼ ≽ ≾ ≿ ⊀ ⊁ ⊂ ⊃ ⊄ ⊅ ⊆ ⊇ ⊈ ⊉ ⊊ ⊋ ⊏ "
        "⊐ ⊑ ⊒ ⊢ ⊣ ⊤ ⊥ ⊨ ⊰ ⊱ ⊲ ⊳ ⊴ ⊵ ⊹ ⊾ ⋇ ⋍ ⋐ ⋑ ⋕ ⋖ ⋗ ⋚ ⋛ "
        "⋜ ⋝ ⋞ ⋟ ⋠ ⋡ ⋢ ⋣ ⋤ ⋥ ⋦ ⋧ ⋨ ⋩ ⋳ ⋵ ⋶ ⋸ ⋹ ⋻ ⋽ ⟀ ⟃ ⟄ ⟓ "
        "⟔ ⥶ ⥸ ⥹ ⥻ ⥾ ⥿ ⦓ ⦔ ⦕ ⦖ ⦛ ⦜ ⦝ ⦞ ⦟ ⦠ ⦡ ⦢ ⦣ ⦤ ⦥ ⦨ ⦩ ⦪ "
        "⦫ ⧣ ⧤ ⧥ ⧺ ⧻ ⨢ ⨣ ⨤ ⨥ ⨦ ⨧ ⨨ ⨩ ⨪ ⨫ ⨬ ⨳ ⩦ ⩧ ⩨ ⩩ ⩪ ⩫ ⩬ "
        "⩭ ⩮ ⩯ ⩰ ⩱ ⩲ ⩳ ⩷ ⩸ ⩹ ⩺ ⩻ ⩼ ⩽ ⩾ ⩿ ⪀ ⪁ ⪂ ⪃ ⪄ ⪅ ⪆ ⪇ ⪈ "
        "⪉ ⪊ ⪋ ⪌ ⪍ ⪎ ⪏ ⪐ ⪑ ⪒ ⪓ ⪔ ⪕ ⪖ ⪗ ⪘ ⪙ ⪚ ⪛ ⪜ ⪝ ⪞ ⪟ ⪠ ⪡ "
        "⪢ ⪦ ⪧ ⪨ ⪩ ⪪ ⪫ ⪬ ⪭ ⪮ ⪯ ⪰ ⪱ ⪲ ⪳ ⪴ ⪵ ⪶ ⪷ ⪸ ⪹ ⪺ ⪽ ⪾ ⪿ "
        "⫀ ⫁ ⫂ ⫃ ⫄ ⫅ ⫆ ⫇ ⫈ ⫉ ⫊ ⫋ ⫌ ⫏ ⫐ ⫑ ⫒ ⫓ ⫔ ⫕ ⫖ ⫟ ⫠ ⫡ ⫢ "
        "⫤ ⫦ ⫧ ⫨ ⫩ ⫪ ⫫ ⫳ ⫴ ⫵ ⫶ ⫹ ⫺ 〒"
    )

    glyphs_by_width = {}
    for glyph in COMMON_WIDTH_MATH_GLYPHS.split(" "):
        codepoint = ord(glyph)
        glyph_name = get_glyph_name(ttFont, codepoint)
        if glyph_name is None:
            # The font does not have this glyph, so move on...
            continue
        glyph_width = ttFont["hmtx"][glyph_name][0]
        if glyph_width not in glyphs_by_width:
            glyphs_by_width[glyph_width] = set([glyph_name])
        else:
            glyphs_by_width[glyph_width].add(glyph_name)

    most_common_width = None
    num_glyphs = 0
    for glyph_width, glyph_names in glyphs_by_width.items():
        if most_common_width is None:
            num_glyphs = len(glyph_names)
            most_common_width = glyph_width
        else:
            if len(glyph_names) > num_glyphs:
                most_common_width = glyph_width
                num_glyphs = len(glyph_names)

    if most_common_width and len(glyphs_by_width.keys()) > 1:
        outliers_summary = []
        for w, names in glyphs_by_width.items():
            if not w == most_common_width:
                outliers_summary.append(f"Width = {w}:\n{', '.join(names)}\n")
        outliers_summary = "\n".join(outliers_summary)
        yield WARN, Message(
            "width-outliers",
            f"The most common width is {most_common_width} among a set of {num_glyphs}"
            " math glyphs.\nThe following math glyphs have a different width, though:"
            f"\n\n{outliers_summary}",
        )
    else:
        yield PASS, "Looks good."
