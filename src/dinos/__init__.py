"""Δῖνος (Dinos) — Dirac–Kerr–Newman electron-as-quantized-Kerr-resonator toolkit.

Reference: Knopp, "The electron as a quantized Kerr resonator with an antipodal
Higgs boundary: a rigorous geometric synthesis of the Dirac–Kerr–Newman soliton"
(2026).
"""

from . import (
    constants, closure, dm, geodesic, cp, casimir, verify,
    coords, temporal_loop, quantum_temporal_loop, qft, spectrum, generations,
    polar_strip, kerr_corrections, generations_extended, cross_repo_experiments,
    quarks, gravity_backreaction, metallic_sweep, pareto_generation_test,
    lepton_tower_derivation, lepton_smt, mobius_z3_cover,
    quarks_foot_test, holonomy_phi, phi_resolution,
    neutrinos_brannen, ckm_foot_test, hierarchy_scale, gauge_extension,
    quantum_gravity_loop,
)

__version__ = "0.1.0"
__all__ = [
    "constants", "closure", "dm", "geodesic", "cp", "casimir", "verify",
    "coords", "temporal_loop", "quantum_temporal_loop", "qft", "spectrum",
    "generations", "polar_strip", "kerr_corrections",
    "generations_extended", "cross_repo_experiments", "quarks",
    "gravity_backreaction", "metallic_sweep", "pareto_generation_test",
    "lepton_tower_derivation", "lepton_smt", "mobius_z3_cover",
    "quarks_foot_test", "holonomy_phi", "phi_resolution",
    "neutrinos_brannen", "ckm_foot_test", "hierarchy_scale",
    "gauge_extension", "quantum_gravity_loop",
]
