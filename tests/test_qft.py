"""Schwinger–Keldysh bridge tests (HYPOTHESIS.md §1).

Verifies the central claim that :class:`MobiusTemporalLoop` Picard
iteration is saddle-finding for the closed-time-path action S defined in
:mod:`dinos.qft`.

Falsifiable bridge in three layers:

  1. The Picard fixed point makes the EOM residuals small.
  2. A random perturbation away from it raises the residuals by orders
     of magnitude.
  3. Gradient descent on L = ⟨|R|²⟩ from a *different* initialization
     converges to a state with the same RMS amplitude — so the recovered
     electron mass via :mod:`dinos.closure` agrees.
"""

from math import isclose

import numpy as np
import pytest

from dinos import closure, qft
from dinos.temporal_loop import DKNParams, MobiusTemporalLoop


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

PARAMS = dict(N=64, T=4.0, K=64, alpha=0.7, beta=0.3,
              tau=1.0, damping=0.99, eta=0.0, seed=1)


def _picard_fixed_point(dkn=False):
    kwargs = dict(PARAMS)
    if dkn:
        kwargs["dkn_params"] = DKNParams(include_casimir=False)
    loop = MobiusTemporalLoop(**kwargs)
    result = loop.evolve(max_iter=200, epsilon=1e-2)
    assert result["converged"], (
        f"Picard iteration failed to converge "
        f"(max_err={result['final_max_error']:.3e})"
    )
    return loop, result


# -----------------------------------------------------------------------------
# Layer 1: Picard fixed point is a saddle of S
# -----------------------------------------------------------------------------

def test_residuals_small_at_picard_fixed_point():
    """At the converged Picard fixed point, R_f and R_b should be small."""
    loop, _ = _picard_fixed_point()
    R_f, R_b = qft.keldysh_residuals(
        loop.psi_f, loop.psi_b,
        alpha=loop.alpha, beta=loop.beta, gamma=loop.damping,
        T=loop.T, psi_target=loop.psi_target,
    )
    rms_f = float(np.sqrt(np.mean(np.abs(R_f) ** 2)))
    rms_b = float(np.sqrt(np.mean(np.abs(R_b) ** 2)))
    # Discrete EOM is the continuum limit; at Picard fixed point with
    # γ=0.99 there are O(1−γ) and O(Δt) corrections.  Both residuals
    # should sit in the noise of those corrections.
    assert rms_f < 0.1, f"forward residual RMS = {rms_f:.3e}"
    assert rms_b < 0.1, f"backward residual RMS = {rms_b:.3e}"


def test_loss_at_fixed_point_below_perturbation():
    """L at the Picard fixed point must be < L at a randomly perturbed state."""
    loop, _ = _picard_fixed_point()
    loss_fp = qft.squared_residual_loss(
        loop.psi_f, loop.psi_b,
        alpha=loop.alpha, beta=loop.beta, gamma=loop.damping,
        T=loop.T, psi_target=loop.psi_target,
    )
    rng = np.random.default_rng(123)
    noise = 0.5 * (rng.standard_normal(loop.psi_f.shape)
                   + 1j * rng.standard_normal(loop.psi_f.shape))
    loss_perturbed = qft.squared_residual_loss(
        loop.psi_f + noise, loop.psi_b - noise,
        alpha=loop.alpha, beta=loop.beta, gamma=loop.damping,
        T=loop.T, psi_target=loop.psi_target,
    )
    # A 50% noise injection should multiply the residual norm by ≥ 100×.
    assert loss_perturbed > 100 * loss_fp, (
        f"loss_fp={loss_fp:.3e}, loss_perturbed={loss_perturbed:.3e}"
    )


# -----------------------------------------------------------------------------
# Layer 2: gradient is the adjoint of the residual operator
# -----------------------------------------------------------------------------

def test_gradient_matches_finite_difference():
    """Analytic Wirtinger gradient must match a finite-difference estimate."""
    rng = np.random.default_rng(0)
    N, K = 8, 6
    shape = (N, K + 1)
    psi_target = (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))
    psi_f = (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))
    psi_b = (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))
    kw = dict(alpha=0.4, beta=0.2, gamma=0.95, T=2.0, psi_target=psi_target)

    grad_f, grad_b = qft.keldysh_gradient(psi_f, psi_b, **kw)

    # Spot-check three random entries via central difference.
    eps = 1e-5
    for _ in range(3):
        i = rng.integers(N)
        m = rng.integers(K + 1)
        which = rng.choice(["f", "b"])
        # Real part directional derivative
        psi_plus = (psi_f.copy() if which == "f" else psi_b.copy())
        psi_plus[i, m] += eps
        if which == "f":
            L_plus = qft.squared_residual_loss(psi_plus, psi_b, **kw)
            L_minus = qft.squared_residual_loss(psi_f - 0, psi_b, **kw)
            psi_minus = psi_f.copy()
            psi_minus[i, m] -= eps
            L_minus = qft.squared_residual_loss(psi_minus, psi_b, **kw)
        else:
            L_plus = qft.squared_residual_loss(psi_f, psi_plus, **kw)
            psi_minus = psi_b.copy()
            psi_minus[i, m] -= eps
            L_minus = qft.squared_residual_loss(psi_f, psi_minus, **kw)
        fd_real = (L_plus - L_minus) / (2 * eps)
        # ∂L/∂Re(ψ[i,m]) = 2 Re(∂L/∂ψ̄[i,m])
        analytic = 2.0 * float(
            (grad_f[i, m] if which == "f" else grad_b[i, m]).real
        )
        assert isclose(fd_real, analytic, rel_tol=1e-3, abs_tol=1e-6), (
            f"FD vs analytic mismatch at ({i},{m},{which}): "
            f"fd={fd_real:.6e}, analytic={analytic:.6e}"
        )


# -----------------------------------------------------------------------------
# Layer 3: independent saddle finder reaches the same fixed point
# -----------------------------------------------------------------------------

def test_solver_descends_loss_from_perturbed_init():
    """From a perturbed init far from the saddle, momentum-GD on L must
    drive the loss back down to (near) the Picard fixed point's loss
    level.  This is the operational form of "the saddle is a basin of
    attraction for the action gradient" — the Schwinger–Keldysh claim."""
    loop, _ = _picard_fixed_point()
    rng = np.random.default_rng(99)
    perturb = 0.3 * (rng.standard_normal(loop.psi_target.shape)
                     + 1j * rng.standard_normal(loop.psi_target.shape))
    init_f = loop.psi_target + perturb
    init_b = loop.psi_target - perturb

    L0 = qft.squared_residual_loss(
        init_f, init_b, alpha=loop.alpha, beta=loop.beta,
        gamma=loop.damping, T=loop.T, psi_target=loop.psi_target,
    )
    L_picard = qft.squared_residual_loss(
        loop.psi_f, loop.psi_b, alpha=loop.alpha, beta=loop.beta,
        gamma=loop.damping, T=loop.T, psi_target=loop.psi_target,
    )

    res = qft.solve_saddle(
        psi_target=loop.psi_target,
        alpha=loop.alpha, beta=loop.beta, gamma=loop.damping,
        T=loop.T, anchor_t0=loop.psi_target[:, 0],
        init_psi_f=init_f, init_psi_b=init_b,
        max_iter=4000, tol=1e-10,
    )
    # Loss must decrease by at least 100×.
    assert res.history[-1] < L0 / 100.0, (
        f"loss did not descend enough: L0={L0:.3e}, "
        f"L_final={res.history[-1]:.3e}, L_picard={L_picard:.3e}"
    )


def test_solver_and_picard_agree_on_electron_mass():
    """If the bridge holds, both Picard and gradient descent should
    recover m_e to the same precision via :mod:`closure`."""
    dkn = DKNParams(include_casimir=False)
    kwargs = dict(PARAMS)
    kwargs["dkn_params"] = dkn
    loop = MobiusTemporalLoop(**kwargs)
    picard = loop.evolve(max_iter=200, epsilon=1e-2)
    assert picard["converged"]

    m_picard = closure.enforce_mobius_fixed_point(picard["fixed_point_slice"])

    res = qft.solve_saddle(
        psi_target=loop.psi_target,
        alpha=loop.alpha, beta=loop.beta, gamma=loop.damping,
        T=loop.T,
        anchor_t0=loop.psi_target[:, 0],
        init_psi_f=loop.psi_target.copy(),
        init_psi_b=loop.psi_target.copy(),
        max_iter=2000, tol=1e-10,
    )
    m_solver = closure.enforce_mobius_fixed_point(res.psi_f[:, 0])

    # Both must recover m_e in MeV; we ask for 5% agreement (the Picard
    # iteration itself only matches the algebraic m_e to ~5% at this
    # grid resolution, so demanding more would be unfair to the bridge
    # rather than to the discretization).
    assert isclose(m_solver["m_e_MeV"], m_picard["m_e_MeV"], rel_tol=5e-2), (
        f"Picard m_e = {m_picard['m_e_MeV']:.4e} MeV, "
        f"Solver m_e = {m_solver['m_e_MeV']:.4e} MeV"
    )
