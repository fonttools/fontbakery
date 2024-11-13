from collections import defaultdict
from typing import Iterable

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.testable import Font
from fontbakery.utils import show_inconsistencies, bullet_list


@check(
    id="opentype/family/panose_familytype",
    rationale="""
        The [PANOSE value](https://monotype.github.io/panose/) in the OS/2 table is a
        way of classifying a font based on its visual appearance and characteristics.

        The first field in the PANOSE classification is the family type: 2 means Latin
        Text, 3 means Latin Script, 4 means Latin Decorative, 5 means Latin Symbol.
        This check ensures that within a family, all fonts have the same family type.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_panose_familytype(fonts: Iterable[Font], config):
    """Fonts have consistent PANOSE family type?"""
    missing = []
    familytypes = defaultdict(list)

    for font in fonts:
        if "OS/2" not in font.ttFont:
            missing.append(font.file_displayname)
            continue
        familytype = font.ttFont["OS/2"].panose.bFamilyType
        familytypes[familytype].append(font.file_displayname)

    if missing:
        yield FAIL, Message(
            "lacks-OS/2",
            "One or more fonts lack the required OS/2 table:\n"
            + bullet_list(config, missing),
        )

    if len(familytypes) > 1:
        yield WARN, Message(
            "inconsistency",
            "PANOSE family type is not the same across this family."
            " In order to fix this, please make sure that"
            " the panose.bFamilyType value is the same"
            " in the OS/2 table of all of this family font files.\n\n"
            "The following PANOSE family types were found:\n\n"
            + show_inconsistencies(familytypes, config),
        )
