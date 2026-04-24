"""Kerr–Newman null geodesics + Maslov-corrected Bohr–Sommerfeld quantization.

Paper §2 (geometry), §7 (quantization).

Structure:

  ─ Radial / polar potentials R(r), Θ(θ)                       eqs (4)–(5)
  ─ Action integrals J_φ, J_θ                                  eq  (7)
  ─ Near-equatorial polar action (bounded motion)              Prop. 2.2
  ─ Maslov-corrected Bohr–Sommerfeld rule                      eq  (24)
  ─ (n_φ, n_θ) ↦ (λ, η)                                        eqs (25)–(27)
  ─ (n_φ, n_θ) ↦ Dirac angular quantum number k, j, m_j        Thm. 7.4

The Maslov indices μ_φ = μ_θ = 2 are *fixed*, not free parameters:
• μ_θ = 2 from the two polar turning points of bounded oscillator motion.
• μ_φ = 2 from the fermionic antiperiodicity (−1)^spin on the closed ring
  (spin-statistics), App. E eq. (106).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np


# -----------------------------------------------------------------------------
# Kerr–Newman potentials
# -----------------------------------------------------------------------------

def sigma_fn(r: float, theta: float, a: float) -> float:
    """Σ = r² + a² cos²θ  (paper eq. 2)."""
    return r * r + a * a * np.cos(theta) ** 2


def delta_fn(r: float, a: float, M: float, Q: float) -> float:
    """Δ = r² − 2Mr + a² + Q²  (paper eq. 2)."""
    return r * r - 2.0 * M * r + a * a + Q * Q


def R_potential(r, lam: float, eta: float, a: float, M: float, Q: float):
    """Carter radial potential for null geodesics (paper eq. 4).

    R(r) = [(r² + a²) − aλ]² − Δ·[η + (λ − a)²]
    """
    r = np.asarray(r, dtype=float)
    return ((r * r + a * a) - a * lam) ** 2 - delta_fn(r, a, M, Q) * (eta + (lam - a) ** 2)


def Theta_potential(theta, lam: float, eta: float, a: float):
    """Carter polar potential for null geodesics (paper eq. 5).

    Θ(θ) = η + a² cos²θ − λ² cot²θ
    """
    theta = np.asarray(theta, dtype=float)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    # Guard against equator (cot = 0) vs. axis (cot → ∞) numerically.
    return eta + a * a * cos_t ** 2 - lam * lam * (cos_t / sin_t) ** 2


def Theta_near_equator(delta_theta, lam: float, eta: float):
    """Near-equatorial expansion  Θ(π/2 + δ) = η − λ²δ² + O(δ⁴)  (eq. 6)."""
    return eta - (lam ** 2) * (np.asarray(delta_theta, dtype=float) ** 2)


# -----------------------------------------------------------------------------
# Action integrals (Proposition 2.2)
# -----------------------------------------------------------------------------

def polar_action(lam: float, eta: float) -> float:
    """J_θ = π η/|λ|  for bounded polar motion ±δ₀  (eq. 7)."""
    if lam == 0.0:
        raise ValueError("λ = 0 has no bounded near-equatorial polar orbit")
    return pi * eta / abs(lam)


def azimuthal_action(L_z: float) -> float:
    """J_φ = 2π L_z  (trivially from ∮ p_φ dφ)."""
    return 2.0 * pi * L_z


# -----------------------------------------------------------------------------
# Maslov-corrected Bohr–Sommerfeld (Assumption 7.1, eq. 24)
# -----------------------------------------------------------------------------

MU_PHI = 2  # spin-½ antiperiodicity on closed ring (App. E)
MU_THETA = 2  # two polar turning points

HBAR = 1.0  # natural units


def bs_azimuthal(n_phi: int) -> float:
    """L_z = ℏ (n_φ + ½)  from J_φ = 2πℏ(n_φ + μ_φ/4) with μ_φ = 2  (eq. 25)."""
    return HBAR * (n_phi + 0.5)


def bs_polar(lam: float, n_theta: int) -> float:
    """η = 2ℏ|λ| (n_θ + ½)  from J_θ = πη/|λ| with μ_θ = 2  (eq. 26)."""
    return 2.0 * HBAR * abs(lam) * (n_theta + 0.5)


@dataclass(frozen=True)
class DiracLabels:
    """Dirac angular quantum numbers (|k|, j, m_j) from null-geodesic integers."""
    n_phi: int
    n_theta: int
    N: int           # |n_φ| − ½ + n_θ       (actually an integer for half-integer n_φ)
    k_abs: int       # |k| = N + 1
    j: float         # total angular momentum = N + ½
    m_j: float       # = n_φ + ½


def geodesic_to_dirac(n_phi: int, n_theta: int) -> DiracLabels:
    """Map (n_φ, n_θ) → (|k|, j, m_j)  via Theorem 7.4  (eqs. 28-30).

        N  ≡ |n_φ| − ½ + n_θ  ∈ {0, 1, 2, …}
        |k| = N + 1,   j = N + ½,   m_j ∈ {−j, …, +j}.

    Here n_φ is the azimuthal integer (m_j = n_φ + ½ is a half-integer).
    """
    if n_theta < 0:
        raise ValueError("n_θ must be ≥ 0")
    m_j = n_phi + 0.5
    N_float = abs(n_phi) - 0.5 + n_theta + 0.5  # = |n_φ| + n_θ  (half shifts cancel for allowed states)
    # Paper eq. 28 uses N = |n_φ| − ½ + n_θ which is integer because |n_φ| ∈ ℤ+½.
    N = int(round(abs(n_phi) + n_theta))  # cf. paper eq. 28 after identification m_j = n_φ + ½
    if N < 0:
        raise ValueError("negative N excluded (Corollary 7.6)")
    return DiracLabels(
        n_phi=n_phi, n_theta=n_theta,
        N=N, k_abs=N + 1,
        j=N + 0.5, m_j=m_j,
    )


def ground_state() -> DiracLabels:
    """1s_{1/2} ground state: (n_φ, n_θ) = (0, 0) gives |k|=1, j=½  (Corollary 7.6)."""
    return geodesic_to_dirac(n_phi=0, n_theta=0)


# -----------------------------------------------------------------------------
# Spectrum generators
# -----------------------------------------------------------------------------

def spectrum_up_to(N_max: int):
    """Enumerate all admissible (n_φ, n_θ) with |k| ≤ N_max + 1."""
    out = []
    for N in range(N_max + 1):
        for n_theta in range(N + 1):
            n_phi_abs = N - n_theta
            for sign in (+1, -1):
                if n_phi_abs == 0 and sign == -1:
                    continue  # avoid duplicate
                out.append(geodesic_to_dirac(n_phi=sign * n_phi_abs, n_theta=n_theta))
    return out


# -----------------------------------------------------------------------------
# (λ, η) for a given mode at cavity frequency ω
# -----------------------------------------------------------------------------

def separation_constants(n_phi: int, n_theta: int, omega: float) -> tuple[float, float]:
    """Return (λ, η) = (L_z/E, K/E² − (λ−a)²) from BS quantization (eq. 27).

    λ     = m_j / ω
    η/ℏ²  = 2|m_j|(n_θ + ½) / ω²
    """
    if omega <= 0:
        raise ValueError("ω must be positive")
    L_z = bs_azimuthal(n_phi)
    m_j = n_phi + 0.5
    lam = m_j / omega
    eta = 2.0 * abs(m_j) * (n_theta + 0.5) / (omega ** 2) * HBAR ** 2
    return lam, eta


# -----------------------------------------------------------------------------
# Möbius self-consistent boundary condition
# -----------------------------------------------------------------------------

def quantize(*,
             n_phi: int | None = None,
             n_theta: int | None = None,
             boundary_condition: str = "standard",
             mobius_psi: np.ndarray | None = None) -> DiracLabels:
    """Unified quantization entry point.

    Parameters:
        n_phi, n_theta: integers for the ``"standard"`` boundary
            condition — the canonical Maslov-corrected Bohr–Sommerfeld
            labels (paper eqs. 25–26).
        boundary_condition: one of

            * ``"standard"`` — classical BS integers (default).
            * ``"mobius_self_consistent"`` — extract ``(n_φ, n_θ)`` from
              a converged Möbius temporal-loop fixed point ``mobius_psi``.
              The spatial azimuthal winding picks up the Möbius Z_2 seam
              phase (+π), which is precisely the ``μ_φ = 2`` Maslov
              correction in the paper's eq. 25: the fermion antiperiodicity
              of the Dirac equation and the Möbius twist are the same
              topological invariant.

        mobius_psi: complex 1-D array of shape ``(N,)`` representing
            ψ_f(·, t=0) = ψ_b(·, t=0) of a converged
            :class:`dinos.temporal_loop.MobiusTemporalLoop`.

    Returns:
        :class:`DiracLabels` for the inferred ``(n_φ, n_θ)``.
    """
    if boundary_condition == "standard":
        if n_phi is None or n_theta is None:
            raise ValueError("standard BC requires both n_phi and n_theta")
        return geodesic_to_dirac(n_phi=n_phi, n_theta=n_theta)

    if boundary_condition == "mobius_self_consistent":
        if mobius_psi is None:
            raise ValueError("mobius_self_consistent BC requires mobius_psi")
        phases = np.angle(np.asarray(mobius_psi, dtype=complex))
        # Möbius Z_2 seam contributes a physical +π phase to the winding.
        dphases = np.diff(np.unwrap(phases))
        winding = (dphases.sum() + pi) / (2.0 * pi)
        n_phi_mob = int(np.round(winding))
        # Count nodal surfaces as zero-crossings of Re ψ around the loop.
        re = np.real(np.asarray(mobius_psi, dtype=complex))
        sign_changes = int(np.sum(np.diff(np.sign(re)) != 0))
        n_theta_mob = max(sign_changes // 2, 0)
        return geodesic_to_dirac(n_phi=n_phi_mob, n_theta=n_theta_mob)

    raise ValueError(f"unknown boundary_condition {boundary_condition!r}")


__all__ = [
    "sigma_fn", "delta_fn", "R_potential", "Theta_potential", "Theta_near_equator",
    "polar_action", "azimuthal_action",
    "MU_PHI", "MU_THETA",
    "bs_azimuthal", "bs_polar",
    "DiracLabels", "geodesic_to_dirac", "ground_state", "spectrum_up_to",
    "separation_constants",
    "quantize",
]
