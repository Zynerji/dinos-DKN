<div align="center">

# Δῖνος — `dinos-DKN`

**The electron as a quantized Kerr resonator with an antipodal Higgs boundary — and a 25-resonance metallic mass atlas spanning eight orders of magnitude that places particle mass spectra at the boundary of substitution dynamics.**

[![Python ≥ 3.10](https://img.shields.io/badge/python-%E2%89%A5%203.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 496 passing](https://img.shields.io/badge/tests-496%20passing-brightgreen.svg)](#testing)
[![Steps: 57 verdicts](https://img.shields.io/badge/HYPOTHESIS-57%20steps-blue.svg)](HYPOTHESIS.md)
[![Whitepaper](https://img.shields.io/badge/whitepaper-PDF-informational.svg)](paper/quantum_bridge.pdf)

*Dinos* (Δῖνος) is the pre-Socratic word for the cosmic vortex.

</div>

---

## What this project actually is (honest, three layers)

This repo contains three distinct levels of work, mapped explicitly to verdicts (`CONFIRMED` / `OPEN` / `FALSIFIED`) in [`HYPOTHESIS.md`](HYPOTHESIS.md).

### Layer 1 — verified single-electron model (Steps 1–11)
- DKN/Möbius temporal loop maps to a Schwinger–Keldysh saddle on a finite contour (Step 1).
- Möbius spectrum identifies with the Dirac azimuthal sector (Step 2).
- −½ Kerr prefactor derived from time averaging (Step 5b).
- Charged-lepton mass tower fully closed: b = √2, a = 313.84 MeV, m_τ predicted within 1σ, φ = 2/9 identified via continued-fraction signature (Steps 8–11).
- Z₃ Möbius cover eigenvalue formula `λ = 2 − 2 cos(2π(n ± 1/3)/N)` confirmed to machine precision (Step 50, Theorem 2).

### Layer 2 — empirical metallic Foot atlas (Steps 15–38)
- 25 confirmed metallic Foot resonances spanning leptons, hadrons, gauge bosons (8 orders of magnitude in mass).
- **Higgs predicted from (W, Z) alone at 0.10%** (within experimental uncertainty), at b = 1/(copper · plastic²) (Step 33).
- Atlas beats random irrational baseline by **18×** at 0.05% tolerance (Step 31).
- Atlas beats other quadratic irrationals by **8×** at 0.05% — selection is to a specific algebraic family, not just "any algebraic number" (Step 54).

### Layer 3 — speculative extensions (Steps 39, 50–57)
0/8 Grok claims, 0/10 cz.txt transdisciplinary claims, 0/20 ej.txt algorithms, 0/20 vv.txt algorithms, 1/5 cj.txt theorems (Z₃ eigenvalue) — each **systematically tested and graded**. The framework's most distinctive feature is its explicit record of what **didn't** work.

## The deep finding (Step 57): atlas as substitution dynamics

The 7 ratios used in the atlas — `golden, silver, bronze, copper, nickel, plastic, supergolden` — are precisely the **asymptotic growth rates of integer linear recurrences with EXACTLY 2 nonzero coefficients**:

| Recurrence | Sequence name | Atlas ratio |
|---|---|---|
| `a_n = a_{n-1} + a_{n-2}` | Fibonacci | golden φ |
| `a_n = 2a_{n-1} + a_{n-2}` | Pell | silver |
| `a_n = 3a_{n-1} + a_{n-2}` | Bronze Fibonacci | bronze |
| `a_n = 4a_{n-1} + a_{n-2}` | | copper |
| `a_n = 5a_{n-1} + a_{n-2}` | | nickel |
| `a_n = a_{n-2} + a_{n-3}` | Padovan | plastic — *smallest Pisot in existence* |
| `a_n = a_{n-1} + a_{n-3}` | Narayana's cow | supergolden |

Excluded by the rule (Pisot but absent from the atlas): tribonacci (3-term), tetranacci (4-term).

This places the framework at the boundary of **Pisot β-numeration and substitution dynamics** (Bertrand-Mathis 1989; Schmidt 1980; Pytheas Fogg 2002; Solomyak; Akiyama). The remaining "why does Möbius-Z₃ couple to 2-symbol substitutions" question lives in algebraic dynamics, not in the framework itself.

---

## Quickstart

```bash
pip install -e ".[dev,notebooks]"
pytest                           # 496 tests, ~10 minutes (most are fast; metallic Foot scans dominate)
pytest tests/test_qft.py -q      # 5 tests, < 5 s
```

```python
# Single-electron mass recovery
from dinos.temporal_loop import MobiusTemporalLoop, DKNParams
from dinos import closure
loop = MobiusTemporalLoop(N=128, T=4.0, K=128, alpha=0.7, beta=0.15,
                            tau=1.0, damping=0.99, eta=0.0,
                            dkn_params=DKNParams(), seed=1)
report = loop.evolve(max_iter=200, epsilon=1e-2)
mass = closure.enforce_mobius_fixed_point(report["fixed_point_slice"])
print(f"m_e recovered = {mass['m_e_MeV']:.4f} MeV")    # 0.5111

# Higgs from (W, Z)
from dinos.foot_predictions_extended import gauge_boson_higgs_prediction
h = gauge_boson_higgs_prediction()
print(f"m_H predicted = {h.predicted_MeV:.0f} MeV vs {h.empirical_MeV:.0f} MeV "
      f"({h.relative_error_pct:.2f}%)")    # 125222 vs 125100 (0.10%)

# Substitution-dynamics characterisation
from dinos.substitution_dynamics_answer import two_term_recurrence_selection
v = two_term_recurrence_selection()
print(v.rule)
```

---

## Repository contents

```
src/dinos/
  Layer 1 (verified):
    qft.py, spectrum.py, polar_strip.py, cp.py, kerr_corrections.py
    temporal_loop.py, closure.py, geodesic.py, casimir.py, coords.py, dm.py
    lepton_tower_derivation.py, lepton_smt.py, mobius_z3_cover.py
    phi_resolution.py, neutrinos_brannen.py, holonomy_phi.py
  Layer 2 (atlas):
    metallic_invariant_sweep.py
    foot_resonance_atlas.py
    foot_mass_predictions.py             — Higgs from (W, Z) lives here
    foot_predictions_extended.py
    foot_canonical_atlas.py              — 19-resonance reference table
    foot_atlas_discrimination.py         — 18× over random baseline
    heavy_baryon_foot.py
    quark_generation_foot.py
    foot_sector_structure.py
    layer2_principles.py                 — open-question deep dive
    metallic_selection_rule.py           — Pisot characterisation
    substitution_dynamics_answer.py      — 2-term recurrence answer
  Layer 3 (speculative scaffolds + validation):
    multi_cover.py, electroweak_strip.py, anomaly_check.py
    ckm_overlaps.py, pmns_overlaps.py, topological_seesaw.py
    hhml_dkn_hybrid.py, lambda_attractor.py, varying_c_pruning.py
    grok_claims_validation.py, cz_claims_validation.py
    ee_ej_validation.py, vv_claims_validation.py
    monodromy_hecke_test.py, theorems_extension.py
    ... (see HYPOTHESIS.md for full list of 60+ modules)

tests/                                   — 496 tests covering every claim
paper/quantum_bridge.tex / .pdf          — main whitepaper (last full rev: Step 33)
HYPOTHESIS.md                            — 57-step verdict log; living document
```

## Falsifiable predictions (the headline ones)

| Prediction | Source | Status |
|---|---|---|
| m_τ = 1776.97 MeV from (m_e, m_μ) at b = √2 | Step 17 | within 1σ of PDG |
| m_H = 125 222 MeV from (m_W, m_Z) at b = 1/(copper · plastic²) | Step 33 | matches PDG within experimental uncertainty (0.10%) |
| Σm_ν = 0.0592 eV (charged-lepton b transferred to neutrino sector) | Step 12a | testable by DESI / Euclid / CMB-S4 |
| Ξ_bb = 10 139 MeV from (Ξ_cc, Ξ_cb) | Step 35 | testable at LHCb |
| Ω_bbb = 14 081 MeV from (Ξ_b, Ξ_bb) | Step 35 | testable at FCC |
| m_t ≈ 168 GeV from (m_c, m_b) at b = √2 | Step 34 | within 2.5% (PDG charm uncertainty dominates) |

## The honest record

The repo distinguishes itself by **not hiding what didn't work**. See:

- [`HYPOTHESIS.md`](HYPOTHESIS.md) — 57 steps with verdicts (CONFIRMED / OPEN / FALSIFIED / TAUTOLOGICAL / etc.)
- `dinos.grok_claims_validation` — 0/8 confirmed
- `dinos.cz_claims_validation` — 0/10 transdisciplinary claims confirmed
- `dinos.vv_claims_validation` — 0/20 'rigorous' algorithms confirmed
- `dinos.theorems_extension` — 1 confirmed (Z₃ eigenvalue formula), 1 falsified, 3 partial / conditional
- `dinos.ee_ej_validation` — Hecke-triangle pathway tested; 1/19 atlas matches → conjecture refuted

Most physics frameworks do not publish their failed conjectures. This one does; treat that as the framework's most reliable feature.

## What's next

Concretely:
1. Enumerate higher-degree 2-letter-image substitutions and predict NEW mass triplets from previously-unidentified Pisot ratios (next concrete extension of the atlas).
2. Compute β-numerations of atlas mass triplets in their respective Pisot bases — search for hidden cross-family structure.
3. Test the prediction that Penrose / Ammann-Beenker / Padovan tiling vertex distributions correlate with measured masses in the corresponding atlas family.
4. Whitepaper revision incorporating Steps 31–57 (currently the published PDF reflects Step 33 only — see HYPOTHESIS.md for the full record).

## Citation

```bibtex
@misc{Knopp2026DinosDKN,
  author = {Knopp, Christopher},
  title  = {{Dinos-DKN}: A numerical toolkit for the Dirac--Kerr--Newman framework
            with metallic Foot mass atlas},
  year   = {2026},
  url    = {https://github.com/Zynerji/dinos-DKN},
  note   = {496 passing tests; 57-step verdict log; substitution-dynamics
            characterisation of mass-triplet metallic invariants.},
}
```

## License

MIT. See [`LICENSE`](LICENSE).

## Contact

`cknopp@gmail.com`
