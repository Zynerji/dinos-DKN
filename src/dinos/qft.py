"""Schwinger–Keldysh action for the Möbius temporal loop.

Implements `HYPOTHESIS.md` Step 1: the closed-time-path action S whose
Euler–Lagrange equations are the prophetic-feedback PDE of
:mod:`dinos.temporal_loop`. Provides the residual operator R = (R_f, R_b)
that vanishes iff the fields are a saddle of S, and a gradient-descent
solver that finds the saddle directly — *without* simulating the time
loop.

If the saddle found by :func:`solve_saddle` matches the fixed point of
:meth:`MobiusTemporalLoop.evolve`, the Picard iteration is literally
Keldysh saddle-finding on the Möbius contour, and the recovered
``m_e = 0.5111 MeV`` is the saddle-point pole mass of a regulated 1+1D
QFT — not just the algebraic root of paper eq. 61.

Continuum action (HYPOTHESIS.md §1, with κ ≡ (1−γ)/Δt the damping rate):

    S = ∫ ds dt  {  ψ̄_f (∂_t − D_s) ψ_f
                 −  ψ̄_b (∂_t + D_s) ψ_b
                 +  α (ψ̄_f − ψ̄_b)(ψ_f − ψ_b)
                 +  (β+κ)/2 (|ψ_f − ψ_target|² + |ψ_b − ψ_target|²)  }

Forward Euler–Lagrange (δS/δψ̄_f = 0):

    R_f = (∂_t − D_s) ψ_f + α(ψ_f − ψ_b) + (β+κ)(ψ_f − ψ_target)

Backward Euler–Lagrange (δS/δψ̄_b = 0):

    R_b = −(∂_t + D_s) ψ_b − α(ψ_f − ψ_b) + (β+κ)(ψ_b − ψ_target)

Boundary conditions (Higgs wall + Möbius temporal seam):

    ψ_f(s, 0) = ψ_b(s, 0) = anchor_t0           ← fixed (in-state)
    ψ_f(s, T) = ψ_b(s, T)                       ← derived (out-state seam)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .temporal_loop import mobius_laplacian


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _kappa(gamma: float, dt: float) -> float:
    """Damping rate κ = (1 − γ)/Δt that appears in the continuum EOM.

    γ < 1 in :class:`MobiusTemporalLoop` is a Higgs-wall damping; in the
    continuum limit it becomes a mass-like term added to β.
    """
    return (1.0 - gamma) / dt


# -----------------------------------------------------------------------------
# Residuals (the EOM operator)
# -----------------------------------------------------------------------------

def keldysh_residuals(
    psi_f: np.ndarray,
    psi_b: np.ndarray,
    *,
    alpha: float,
    beta: float,
    gamma: float,
    T: float,
    psi_target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Discrete Euler–Lagrange residuals on the (N, K+1) strip.

    Returns (R_f, R_b), each of shape (N, K) — one residual per interior
    time interval.  ``R_f[:, k]`` couples slices k ↔ k+1 with a forward
    difference; ``R_b[:, k]`` couples slices k ↔ k+1 with a backward
    difference (i.e. the time-reversed branch).

    Vanishes identically (up to discretization) at any saddle of S.
    """
    psi_f = np.asarray(psi_f, dtype=complex)
    psi_b = np.asarray(psi_b, dtype=complex)
    psi_target = np.asarray(psi_target, dtype=complex)
    N, Kp1 = psi_f.shape
    K = Kp1 - 1
    if K < 1:
        raise ValueError("need K ≥ 1 time intervals (psi shape (N, K+1))")
    dt = T / K
    wall = beta + _kappa(gamma, dt)

    R_f = np.empty((N, K), dtype=complex)
    R_b = np.empty((N, K), dtype=complex)
    for k in range(K):
        # Forward EOM at time slice k.
        d_t_f = (psi_f[:, k + 1] - psi_f[:, k]) / dt
        lap_f = mobius_laplacian(psi_f[:, k])
        R_f[:, k] = (
            d_t_f
            - lap_f
            + alpha * (psi_f[:, k] - psi_b[:, k])
            + wall * (psi_f[:, k] - psi_target[:, k])
        )
        # Backward EOM at time slice k+1.
        # −∂_t ψ_b = D_s ψ_b + α(ψ_f − ψ_b) + (β+κ)(ψ_target − ψ_b)
        d_t_b = (psi_b[:, k + 1] - psi_b[:, k]) / dt   # this is +∂_t ψ_b
        lap_b = mobius_laplacian(psi_b[:, k + 1])
        R_b[:, k] = (
            -d_t_b
            - lap_b
            + alpha * (psi_b[:, k + 1] - psi_f[:, k + 1])
            + wall * (psi_b[:, k + 1] - psi_target[:, k + 1])
        )
    return R_f, R_b


def keldysh_action(
    psi_f: np.ndarray,
    psi_b: np.ndarray,
    *,
    alpha: float,
    beta: float,
    gamma: float,
    T: float,
    psi_target: np.ndarray,
) -> complex:
    """Discretized S[ψ_f, ψ_b] (informational; complex-valued in general).

    Useful for sanity checks; the actual saddle-finding uses
    :func:`squared_residual_loss` because L = ⟨|R|²⟩ is real-valued and
    bounded below by zero.
    """
    psi_f = np.asarray(psi_f, dtype=complex)
    psi_b = np.asarray(psi_b, dtype=complex)
    psi_target = np.asarray(psi_target, dtype=complex)
    N, Kp1 = psi_f.shape
    K = Kp1 - 1
    dt = T / K
    ds = 2.0 * np.pi / N
    wall = beta + _kappa(gamma, dt)

    S = 0.0 + 0.0j
    for k in range(K):
        d_t_f = (psi_f[:, k + 1] - psi_f[:, k]) / dt
        lap_f = mobius_laplacian(psi_f[:, k])
        kin_f = np.sum(psi_f[:, k].conj() * (d_t_f - lap_f))

        d_t_b = (psi_b[:, k + 1] - psi_b[:, k]) / dt
        lap_b = mobius_laplacian(psi_b[:, k])
        kin_b = -np.sum(psi_b[:, k].conj() * (d_t_b + lap_b))

        coup = alpha * np.sum(np.abs(psi_f[:, k] - psi_b[:, k]) ** 2)

        wall_term = 0.5 * wall * (
            np.sum(np.abs(psi_f[:, k] - psi_target[:, k]) ** 2)
            + np.sum(np.abs(psi_b[:, k] - psi_target[:, k]) ** 2)
        )
        S += (kin_f + kin_b + coup + wall_term) * ds * dt
    return complex(S)


def squared_residual_loss(
    psi_f: np.ndarray,
    psi_b: np.ndarray,
    *,
    alpha: float,
    beta: float,
    gamma: float,
    T: float,
    psi_target: np.ndarray,
) -> float:
    """L = ⟨|R_f|²⟩ + ⟨|R_b|²⟩.  Zero iff (ψ_f, ψ_b) is a saddle of S."""
    R_f, R_b = keldysh_residuals(
        psi_f, psi_b, alpha=alpha, beta=beta, gamma=gamma,
        T=T, psi_target=psi_target,
    )
    return float(np.mean(np.abs(R_f) ** 2) + np.mean(np.abs(R_b) ** 2))


# -----------------------------------------------------------------------------
# Wirtinger gradient of L w.r.t. ψ̄_f, ψ̄_b
# -----------------------------------------------------------------------------

def keldysh_gradient(
    psi_f: np.ndarray,
    psi_b: np.ndarray,
    *,
    alpha: float,
    beta: float,
    gamma: float,
    T: float,
    psi_target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Wirtinger gradient (∂L/∂ψ̄_f, ∂L/∂ψ̄_b).

    Steepest descent of the real-valued L is along the direction of these
    gradients (with a sign flip).  The residual map R is linear in (ψ_f,
    ψ_b), so the gradient is just R applied through the adjoint — and
    because the Möbius Laplacian is real and self-adjoint, the adjoint is
    the same operator.
    """
    R_f, R_b = keldysh_residuals(
        psi_f, psi_b, alpha=alpha, beta=beta, gamma=gamma,
        T=T, psi_target=psi_target,
    )
    N, Kp1 = psi_f.shape
    K = Kp1 - 1
    dt = T / K
    wall = beta + _kappa(gamma, dt)
    inv_dt = 1.0 / dt
    diag_f = -inv_dt + alpha + wall   # ∂R_f[i,k]/∂ψ_f[i,k]
    diag_b = -inv_dt + alpha + wall   # ∂R_b[i,k]/∂ψ_b[i,k+1]

    grad_f = np.zeros_like(psi_f)
    grad_b = np.zeros_like(psi_b)
    for k in range(K):
        # Adjoint contributions from R_f[:, k]:
        grad_f[:, k + 1] += R_f[:, k] * inv_dt
        grad_f[:, k] += R_f[:, k] * diag_f - mobius_laplacian(R_f[:, k])
        grad_b[:, k] += R_f[:, k] * (-alpha)
        # Adjoint contributions from R_b[:, k]:
        grad_b[:, k + 1] += R_b[:, k] * diag_b - mobius_laplacian(R_b[:, k])
        grad_b[:, k] += R_b[:, k] * inv_dt
        grad_f[:, k + 1] += R_b[:, k] * (-alpha)

    norm = float(N * K)
    grad_f /= norm
    grad_b /= norm
    return grad_f, grad_b


# -----------------------------------------------------------------------------
# Saddle solver (Adam optimizer on L)
# -----------------------------------------------------------------------------

@dataclass
class SaddleResult:
    """Output of :func:`solve_saddle`."""
    psi_f: np.ndarray
    psi_b: np.ndarray
    final_loss: float
    iterations: int
    history: list[float]
    converged: bool


def solve_saddle(
    psi_target: np.ndarray,
    *,
    alpha: float,
    beta: float,
    gamma: float,
    T: float,
    anchor_t0: np.ndarray,
    init_psi_f: Optional[np.ndarray] = None,
    init_psi_b: Optional[np.ndarray] = None,
    lr: Optional[float] = None,
    momentum: float = 0.9,
    max_iter: int = 4000,
    tol: float = 1e-10,
    lambda_seam: float = 10.0,
    seed: int = 0,
) -> SaddleResult:
    """Find a saddle of S by heavy-ball gradient descent on L = ⟨|R|²⟩ + λ·seam.

    Hard anchor: ``ψ_f(:, 0) = ψ_b(:, 0) = anchor_t0`` (Higgs wall, in-state).
    Soft anchor: ``ψ_f(:, K) = ψ_b(:, K)`` enforced via ``λ_seam`` penalty
    (Möbius temporal seam, out-state).

    Loss is quadratic (residuals are linear in the fields), so plain
    momentum-GD is the right tool — Adam's adaptive normalization
    destabilizes the iteration when the gradient is small (i.e. near a
    saddle).  Step size defaults to a Hessian-based safe value
    ``lr = 0.5 · Δt²``: the Hessian's largest eigenvalue scales like
    ``1/Δt²`` from the time-derivative term, so this is comfortably below
    the divergence threshold ``2/L_max``.

    The Picard iteration in :class:`MobiusTemporalLoop` finds the same
    saddle by alternating sweeps + symmetrization; this routine finds it
    by gradient descent on the action's residual norm.  Agreement
    between the two procedures (modulo discretization) is the bridge
    claim of HYPOTHESIS.md §1.
    """
    psi_target = np.asarray(psi_target, dtype=complex)
    anchor_t0 = np.asarray(anchor_t0, dtype=complex)
    N, Kp1 = psi_target.shape
    K = Kp1 - 1
    dt = T / K
    if lr is None:
        lr = 0.5 * dt * dt
    rng = np.random.default_rng(seed)

    if init_psi_f is None:
        init_psi_f = psi_target.copy() + 0.05 * (
            rng.standard_normal(psi_target.shape)
            + 1j * rng.standard_normal(psi_target.shape)
        )
    if init_psi_b is None:
        init_psi_b = psi_target.copy() - 0.05 * (
            rng.standard_normal(psi_target.shape)
            + 1j * rng.standard_normal(psi_target.shape)
        )
    psi_f = np.asarray(init_psi_f, dtype=complex).copy()
    psi_b = np.asarray(init_psi_b, dtype=complex).copy()
    psi_f[:, 0] = anchor_t0
    psi_b[:, 0] = anchor_t0

    v_f = np.zeros_like(psi_f)   # heavy-ball velocity
    v_b = np.zeros_like(psi_b)

    history: list[float] = []
    converged = False
    final_it = 0
    for it in range(1, max_iter + 1):
        L_R = squared_residual_loss(
            psi_f, psi_b, alpha=alpha, beta=beta, gamma=gamma,
            T=T, psi_target=psi_target,
        )
        seam_diff = psi_f[:, K] - psi_b[:, K]
        L_seam = lambda_seam * float(np.mean(np.abs(seam_diff) ** 2))
        L = L_R + L_seam
        history.append(L)
        final_it = it
        if L < tol:
            converged = True
            break

        gf, gb = keldysh_gradient(
            psi_f, psi_b, alpha=alpha, beta=beta, gamma=gamma,
            T=T, psi_target=psi_target,
        )
        # Add seam-penalty gradient (∂/∂ψ̄_f[:, K] of λ·⟨|ψ_f[K]-ψ_b[K]|²⟩):
        gf[:, K] += lambda_seam * seam_diff / float(N)
        gb[:, K] += lambda_seam * (-seam_diff) / float(N)
        # Hard anchor at k=0 — zero its gradient.
        gf[:, 0] = 0.0
        gb[:, 0] = 0.0

        v_f = momentum * v_f - lr * gf
        v_b = momentum * v_b - lr * gb
        psi_f += v_f
        psi_b += v_b
        # Re-clamp the hard anchor.
        psi_f[:, 0] = anchor_t0
        psi_b[:, 0] = anchor_t0

    return SaddleResult(
        psi_f=psi_f, psi_b=psi_b,
        final_loss=history[-1] if history else float("nan"),
        iterations=final_it,
        history=history,
        converged=converged,
    )


__all__ = [
    "keldysh_residuals",
    "keldysh_action",
    "squared_residual_loss",
    "keldysh_gradient",
    "solve_saddle",
    "SaddleResult",
]
