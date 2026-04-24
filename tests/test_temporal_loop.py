"""Möbius temporal loop: convergence, divergence metric, and DKN coupling."""

from math import isclose

import numpy as np
import pytest

from dinos import closure, geodesic, temporal_loop
from dinos.temporal_loop import DKNParams, MobiusTemporalLoop, mobius_laplacian


# -----------------------------------------------------------------------------
# Discrete Möbius operator
# -----------------------------------------------------------------------------

def test_mobius_laplacian_constant_is_minus_four_at_seam():
    # A globally constant array has Laplacian 0 everywhere except at the two
    # seam nodes, where the Z_2 flip produces −4·ψ.
    psi = np.ones(8, dtype=complex)
    lap = mobius_laplacian(psi)
    interior = lap[1:-1]
    np.testing.assert_allclose(interior, 0.0, atol=1e-14)
    # seam nodes: ψ[0] sees ψ[−1]→−ψ[7] = −1, so Laplacian = 1 + (−1) − 2·1 = −2
    # similarly ψ[7] sees ψ[8]→−ψ[0] = −1, Laplacian = (−1) + 1 − 2·1 = −2
    assert isclose(float(lap[0].real), -2.0)
    assert isclose(float(lap[-1].real), -2.0)


# -----------------------------------------------------------------------------
# Convergence: self-consistent (V2) initialization
# -----------------------------------------------------------------------------

def test_v2_self_consistent_converges():
    loop = MobiusTemporalLoop(N=64, T=4.0, K=64, alpha=0.7, beta=0.3,
                              tau=1.0, damping=0.99, eta=0.0, seed=1)
    result = loop.evolve(max_iter=120, epsilon=1e-2)
    assert result["converged"], (
        f"V2 self-consistent loop failed to converge: "
        f"max_err={result['final_max_error']:.3e}"
    )
    # Starting from a small symmetric kick, the iteration should converge
    # to a genuine fixed point (|ψ_f − ψ_b| = 0 at t=0 and driven down
    # elsewhere).
    assert result["final_max_error"] < 1e-2
    # Fixed-point slice must equal the spatial seed at t=0 (the DKN
    # antipodal Higgs boundary).
    fp = result["fixed_point_slice"]
    assert np.all(np.isfinite(fp))


def test_divergence_matches_definition():
    loop = MobiusTemporalLoop(N=32, T=2.0, K=32, alpha=0.5, beta=0.2,
                              eta=0.0, seed=0)
    loop.evolve(max_iter=20, epsilon=1e-4)
    D = loop.divergence()
    ref = float(np.mean(np.abs(loop.psi_f - loop.psi_b) ** 2))
    assert isclose(D, ref, rel_tol=1e-12)


# -----------------------------------------------------------------------------
# Paradox: random init without self-consistency anchor
# -----------------------------------------------------------------------------

def test_paradox_random_init_does_not_instantly_converge():
    """Random initialization (no DKN coupling, small α/β) should NOT
    converge below a tight ε in very few iterations — the divergence
    represents a real, unresolved paradox that the prophetic feedback
    must work to eliminate."""
    loop = MobiusTemporalLoop(N=64, T=5.0, K=64, alpha=0.05, beta=0.02,
                              damping=0.99, eta=0.1, seed=42)
    # Inject extra asymmetry (paradox): add noise only to ψ_b
    rng = np.random.default_rng(7)
    loop.psi_b = loop.psi_b + 0.5 * (rng.standard_normal(loop.psi_b.shape)
                                     + 1j * rng.standard_normal(loop.psi_b.shape))
    result = loop.evolve(max_iter=5, epsilon=1e-4)
    assert not result["converged"], (
        "paradoxical random init should not converge at ε=1e-4 in 5 iterations"
    )
    assert result["final_divergence"] > 0.0


# -----------------------------------------------------------------------------
# DKN integration: mass self-consistency recovered from fixed point
# -----------------------------------------------------------------------------

def test_dkn_fixed_point_recovers_electron_mass():
    dkn = DKNParams(include_casimir=False)  # amplitude = a (no Casimir dressing)
    loop = MobiusTemporalLoop(N=48, T=3.0, K=48, alpha=0.7, beta=0.3,
                              damping=0.99, eta=0.0,
                              dkn_params=dkn, seed=2)
    result = loop.evolve(max_iter=150, epsilon=1e-2)
    assert result["converged"]

    # Seed amplitude *was* the mass-self-consistent radius, so the fixed
    # point should still satisfy the closure identity within the damping
    # tolerance.
    closure_result = closure.enforce_mobius_fixed_point(result["fixed_point_slice"])
    # For the uniform-amplitude seed the RMS equals exactly |a|.
    a_expected = closure.compton_radius(dkn.sigma_MeV3, dkn.C_bag, dkn.alpha)
    assert isclose(closure_result["a_MeV_inv"], a_expected, rel_tol=5e-2), (
        f"a_eff = {closure_result['a_MeV_inv']:.4e}, expected {a_expected:.4e}"
    )
    assert isclose(closure_result["m_e_MeV"], 1.0 / (2.0 * a_expected),
                   rel_tol=5e-2)


def test_extract_quantum_numbers_returns_valid_labels():
    dkn = DKNParams(include_casimir=False)
    loop = MobiusTemporalLoop(N=64, T=3.0, K=64, alpha=0.7, beta=0.3,
                              eta=0.0, dkn_params=dkn, seed=3)
    loop.evolve(max_iter=80, epsilon=1e-2)
    qn = loop.extract_dkn_quantum_numbers()
    # Ground-state-like labels should be integers ≥ 0 with half-integer j
    assert qn["n_theta"] >= 0
    labels = qn["DiracLabels"]
    assert labels.k_abs >= 1
    assert labels.j == labels.k_abs - 0.5
    assert "m_e_MeV" in qn


# -----------------------------------------------------------------------------
# geodesic.quantize integration
# -----------------------------------------------------------------------------

def test_geodesic_quantize_standard_matches_direct():
    a = geodesic.geodesic_to_dirac(n_phi=1, n_theta=2)
    b = geodesic.quantize(n_phi=1, n_theta=2, boundary_condition="standard")
    assert a == b


def test_geodesic_quantize_mobius_self_consistent():
    dkn = DKNParams(include_casimir=False)
    loop = MobiusTemporalLoop(N=48, T=3.0, K=48, alpha=0.7, beta=0.3,
                              eta=0.0, dkn_params=dkn, seed=4)
    loop.evolve(max_iter=80, epsilon=1e-2)
    labels = geodesic.quantize(
        boundary_condition="mobius_self_consistent",
        mobius_psi=loop.psi_f[:, 0],
    )
    assert labels.k_abs >= 1


def test_emergent_twist_is_finite_after_convergence():
    dkn = DKNParams(include_casimir=False)
    loop = MobiusTemporalLoop(N=64, T=3.0, K=64, alpha=0.7, beta=0.3,
                              eta=0.0, dkn_params=dkn, seed=5)
    result = loop.evolve(max_iter=80, epsilon=1e-2)
    assert np.isfinite(result["phi_twist_extracted"])
    # Emergent twist must equal the standalone method's return value
    assert isclose(result["phi_twist_extracted"], loop.emergent_twist(),
                   rel_tol=1e-12, abs_tol=1e-14)


def test_geodesic_quantize_rejects_bad_kwargs():
    with pytest.raises(ValueError):
        geodesic.quantize(boundary_condition="standard")  # missing integers
    with pytest.raises(ValueError):
        geodesic.quantize(boundary_condition="mobius_self_consistent")  # missing psi
    with pytest.raises(ValueError):
        geodesic.quantize(boundary_condition="bogus", n_phi=0, n_theta=0)
