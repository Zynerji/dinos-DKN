"""Z_2 x Z_3 holonomy → phi candidate tests (HYPOTHESIS Step 10b)."""

from math import isclose

from dinos import holonomy_phi as hp


# -----------------------------------------------------------------------------
# Empirical phi
# -----------------------------------------------------------------------------

def test_empirical_phi_lepton_value():
    """Empirical phi from Foot derivation should be ~ 0.2223 rad."""
    phi = hp.empirical_phi_lepton()
    assert isclose(phi, 0.22227, abs_tol=1e-4)


# -----------------------------------------------------------------------------
# 2/9 candidate (the suspicious one)
# -----------------------------------------------------------------------------

def test_two_ninths_is_within_one_part_in_4000_of_phi_lepton():
    """phi_lepton differs from 2/9 = 0.2222... by less than 5e-5 rad
    (~ 0.025% relative), which is the closest of any simple fraction
    or simple holonomy combination tested."""
    phi = hp.empirical_phi_lepton()
    two_ninths = 2.0 / 9.0
    diff = abs(phi - two_ninths)
    rel = diff / phi
    assert diff < 1e-4, f"phi - 2/9 = {diff}, expected < 1e-4"
    assert rel < 3e-4, f"|phi - 2/9|/phi = {rel}, expected < 3e-4"


def test_two_ninths_beats_cabibbo():
    """2/9 is significantly closer to phi_lepton than Cabibbo angle."""
    phi = hp.empirical_phi_lepton()
    diff_two_ninths = abs(phi - 2.0 / 9.0)
    diff_cabibbo = abs(phi - hp.THETA_CABIBBO_RAD)
    assert diff_two_ninths < diff_cabibbo / 50, (
        f"2/9 diff = {diff_two_ninths}, Cabibbo diff = {diff_cabibbo}"
    )


# -----------------------------------------------------------------------------
# Best candidate ranking
# -----------------------------------------------------------------------------

def test_best_simple_fraction_is_two_ninths():
    """Of all simple-fraction candidates, 2/9 is the closest."""
    best = hp.best_candidate()
    assert "2/9" in best.label or "1/3 - 1/9" in best.label, (
        f"best candidate: {best}"
    )


def test_score_candidates_returns_sorted():
    """Candidates returned in order of increasing |diff|."""
    cands = hp.score_candidates(hp.simple_fraction_candidates())
    diffs = [abs(c.diff_rad) for c in cands]
    assert all(d1 <= d2 for d1, d2 in zip(diffs, diffs[1:])), (
        "candidates not sorted by absolute difference"
    )


# -----------------------------------------------------------------------------
# Holonomy combinations
# -----------------------------------------------------------------------------

def test_z2_z3_combinations_are_in_unit_cell():
    """All Z_2 x Z_3 combinations lie in [0, 2pi)."""
    from math import pi
    combos = hp.combined_phase_combinations(n_max=5)
    for label, val in combos.items():
        assert 0 <= val < 2 * pi, f"combo {label} = {val} out of [0, 2pi)"


def test_holonomy_report_includes_all_diagnostics():
    """The report should include empirical phi, Cabibbo, simple-fraction
    candidate, and holonomy combination."""
    report = hp.generate_holonomy_report()
    assert isclose(report.empirical_phi_rad, 0.22227, abs_tol=1e-4)
    assert report.closest_simple_fraction is not None
    assert report.closest_holonomy_combo is not None
    # 2/9 (label "2/9") should be the simple-fraction winner.
    assert "2/9" in report.closest_simple_fraction.label or \
           "1/3 - 1/9" in report.closest_simple_fraction.label
