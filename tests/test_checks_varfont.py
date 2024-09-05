from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.status import FAIL, WARN


def test_check_fvar_name_entries():
    """Check variable font instances."""
    # TODO: Implement-me!


def test_check_varfont_consistent_axes():
    """Check variable font instances."""
    # TODO: Implement-me!


def test_check_varfont_duplexed_axis_reflow():
    """Ensure VFs with the GRAD axis do not vary horizontal advance."""
    check = CheckTester("varfont/duplexed_axis_reflow")

    ttFont = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    assert_results_contain(check(ttFont), FAIL, "grad-causes-reflow")

    # Zero out the horizontal advances
    gvar = ttFont["gvar"]
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            if "GRAD" not in delta.axes:
                continue
            if delta.coordinates:
                delta.coordinates = delta.coordinates[:-4] + [(0, 0)] * 4

    # But the kern rules should still be a problem
    assert_results_contain(check(ttFont), FAIL, "duplexed-kern-causes-reflow")

    ttFont["GPOS"].table.LookupList.Lookup = []
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("bad_fonts/reflowing_ROND/BadRoundness-VF.ttf"))
    assert_results_contain(check(ttFont), FAIL, "rond-causes-reflow")


def test_check_varfont_unsupported_axes():
    """Ensure VFs do not contain (yet) the ital axis."""
    check = CheckTester("varfont/unsupported_axes")

    # Our reference varfont, CabinVFBeta.ttf, lacks 'ital' and 'slnt' variation axes.
    # So, should pass the check:
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # If we add 'ital' it must FAIL:
    from fontTools.ttLib.tables._f_v_a_r import Axis

    new_axis = Axis()
    new_axis.axisTag = "ital"
    ttFont["fvar"].axes.append(new_axis)
    assert_results_contain(check(ttFont), FAIL, "unsupported-ital")


def test_check_mandatory_avar_table():
    """Ensure variable fonts include an avar table."""
    check = CheckTester("mandatory_avar_table")

    ttFont = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(ttFont))

    del ttFont["avar"]
    assert_results_contain(check(ttFont), WARN, "missing-avar")


def test_varfont_instances_in_order():
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    check = CheckTester("varfont/instances_in_order")

    assert_PASS(check(ttFont))

    # Move the second instance to the front
    ttFont["fvar"].instances = [
        ttFont["fvar"].instances[1],
        ttFont["fvar"].instances[0],
    ] + ttFont["fvar"].instances[1:]
    assert_results_contain(check(ttFont), FAIL, "instances-not-in-order")
