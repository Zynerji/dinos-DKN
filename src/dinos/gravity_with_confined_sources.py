"""Self-consistent metric backreaction with confined sources scaffold
(HYPOTHESIS Step 47c).

Honest scope
------------
This module DOES:
  - Wrap the existing `dinos.gravity_backreaction` perturbative result.
  - Add an additional "confined source" term parameterised by a
    string-tension proxy sigma (input).
  - Report the combined δg/g estimate.

This module DOES NOT:
  - Solve the full Einstein equations with confined sources. The
    existing perturbative result for the electron gives δg/g ~ 10^-42
    (negligible at the electron Compton scale); adding a string-tension
    contribution does not change this orders of magnitude unless sigma
    is set to a wildly unphysical value.
  - Iterate the Kerr parameters self-consistently — that requires
    solving a coupled nonlinear system not implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import gravity_backreaction as gb


@dataclass(frozen=True)
class ConfinedBackreactionReport:
    sigma_QCD_GeV2: float
    delta_g_over_g_higgs_only: float
    delta_g_over_g_with_confinement: float
    notes: str


def confined_metric_backreaction(sigma_QCD_GeV2: float = 0.18,
                                   electron_compton_GeV_inv: float = 1.967e-3
                                   ) -> ConfinedBackreactionReport:
    """Estimate dg/g from Higgs wall + a string-tension proxy.

    The string-tension contribution is sigma * compton_radius — both in
    natural units. At the electron scale this is dwarfed by m_e itself.
    """
    # Higgs-only result from existing module
    base = gb.dkn_backreaction_at_electron()
    delta_g_higgs = float(base.delta_g_over_g)

    # String tension contribution: sigma * Compton wavelength (rough estimate)
    flux_energy_GeV = sigma_QCD_GeV2 * electron_compton_GeV_inv
    M_Planck_GeV = 1.22e19
    delta_flux = float((flux_energy_GeV / M_Planck_GeV) ** 2)

    delta_total = delta_g_higgs + delta_flux

    return ConfinedBackreactionReport(
        sigma_QCD_GeV2=float(sigma_QCD_GeV2),
        delta_g_over_g_higgs_only=delta_g_higgs,
        delta_g_over_g_with_confinement=delta_total,
        notes=("δg/g remains negligible at the electron scale even with "
               "QCD-strength confinement contribution — the Compton scale "
               "is many orders of magnitude below the gravity-relevant scale. "
               "Self-consistent iteration of the Kerr parameters (Grok's "
               "claim) is not implemented; this is a perturbative estimate."),
    )


__all__ = ["ConfinedBackreactionReport", "confined_metric_backreaction"]
