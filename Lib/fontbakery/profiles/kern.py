from fontbakery.callable import check
from fontbakery.status import FAIL, INFO, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import (  # NOQA pylint: disable=unused-import
    profile_factory,
)


@check(
    id="com.google.fonts/check/kern_table",
    rationale="""
        Even though all fonts should have their kerning implemented in the GPOS table,
        there may be kerning info at the kern table as well.

        Some applications such as MS PowerPoint require kerning info on the kern table.
        More specifically, they require a format 0 kern subtable from a kern table
        version 0 with only glyphs defined in the cmap table, which is the only one
        that Windows understands (and which is also the simplest and more limited
        of all the kern subtables).

        Google Fonts ingests fonts made for download and use on desktops, and does
        all web font optimizations in the serving pipeline (using libre libraries
        that anyone can replicate.)

        Ideally, TTFs intended for desktop users (and thus the ones intended for
        Google Fonts) should have both KERN and GPOS tables.

        Given all of the above, we currently treat kerning on a v0 kern table
        as a good-to-have (but optional) feature.
    """,
    proposal=[
        "legacy:check/066",
        "https://github.com/googlefonts/fontbakery/issues/1675",
        "https://github.com/googlefonts/fontbakery/issues/3148",
    ],
)
def com_google_fonts_check_kern_table(ttFont):
    """Is there a usable "kern" table declared in the font?"""

    kern = ttFont.get("kern")
    if kern:
        # Scour all cmap tables for encoded glyphs.
        characterGlyphs = set()
        for table in ttFont["cmap"].tables:
            characterGlyphs.update(table.cmap.values())

        nonCharacterGlyphs = set()
        for kernTable in kern.kernTables:
            if kernTable.format == 0:
                for leftGlyph, rightGlyph in kernTable.kernTable.keys():
                    if leftGlyph not in characterGlyphs:
                        nonCharacterGlyphs.add(leftGlyph)
                    if rightGlyph not in characterGlyphs:
                        nonCharacterGlyphs.add(rightGlyph)
        if all(kernTable.format != 0 for kernTable in kern.kernTables):
            yield WARN, Message(
                "kern-unknown-format",
                'The "kern" table does not have any format-0 subtable '
                "and will not work in a few programs that may require "
                "the table.",
            )
        elif nonCharacterGlyphs:
            yield FAIL, Message(
                "kern-non-character-glyphs",
                'The following glyphs should not be used in the "kern" '
                'table because they are not in the "cmap" table: %s'
                % ", ".join(sorted(nonCharacterGlyphs)),
            )
        else:
            yield INFO, Message(
                "kern-found",
                "Only a few programs may require the kerning"
                ' info that this font provides on its "kern" table.',
            )
    else:
        yield PASS, 'Font does not declare an optional "kern" table.'
