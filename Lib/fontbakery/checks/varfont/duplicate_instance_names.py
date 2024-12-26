from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID
from fontbakery.prelude import check, Message, FAIL


@check(
    id="varfont/duplicate_instance_names",
    rationale="""
        This check's purpose is to detect duplicate named instances names in a
        given variable font.

        Repeating instance names may be the result of instances for several VF axes
        defined in `fvar`, but in some setups only weight+italic tokens are used
        in instance names, so they end up repeating.

        Only a base set of fonts for the most default representation of the
        family can be defined through instances in the `fvar` table, all other
        instances will have to be left to access through the `STAT` table.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2986",
)
def check_varfont_duplicate_instance_names(ttFont):
    """Check variable font instances don't have duplicate names"""
    seen = set()
    duplicate = set()
    PLAT_ID = PlatformID.WINDOWS
    ENC_ID = WindowsEncodingID.UNICODE_BMP
    LANG_ID = WindowsLanguageID.ENGLISH_USA

    for instance in ttFont["fvar"].instances:
        name_id = instance.subfamilyNameID
        name = ttFont["name"].getName(name_id, PLAT_ID, ENC_ID, LANG_ID)

        if name:
            name = name.toUnicode()

            if name in seen:
                duplicate.add(name)
            else:
                seen.add(name)
        else:
            yield FAIL, Message(
                "name-record-not-found",
                f"A 'name' table record for platformID {PLAT_ID},"
                f" encodingID {ENC_ID}, languageID {LANG_ID}({LANG_ID:04X}),"
                f" and nameID {name_id} was not found.",
            )

    if duplicate:
        duplicate_instances = "".join(f"* {inst}\n" for inst in sorted(duplicate))
        yield FAIL, Message(
            "duplicate-instance-names",
            f"Following instances names are duplicate:\n\n{duplicate_instances}",
        )
