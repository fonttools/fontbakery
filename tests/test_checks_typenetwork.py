from fontTools.ttLib import TTFont

from fontbakery.status import ERROR, FAIL, WARN, INFO, PASS, SKIP
from fontbakery.codetesting import (
    assert_results_contain,
    assert_PASS,
    TEST_FILE,
    CheckTester,
)

check_statuses = (ERROR, FAIL, WARN, INFO, PASS, SKIP)


def test_check_fstype():
    """Checking OS/2 fsType"""
    check = CheckTester("typenetwork/fstype")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    for value in [0, 1, 2, 4, 8, 0x0100, 0x0200]:
        ttFont["OS/2"].fsType = value
        if value == 4:
            assert_PASS(check(ttFont), "with a good font.")
        else:
            assert_results_contain(
                check(ttFont),
                WARN,
                "no-preview-print",
                "with a bad fstype value.",
            )


# ========= TODO: Implement code-test: ============
#  typenetwork/glyph_coverage
#  """Type Network expects that fonts in its catalog support at least the
#     minimal set of characters."""


# ========= TODO: Implement code-test: ============
#  typenetwork/vertical_metrics
#  """OS/2 and hhea vertical metric values should match.
#     This will produce the same linespacing on Mac, GNU+Linux and Windows."""


# ========= TODO: Implement code-test: ============
#  font_is_centered_vertically


# ========= TODO: Implement code-test: ============
#  typenetwork/tnum_horizontal_metrics
#  """Tabular figures need to have the same metrics in all styles in order
#     to allow tables to be set with proper typographic control, but to maintain
#     the placement of decimals and numeric columns between rows."""


# ========= TODO: Implement code-test: ============
#  typenetwork/family/equal_numbers_of_glyphs
#  """Check if all fonts in a family have the same number of glyphs."""


# ========= TODO: Implement code-test: ============
#  typenetwork/usweightclass
#  """Check usweightclass value."""


# ========= TODO: Implement code-test: ============
#  family/valid_underline
#  """If underline thickness is not set nothing gets rendered on Figma."""


# ========= TODO: Implement code-test: ============
#  family/valid_strikeout
#  """If strikeout size is not set, nothing gets rendered on Figma."""


# ========= TODO: Implement code-test: ============
#  typenetwork/composite_glyphs
#  """For performance reasons, is desirable that TTF fonts use composites glyphs."""


# ========= TODO: Implement code-test: ============
#  PUA_encoded_glyphs
#  """Since the use of PUA encoded glyphs is not frequent,
#     we want to WARN when a font can be a bad use of it,
#     like to encode small caps glyphs."""


# ========= TODO: Implement code-test: ============
#  marks_width
#  """To avoid incorrect overlappings when typing, glyphs that are spacing marks
#     must have width, on the other hand, combining marks should be 0 width."""


# ========= TODO: Implement code-test: ============
#  typenetwork/name/mandatory_entries
#  """For proper functioning, fonts must have some specific records.
#     Other name records are optional but desireable to be present."""


# ========= TODO: Implement code-test: ============
#  varfont/axes_have_variation
#  """Axes on a variable font must have variation. In other words min and max values
#     need to be different. It’s common to find fonts with unnecesary axes
#     added like `ital`."""


# ========= TODO: Implement code-test: ============
#  varfont/fvar_axes_order
#  """If a font doesn’t have a STAT table, instances get sorted better on Adobe Apps
#     when fvar axes follow a specific order: 'opsz', 'wdth', 'wght','ital', 'slnt'.
#     **Note:** We should deprecate this check since STAT is a required table."""


# ========= TODO: Implement code-test: ============
#  typenetwork/family/duplicated_names
#  """Check if font doesn’t have duplicated names within a family.
#     Having duplicated name records can produce several issues like not all fonts
#     being listed on design apps or incorrect automatic creation of CSS classes
#     and @font-face rules."""
