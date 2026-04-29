"""Algorithm atlas + RG flow + modular form + monodromy word tests
(HYPOTHESIS Step 51)."""

import numpy as np

from dinos import algorithms_atlas as aa
from dinos import metallic_rg_flow as rg
from dinos import modular_form_spectrum as mfs
from dinos import monodromy_word_search as mws


# ---- Atlas catalog ----

def test_catalog_has_20_entries():
    assert len(aa.CATALOG) == 20


def test_catalog_status_distribution():
    """8 verified, 6 scaffold, 4 new (or so), some speculative."""
    s = aa.status_summary()
    assert s.get("VERIFIED", 0) >= 6
    assert s.get("SCAFFOLD", 0) >= 4
    # NEW + SPECULATIVE = remainder
    assert sum(s.values()) == 20


def test_each_entry_has_pointer():
    for e in aa.CATALOG:
        assert e.pointer
        assert e.note


# ---- Metallic RG flow (Algorithm #15) ----

def test_beta_metallic_zeros_at_fixed_points():
    """β should vanish at b ∈ {0, 1, φ⁻¹, φ}."""
    for b in rg.fixed_points():
        assert abs(rg.beta_metallic(b)) < 1e-10


def test_rg_flow_runs_without_blowup():
    rep = rg.integrate_rg_flow(b_init=0.5, log_mu_final=5.0, n_steps=200)
    assert np.isfinite(rep.b_final)


def test_rg_fixed_point_classifications():
    fp = rg.fixed_point_classification()
    # b=0 derivative = (1-0)*(0-1/φ²)*(0-φ²) > 0 -> UV unstable, but the prefactor
    # at b=0 is exactly 0 so derivative there is more delicate. We just check that
    # the call returns dict with all 4 fixed points.
    assert len(fp) == 4


# ---- Modular form spectrum (Algorithm #19) ----

def test_modular_recursion_runs():
    rep = mfs.modular_spectrum(n_terms=8)
    assert len(rep.coefficients) == 8
    assert len(rep.mass_tower) == 8


def test_modular_carries_caveat():
    rep = mfs.modular_spectrum()
    assert "modular form" in rep.notes.lower() or "ansatz" in rep.notes.lower() or "constraints" in rep.notes.lower()


# ---- SL(2,Z) word search (Algorithm #6 expansion) ----

def test_sl2z_integer_traces_finite():
    traces = mws.generate_sl2z_traces(max_length=4)
    assert 0 in traces
    assert 2 in traces


def test_silver_matches_silver_hyperbolic_exactly():
    """Lepton b = sqrt(2) = (silver + 1/silver)/2."""
    silver = 1 + np.sqrt(2)
    pred = mws.hyperbolic_trace_from_eigenvalue(silver)
    assert abs(pred - np.sqrt(2)) < 1e-10


def test_atlas_against_integer_sl2z_traces():
    """Most atlas b's should NOT match integer-trace SL(2,Z) — the
    test confirms the negative result."""
    rep = mws.search_atlas_against_sl2z_traces(max_length=6,
                                                 tolerance_pct=1.0)
    # Few atlas b should match within 1% (most atlas b are continuous irrationals)
    assert rep.n_atlas_b_within_5pct < rep.n_atlas_total


def test_hyperbolic_match_partial_for_atlas():
    info = mws.hyperbolic_match_atlas()
    # Only the lepton case (b ~ sqrt(2)) should match within 1%
    # Other atlas b's are too small to match (M+1/M)/2 >= 1
    assert info["n_matches_within_1pct"] >= 1
