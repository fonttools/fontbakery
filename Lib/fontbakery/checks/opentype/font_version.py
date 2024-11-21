import fractions

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.constants import NameID


def parse_version_string(name: str) -> float:
    """Parse a version string (name ID 5) as a decimal and
    return as fractions.Fraction.

    Example of the expected format: 'Version 01.003; Comments'. Version
    strings like "Version 1.300" will be post-processed into
    Fraction(13, 10).
    The parsed version numbers will therefore match as numbers, but not
    necessarily in string form.
    """
    import re

    # We assume ";" is the universal delimiter here.
    version_entry = name.split(";")[0]

    # Catch both "Version 1.234" and "1.234" but not "1x2.34". Note: search()
    # will return the first match.
    version_string = re.search(r"(?: |^)(\d+\.\d+)", version_entry)

    if version_string is None:
        raise ValueError(
            "The version string didn't contain a number of the format `major.minor`."
        )

    return fractions.Fraction(version_string.group(1))


@check(
    id="opentype/font_version",
    rationale="""
            The OpenType specification provides for two fields which contain
            the version number of the font: fontRevision in the head table,
            and nameID 5 in the name table. If these fields do not match,
            different applications will report different version numbers for
            the font.
        """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_font_version(ttFont):
    """Checking font version fields (head and name table)."""

    # Get font version from the head table as an exact Fraction.
    head_version = fractions.Fraction(ttFont["head"].fontRevision)

    # 1/0x10000 is the best achievable when converting a decimal
    # to 16.16 Fixed point.
    warn_tolerance = 1 / 0x10000
    # Some tools aren't that accurate and only care to do a
    # conversion to 3 decimal places.
    # 1/2000 is the tolerance for accepting equality to 3 decimal places.
    fail_tolerance = fractions.Fraction(1, 2000)

    # Compare the head version against the name ID 5 strings in all name records.
    name_id_5_records = [
        record
        for record in ttFont["name"].names
        if record.nameID == NameID.VERSION_STRING
    ]

    if name_id_5_records:
        for record in name_id_5_records:
            try:
                name_version = parse_version_string(record.toUnicode())
                if abs(name_version - head_version) > fail_tolerance:
                    yield FAIL, Message(
                        "mismatch",
                        f'head version is "{float(head_version):.5f}"'
                        f" while name version string (for"
                        f" platform {record.platformID},"
                        f" encoding {record.platEncID}) is"
                        f' "{record.toUnicode()}".',
                    )
                elif abs(name_version - head_version) > warn_tolerance:
                    yield WARN, Message(
                        "near-mismatch",
                        f'head version is "{float(head_version):.5f}"'
                        f" while name version string (for"
                        f" platform {record.platformID},"
                        f" encoding {record.platEncID}) is"
                        f' "{record.toUnicode()}".'
                        f" This matches to 3 decimal places, but"
                        f" is not as accurate as possible.",
                    )
            except ValueError:
                yield FAIL, Message(
                    "parse",
                    f"name version string for"
                    f" platform {record.platformID},"
                    f" encoding {record.platEncID}"
                    f' ("{record.toUnicode()}"),'
                    f" could not be parsed.",
                )
    else:
        yield FAIL, Message(
            "missing", "There is no name ID 5 (version string) in the font."
        )
