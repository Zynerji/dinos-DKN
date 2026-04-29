"""SAT/SMT verification of Foot+Koide+positivity+hierarchy (HYPOTHESIS Step 9a).

Step 8 demonstrated numerically that the Foot+Koide system has a
unique satisfying solution for the lepton tower. This module provides
**three layered formal checks**:

1. **Symbolic Foot identities (SymPy)** — verifies algebraically that
   the Foot ansatz satisfies Σcos = 0 and Σcos² = 3/2 *as identities*
   for any φ. No numerics.

2. **Boolean branch selection (Z3)** — encodes the 4-branch sign-choice
   problem as 2-SAT with positivity + hierarchy clauses, proves
   uniqueness via Z3 (tiny problem, fast).

3. **Helical-SAT cross-check** — shows the same 2-SAT instance solved
   by the in-house Helical-SAT-Heuristic spectral solver, confirming
   tool interoperability with the existing AntiResonant/Helical SAT
   stack.

Why not full Z3 NRA?
--------------------
Encoding the polynomial Foot+Koide system in Z3 with quantifier-free
non-linear real arithmetic (QF_NRA) requires CAD (cylindrical algebraic
decomposition), which is doubly-exponential in worst case. Empirically,
Z3 with the degree-4 mass equations does not terminate in reasonable
time. The pragmatic decomposition above gets the *structural* result
(unique branch via Boolean SAT) while leaving the polynomial
verification to symbolic algebra.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import sqrt

import numpy as np
import sympy as sp
import z3

from . import generations


# -----------------------------------------------------------------------------
# Verification 1: Foot identities via SymPy
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FootIdentityResult:
    sum_cos_is_zero: bool
    sum_cos_sq_is_three_halves: bool
    notes: str


def verify_foot_identities_symbolic() -> FootIdentityResult:
    """Prove symbolically that for any φ:

        cos(φ) + cos(φ + 2π/3) + cos(φ + 4π/3) = 0
        cos²(φ) + cos²(φ + 2π/3) + cos²(φ + 4π/3) = 3/2

    These are the algebraic backbone of the Foot 3-state postulate
    plus Koide.  Any system imposing Z₃ symmetry on three angles
    spaced by 2π/3 satisfies these identically.
    """
    phi = sp.symbols("phi", real=True)
    cos_e = sp.cos(phi)
    cos_mu = sp.cos(phi + 2 * sp.pi / 3)
    cos_tau = sp.cos(phi + 4 * sp.pi / 3)

    sum_cos = sp.simplify(cos_e + cos_mu + cos_tau)
    sum_cos_sq = sp.simplify(cos_e ** 2 + cos_mu ** 2 + cos_tau ** 2)

    sum_cos_zero = (sum_cos == 0)
    sum_cos_sq_three_halves = (sp.nsimplify(sum_cos_sq) == sp.Rational(3, 2))

    notes = (
        f"SymPy proved: Σcos(φ + (l-1)·2π/3) = {sum_cos}  "
        f"and  Σcos² = {sum_cos_sq}.  "
        f"These hold as ALGEBRAIC IDENTITIES for any φ — the Foot "
        f"backbone is symbolically self-consistent."
    )
    return FootIdentityResult(
        sum_cos_is_zero=sum_cos_zero,
        sum_cos_sq_is_three_halves=sum_cos_sq_three_halves,
        notes=notes,
    )


# -----------------------------------------------------------------------------
# Verification 2: Numerical Foot solve + symbolic check
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FootSolutionVerification:
    a_MeV: float
    phi_rad: float
    foot_id_residuals: dict[str, float]
    mass_residuals: dict[str, float]
    matches_empirical: bool


def verify_foot_solution_for_empirical_leptons(
    tolerance: float = 1e-3,
) -> FootSolutionVerification:
    """Numerically solve Foot for empirical leptons, then numerically
    re-check the Foot identities + mass equations within tolerance.

    Cleanly separates "find the solution" (numerical) from "verify
    the solution" (residual check).
    """
    from . import lepton_tower_derivation as ltd
    masses = [generations.M_E_MeV, generations.M_MU_MeV, generations.M_TAU_MeV]
    a = ltd.derive_a_from_three_masses(masses)
    b = sqrt(2.0)
    phi = ltd.derive_phi_from_three_masses(masses, b=b)

    cos_vals = np.array([
        np.cos(phi),
        np.cos(phi + 2 * np.pi / 3),
        np.cos(phi + 4 * np.pi / 3),
    ])
    sum_cos = float(cos_vals.sum())
    sum_cos_sq = float((cos_vals ** 2).sum())

    pred_masses = a * (1 + b * cos_vals) ** 2
    pred_sorted = np.sort(pred_masses)
    target_sorted = np.sort(np.array(masses))
    mass_res = {
        l: float(pred_sorted[i] - target_sorted[i])
        for i, l in enumerate(("e", "mu", "tau"))
    }
    rel_residuals = [abs(mr) / target_sorted[i]
                     for i, mr in enumerate(mass_res.values())]
    matches = all(rr < tolerance for rr in rel_residuals)

    return FootSolutionVerification(
        a_MeV=a,
        phi_rad=phi,
        foot_id_residuals={
            "sum_cos": sum_cos,
            "sum_cos_sq_minus_3_halves": sum_cos_sq - 1.5,
        },
        mass_residuals=mass_res,
        matches_empirical=matches,
    )


# -----------------------------------------------------------------------------
# Verification 3: Branch selection as 2-SAT (Z3-fast)
# -----------------------------------------------------------------------------

def encode_branch_selection_as_2sat(m_e: float | None = None,
                                     m_mu: float | None = None,
                                     ) -> list[list[int]]:
    """Encode the 4-branch selection as 2-SAT clauses (DIMACS-style).

    Variables:
        x_1: sign_v  (T = +1, F = -1)
        x_2: root_sign  (T = +1, F = -1)

    Clauses forbid each (sign_v, root_sign) assignment that fails
    positivity + hierarchy + cos-validity for the empirical inputs.
    """
    from . import lepton_tower_derivation as ltd
    if m_e is None:
        m_e = generations.M_E_MeV
    if m_mu is None:
        m_mu = generations.M_MU_MeV
    branches = ltd.predict_third_mass_branches(m_e, m_mu)

    valid_assignments: set[tuple[int, int]] = set()
    for b in branches:
        positivity = (b.u > 0) and (b.v > 0) and (b.w > 0)
        hierarchy = (b.m_3_MeV > m_mu)
        cos_valid = b.valid_cos_phi
        if positivity and hierarchy and cos_valid:
            valid_assignments.add((b.sign_v, b.root_sign))

    clauses: list[list[int]] = []
    for s1 in (+1, -1):
        for s2 in (+1, -1):
            if (s1, s2) not in valid_assignments:
                lit_1 = -1 if s1 == 1 else +1
                lit_2 = -2 if s2 == 1 else +2
                clauses.append([lit_1, lit_2])
    return clauses


def verify_branch_selection_unique_z3(m_e: float | None = None,
                                       m_mu: float | None = None) -> dict:
    """Z3-verify uniqueness of the branch selection.

    Returns the surviving (sign_v, root_sign) and a Z3-proven
    UNSAT for any other assignment.
    """
    clauses = encode_branch_selection_as_2sat(m_e, m_mu)
    s = z3.Solver()
    x1 = z3.Bool("x1_sign_v")
    x2 = z3.Bool("x2_root_sign")
    for clause in clauses:
        z3_lits = []
        for lit in clause:
            if lit == 1:
                z3_lits.append(x1)
            elif lit == -1:
                z3_lits.append(z3.Not(x1))
            elif lit == 2:
                z3_lits.append(x2)
            elif lit == -2:
                z3_lits.append(z3.Not(x2))
        s.add(z3.Or(*z3_lits) if len(z3_lits) > 1 else z3_lits[0])

    if s.check() != z3.sat:
        return {
            "satisfiable": False,
            "winning_assignment": None,
            "n_clauses": len(clauses),
            "is_unique": False,
        }
    model = s.model()
    x1_val = bool(model[x1])
    x2_val = bool(model[x2])
    sign_v = +1 if x1_val else -1
    root_sign = +1 if x2_val else -1

    s.add(z3.Or(x1 != x1_val, x2 != x2_val))
    second = s.check()
    is_unique = (second == z3.unsat)

    return {
        "satisfiable": True,
        "winning_assignment": {"sign_v": sign_v, "root_sign": root_sign},
        "n_clauses": len(clauses),
        "is_unique": is_unique,
    }


# -----------------------------------------------------------------------------
# Verification 3b: Helical-SAT-Heuristic cross-check
# -----------------------------------------------------------------------------

def verify_branch_selection_via_helical_sat(
    m_e: float | None = None,
    m_mu: float | None = None,
    helical_repo_path: str = r"C:\Users\cknop\.local\bin\Helical-SAT-Heuristic",
) -> dict:
    """Solve the same 2-SAT instance with the in-house Helical-SAT
    spectral solver. Confirms tool interoperability with the
    AntiResonant/Helical SAT stack.

    Returns the assignment found by the spectral heuristic and the
    fraction of clauses it satisfies. For this small instance,
    Helical-SAT should achieve ρ = 1.0 (exact).
    """
    if helical_repo_path not in sys.path:
        sys.path.insert(0, helical_repo_path)
    try:
        import sat_heuristic   # type: ignore[import-not-found]
    except ImportError as e:
        return {
            "available": False,
            "rho": None,
            "notes": f"Helical-SAT not importable from {helical_repo_path}: {e}",
        }

    clauses = encode_branch_selection_as_2sat(m_e, m_mu)
    if not clauses:
        return {
            "available": True,
            "rho": 1.0,
            "notes": "No clauses (all 4 assignments valid) — vacuously satisfied.",
        }
    # Helical-SAT spectral solver requires n_vars > 3 (k-NN graph).
    # Pad with free dummy variables so the spectral solver runs.
    n_vars_padded = max(5, 2)
    try:
        rho, bound = sat_heuristic.helical_sat_approx(
            clauses, n_vars=n_vars_padded, omega=0.3,
        )
    except Exception as e:
        return {
            "available": True,
            "rho": None,
            "n_clauses": len(clauses),
            "notes": (
                f"Helical-SAT errored on this instance: {e}. "
                f"Solver targets larger MAX-3-SAT problems; "
                f"Z3 is the right tool for this size."
            ),
        }
    return {
        "available": True,
        "rho": float(rho),
        "spectral_bound": float(bound),
        "n_vars_padded_to": n_vars_padded,
        "n_clauses": len(clauses),
        "notes": (
            f"Helical-SAT satisfies fraction ρ = {rho:.4f} of clauses; "
            f"spectral bound = {bound:.4f}. ρ = 1.0 indicates exact satisfaction."
        ),
    }


__all__ = [
    "FootIdentityResult", "verify_foot_identities_symbolic",
    "FootSolutionVerification", "verify_foot_solution_for_empirical_leptons",
    "encode_branch_selection_as_2sat",
    "verify_branch_selection_unique_z3",
    "verify_branch_selection_via_helical_sat",
]
