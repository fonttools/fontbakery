import re

from fontbakery.prelude import check, FAIL, Message
from fontbakery.constants import NameID


TRADEMARK = r"(Noto|Arimo|Tinos) is a trademark of Google (Inc|LLC)"


@check(
    id="notofonts/name/trademark",
    rationale="""
        Noto fonts must contain the correct trademark entry in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_name_trademark(ttFont):
    """Ensure the trademark matches the expected string."""
    from fontbakery.utils import get_name_entry_strings

    trademarks = get_name_entry_strings(ttFont, NameID.TRADEMARK)
    if not trademarks:
        yield FAIL, Message("no-trademark", "The font contained no trademark entry.")
    for trademark in trademarks:
        if not re.match(TRADEMARK, trademark):
            yield FAIL, Message(
                "bad-trademark",
                f"The trademark entry should be '{TRADEMARK}' "
                f"but was actually '{trademark}'",
            )
