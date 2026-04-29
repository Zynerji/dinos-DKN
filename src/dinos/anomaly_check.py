"""Real chiral anomaly check for the SM and proposed Möbius extensions
(HYPOTHESIS Step 41 — anomaly half).

Honest scope
------------
This module DOES:
  - Compute the U(1)_Y^3 anomaly coefficient sum_f chirality * Y_f^3
    over a user-specified fermion content. For the SM per-generation
    content, this sum is exactly zero (the famous SM anomaly cancellation).
  - Compute the [SU(2)]^2 U(1)_Y and [SU(3)]^2 U(1)_Y mixed anomalies
    by analogous trace formulas.
  - Verify that the SM cancels per-generation; verify that an arbitrary
    "Möbius-only" content (with Z2/Z3 quantum numbers but no SM-specific
    charges) does NOT automatically cancel.

This module DOES NOT:
  - Derive a specific fermion content from the Möbius framework. The
    Z2 seam pairs LH/RH modes, but the *charges* under SU(2)/SU(3)/U(1)
    must be specified externally. Until then, "topological anomaly
    cancellation" is a conjecture, not a theorem.
  - Verify the gravitational anomaly [grav]^2 U(1)_Y (sum_f Y_f); also
    cancels in the SM but is included here for completeness.

Verdict on Grok's "Z2xZ3 chiral index = 0 by topology" claim:
HARD-CODED. Grok's function literally returns 0 with no fermion
content specified. This module computes the actual anomaly given
explicit content.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FermionMultiplet:
    """A chiral fermion multiplet with hypercharge Y, isospin
    representation T2 (2T+1 = SU(2) dim), color rep T3 (1 or 3),
    and chirality (+1 = left, -1 = right)."""
    label: str
    Y: float        # hypercharge
    n_SU2: int      # SU(2) representation dim (1 = singlet, 2 = doublet)
    n_SU3: int      # SU(3) representation dim (1 = singlet, 3 = fundamental)
    chirality: int  # +1 = LH, -1 = RH


def standard_model_one_generation() -> list[FermionMultiplet]:
    """One generation of SM chiral fermions in the LH-only convention
    (RH fields treated as LH conjugates with flipped Y, hence -Y)."""
    return [
        FermionMultiplet("Q_L  (u,d)_L",  Y=+1/6,  n_SU2=2, n_SU3=3, chirality=+1),
        FermionMultiplet("u_R^c",         Y=-2/3,  n_SU2=1, n_SU3=3, chirality=+1),
        FermionMultiplet("d_R^c",         Y=+1/3,  n_SU2=1, n_SU3=3, chirality=+1),
        FermionMultiplet("L_L  (nu,e)_L", Y=-1/2,  n_SU2=2, n_SU3=1, chirality=+1),
        FermionMultiplet("e_R^c",         Y=+1,    n_SU2=1, n_SU3=1, chirality=+1),
    ]


@dataclass(frozen=True)
class AnomalyCoefficients:
    """All chiral anomaly coefficients for a given fermion content."""
    label: str
    U1Y_cubed: float           # [U(1)_Y]^3
    SU2_squared_U1Y: float     # [SU(2)]^2 U(1)_Y
    SU3_squared_U1Y: float     # [SU(3)]^2 U(1)_Y
    grav_squared_U1Y: float    # [gravity]^2 U(1)_Y
    cancels: bool


def compute_anomalies(content: list[FermionMultiplet],
                       label: str = "") -> AnomalyCoefficients:
    """Sum chirality * (multiplicity factors) * (Y power) over content."""
    A_Y3 = 0.0
    A_SU2_Y = 0.0
    A_SU3_Y = 0.0
    A_grav_Y = 0.0
    for f in content:
        n_total = f.n_SU2 * f.n_SU3
        A_Y3 += f.chirality * n_total * f.Y ** 3
        # [SU(2)]^2 only sees SU(2)-non-singlets; trace T(R)=1/2 for fundamental
        if f.n_SU2 > 1:
            A_SU2_Y += f.chirality * f.n_SU3 * 0.5 * f.Y * (f.n_SU2 - 0)
        # Actually correct convention: T(R) = 1/2 for fundamental of SU(N)
        # number of generators contributing = (n_SU2 - 1) for irreducible
        # Standard SM result: A_SU2_Y = Tr(Y) over LH SU(2) doublets
        # The formula above approximates this; rigorously:
        if f.n_SU3 > 1:
            A_SU3_Y += f.chirality * f.n_SU2 * 0.5 * f.Y
        A_grav_Y += f.chirality * n_total * f.Y

    # SM convention: A_SU2_Y = sum over LH SU(2) doublets of (n_color * Y)
    A_SU2_Y_clean = 0.0
    for f in content:
        if f.n_SU2 == 2:
            A_SU2_Y_clean += f.chirality * f.n_SU3 * f.Y

    # SM convention: A_SU3_Y = sum over color triplets of (n_SU2 * Y)
    A_SU3_Y_clean = 0.0
    for f in content:
        if f.n_SU3 == 3:
            A_SU3_Y_clean += f.chirality * f.n_SU2 * f.Y

    cancels = (
        abs(A_Y3) < 1e-12
        and abs(A_SU2_Y_clean) < 1e-12
        and abs(A_SU3_Y_clean) < 1e-12
        and abs(A_grav_Y) < 1e-12
    )
    return AnomalyCoefficients(
        label=label,
        U1Y_cubed=float(A_Y3),
        SU2_squared_U1Y=float(A_SU2_Y_clean),
        SU3_squared_U1Y=float(A_SU3_Y_clean),
        grav_squared_U1Y=float(A_grav_Y),
        cancels=cancels,
    )


def standard_model_anomalies() -> AnomalyCoefficients:
    """Verify that one SM generation cancels all chiral anomalies."""
    return compute_anomalies(standard_model_one_generation(),
                              label="SM one generation")


def mobius_only_content_test() -> AnomalyCoefficients:
    """Toy 'Möbius-only' content: just one LH and one RH chiral fermion
    with Y = +1 each. Demonstrates that without proper SM-style charges,
    anomaly cancellation is NOT automatic."""
    toy = [
        FermionMultiplet("Mobius_LH", Y=+1.0, n_SU2=1, n_SU3=1, chirality=+1),
        FermionMultiplet("Mobius_RH", Y=+1.0, n_SU2=1, n_SU3=1, chirality=-1),
    ]
    # Note: same Y, opposite chirality cancels A_Y3 trivially.
    return compute_anomalies(toy, label="Möbius-only toy (vector-like)")


def mobius_only_chiral_content_test() -> AnomalyCoefficients:
    """A genuinely chiral toy: only LH fermion with Y=+1. Anomalous."""
    toy = [
        FermionMultiplet("Mobius_chiral_LH", Y=+1.0, n_SU2=1, n_SU3=1, chirality=+1),
    ]
    return compute_anomalies(toy, label="Möbius-only chiral toy (anomalous)")


__all__ = [
    "FermionMultiplet", "standard_model_one_generation",
    "AnomalyCoefficients", "compute_anomalies",
    "standard_model_anomalies",
    "mobius_only_content_test", "mobius_only_chiral_content_test",
]
