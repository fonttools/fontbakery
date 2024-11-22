from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/metadata/primary_script",
    conditions=["family_metadata"],
    rationale="""
        Try to guess font's primary script and see if that's set in METADATA.pb.
        This is an educated guess based on the number of glyphs per script in the font
        and should be taken with caution.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4109",
)
def check_metadata_primary_script(ttFont, family_metadata):
    """METADATA.pb: Check for primary_script"""

    def get_primary_script(ttFont):
        from fontTools import unicodedata
        from collections import Counter

        script_count = Counter()
        for c in ttFont.getBestCmap().keys():
            for script in unicodedata.script_extension(chr(c)):
                if script not in ["Zinh", "Zyyy", "Zzzz"]:
                    # Zinh: "Inherited"
                    # Zyyy: "Common"
                    # Zzzz: "Unknown"
                    script_count[script] += 1
        most_common = script_count.most_common(1)
        if most_common:
            script = most_common[0][0]
            return script

    siblings = (
        ("Kore", "Hang"),
        ("Jpan", "Hani", "Hant", "Hans"),
        ("Hira", "Kana"),
    )

    def is_sibling_script(target, guessed):
        for family in siblings:
            if guessed in family and target in family:
                return True

    def get_sibling_scripts(target):
        for family in siblings:
            if target in family:
                return family

    guessed_primary_script = get_primary_script(ttFont)
    if guessed_primary_script != "Latn":
        # family_metadata.primary_script is empty but should be set
        if family_metadata.primary_script in (None, ""):
            message = (
                f"METADATA.pb: primary_script field"
                f" should be '{guessed_primary_script}' but is missing."
            )
            sibling_scripts = get_sibling_scripts(guessed_primary_script)
            if sibling_scripts:
                sibling_scripts = ", ".join(sibling_scripts)
                message += (
                    f"\nMake sure that '{guessed_primary_script}' is"
                    f" actually the correct one (out of {sibling_scripts})."
                )
            yield WARN, Message("missing-primary-script", message)

        # family_metadata.primary_script is set
        # but it's not the same as guessed_primary_script
        if (
            family_metadata.primary_script not in (None, "")
            and family_metadata.primary_script != guessed_primary_script
            and is_sibling_script(
                family_metadata.primary_script, guessed_primary_script
            )
            is None
        ):
            yield WARN, Message(
                "wrong-primary-script",
                (
                    f"METADATA.pb: primary_script is '{family_metadata.primary_script}'"
                    f"\nIt should instead be '{guessed_primary_script}'."
                ),
            )
