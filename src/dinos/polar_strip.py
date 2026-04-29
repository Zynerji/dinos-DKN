"""Polar excitations of the Möbius construction (HYPOTHESIS.md Step 4).

Step 2 (`dinos.spectrum`) showed:
- Möbius `-D_s` eigenvalue = m_j² (azimuthal, exact).
- Adding `Δ_polar(m_j) = m_j + ¼` recovers Dirac `|k|²` for the **n_θ = 0
  ground state**.

This module generalises the polar shift to **arbitrary n_θ**, deriving the
exact closed form and verifying it reproduces the full ladder
``|k|² = (|m_j| + n_θ + ½)²`` for every (m_j, n_θ).

Generalised polar shift
-----------------------

For n_θ ≥ 0 polar excitations on the spinor 2-sphere:

    Δ_polar(n_θ, m_j) = (n_θ + ½)(2|m_j| + n_θ + ½).

Identity (algebraic, exact for all half-integer m_j and integer n_θ ≥ 0):

    m_j² + Δ_polar(n_θ, m_j)  =  (|m_j| + n_θ + ½)²  =  |k|².

Verification:

    m_j² + (n_θ + ½)(2|m_j| + n_θ + ½)
        = m_j² + 2|m_j|(n_θ + ½) + (n_θ + ½)²
        = (|m_j| + n_θ + ½)²
        = |k|²       (since |k| = j + ½ = |m_j| + n_θ + ½ for the
                      n_θ-th polar excitation in the m_j azimuthal sector).

Reduction to Step 2: at n_θ = 0,

    Δ_polar(0, m_j) = ½ · (2|m_j| + ½) = |m_j| + ¼,

recovering :func:`dinos.spectrum.polar_shift` exactly.

What this is and isn't
----------------------
- This is the **analytic** spin-orbit + polar-mode contribution from the
  spinor angular operator on S² — the missing piece between Möbius
  (1D, azimuthal-only) and the full Dirac angular spectrum.
- It is **not** a discrete 2D operator. A true 2D spinor Laplacian would
  need a non-trivial spin connection on the sphere — structurally
  outside what a Möbius strip naturally carries. We surface this
  structural gap honestly rather than papering over it.

Cross-check on `dinos.cp`
-------------------------
:func:`dinos.cp.solve_cp_exact` is a shooter for a *related* angular ODE
(paper eq. 87) but its eigenvalue convention does **not** match Dirac
``|k|²``: in flat limit it returns ``λ² ≈ l(l+1)``, where ``l`` is the
*orbital* angular momentum of the upper spinor component (l = j ± ½ for
j the Dirac total angular momentum). The closed-form claim
``λ_CP² = k²`` in `cp.py`'s docstring describes the **leading expansion
constant**, not the operator's discrete spectrum. This is documented in
the test file but not fixed here (out of scope; the rest of the
framework uses :func:`dinos.cp.lambda_CP_leading` which is correct).
"""

from __future__ import annotations

import numpy as np


# -----------------------------------------------------------------------------
# Generalised polar shift
# -----------------------------------------------------------------------------

def polar_shift_generalised(n_theta: int, m_j: float) -> float:
    """Δ_polar(n_θ, m_j) = (n_θ + ½)(2|m_j| + n_θ + ½).

    Adding this to ``m_j²`` (the Möbius azimuthal eigenvalue) yields
    Dirac ``|k|²`` for the (n_θ, m_j) angular state.
    """
    if n_theta < 0:
        raise ValueError("n_theta must be a non-negative integer")
    return (n_theta + 0.5) * (2.0 * abs(m_j) + n_theta + 0.5)


def dirac_k_squared(n_theta: int, m_j: float) -> float:
    """``|k|² = (|m_j| + n_θ + ½)²``."""
    return (abs(m_j) + n_theta + 0.5) ** 2


def total_eigenvalue_from_mobius(mobius_azimuthal: float, n_theta: int,
                                  m_j: float) -> float:
    """Combine an azimuthal Möbius eigenvalue with the polar shift.

    ``λ_total = mobius_azimuthal + Δ_polar(n_θ, m_j)``.

    For the canonical Möbius construction at the m_j mode,
    ``mobius_azimuthal = m_j²`` (continuum limit), in which case this
    function returns ``|k|²`` exactly.
    """
    return mobius_azimuthal + polar_shift_generalised(n_theta, m_j)


# -----------------------------------------------------------------------------
# Convenience: 2D ladder for plotting / inspection
# -----------------------------------------------------------------------------

def k_squared_ladder(n_theta_max: int, n_phi_max: int) -> np.ndarray:
    """``|k|²`` table indexed by (n_θ, n_φ) where ``m_j = n_φ + ½``.

    Returns an array of shape ``(n_theta_max + 1, n_phi_max + 1)``
    suitable for a heatmap.  Entries equal ``(n_φ + n_θ + 1)²``.
    """
    out = np.empty((n_theta_max + 1, n_phi_max + 1), dtype=float)
    for nt in range(n_theta_max + 1):
        for nphi in range(n_phi_max + 1):
            out[nt, nphi] = dirac_k_squared(nt, nphi + 0.5)
    return out


def polar_shift_ladder(n_theta_max: int, n_phi_max: int) -> np.ndarray:
    """``Δ_polar`` table indexed by (n_θ, n_φ).  Same shape as
    :func:`k_squared_ladder`."""
    out = np.empty((n_theta_max + 1, n_phi_max + 1), dtype=float)
    for nt in range(n_theta_max + 1):
        for nphi in range(n_phi_max + 1):
            out[nt, nphi] = polar_shift_generalised(nt, nphi + 0.5)
    return out


__all__ = [
    "polar_shift_generalised",
    "dirac_k_squared",
    "total_eigenvalue_from_mobius",
    "k_squared_ladder",
    "polar_shift_ladder",
]
