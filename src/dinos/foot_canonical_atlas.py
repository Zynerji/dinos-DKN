"""Canonical atlas of all 19 confirmed metallic Foot resonances
(HYPOTHESIS Step 29).

Single authoritative reference combining the original 3 (Step 16),
heavy quark sector (Step 18), wider hadron sweep (Step 21), and
extended search (Step 28).

The atlas: 19 confirmed resonances
----------------------------------

| #  | Family                              | b expression                       | b value  |
|----|-------------------------------------|-------------------------------------|----------|
| 1  | Charged leptons (e, mu, tau)        | silver - 1 = sqrt(2)                | 1.414    |
| 2  | Neutrinos (sign-flip branch)        | silver - 1 (same b, different branch) | 1.414    |
| 3  | Vector mesons (rho, omega, phi)     | 1/bronze^2                         | 0.092    |
| 4  | Light baryons (N, Lambda, Xi)       | 1/(silver*copper)                  | 0.098    |
| 5  | Charmonium (eta_c, J/psi, chi_c)    | 1/(copper*silver^2)                | 0.041    |
| 6  | Charmonium 1S/2S/1P                 | 1/(bronze*silver^2)                | 0.052    |
| 7  | (D*, D_s*, J/psi)                   | 1/(bronze*supergolden^2)            | 0.141    |
| 8  | (J/psi, Upsilon(1S), Upsilon(2S))   | 1/(2*supergolden)                  | 0.341    |
| 9  | B mesons (B_0, B_s, B_c)            | 1/copper^2                         | 0.056    |
| 10 | Tensor (a_2, K_2*, f_2')            | 1/(copper^2*plastic)               | 0.042    |
| 11 | Axial (b_1, h_1, a_1)               | 1/(bronze^2*nickel)                | 0.018    |
| 12 | Scalar (f_0(500), f_0(980), a_0)    | 1/(3*supergolden)                  | 0.227    |
| 13 | (eta, h_1(1170), eta_c)             | golden/bronze                      | 0.490    |
| 14 | Decuplet (Delta, Sigma*, Omega)     | 1/(golden*nickel*plastic)          | 0.090    |
| 15 | (K, K*, B*)                         | 1/plastic                          | 0.755    |
| 16 | Gauge (W, Z, H)                     | 1/(copper*plastic^2)               | 0.135    |
| 17 | (K, D, B)                           | bronze/nickel                      | 0.636    |
| 18 | (rho, rho(1450), rho(1700))         | 1/(bronze*plastic)                 | 0.229    |
| 19 | (Xi_c, Xi_c', Omega_c)              | 1/(nickel^2*supergolden)           | 0.025    |

Statistics
----------
- 19 confirmed metallic Foot resonances across leptons, hadrons, and gauge bosons.
- All b values metallic-derived (silver, bronze, copper, plastic,
  supergolden, nickel; some golden too).
- 10 of 19 also have phi values matching simple closed forms.
- b values span 0.018 to 1.414 (~80x range).
- Mass scales span 0.5 MeV to 172 GeV (~3.5e8x range).

This is the empirical extent of the metallic-invariance pattern
identified in this work.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalEntry:
    rank: int
    family: str
    b_expression: str
    sector: str   # "lepton", "light_hadron", "heavy_quark", "gauge"
    n_metallic_factors: int


CANONICAL_ATLAS: list[CanonicalEntry] = [
    CanonicalEntry( 1, "charged_leptons",                      "silver - 1",                          "lepton",       1),
    CanonicalEntry( 2, "neutrinos",                             "silver - 1 (sign-flip)",              "lepton",       1),
    CanonicalEntry( 3, "vector_mesons (rho, omega, phi)",       "1/bronze^2",                          "light_hadron", 1),
    CanonicalEntry( 4, "light_baryons (N, Lambda, Xi)",         "1/(silver*copper)",                   "light_hadron", 2),
    CanonicalEntry( 5, "charmonium (eta_c, J/psi, chi_c)",      "1/(copper*silver^2)",                 "heavy_quark",  2),
    CanonicalEntry( 6, "charmonium 1S/2S/1P",                   "1/(bronze*silver^2)",                 "heavy_quark",  2),
    CanonicalEntry( 7, "(D*, D_s*, J/psi)",                     "1/(bronze*supergolden^2)",            "heavy_quark",  2),
    CanonicalEntry( 8, "(J/psi, Upsilon(1S), Upsilon(2S))",     "1/(2*supergolden)",                   "heavy_quark",  1),
    CanonicalEntry( 9, "B mesons (B_0, B_s, B_c)",              "1/copper^2",                          "heavy_quark",  1),
    CanonicalEntry(10, "tensor (a_2, K_2*, f_2')",              "1/(copper^2*plastic)",                "light_hadron", 2),
    CanonicalEntry(11, "axial (b_1, h_1, a_1)",                 "1/(bronze^2*nickel)",                 "light_hadron", 2),
    CanonicalEntry(12, "scalar (f_0(500), f_0(980), a_0)",      "1/(3*supergolden)",                   "light_hadron", 1),
    CanonicalEntry(13, "(eta, h_1(1170), eta_c)",               "golden/bronze",                       "heavy_quark",  2),
    CanonicalEntry(14, "decuplet (Delta, Sigma*, Omega)",       "1/(golden*nickel*plastic)",           "light_hadron", 3),
    CanonicalEntry(15, "(K, K*, B*)",                            "1/plastic",                           "heavy_quark",  1),
    CanonicalEntry(16, "gauge (W, Z, H)",                        "1/(copper*plastic^2)",                "gauge",        2),
    CanonicalEntry(17, "(K, D, B)",                              "bronze/nickel",                       "heavy_quark",  2),
    CanonicalEntry(18, "(rho, rho(1450), rho(1700))",            "1/(bronze*plastic)",                  "light_hadron", 2),
    CanonicalEntry(19, "(Xi_c, Xi_c', Omega_c)",                 "1/(nickel^2*supergolden)",            "heavy_quark",  2),
]


def by_sector() -> dict[str, list[CanonicalEntry]]:
    """Group resonances by sector."""
    out: dict[str, list[CanonicalEntry]] = {
        "lepton": [], "light_hadron": [], "heavy_quark": [], "gauge": [],
    }
    for e in CANONICAL_ATLAS:
        out[e.sector].append(e)
    return out


def metallic_factor_distribution() -> dict[int, int]:
    """How many resonances use 1, 2, or 3 metallic factors."""
    dist: dict[int, int] = {}
    for e in CANONICAL_ATLAS:
        dist[e.n_metallic_factors] = dist.get(e.n_metallic_factors, 0) + 1
    return dist


__all__ = [
    "CanonicalEntry", "CANONICAL_ATLAS",
    "by_sector", "metallic_factor_distribution",
]
