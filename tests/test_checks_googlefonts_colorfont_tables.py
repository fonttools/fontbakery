from fontTools.ttLib import newTable, TTFont
from fontTools.ttLib.tables.S_V_G_ import SVGDocument

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import FAIL


@check_id("googlefonts/colorfont_tables")
def test_check_colorfont_tables(check):
    """Ensure font has the expected color font tables."""

    ttFont = TTFont(TEST_FILE("color_fonts/noto-glyf_colr_1.ttf"))
    assert "SVG " not in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    # Check colr v1 static font has an svg table (since v1 isn't yet broadly supported).
    # Will fail since font doesn't have one.
    assert_results_contain(
        check(ttFont), FAIL, "add-svg", "with a static colr v1 font lacking SVG table"
    )

    # Fake a variable font by adding an fvar table.
    ttFont["fvar"] = newTable("fvar")
    assert "fvar" in ttFont.keys()

    # SVG does not support OpenType Variations
    assert_PASS(check(ttFont), "with a variable color font without SVG table")

    # Fake an SVG table:
    ttFont["SVG "] = newTable("SVG ")
    assert "SVG " in ttFont.keys()

    assert_results_contain(
        check(ttFont), FAIL, "variable-svg", "with a variable color font with SVG table"
    )

    # A variable font whose SVG color glyphs have no variation data
    # must not be flagged (issue #4946). Replace the fake SVG table with
    # one describing a real glyph, and add an empty gvar table:
    svg_table = newTable("SVG ")
    glyph_id = ttFont.getGlyphOrder().index("uE0062")
    svg_table.docList = [
        SVGDocument(
            data="<svg></svg>",
            startGlyphID=glyph_id,
            endGlyphID=glyph_id,
        )
    ]
    ttFont["SVG "] = svg_table
    ttFont["gvar"] = newTable("gvar")
    assert_PASS(
        check(ttFont),
        "with a variable font whose SVG color glyphs have no variation data",
    )

    # But it must still FAIL when an SVG color glyph does have variations:
    ttFont["gvar"].variations = {"uE0062": [({}, None)]}
    assert_results_contain(
        check(ttFont),
        FAIL,
        "variable-svg",
        "with a variable font whose SVG color glyph has variations",
    )
    del ttFont["gvar"]

    # Make it a static again:
    del ttFont["fvar"]
    assert "fvar" not in ttFont.keys()

    assert "SVG " in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    assert_PASS(check(ttFont), "with a static colr v1 font containing both tables.")

    # Now downgrade to colr table to v0:
    ttFont["COLR"].version = 0
    assert "SVG " in ttFont.keys()
    assert_results_contain(
        check(ttFont),
        FAIL,
        "drop-svg",
        "with a font which should not have an SVG table",
    )

    # Delete colr table and keep SVG:
    del ttFont["COLR"]
    assert "SVG " in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_results_contain(
        check(ttFont), FAIL, "add-colr", "with a font which should have a COLR table"
    )

    # Finally delete both color font tables
    del ttFont["SVG "]
    assert "SVG " not in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_PASS(check(ttFont), "with a good font without SVG or COLR tables.")


@check_id("googlefonts/colorfont_tables")
def test_check_colorfont_tables_cff2_variable_svg(check):
    """SVG color glyphs without variation data must not FAIL on CFF2 VFs (issue #4946)."""
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    assert "fvar" in ttFont.keys()
    assert "CFF2" in ttFont.keys()
    glyph_order = ttFont.getGlyphOrder()

    def svg_table_covering(glyph_name):
        svg_table = newTable("SVG ")
        glyph_id = glyph_order.index(glyph_name)
        svg_table.docList = [
            SVGDocument(
                data="<svg></svg>",
                startGlyphID=glyph_id,
                endGlyphID=glyph_id,
            )
        ]
        return svg_table

    # "space" has no variation data: no "variable-svg" FAIL is expected.
    ttFont["SVG "] = svg_table_covering("space")
    assert not any(
        getattr(subresult.message, "code", None) == "variable-svg"
        for subresult in check(ttFont)
    ), "a variable CFF2 font whose SVG color glyphs do not vary must not FAIL"

    # "A" does have variation data: "variable-svg" FAIL is expected.
    ttFont["SVG "] = svg_table_covering("A")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "variable-svg",
        "with a variable CFF2 font whose SVG color glyph has variations",
    )
