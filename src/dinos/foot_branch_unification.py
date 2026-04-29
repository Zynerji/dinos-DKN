"""Foot branch unification: leptons and neutrinos as resonances at b = sqrt(2)
(HYPOTHESIS Step 13).

Synthesises Steps 8 (charged leptons) and 12a (neutrinos) into a single
unified picture: the Foot+Koide ansatz with universal coupling
b = sqrt(2) admits two distinct physical resonance branches, each
characterised by:
  (i)  a sign pattern of (1 + b cos(phi + (l-1)*2*pi/3));
  (ii) a mixing angle phi;
  (iii) an overall scale a.

The two observed fermion families (charged leptons and neutrinos) sit
in the two distinct branches.

Branch table
------------

| Branch       | Sign pattern   | Q       | phi (rad) | a            | Family            |
|--------------|----------------|---------|-----------|--------------|-------------------|
| All-positive | (+, +, +)      | 3/2     | 2/9       | 313.84 MeV   | Charged leptons   |
| One-flip     | (+, -, +)      | 1.9048  | 0.4768    | 9.87e-3 eV   | Neutrinos (NO)    |

Both share **b = sqrt(2) universal**. The Foot ansatz is the same in
both branches; only the sign sector and the (a, phi) parameters
differ.

Resonance interpretation
------------------------
At b = sqrt(2), the Foot construction has a discrete set of physical
branches (sign sectors of the (1 + b cos) factors). Each branch is a
"resonance" of the underlying Z_3-symmetric structure, with its own
characteristic phi and scale a. The two observed fermion families
populate two of these resonances:

- **Lepton resonance**: Q = 3/2, all-positive, phi = 2/9, MeV scale.
- **Neutrino resonance**: Q ~ 1.90, one-sign-flip, phi ~ 0.48, meV scale.

This is a structural unification: one Foot ansatz with one universal
coupling gives both fermion mass towers, simply by selecting different
branches.

Honest scope statement
----------------------
- This module FORMALISES the relationship between Steps 8 and 12a.
- It does NOT introduce new derivations beyond what Steps 8 and 12a
  already provide.
- The "two resonances" interpretation is a structural framing, not a
  new physical claim. The numerical predictions are inherited from
  the prior steps.
- The mass-scale ratio a_L / a_nu ~ 3e10 (MeV vs meV) is NOT derived;
  each scale is set independently by its respective family's masses.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sqrt

import numpy as np


B_UNIVERSAL: float = sqrt(2.0)


@dataclass(frozen=True)
class FootResonance:
    """One Foot resonance: family, sign pattern, phi, a, Koide Q."""
    family: str
    sign_pattern: tuple[int, int, int]   # signs of (1 + b cos) for l=0,1,2
    phi_rad: float
    a_MeV_or_eV: float           # scale (MeV for leptons, eV for neutrinos)
    a_unit: str
    koide_q: float
    masses_in_unit: tuple[float, float, float]


def lepton_resonance() -> FootResonance:
    """Charged-lepton resonance at b = sqrt(2): all-positive branch,
    Q = 3/2, phi = 2/9, a = 313.84 MeV."""
    from . import generations
    from . import lepton_tower_derivation as ltd
    masses = sorted([generations.M_E_MeV,
                     generations.M_MU_MeV,
                     generations.M_TAU_MeV])
    a = ltd.derive_a_from_three_masses(masses)
    phi = 2.0 / 9.0
    facts = [1 + B_UNIVERSAL * cos(l * 2 * pi / 3 + phi) for l in range(3)]
    signs = tuple(1 if f >= 0 else -1 for f in facts)
    sum_sqrt = sum(np.sqrt(m) for m in masses)
    Q = (sum_sqrt ** 2) / sum(masses)
    return FootResonance(
        family="charged_leptons",
        sign_pattern=signs,
        phi_rad=phi,
        a_MeV_or_eV=a,
        a_unit="MeV",
        koide_q=Q,
        masses_in_unit=tuple(masses),
    )


def neutrino_resonance() -> FootResonance:
    """Neutrino resonance at b = sqrt(2): one-sign-flip branch,
    Q ~ 1.90, phi ~ 0.477, a ~ 9.87e-3 eV."""
    from . import neutrinos_brannen
    a, phi, masses = neutrinos_brannen.solve_foot_for_neutrinos()
    facts = [1 + B_UNIVERSAL * cos(l * 2 * pi / 3 + phi) for l in range(3)]
    signs = tuple(1 if f >= 0 else -1 for f in facts)
    sum_sqrt = sum(np.sqrt(m) for m in masses)
    Q = (sum_sqrt ** 2) / sum(masses)
    return FootResonance(
        family="neutrinos",
        sign_pattern=signs,
        phi_rad=phi,
        a_MeV_or_eV=a,
        a_unit="eV",
        koide_q=Q,
        masses_in_unit=tuple(sorted(masses)),
    )


@dataclass(frozen=True)
class UnificationReport:
    """Side-by-side report of the two resonances."""
    leptons: FootResonance
    neutrinos: FootResonance
    b_universal: float
    scale_ratio_L_over_nu: float       # a_L / a_nu (in same units)
    notes: str


def generate_unification_report() -> UnificationReport:
    """Compile the full unification report."""
    L = lepton_resonance()
    nu = neutrino_resonance()
    # Convert lepton a to eV for ratio
    a_L_eV = L.a_MeV_or_eV * 1e6
    a_nu_eV = nu.a_MeV_or_eV
    ratio = a_L_eV / a_nu_eV
    notes = (
        f"Two Foot resonances at b = sqrt(2) = {B_UNIVERSAL:.4f}: "
        f"(charged leptons) all-positive branch, phi = 2/9, a = "
        f"{L.a_MeV_or_eV:.2f} MeV, Q = {L.koide_q:.4f}; "
        f"(neutrinos) one-sign-flip branch, phi = {nu.phi_rad:.4f}, "
        f"a = {nu.a_MeV_or_eV:.4e} eV, Q = {nu.koide_q:.4f}. "
        f"Mass-scale ratio a_L / a_nu = {ratio:.3e} "
        f"(NOT derived; each scale set by its family's masses). "
        f"Both resonances share the same Foot ansatz and universal b. "
        f"This is a structural unification of Steps 8 and 12a."
    )
    return UnificationReport(
        leptons=L,
        neutrinos=nu,
        b_universal=B_UNIVERSAL,
        scale_ratio_L_over_nu=ratio,
        notes=notes,
    )


__all__ = [
    "B_UNIVERSAL",
    "FootResonance", "lepton_resonance", "neutrino_resonance",
    "UnificationReport", "generate_unification_report",
]
