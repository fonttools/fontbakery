import re

from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL


@check(
    id="name/char_restrictions",
    rationale="""
        The OpenType spec requires a subset of ASCII
        (any printable characters except "[]{}()<>/%") for
        POSTSCRIPT_NAME (nameID 6),
        POSTSCRIPT_CID_NAME (nameID 20), and
        an even smaller subset ("a-zA-Z0-9") for
        VARIATIONS_POSTSCRIPT_NAME_PREFIX (nameID 25).
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1718",
        "https://github.com/fonttools/fontbakery/issues/1663",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_name_char_restrictions(ttFont):
    """Are there disallowed characters in the NAME table?"""
    bad_entries = []

    restricted_chars = re.compile(r"[^!-$&'*-.0-;=?-Z^-z|~]")
    prefix_restricted_chars = re.compile(r"[^a-zA-Z0-9]")
    restrictions = {
        NameID.POSTSCRIPT_NAME: restricted_chars,
        NameID.POSTSCRIPT_CID_NAME: restricted_chars,
        NameID.VARIATIONS_POSTSCRIPT_NAME_PREFIX: prefix_restricted_chars,
    }

    for name in ttFont["name"].names:
        if name.nameID in restrictions.keys():
            string = name.string.decode(name.getEncoding())
            if restrictions[name.nameID].search(string):
                bad_entries.append(name)
                badstring = string.encode("ascii", errors="xmlcharrefreplace")
                yield FAIL, Message(
                    "bad-string",
                    (
                        f"Bad string at"
                        f" [nameID {name.nameID}, platformID {name.platformID},"
                        f" langID {name.langID}, encoding '{name.getEncoding()}']:"
                        f" '{badstring}'"
                    ),
                )
    if len(bad_entries) > 0:
        yield FAIL, Message(
            "bad-strings",
            (
                f"There are {len(bad_entries)} strings containing"
                " disallowed characters in the restricted"
                " NAME table entries."
            ),
        )
