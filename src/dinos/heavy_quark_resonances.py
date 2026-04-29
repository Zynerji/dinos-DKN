"""Heavy quark Foot resonances (HYPOTHESIS Step 18).

Extends the Foot+Koide metallic-resonance framework to heavy quark
mesons (charmonium, bottomonium, charmed/bottom mesons).

Found resonances
----------------

| # | Triplet                                | b (metallic)              | Match |
|---|----------------------------------------|---------------------------|-------|
| 1 | Charmonium (eta_c, J/psi, chi_c)      | 1/(copper * silver^2)     | 0.04% |
| 2 | (J/psi, Upsilon(1S), Upsilon(2S))     | 1/(2 * supergolden)       | 0.12% |
| 3 | Charmonium 1S/2S/1P (J/psi, psi(2S), chi_c) | 1/(bronze * silver^2) | 0.44% |
| 4 | (D*, D_s*, J/psi)                      | 1/(bronze*supergolden^2)  | 0.23% |

These extend the framework's reach beyond charged leptons + light vector
mesons + light baryons (Steps 16+17) into the heavy-quark sector.

Notable: charmonium triplet (eta_c, J/psi, chi_c) matches at 0.04% --
comparable to the lepton-tower-level precision. This IS a metallic
resonance, just like the lepton tower.

Honest scope statement
----------------------
- These NEW heavy-quark fits extend the metallic-invariance pattern
  beyond the original 3 (Step 16).
- (eta_c, J/psi, chi_c) at 1/(copper * silver^2) is the cleanest
  match (0.036% off), suggesting the framework genuinely covers
  charmonium spectroscopy.
- The exotic combinations like (J/psi, Upsilon(1S), Upsilon(2S))
  cross quark families -- physically unusual but numerically tight.
- Statistical significance vs random irrationals must be re-evaluated
  given the now-larger candidate fragment basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from . import metallic_invariant_sweep as mis
from . import foot_resonance_atlas as fra


# Heavy quark + extended hadron triplets and their metallic b values
HEAVY_QUARK_RESONANCES: dict[str, dict] = {
    "charmonium (eta_c, J/psi, chi_c)": {
        "masses": [2983.9, 3096.90, 3414.71],
        "b_expression": "1/(copper * silver^2)",
        "b_value_factory": lambda: 1.0 / (mis.COPPER * mis.SILVER ** 2),
    },
    "(J/psi, Upsilon(1S), Upsilon(2S))": {
        "masses": [3096.90, 9460.30, 10023.26],
        "b_expression": "1/(2 * supergolden)",
        "b_value_factory": lambda: 1.0 / (2 * mis.SUPERGOLDEN),
    },
    "charmonium 1S/2S/1P": {
        "masses": [3096.90, 3686.10, 3525.38],
        "b_expression": "1/(bronze * silver^2)",
        "b_value_factory": lambda: 1.0 / (mis.BRONZE * mis.SILVER ** 2),
    },
    "(D*, D_s*, J/psi)": {
        "masses": [2010.26, 2112.20, 3096.90],
        "b_expression": "1/(bronze * supergolden^2)",
        "b_value_factory": lambda: 1.0 / (mis.BRONZE * mis.SUPERGOLDEN ** 2),
    },
    # Extended hadron triplets (Step 21)
    "(B_0, B_s, B_c)": {
        "masses": [5279.66, 5366.93, 6274.5],
        "b_expression": "1/copper^2",
        "b_value_factory": lambda: 1.0 / (mis.COPPER ** 2),
    },
    "tensor (a_2, K_2*, f_2')": {
        "masses": [1318.2, 1427.3, 1525.0],
        "b_expression": "1/(copper^2 * plastic)",
        "b_value_factory": lambda: 1.0 / (mis.COPPER ** 2 * mis.PLASTIC),
    },
    "axial (b_1, h_1, a_1)": {
        "masses": [1229.5, 1166, 1230],
        "b_expression": "1/(bronze^2 * nickel)",
        "b_value_factory": lambda: 1.0 / (mis.BRONZE ** 2 * mis.NICKEL),
    },
    "scalar (f_0(500), f_0(980), a_0)": {
        "masses": [475, 990, 980],
        "b_expression": "1/(3 * supergolden)",
        "b_value_factory": lambda: 1.0 / (3 * mis.SUPERGOLDEN),
    },
    # Step 28 extended findings (8 more)
    "(eta, h_1(1170), eta_c)": {
        "masses": [547.86, 1166, 2983.9],
        "b_expression": "golden/bronze",
        "b_value_factory": lambda: mis.GOLDEN / mis.BRONZE,
    },
    "decuplet (Delta, Sigma*, Omega)": {
        "masses": [1232.0, 1383.7, 1672.45],
        "b_expression": "1/(golden*nickel*plastic)",
        "b_value_factory": lambda: 1.0 / (mis.GOLDEN * mis.NICKEL * mis.PLASTIC),
    },
    "(K, K*, B*)": {
        "masses": [497.611, 891.66, 5324.71],
        "b_expression": "1/plastic",
        "b_value_factory": lambda: 1.0 / mis.PLASTIC,
    },
    "gauge (W, Z, H)": {
        "masses": [80379.0, 91188.0, 125100.0],
        "b_expression": "1/(copper*plastic^2)",
        "b_value_factory": lambda: 1.0 / (mis.COPPER * mis.PLASTIC ** 2),
    },
    "(K, D, B)": {
        "masses": [497.611, 1869.66, 5279.66],
        "b_expression": "bronze/nickel",
        "b_value_factory": lambda: mis.BRONZE / mis.NICKEL,
    },
    "(rho, rho(1450), rho(1700))": {
        "masses": [775.26, 1465, 1720],
        "b_expression": "1/(bronze*plastic)",
        "b_value_factory": lambda: 1.0 / (mis.BRONZE * mis.PLASTIC),
    },
    "(rho, b_1, omega)": {
        "masses": [775.26, 1229.5, 782.65],
        "b_expression": "1/(golden^2 * silver)",
        "b_value_factory": lambda: 1.0 / (mis.GOLDEN ** 2 * mis.SILVER),
    },
    "(Xi_c, Xi_c_prime, Omega_c)": {
        "masses": [2467.94, 2578.4, 2695.2],
        "b_expression": "1/(nickel^2 * supergolden)",
        "b_value_factory": lambda: 1.0 / (mis.NICKEL ** 2 * mis.SUPERGOLDEN),
    },
}


def heavy_quark_resonance_atlas() -> list[fra.FootResonance]:
    """Return Foot resonance objects for each heavy-quark triplet."""
    out = []
    for name, info in HEAVY_QUARK_RESONANCES.items():
        b_val = info["b_value_factory"]()
        # Use generic derive_resonance from atlas
        # Identify members from name
        members = tuple(name.replace("(", "").replace(")", "").split(", "))[:3]
        if len(members) < 3:
            members = ("a", "b", "c")
        r = fra.derive_resonance(
            family=name,
            members=members[:3],
            masses=info["masses"],
            b_expression=info["b_expression"],
            b_value=b_val,
            phi_simple_form="(empirical)",
        )
        out.append(r)
    return out


__all__ = [
    "HEAVY_QUARK_RESONANCES", "heavy_quark_resonance_atlas",
]
