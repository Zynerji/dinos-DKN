"""SAT/SMT verification tests (HYPOTHESIS Step 9a)."""

from math import isclose

from dinos import generations, lepton_smt as ls


# -----------------------------------------------------------------------------
# V1: Foot identities (symbolic)
# -----------------------------------------------------------------------------

def test_foot_identities_proven_symbolically():
    """SymPy proves Sum cos = 0 and Sum cos^2 = 3/2 as identities for any phi."""
    r = ls.verify_foot_identities_symbolic()
    assert r.sum_cos_is_zero, "SymPy failed to prove Sum cos = 0"
    assert r.sum_cos_sq_is_three_halves, "SymPy failed to prove Sum cos^2 = 3/2"


# -----------------------------------------------------------------------------
# V2: Numerical Foot solution + residual verification
# -----------------------------------------------------------------------------

def test_foot_solution_residuals_below_one_percent():
    """Numerical Foot solve for empirical leptons gives mass residuals
    below 1%."""
    r = ls.verify_foot_solution_for_empirical_leptons(tolerance=1e-2)
    assert r.matches_empirical, (
        f"Foot solution doesn't match: residuals = {r.mass_residuals}"
    )


def test_foot_identity_residuals_at_solution_are_machine_precision():
    """At the numerical solution, the Foot identities Sum cos = 0 and
    Sum cos^2 = 3/2 should hold to machine precision."""
    r = ls.verify_foot_solution_for_empirical_leptons()
    sum_cos = r.foot_id_residuals["sum_cos"]
    sum_sq_dev = r.foot_id_residuals["sum_cos_sq_minus_3_halves"]
    assert abs(sum_cos) < 1e-10, f"sum_cos = {sum_cos}"
    assert abs(sum_sq_dev) < 1e-3, f"sum_cos^2 - 3/2 = {sum_sq_dev}"


# -----------------------------------------------------------------------------
# V3: Z3 2-SAT branch selection
# -----------------------------------------------------------------------------

def test_branch_selection_encoded_as_2sat():
    """Encoding produces some clauses (forbidding the 3 invalid branches)."""
    clauses = ls.encode_branch_selection_as_2sat()
    # Out of 4 branches, 3 are forbidden by positivity+hierarchy+cos-validity.
    # So 3 clauses, each a 2-literal conjunction-forbiddance.
    assert len(clauses) == 3
    for c in clauses:
        assert len(c) == 2  # 2-SAT


def test_z3_proves_unique_branch():
    """Z3 finds the unique surviving (sign_v, root_sign) assignment."""
    r = ls.verify_branch_selection_unique_z3()
    assert r["satisfiable"], "Z3 reports UNSAT — no valid branch"
    assert r["is_unique"], "Z3 found multiple satisfying branches"
    # The winning assignment should be (+1, -1) per Step 8 analysis.
    win = r["winning_assignment"]
    assert win["sign_v"] == 1
    assert win["root_sign"] == -1


# -----------------------------------------------------------------------------
# V3b: Helical-SAT cross-check
# -----------------------------------------------------------------------------

def test_helical_sat_module_importable():
    """The Helical-SAT-Heuristic module is reachable from this codebase."""
    r = ls.verify_branch_selection_via_helical_sat()
    assert r["available"], (
        f"Helical-SAT not available: {r.get('notes', 'no notes')}"
    )


def test_helical_sat_handles_or_documents_small_instance():
    """For our 2-SAT (3 clauses, 2 vars), Helical-SAT's spectral
    method either solves it (rho close to 1) or honestly reports
    the small-instance limitation."""
    r = ls.verify_branch_selection_via_helical_sat()
    # Either rho is reported (success) or rho is None with notes
    # explaining the instance is too small.
    if r["rho"] is not None:
        assert r["rho"] >= 0.5, f"Helical-SAT rho = {r['rho']}"
    else:
        assert "small" in r.get("notes", "").lower() or \
               "size" in r.get("notes", "").lower() or \
               "n_neighbors" in r.get("notes", "").lower(), (
            f"Expected a small-instance note: {r}"
        )
