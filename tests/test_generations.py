"""Generation-mass tower test (HYPOTHESIS.md Step 3).

Documents the falsification: lepton mass ratios cannot be produced as
topological excitations (n_φ, n_θ) of a single Möbius loop with fixed
σ, α. Both μ and τ require the Casimir parameter C to saturate near
the upper bound (1−α)/2 ≈ 0.4963, leaving no room to distinguish them.
"""

from math import isclose

import numpy as np

from dinos import generations


# -----------------------------------------------------------------------------
# Sanity / inversion
# -----------------------------------------------------------------------------

def test_C_required_for_unit_ratio_is_C_e():
    """Trivial check: ratio = 1 should reproduce the input C_e."""
    C_e = 0.17695
    out = generations.C_required_for_ratio(1.0, C_e=C_e)
    assert isclose(out, C_e, abs_tol=1e-12)


def test_mass_for_C_inverts_C_required_for_ratio():
    """mass_for_C ∘ C_required_for_ratio should round-trip."""
    target_ratio = 5.0
    C_l = generations.C_required_for_ratio(target_ratio)
    m_l = generations.mass_for_C(C_l)
    m_e = generations.mass_for_C(generations.C.C_bag_Dirac if False else 0.17695)
    # Use closure's electron-mass value as ground truth.
    from dinos import closure
    m_e_check = closure.electron_mass(
        sigma_MeV3=closure.required_surface_tension(),
    )
    assert isclose(m_l / m_e_check, target_ratio, rel_tol=1e-9)


# -----------------------------------------------------------------------------
# Falsification — the actual content
# -----------------------------------------------------------------------------

def test_required_Cs_for_mu_and_tau_both_saturate():
    """C_μ and C_τ both push against (1−α)/2 ≈ 0.4963 — they're
    indistinguishable to ~10⁻⁶ even though m_μ and m_τ are 17× apart."""
    Cs = generations.required_C_per_generation()
    C_max = generations.C_max()
    # Both should be within 1e-3 of C_max.
    assert C_max - Cs["mu"] < 1e-3, (
        f"C_μ = {Cs['mu']}, C_max = {C_max}, gap = {C_max - Cs['mu']}"
    )
    assert C_max - Cs["tau"] < 1e-7, (
        f"C_τ = {Cs['tau']}, C_max = {C_max}, gap = {C_max - Cs['tau']}"
    )
    # The two must be within 1e-3 of each other despite the 17× mass gap.
    assert abs(Cs["mu"] - Cs["tau"]) < 1e-3, (
        f"|C_μ − C_τ| = {abs(Cs['mu'] - Cs['tau'])}; "
        f"if topological, this gap should reflect the m_τ/m_μ ratio"
    )


def test_topological_power_law_does_not_fit():
    """Fit C_l = c₀ |k|^p with |k| ∈ {1, 2, 3}.  A clean topological
    law would have residual ≪ 1; in fact the residual exceeds 5%."""
    Cs = generations.required_C_per_generation()
    ks = generations.k_dirac_per_generation()
    fit = generations.fit_C_power_law(Cs, ks)
    # The residual is around 30% — strongly inconsistent with a clean law.
    assert fit.relative_residual > 0.05, (
        f"power-law residual = {fit.relative_residual:.4f} — surprisingly low; "
        f"recheck the falsification logic.  Fit: c0={fit.c0}, p={fit.p}"
    )


def test_two_point_extrapolation_misses_tau_by_orders_of_magnitude():
    """Calibrate C ∝ |k|^p on (e, μ); predict m_τ.  Empirical m_τ =
    1776.86 MeV.  A topological framework would predict this within
    ~10%; the actual prediction is wildly off."""
    pred = generations.predict_tau_from_e_and_mu()
    # Either infinite (saturated C) or off by orders of magnitude.
    assert pred["rel_error"] > 0.5, (
        f"Predicted m_τ = {pred['m_tau_predicted_MeV']} MeV vs empirical "
        f"{pred['m_tau_empirical_MeV']} MeV; rel_error = {pred['rel_error']}. "
        f"This test expects the framework to FAIL — if it passes by being "
        f"close, the topological-tower hypothesis is unexpectedly viable."
    )


def test_per_generation_sigma_scales_as_mass_cubed():
    """If we fix C and let σ vary per generation, σ_l ∝ m_l³.  This is
    the *only* way the framework accommodates the lepton tower — but
    it's a restatement of the masses, not a prediction."""
    from dinos import closure
    sigma_e = closure.required_surface_tension(m_e_MeV=generations.M_E_MeV)
    sigma_mu = closure.required_surface_tension(m_e_MeV=generations.M_MU_MeV)
    sigma_tau = closure.required_surface_tension(m_e_MeV=generations.M_TAU_MeV)
    ratio_mu = sigma_mu / sigma_e
    ratio_tau = sigma_tau / sigma_e
    expected_mu = (generations.M_MU_MeV / generations.M_E_MeV) ** 3
    expected_tau = (generations.M_TAU_MeV / generations.M_E_MeV) ** 3
    assert isclose(ratio_mu, expected_mu, rel_tol=1e-9)
    assert isclose(ratio_tau, expected_tau, rel_tol=1e-9)


def test_log_residue_vs_log_mass_slope_is_minus_three():
    """In log-space, the closure r = 1 − 2C − α gives the algebraic
    identity log(r_l/r_e) = -3 log(m_l/m_e) — exact, not a fit.

    This is the cleanest visualisation of the falsification: residues
    span ~25 in natural log across the lepton tower, while log|k| spans
    only ~1.  No topological label can produce that."""
    slope = generations.log_residue_vs_log_mass_slope()
    assert isclose(slope, -3.0, abs_tol=1e-6), (
        f"log r vs log m slope = {slope}; closure identity demands -3 exactly"
    )


def test_log_residue_spans_orders_of_magnitude_while_log_k_does_not():
    """Quantify the falsification: log r spans >20, log |k| spans <1.5."""
    log_r = generations.log_residue_per_generation()
    log_k = {l: float(np.log(k))
             for l, k in generations.k_dirac_per_generation().items()}
    log_r_range = max(log_r.values()) - min(log_r.values())
    log_k_range = max(log_k.values()) - min(log_k.values())
    # log r spans ~25, log |k| spans log(3) ≈ 1.1.
    assert log_r_range > 20.0, f"log r range = {log_r_range}"
    assert log_k_range < 1.5, f"log k range = {log_k_range}"
    # Their ratio is the order-of-magnitude mismatch between residue
    # and topological label — must exceed 10.
    assert log_r_range / log_k_range > 10.0, (
        f"log_r/log_k range ratio = {log_r_range/log_k_range}; "
        f"a topological tower would need ratio ~1"
    )


def test_falsification_summary_report():
    """Print the full falsification table so the verdict is on record.

    This test always passes; it exists to surface the numbers in the
    test log for posterity.
    """
    Cs = generations.required_C_per_generation()
    pred = generations.predict_tau_from_e_and_mu()
    fit = generations.fit_C_power_law(
        Cs, generations.k_dirac_per_generation()
    )
    print()
    print("=" * 60)
    print("LEPTON-TOWER FALSIFICATION REPORT (HYPOTHESIS Step 3)")
    print("=" * 60)
    print(f"Required C_e   = {Cs['e']:.6f}   (input C_bag_Dirac)")
    print(f"Required C_mu  = {Cs['mu']:.6f}")
    print(f"Required C_tau = {Cs['tau']:.6f}")
    print(f"C_max bound    = {generations.C_max():.6f}")
    print(f"|C_mu - C_tau| = {abs(Cs['mu'] - Cs['tau']):.3e}  (vs 17x mass gap)")
    print()
    print(f"Power-law fit C = c0 * |k|^p :")
    print(f"  c0 = {fit.c0:.4f},  p = {fit.p:.4f}")
    print(f"  residual = {fit.relative_residual:.4f}  (clean fit would be << 0.01)")
    print()
    print(f"Predict m_tau from (e, mu) calibration:")
    print(f"  predicted = {pred['m_tau_predicted_MeV']} MeV")
    print(f"  empirical = {pred['m_tau_empirical_MeV']} MeV")
    print(f"  rel error = {pred['rel_error']}")
    print("=" * 60)
    print("VERDICT: lepton tower is NOT a topological excitation of the")
    print("same Mobius loop.  Per-generation sigma_l ~ m_l^3 is required -")
    print("a restatement, not a prediction.")
    print("=" * 60)
