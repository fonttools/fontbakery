from fontbakery.constants import REGISTERED_AXIS_TAGS
from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/varfont/foundry_defined_tag_name",
    rationale="""
        According to the OpenType spec's syntactic requirements for
        foundry-defined design-variation axis tags available at
        https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxisreg

        Foundry-defined tags must begin with an uppercase letter
        and must use only uppercase letters or digits.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/4043",
)
def check_varfont_foundry_defined_tag_name(ttFont):
    "Validate foundry-defined design-variation axis tag names."
    for axis in ttFont["fvar"].axes:
        axisTag = axis.axisTag
        if axisTag in REGISTERED_AXIS_TAGS:
            continue
        if axisTag.lower() in REGISTERED_AXIS_TAGS:
            yield WARN, Message(
                "foundry-defined-similar-registered-name",
                f'Foundry-defined tag "{axisTag}" is very similar to'
                f' registered tag "{axisTag.lower()}", consider renaming.\n'
                f"If this tag was meant to be a registered tag, please"
                f" use all lowercase letters in the tag name.",
            )

        firstChar = ord(axisTag[0])
        if not (firstChar >= ord("A") and firstChar <= ord("Z")):
            yield FAIL, Message(
                "invalid-foundry-defined-tag-first-letter",
                f'Please fix axis tag "{axisTag}".\n'
                f"Foundry-defined tags must begin with an uppercase letter.",
            )

        for i in range(3):
            char = ord(axisTag[1 + i])
            if not (
                (char >= ord("0") and char <= ord("9"))
                or (char >= ord("A") and char <= ord("Z"))
            ):
                yield FAIL, Message(
                    "invalid-foundry-defined-tag-chars",
                    f'Please fix axis tag "{axisTag}".\n'
                    f"Foundry-defined tags must only use"
                    f" uppercase or digits.",
                )
