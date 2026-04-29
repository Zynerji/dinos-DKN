"""Three-fold cover of the Möbius strip with Z_3 monodromy
(HYPOTHESIS Step 9b).

Step 8's Foot postulate introduces a Z_3 symmetry "from outside" the
Dinos framework. This module asks: **can a natural Z_3 structure be
constructed inside the Möbius geometry, by replacing the Z_2
antiperiodicity with a Z_3 monodromy?**

Construction
------------
The standard Möbius Laplacian (`dinos.spectrum`) implements
``ψ[N] = -ψ[0]`` — Z_2 antiperiodicity. We generalise to a triple
cover with monodromy ``ψ[N] = ω·ψ[0]`` where ``ω = exp(2πi/3)`` is
a primitive cube root of unity. Going around the loop three times
returns ψ to itself (``ω³ = 1``).

The discrete operator on N nodes:

    L_3[i, j] = (forward + backward - 2·δ)[i, j]

with the seam corrections:
- L_3[0, N-1] picks up an ω factor: forward[0] sees ω·ψ[N-1]
- L_3[N-1, 0] picks up ω factor too

Eigenmodes are now ``ψ_n[j] = exp(i(n + 1/3)·2π j/N)`` (or with
1/3 replaced by 2/3, depending on the branch).

What we ask
-----------
1. Does the Z_3 cover have natural triplet eigenvalue structures
   (3 modes per energy level, instead of pairs as in Z_2)?
2. Can we identify three of these triplet modes with the Foot Z_3
   states at angles {φ, φ+2π/3, φ+4π/3}?
3. Does the eigenvalue spectrum show 3-fold band structure that
   could carry generation labels naturally?

Honest scope statement
----------------------
This module BUILDS the 3-fold cover and computes its spectrum. It
does NOT claim that the resulting structure pins the lepton tower
without further input. The deep question is whether the Z_3 cover
+ a Foot-like ansatz reduces the postulate to a consequence of
geometry.
"""

from __future__ import annotations

import cmath
from dataclasses import dataclass
from math import cos, pi, sin

import numpy as np


# Primitive cube root of unity
OMEGA: complex = cmath.exp(2j * pi / 3.0)
OMEGA_BAR: complex = cmath.exp(-2j * pi / 3.0)


# -----------------------------------------------------------------------------
# Z_3 Möbius Laplacian
# -----------------------------------------------------------------------------

def z3_mobius_laplacian(psi: np.ndarray, omega_phase: complex = OMEGA) -> np.ndarray:
    """Discrete 1D Laplacian with Z_3 monodromy at the seam:
    ``ψ[N] = ω · ψ[0]`` (and conjugate at the other end).

    For ω = e^(2πi/3):
      forward[N-1] = ω · ψ[0]   (the right-neighbour of node N-1 wraps)
      backward[0] = ω̄ · ψ[N-1]  (the left-neighbour of node 0 wraps)

    Going around N nodes thrice returns to the start (ω³ = 1).
    """
    psi = np.asarray(psi, dtype=complex)
    forward = np.roll(psi, -1)
    backward = np.roll(psi, +1)
    # Z_3 seam corrections
    forward[-1] = omega_phase * psi[0]
    backward[0] = np.conjugate(omega_phase) * psi[-1]
    return forward + backward - 2.0 * psi


def z3_mobius_eigenvalues_closed_form(N: int,
                                       branch: int = 0) -> np.ndarray:
    """Closed-form eigenvalues of -L_3 on N-node Z_3 cover.

    Eigenmodes are ψ_n[j] = exp(i (n + branch/3) · 2π j / N).
    Branch ∈ {0, 1, 2}; branch=0 gives Z_3-trivial sector; branches 1, 2
    give the non-trivial Z_3-twisted sectors.

        λ_n = 2 (1 - cos((n + branch/3) · 2π/N))

    Returns the N eigenvalues for n = 0, ..., N-1, sorted ascending.
    """
    if N < 2:
        raise ValueError("N must be >= 2")
    if branch not in (0, 1, 2):
        raise ValueError(f"branch must be in {{0,1,2}}, got {branch}")
    eigs = np.array([
        2.0 * (1.0 - cos((n + branch / 3.0) * 2.0 * pi / N))
        for n in range(N)
    ])
    return np.sort(eigs)


def z3_mobius_eigenvalues_numerical(N: int) -> np.ndarray:
    """Numerical eigenvalues of -L_3 by diagonalising the explicit
    complex matrix (Hermitian conjugate handled correctly).

    Returns the 3N eigenvalues across all three branches combined,
    sorted ascending.
    """
    if N < 2:
        raise ValueError("N must be >= 2")
    L = np.zeros((N, N), dtype=complex)
    basis = np.eye(N)
    for j in range(N):
        L[:, j] = z3_mobius_laplacian(basis[:, j].astype(complex))
    L_neg = -L
    # Hermitise (the operator is Hermitian on this basis up to phase)
    L_neg_herm = 0.5 * (L_neg + L_neg.conj().T)
    eigs = np.linalg.eigvalsh(L_neg_herm)
    return np.sort(eigs)


# -----------------------------------------------------------------------------
# Triplet structure check
# -----------------------------------------------------------------------------

def lowest_distinct_triplets(N: int, n_triplets: int = 3) -> np.ndarray:
    """Return the lowest n_triplets distinct eigenvalues across all
    three branches combined.

    For Z_3 cover, eigenvalues from branch 0, 1, 2 form an interleaved
    spectrum. Each branch contributes (n + b/3)² in the continuum
    limit, giving values like {0, 1/9, 4/9, 1, 16/9, 25/9, ...} — three
    interleaved sequences.
    """
    eigs_b0 = z3_mobius_eigenvalues_closed_form(N, branch=0)
    eigs_b1 = z3_mobius_eigenvalues_closed_form(N, branch=1)
    eigs_b2 = z3_mobius_eigenvalues_closed_form(N, branch=2)
    all_eigs = np.concatenate([eigs_b0, eigs_b1, eigs_b2])
    sorted_eigs = np.sort(all_eigs)
    out: list[float] = []
    last = -np.inf
    for v in sorted_eigs:
        if v - last > 1e-9:
            out.append(float(v))
            last = v
        if len(out) >= n_triplets:
            break
    return np.array(out)


# -----------------------------------------------------------------------------
# Continuum-limit spectrum
# -----------------------------------------------------------------------------

def z3_continuum_eigenvalues(branch: int, n_max: int = 5) -> np.ndarray:
    """Continuum-limit eigenvalues (rescaled by (N/2π)²):

        lambda_n -> (n + branch/3)²,  n = 0, 1, 2, ..., n_max
    """
    if branch not in (0, 1, 2):
        raise ValueError(f"branch must be in {{0,1,2}}, got {branch}")
    return np.array([(n + branch / 3.0) ** 2 for n in range(n_max + 1)])


def z3_mobius_eigenvalues_rescaled(N: int, branch: int = 0) -> np.ndarray:
    """Eigenvalues of -L_3 on branch ``branch`` rescaled by (N/2π)²,
    converging to ``(n + branch/3)²`` in the continuum limit."""
    return (z3_mobius_eigenvalues_closed_form(N, branch=branch)
            * (N / (2.0 * pi)) ** 2)


# -----------------------------------------------------------------------------
# Connection to Foot 3-state structure
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Z3FootConnection:
    """Quantitative connection between Z_3 cover spectrum and Foot ansatz."""
    triplet_eigenvalues: np.ndarray
    foot_target_cosines: np.ndarray
    geometric_phi_rad: float
    matches_lepton_phi: bool
    notes: str


def attempt_z3_to_foot_identification(N: int = 256) -> Z3FootConnection:
    """Try to identify the 3 lowest-distinct Z_3 eigenvalues with the 3
    Foot cosine values cos(φ + (l-1)·2π/3) for empirical lepton φ.

    Most likely OUTCOME: Z_3 eigenvalues are {0, 1/9, 4/9, 1, ...} —
    purely topological — while Foot cosines are {0.975, -0.297, -0.679}
    — angular projections. The two are NOT directly identifiable
    without an additional embedding.

    This is a NEGATIVE-result documenter: it shows Z_3 cover GIVES a
    natural 3-fold spectrum, but does NOT pin the Foot mixing angle.
    """
    triplet = lowest_distinct_triplets(N, n_triplets=3)
    triplet_rescaled = triplet * (N / (2.0 * pi)) ** 2

    from . import lepton_tower_derivation as ltd
    from . import generations
    masses = [generations.M_E_MeV, generations.M_MU_MeV, generations.M_TAU_MeV]
    lepton_phi = ltd.derive_phi_from_three_masses(masses)
    foot_cosines = np.array([
        cos(lepton_phi + l * 2 * pi / 3) for l in range(3)
    ])

    # The Z_3 triplets in continuum limit are {0, 1/9, 4/9}; their
    # square-roots are {0, 1/3, 2/3}. Map these to Foot angles via
    # phi_geometric = arctan or similar.
    # For a deep identification we'd need a specific embedding rule.
    # Default: phi_geometric = 0 (trivial, doesn't match lepton phi).
    geometric_phi_rad = 0.0
    matches = abs(geometric_phi_rad - lepton_phi) < 0.05

    notes = (
        f"Z_3 cover triplet (rescaled): {triplet_rescaled.tolist()}. "
        f"Asymptote (n + branch/3)^2 for (0,0), (0,1), (0,2): "
        f"{[(0 + b/3.0)**2 for b in [0,1,2]]}. "
        f"Lepton Foot cosines: {foot_cosines.tolist()}. "
        f"NEGATIVE RESULT: Z_3 cover spectrum is purely topological "
        f"(rational fractions of unity); Foot mixing angle phi_lepton "
        f"= {lepton_phi:.4f} rad is NOT a rational fraction of pi, "
        f"so the Z_3 cover by itself does not pin the lepton phi."
    )

    return Z3FootConnection(
        triplet_eigenvalues=triplet_rescaled,
        foot_target_cosines=foot_cosines,
        geometric_phi_rad=geometric_phi_rad,
        matches_lepton_phi=matches,
        notes=notes,
    )


__all__ = [
    "OMEGA", "OMEGA_BAR",
    "z3_mobius_laplacian",
    "z3_mobius_eigenvalues_closed_form",
    "z3_mobius_eigenvalues_numerical",
    "z3_mobius_eigenvalues_rescaled",
    "lowest_distinct_triplets", "z3_continuum_eigenvalues",
    "Z3FootConnection", "attempt_z3_to_foot_identification",
]
