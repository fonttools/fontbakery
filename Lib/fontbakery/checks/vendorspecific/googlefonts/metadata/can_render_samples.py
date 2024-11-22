from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import (
    can_shape,
    exit_with_install_instructions,
)


@check(
    id="googlefonts/metadata/can_render_samples",
    rationale="""
        In order to prevent tofu from being seen on fonts.google.com, this check
        verifies that all samples specified by METADATA.pb can be properly
        rendered by the font.
    """,
    conditions=["family_metadata"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3419",
        "https://github.com/fonttools/fontbakery/issues/3605",
    ],
)
def check_metadata_can_render_samples(ttFont, family_metadata):
    """Check samples can be rendered."""
    try:
        from gflanguages import LoadLanguages
    except ImportError:
        exit_with_install_instructions("googlefonts")

    languages = LoadLanguages()
    for lang in family_metadata.languages:
        if lang not in languages:
            yield WARN, Message(
                "no-sample-string",
                f"Aparently there's no sample strings for"
                f" '{lang}' in the gflanguages package.",
            )
            continue

        # Note: checking against all samples often results in
        #       a way too verbose output. That's why I only left
        #       the "tester" string for now.
        SAMPLES = {
            # 'styles': languages[lang].sample_text.styles,
            "tester": languages[lang].sample_text.tester,
            # 'specimen_16': languages[lang].sample_text.specimen_16,
            # 'specimen_21': languages[lang].sample_text.specimen_21,
            # 'specimen_32': languages[lang].sample_text.specimen_32,
            # 'specimen_36': languages[lang].sample_text.specimen_36,
            # 'specimen_48': languages[lang].sample_text.specimen_48
        }
        for sample_type, sample_text in SAMPLES.items():
            # Remove line-breaks and zero width space (U+200B) characteres.
            # For more info, see https://github.com/fonttools/fontbakery/issues/3990
            sample_text = sample_text.replace("\n", "").replace("\u200b", "")

            if not can_shape(ttFont, sample_text):
                yield FAIL, Message(
                    "sample-text",
                    f'Font can\'t render "{lang}" sample text:\n"{sample_text}"\n',
                )
