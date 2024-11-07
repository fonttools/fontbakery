from fontbakery.glyphdata import desired_glyph_data
from fontbakery.prelude import PASS, WARN, FAIL, Message, check
from fontbakery.utils import (
    bullet_list,
    get_font_glyph_data,
    pretty_print_list,
)


@check(
    id="contour_count",
    conditions=["is_ttf", "not is_variable_font"],
    rationale="""
        Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
        be constructured in a handful of ways. This means a glyph's contour count
        will only differ slightly amongst different fonts, e.g a 'g' could either
        be 2 or 3 contours, depending on whether its double story or single story.

        However, a quotedbl should have 2 contours, unless the font belongs
        to a display family.

        This check currently does not cover variable fonts because there's plenty
        of alternative ways of constructing glyphs with multiple outlines for each
        feature in a VarFont. The expected contour count data for this check is
        currently optimized for the typical construction of glyphs in static fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_contour_count(ttFont, config):
    """Check if each glyph has the recommended amount of contours.

    This check is useful to assure glyphs aren't incorrectly constructed.

    The desired_glyph_data module contains the 'recommended' countour count
    for encoded glyphs. The contour counts are derived from fonts which were
    chosen for their quality and unique design decisions for particular glyphs.

    In the future, additional glyph data can be included. A good addition would
    be the 'recommended' anchor counts for each glyph.
    """

    def in_PUA_range(codepoint):
        """
        In Unicode, a Private Use Area (PUA) is a range of code points that,
        by definition, will not be assigned characters by the Unicode Consortium.
        Three private use areas are defined:
          one in the Basic Multilingual Plane (U+E000–U+F8FF),
          and one each in, and nearly covering, planes 15 and 16
          (U+F0000–U+FFFFD, U+100000–U+10FFFD).
        """
        return (
            (codepoint >= 0xE000 and codepoint <= 0xF8FF)
            or (codepoint >= 0xF0000 and codepoint <= 0xFFFFD)
            or (codepoint >= 0x100000 and codepoint <= 0x10FFFD)
        )

    # rearrange data structure:
    desired_glyph_data_by_codepoint = {}
    desired_glyph_data_by_glyphname = {}
    for glyph in desired_glyph_data:
        desired_glyph_data_by_glyphname[glyph["name"]] = glyph
        # since the glyph in PUA ranges have unspecified meaning,
        # it doesnt make sense for us to have an expected contour cont for them
        if not in_PUA_range(glyph["unicode"]):
            desired_glyph_data_by_codepoint[glyph["unicode"]] = glyph

    bad_glyphs = []
    desired_glyph_contours_by_codepoint = {
        f: desired_glyph_data_by_codepoint[f]["contours"]
        for f in desired_glyph_data_by_codepoint
    }
    desired_glyph_contours_by_glyphname = {
        f: desired_glyph_data_by_glyphname[f]["contours"]
        for f in desired_glyph_data_by_glyphname
    }

    font_glyph_data = get_font_glyph_data(ttFont)

    if font_glyph_data is None:
        yield FAIL, Message("lacks-cmap", "This font lacks cmap data.")
    else:
        font_glyph_contours_by_codepoint = {
            f["unicode"]: list(f["contours"])[0] for f in font_glyph_data
        }
        font_glyph_contours_by_glyphname = {
            f["name"]: list(f["contours"])[0] for f in font_glyph_data
        }

        shared_glyphs_by_codepoint = set(desired_glyph_contours_by_codepoint) & set(
            font_glyph_contours_by_codepoint
        )
        for glyph in sorted(shared_glyphs_by_codepoint):
            if (
                font_glyph_contours_by_codepoint[glyph]
                not in desired_glyph_contours_by_codepoint[glyph]
            ):
                bad_glyphs.append(
                    [
                        glyph,
                        font_glyph_contours_by_codepoint[glyph],
                        desired_glyph_contours_by_codepoint[glyph],
                    ]
                )

        shared_glyphs_by_glyphname = set(desired_glyph_contours_by_glyphname) & set(
            font_glyph_contours_by_glyphname
        )
        for glyph in sorted(shared_glyphs_by_glyphname):
            if (
                font_glyph_contours_by_glyphname[glyph]
                not in desired_glyph_contours_by_glyphname[glyph]
            ):
                bad_glyphs.append(
                    [
                        glyph,
                        font_glyph_contours_by_glyphname[glyph],
                        desired_glyph_contours_by_glyphname[glyph],
                    ]
                )

        if len(bad_glyphs) > 0:
            cmap = ttFont.getBestCmap()

            def _glyph_name(cmap, name):
                if name in cmap:
                    return cmap[name]
                else:
                    return name

            bad_glyphs_message = []
            zero_contours_message = []

            for name, count, expected in bad_glyphs:
                if count == 0:
                    zero_contours_message.append(
                        f"Glyph name: {_glyph_name(cmap, name)}\t"
                        f"Expected: {pretty_print_list(config, expected, glue=' or ')}"
                    )
                else:
                    bad_glyphs_message.append(
                        f"Glyph name: {_glyph_name(cmap, name)}\t"
                        f"Contours detected: {count}\t"
                        f"Expected: {pretty_print_list(config, expected, glue=' or ')}"
                    )

            if bad_glyphs_message:
                bad_glyphs_message = bullet_list(config, bad_glyphs_message)
                yield WARN, Message(
                    "contour-count",
                    "This check inspects the glyph outlines and detects the total"
                    " number of contours in each of them. The expected values are"
                    " infered from the typical ammounts of contours observed in a"
                    " large collection of reference font families. The divergences"
                    " listed below may simply indicate a significantly different"
                    " design on some of your glyphs. On the other hand, some of these"
                    " may flag actual bugs in the font such as glyphs mapped to an"
                    " incorrect codepoint. Please consider reviewing the design and"
                    " codepoint assignment of these to make sure they are correct.\n\n"
                    "The following glyphs do not have the recommended number of"
                    f" contours:\n\n{bad_glyphs_message}\n",
                )

            if zero_contours_message:
                zero_contours_message = bullet_list(config, zero_contours_message)
                yield FAIL, Message(
                    "no-contour",
                    "The following glyphs have no contours even though they were"
                    f" expected to have some:\n\n{zero_contours_message}\n",
                )
        else:
            yield PASS, "All glyphs have the recommended amount of contours"
