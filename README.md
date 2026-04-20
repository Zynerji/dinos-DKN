# Δῖνος — Dinos

**Numerical and symbolic toolkit for the Dirac–Kerr–Newman (DKN) electron-as-quantized-Kerr-resonator framework.**

Implements every computable claim of Knopp (2026), *"The electron as a quantized Kerr resonator with an antipodal Higgs boundary: a rigorous geometric synthesis of the Dirac–Kerr–Newman soliton"* — the full paper is included at [`paper/kerr-resonator.pdf`](paper/kerr-resonator.pdf).

*Dinos* (Δῖνος) is the pre-Socratic word for the cosmic vortex — the organizing principle Anaxagoras and Democritus placed at the root of matter. Over-rotating Kerr–Newman geometry is, literally, a spacetime vortex: the DKN ansatz takes that vortex seriously as the electron.

## Modules

| Module | Paper section | What it does |
|---|---|---|
| `dinos.closure` | §14 (eqs 61–67) | Solves the mass self-consistency `1 = 8πa³σ + 2𝒞 + α`. Forward (σ,𝒞,α → m_e) and inverse (m_e → σ). Reproduces Table 14.2 fractional decomposition. |
| `dinos.dm` | §16 (eqs 71–82), P1–P4 | Joint closure → `m* ≈ 156 keV`, `λ_H ≈ 0.129`, `v_bag ≈ 0.43 MeV`. Electron–DM cross section, 21-cm EDGES signature, stellar cooling, scalar-exchange g−2 correction. Bounds vs. XENONnT / SENSEI / RGB. |
| `dinos.geodesic` | §2, §7 (eqs 4–7, 24–30) | Null geodesics in Kerr–Newman with potentials `R(r), Θ(θ)`; Maslov-corrected Bohr–Sommerfeld quantization with μ_φ=μ_θ=2; map `(λ,η) → (n_φ,n_θ) → ‖k‖` (Theorem 7.4). |
| `dinos.cp` | §4, App. B (eqs 12–14, 87–88) | Chandrasekhar–Page angular eigenvalues `λ_CP(ω,μ,a,m_j)`. Rayleigh–Schrödinger expansion + optional exact diagonalization. |
| `dinos.casimir` | App. D (eqs 95–105) | Oblate-Kerr-bag Casimir for confined massive scalar multiplet with Robin (MIT-bag-compatible) BC. Closes Derrick gap `Δ𝒞 ≈ 0.153`. |
| `dinos.verify` | §7, §12, §14, §16, App. C | SymPy symbolic verification of the paper's key algebraic identities. |

## Install

```bash
pip install -e .
# or with dev extras
pip install -e ".[dev,notebooks]"
```

## Quickstart

```python
from dinos import closure, dm

# Forward: given Casimir constant, α, and σ, predict m_e
m_e = closure.electron_mass(sigma_MeV3=2.74e-2, C=0.17695, alpha=7.2974e-3)
print(f"m_e = {m_e:.4f} MeV  (target 0.511)")

# Fractional decomposition (Table 14.2)
print(closure.mass_fractions(C=0.17695, alpha=7.2974e-3))
# {'higgs_wall': 0.6388, 'dirac_casimir': 0.3539, 'em_self': 0.0073}

# Single-point DM prediction
pred = dm.joint_closure()
print(pred)  # m_star, lambda_H, v_bag, y_e, cross sections
```

## Reproduce the paper

```bash
jupyter notebook notebooks/reproduce_paper.ipynb
```

## Tests

```bash
pytest
```

## License

MIT. See `LICENSE`.

## Citation

```bibtex
@unpublished{Knopp2026DKN,
  author = {Christian Knopp},
  title  = {The Electron as a Quantized Kerr Resonator with an Antipodal Higgs Boundary},
  year   = {2026},
  note   = {Independent researcher; cknopp@gmail.com},
}
```
