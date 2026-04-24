<div align="center">

# Δῖνος — `dinos-DKN`

**The electron as a quantized Kerr resonator with an antipodal Higgs boundary — a production-quality numerical toolkit for the Dirac–Kerr–Newman framework.**

[![Python ≥ 3.10](https://img.shields.io/badge/python-%E2%89%A5%203.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 57 passing](https://img.shields.io/badge/tests-57%20passing-brightgreen.svg)](#testing)
[![Paper: PDF](https://img.shields.io/badge/whitepaper-PDF-informational.svg)](paper/temporal_loop_dkn.pdf)
[![DKN paper](https://img.shields.io/badge/DKN_paper-PDF-informational.svg)](paper/kerr-resonator.pdf)

*Dinos* (Δῖνος) is the pre-Socratic word for the cosmic vortex — the organising principle Anaxagoras and Democritus placed at the root of matter. Over-rotating Kerr–Newman geometry is, literally, a spacetime vortex: the DKN ansatz takes that vortex seriously as the electron.

</div>

---

## What this is

A peer-reviewable numerical implementation of every computable claim in Knopp (2026), *"The electron as a quantized Kerr resonator with an antipodal Higgs boundary,"* plus a finite-Möbius **self-consistent CTC simulator** that resolves three open problems in the Dirac-Kerr-Newman / Tipler-cylinder literature:

1. **Burinskii's naked ring singularity** and missing mass self-consistency (2005, 2008, 2021; Arcos & Pereira 2004; Carter 1968; Dymnikova 2021).
2. **Tipler's infinite-length / exotic-matter requirement** (1974; Mallett 2003; Hawking 1992 chronology protection).
3. **Kerr-interior instability / CTC leakage** (Carter 1968; Astefanesei et al. 2005).

Every resolution is a runnable cell in [`notebooks/reproduce_temporal_loop_dkn.ipynb`](notebooks/reproduce_temporal_loop_dkn.ipynb) and a numerical table in [`paper/temporal_loop_dkn.pdf`](paper/temporal_loop_dkn.pdf).

## Quickstart

```bash
pip install -e ".[dev,notebooks]"
pytest                                                      # 57 tests, < 3 s
jupyter notebook notebooks/reproduce_temporal_loop_dkn.ipynb
```

```python
from dinos.temporal_loop import MobiusTemporalLoop, DKNParams
from dinos import closure, geodesic

loop = MobiusTemporalLoop(
    N=128, T=4.0, K=128,
    alpha=0.7, beta=0.15, tau=1.0, damping=0.99, eta=0.0,
    dkn_params=DKNParams(),
    seed=1,
)
report = loop.evolve(max_iter=200, epsilon=1e-2)

mass = closure.enforce_mobius_fixed_point(report["fixed_point_slice"])
print(f"m_e recovered = {mass['m_e_MeV']:.4f} MeV   (paper target 0.5110)")

labels = geodesic.quantize(
    boundary_condition="mobius_self_consistent",
    mobius_psi=report["fixed_point_slice"],
)
print(f"Dirac labels:  |k|={labels.k_abs}, j={labels.j}, m_j={labels.m_j}")
print(f"contraction A = {report['contraction_factor_A']:.2f}")
print(f"emergent ϕ_twist = {report['phi_twist_extracted']:.2e}")
```

Output on a laptop in about 1 second:

```
m_e recovered = 0.5111 MeV   (paper target 0.5110)
Dirac labels:  |k|=2, j=1.5, m_j=1.5
contraction A = 0.36
emergent ϕ_twist = -4.19e-05
```

## Table of contents

- [Modules](#modules)
- [Quickstart](#quickstart)
- [Möbius temporal loop](#möbius-temporal-loop)
- [Prior-art resolutions](#prior-art-resolutions)
- [Testing](#testing)
- [Documentation](#documentation)
- [Citation](#citation)
- [License](#license)

## Modules

| Module | Paper section | What it does |
|---|---|---|
| `dinos.closure` | §14 (eqs 61–67) | Mass self-consistency `1 = 8πa³σ + 2𝒞 + α`. Forward/inverse closure. Reproduces Table 14.2. |
| `dinos.dm` | §16 (eqs 71–82), P1–P4 | Joint closure → `m* ≈ 156 keV`, `λ_H ≈ 0.129`, `v_bag ≈ 0.43 MeV`. DM predictions. |
| `dinos.geodesic` | §2, §7 (eqs 4–7, 24–30) | Null geodesics + Maslov-corrected Bohr–Sommerfeld; `(λ,η) → (n_φ, n_θ)` map. |
| `dinos.cp` | §4, App. B (eqs 12–14, 87–88) | Chandrasekhar–Page angular eigenvalues. |
| `dinos.casimir` | App. D (eqs 95–105) | Oblate-Kerr-bag Casimir with Robin BC; closes Derrick gap `Δ𝒞 ≈ 0.153`. |
| `dinos.coords` | §2 (eq 1) | Boyer–Lindquist ↔ oblate-spheroidal cylindrical; raw Kerr–Newman metric; vortex visualisation. |
| `dinos.temporal_loop` | whitepaper §§2–5, Apps. A–B | Möbius spatial strip + temporal loop; prophetic-feedback dynamics; self-consistent CTC fixed point; DKN coupling. |
| `dinos.quantum_temporal_loop` | whitepaper §7 | Density-operator CPTP evolution (pure NumPy, QuTiP-optional). |
| `dinos.verify` | §§7, 12, 14, 16, App. C | SymPy symbolic verification incl. the Möbius ↔ Kerr frame-dragging isomorphism. |

## Möbius temporal loop

`dinos.temporal_loop` expresses the DKN electron as a **self-initialised, Higgs-capped Tipler cylinder** — the numerical realisation of the framework:

| Classical picture | DKN realisation |
|---|---|
| Tipler cylinder — infinite, dust-free, rotating past light-speed | Over-rotating Kerr–Newman geometry (`a > M`, naked ring) |
| Closed timelike curves on the cylinder surface | Möbius temporal loop of length T around the ring |
| Grandfather paradox — unconstrained CTCs are ill-posed | *Prophetic feedback* α(ψ_b − ψ_f) drives a self-consistent fixed point |
| Pathological "boundary at infinity" | **Antipodal Higgs boundary** — ψ_f(0) = ψ_b(0), amplitude pinned to the Compton radius (`closure.py`, eq 62) |
| No quantisation of rotation | Phase winding around the spatial Möbius strip picks up the Z₂ seam — exactly the fermion Maslov index μ_φ = 2 and hence the BS azimuthal integer n_φ |

> **The electron is a Tipler cylinder quantised as a Kerr resonator via a self-consistent Möbius temporal loop, with the Higgs wall as the antipodal boundary that turns a generically paradoxical CTC into a well-posed soliton.**

## Prior-art resolutions

Full numerical derivations are in [`paper/temporal_loop_dkn.pdf`](paper/temporal_loop_dkn.pdf) §5; each is a runnable cell in the notebook §6.

| # | Prior art | Open issue | Numerical fix |
|---|---|---|---|
| 1 | Burinskii 2005/2008/2021; Arcos & Pereira 2004; Carter 1968; Dymnikova 2021 | Naked ring singularity; no CTC confinement; no mass self-consistency | Higgs wall + self-consistent init → `m_e` recovered to **0.02%**; fixed-point amplitude spread **5.8 × 10⁻³** ⇒ CTC confined |
| 2 | Tipler 1974; Mallett 2003; Hawking 1992 | Infinite length or exotic (negative-energy) matter required | Finite Möbius loop; contraction factor `A = (1−β)(1−α) + βα` measured in **[0.34, 0.66]** ⇒ exponential convergence, min\|ψ_target\| > 0 (no exotic matter) |
| 3 | Carter 1968; Astefanesei et al. 2005 | Kerr-interior instability; CTC leakage | Emergent twist `ϕ*_twist` is a topological invariant — std across 80 perturbations = **1.3 × 10⁻⁴** (two orders below ε=10⁻²) |

## Testing

```bash
pytest              # 57 tests, full coverage of every new module
pytest tests/test_temporal_loop.py -v
```

Symbolic identity checks from the paper:

```bash
python -m dinos.verify
# 6/6 symbolic identities verified:
#   [OK] geodesic→Dirac index (§7.2)
#   [OK] Derrick virial (§12.2)
#   [OK] mass closure (§14.1)
#   [OK] joint closure (§16.1)
#   [OK] bulk–boundary duality (App C)
#   [OK] Möbius–Kerr isomorphism (§7+Möbius)
```

## Documentation

- **Whitepaper** (13 pages, with figures and two appendix proofs): [`paper/temporal_loop_dkn.pdf`](paper/temporal_loop_dkn.pdf) · LaTeX source: [`paper/temporal_loop_dkn.tex`](paper/temporal_loop_dkn.tex)
- **Main DKN paper** (Knopp 2026): [`paper/kerr-resonator.pdf`](paper/kerr-resonator.pdf)
- **Tutorial notebooks**:
  - [`notebooks/reproduce_paper.ipynb`](notebooks/reproduce_paper.ipynb) — reproduces every numerical claim in the main paper.
  - [`notebooks/reproduce_temporal_loop_dkn.ipynb`](notebooks/reproduce_temporal_loop_dkn.ipynb) — full V2 self-consistent walkthrough + the three prior-art fixes.

## Citation

```bibtex
@unpublished{Knopp2026DKN,
  author = {Christian Knopp},
  title  = {The Electron as a Quantized Kerr Resonator with an Antipodal Higgs Boundary},
  year   = {2026},
  note   = {cknopp@gmail.com},
}

@unpublished{Knopp2026TemporalLoop,
  author = {Christian Knopp},
  title  = {Perfect Temporal Loop in the Dirac--Kerr--Newman Framework:
            the electron as a quantized, self-consistent Tipler cylinder resonator},
  year   = {2026},
  note   = {cknopp@gmail.com},
}
```

## License

MIT. See [`LICENSE`](LICENSE).

## Contact

Christian Knopp · `cknopp@gmail.com`
