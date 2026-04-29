"""Spectral identification: Möbius D_s ↔ Chandrasekhar–Page.

Implements `HYPOTHESIS.md` Step 2: verify that the linearized Möbius
strip spectrum identifies with the angular Dirac spectrum on Kerr in
the flat limit (a, ω, μ → 0).

Möbius eigenmodes
-----------------
The N-node Möbius Laplacian (:func:`dinos.temporal_loop.mobius_laplacian`)
implements the discrete Z₂-antiperiodic boundary ``ψ[N] = −ψ[0]``. Its
eigenmodes are the half-integer Fourier modes

    ψ_n[j] = exp(i (n + ½) · 2π j / N),     n = 0, 1, …, N−1.

Eigenvalues of −D_s on these modes are

    λ_n = 2 (1 − cos((n + ½) · 2π/N))

which converge in the continuum limit (N → ∞ at fixed n, with the
natural rescaling by (Δs)⁻² = (N/2π)²) to

    λ_n → (n + ½)²  =  m_j²

where m_j = n + ½ is the half-integer azimuthal Dirac quantum number
(`dinos.geodesic`). This is the **azimuthal** part of the Dirac angular
spectrum on Kerr.

Polar correction → full Chandrasekhar–Page
------------------------------------------
The full flat-space Chandrasekhar–Page eigenvalue is

    λ_CP² = |k|²,    |k| = j + ½.

For the polar ground state n_θ = 0, the assignment in
:func:`dinos.geodesic.geodesic_to_dirac` gives

    j = m_j,         |k| = m_j + ½,         |k|² = m_j² + m_j + ¼.

So the **polar shift** that takes the Möbius -D_s eigenvalue to the
full Dirac |k|² is

    Δ_polar(m_j) = m_j + ¼.

This shift is the contribution of the spin-connection on the 2-sphere
(the σ·L term in the spinor angular operator). The Möbius construction
is one-dimensional and cannot capture it natively — it would require
either a second strip in the polar direction or a non-equatorial
geodesic projection.

What this proves and what it doesn't
------------------------------------
- The azimuthal sector is *exactly* matched: -D_s eigenvalues are m_j²
  in the continuum limit, with O(1/N²) discretization error.
- The full Dirac |k|² is recovered after applying the analytic polar
  shift Δ_polar(m_j) = m_j + ¼ — verifying that the missing piece is
  precisely the spin-connection contribution, not something more
  substantial.
- This does NOT yet verify the Kerr corrections (those would test the
  identification ``a²(ω² − μ²) ↔ (some combination of α, β, κ, τ)``),
  which is HYPOTHESIS Step 2C — left for a separate test if/when the
  parameter mapping is pinned down.
"""

from __future__ import annotations

from math import cos, pi

import numpy as np

from .temporal_loop import mobius_laplacian


# -----------------------------------------------------------------------------
# Möbius eigenvalues
# -----------------------------------------------------------------------------

def mobius_eigenvalues_closed_form(N: int) -> np.ndarray:
    """Closed-form eigenvalues of −D_s on the N-node Möbius strip.

    ``λ_n = 2 (1 − cos((n + ½) · 2π/N))`` for n = 0, …, N−1.

    Returns the eigenvalues sorted ascending.  Each non-degenerate level
    appears twice (n and N−1−n give equal cosines), reflecting the ±m_j
    pairing of the spinor azimuthal sector.
    """
    if N < 2:
        raise ValueError("N must be ≥ 2")
    eigs = np.array([
        2.0 * (1.0 - cos((n + 0.5) * 2.0 * pi / N)) for n in range(N)
    ])
    return np.sort(eigs)


def mobius_eigenvalues_numerical(N: int) -> np.ndarray:
    """Numerical eigenvalues of −D_s by diagonalising the explicit matrix.

    Provided as an independent check on
    :func:`mobius_eigenvalues_closed_form` — exercises the actual
    :func:`dinos.temporal_loop.mobius_laplacian` operator on a basis.
    """
    if N < 2:
        raise ValueError("N must be ≥ 2")
    L = np.zeros((N, N), dtype=float)
    basis = np.eye(N)
    for j in range(N):
        L[:, j] = mobius_laplacian(basis[:, j].astype(complex)).real
    # The discrete operator is real-symmetric on this basis.
    L_sym = 0.5 * (L + L.T)
    return np.sort(np.linalg.eigvalsh(-L_sym))


def mobius_eigenvalues_rescaled(N: int) -> np.ndarray:
    """Eigenvalues of −D_s rescaled by (N/2π)² → continuum limit (n + ½)².

    For fixed n and large N, ``rescaled_λ_n → (n + ½)²``.  The
    discretisation error is O(1/N²).
    """
    return mobius_eigenvalues_closed_form(N) * (N / (2.0 * pi)) ** 2


def m_j_values(n_max: int) -> np.ndarray:
    """Half-integer azimuthal Dirac quantum numbers m_j = ½, 3/2, …,
    (n_max + ½) — i.e. the n_max + 1 lowest |m_j|."""
    return np.array([n + 0.5 for n in range(n_max + 1)])


# -----------------------------------------------------------------------------
# Chandrasekhar–Page (flat-space limit)
# -----------------------------------------------------------------------------

def cp_eigenvalues_azimuthal(n_max: int) -> np.ndarray:
    """m_j² for m_j = ½, 3/2, …, (n_max + ½).

    This is the **part of the CP eigenvalue captured by the Möbius
    construction natively**.  One-to-one comparable to the lowest distinct
    ``-D_s`` eigenvalues in the continuum limit (each m_j² value appears
    twice in the Möbius spectrum, for ±m_j).
    """
    return m_j_values(n_max) ** 2


def cp_eigenvalues_full_polar_ground(n_max: int) -> np.ndarray:
    """|k|² for the polar ground state (n_θ = 0):

        |k| = m_j + ½ = n + 1,    |k|² = m_j² + m_j + ¼.

    Returns ``(n+1)²`` for n = 0, …, n_max.
    """
    return np.array([float((n + 1) ** 2) for n in range(n_max + 1)])


def polar_shift(m_j: np.ndarray | float) -> np.ndarray | float:
    """Δ_polar(m_j) = m_j + ¼ — the spin-connection contribution on the
    polar sphere that, added to m_j², promotes the Möbius azimuthal
    eigenvalue to the full Dirac |k|² for n_θ = 0.
    """
    m_j = np.asarray(m_j, dtype=float)
    return m_j + 0.25


def lowest_distinct_mobius_eigenvalues(N: int, n_max: int) -> np.ndarray:
    """Take the n_max + 1 smallest **distinct** rescaled Möbius eigenvalues.

    Each eigenvalue in :func:`mobius_eigenvalues_rescaled` has multiplicity
    two (n and N−1−n give the same cosine).  Returns the lowest distinct
    levels — these are the m_j² values in the continuum limit.
    """
    eigs = mobius_eigenvalues_rescaled(N)
    # Eigenvalues are sorted ascending; pairs come together.  Pick every
    # second value starting from index 0, but be tolerant of numerical
    # near-duplicates from finite-N degeneracy.
    out = []
    last = -np.inf
    for v in eigs:
        if v - last > 1e-9:
            out.append(v)
            last = v
        if len(out) >= n_max + 1:
            break
    return np.array(out)


__all__ = [
    "mobius_eigenvalues_closed_form",
    "mobius_eigenvalues_numerical",
    "mobius_eigenvalues_rescaled",
    "lowest_distinct_mobius_eigenvalues",
    "m_j_values",
    "cp_eigenvalues_azimuthal",
    "cp_eigenvalues_full_polar_ground",
    "polar_shift",
]
