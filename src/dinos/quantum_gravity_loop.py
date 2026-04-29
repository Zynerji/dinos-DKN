"""Quantum gravity perturbative estimate (HYPOTHESIS Step 12e).

Step 6c showed the leading classical metric backreaction from the
Higgs source is delta g/g ~ 10^-47 at electron Compton scale --
fantastically negligible.

This module estimates the next-order quantum-gravity correction:
the one-loop graviton contribution to the electron self-energy. The
result is also negligible (suppressed by m_e^2 / M_Pl^2 ~ 10^-44),
confirming that the framework's neglect of quantum gravity is
quantitatively justified at electron scale.

Honest scope statement
----------------------
- This module CAN: estimate the order-of-magnitude graviton-loop
  correction to m_e.
- This module CANNOT: solve quantum gravity. The graviton-loop estimate
  uses an effective field theory cutoff at M_Pl; renormalisability
  is unresolved.
- VERDICT: at electron scale, all quantum-gravity corrections are
  ~ 10^-44 of m_e. The framework's classical Kerr-Newman background
  is an excellent approximation. Full quantum gravity remains unsolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import constants as C
from . import gravity_backreaction as gb


# Newton's constant in natural units (1/M_Pl^2 in GeV)
G_NEWTON_GeV_INV2: float = 1.0 / (gb.M_PL_GeV ** 2)


@dataclass(frozen=True)
class QGLoopReport:
    classical_delta_g_over_g: float       # Step 6c
    one_loop_correction_order: float       # m_e^2 / M_Pl^2
    is_safely_neglected: bool
    notes: str


def estimate_one_loop_correction() -> QGLoopReport:
    """Order-of-magnitude estimate of the leading quantum-gravity
    correction to the electron mass.

    Standard EFT result: a graviton loop contributes a self-energy
    correction of order m_e^3 / M_Pl^2 (i.e., m_e * (m_e/M_Pl)^2).
    The relative correction to m_e is therefore (m_e/M_Pl)^2.
    """
    classical_report = gb.dkn_backreaction_at_electron()
    one_loop_relative = (C.m_e_MeV / gb.M_PL_MeV) ** 2
    is_negligible = one_loop_relative < 1e-30
    notes = (
        f"Classical metric backreaction (Step 6c): "
        f"delta g/g = {classical_report.delta_g_over_g:.3e}. "
        f"One-loop graviton correction to m_e: of order "
        f"(m_e/M_Pl)^2 = {one_loop_relative:.3e} (relative). "
        f"Both are deeply below the mass-closure precision of 10^-4. "
        f"VERDICT: quantum-gravity effects are quantitatively "
        f"negligible at electron scale. Framework's classical "
        f"Kerr-Newman background is justified. Full quantum-gravity "
        f"renormalisability is NOT addressed by this module --- the "
        f"effective-field-theory estimate uses M_Pl as a cutoff."
    )
    return QGLoopReport(
        classical_delta_g_over_g=classical_report.delta_g_over_g,
        one_loop_correction_order=one_loop_relative,
        is_safely_neglected=is_negligible,
        notes=notes,
    )


__all__ = [
    "G_NEWTON_GeV_INV2",
    "QGLoopReport", "estimate_one_loop_correction",
]
