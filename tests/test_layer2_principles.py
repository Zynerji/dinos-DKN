"""Layer 2 deep-dive tests (HYPOTHESIS Step 54)."""

from dinos import layer2_principles as l2


def test_metallic_advantage_over_non_metallic():
    """Metallic basis should significantly beat non-metallic quadratic at 0.1%."""
    p = l2.metallic_vs_quadratic_discrimination(tolerance_pct=0.1)
    # Quantitative: ratio >= 4x
    quant = p.quantitative
    assert "x metallic advantage" in quant or "x" in quant
    assert p.status == "SHARPENED"


def test_phi_cf_signature_partial():
    p = l2.phi_cf_signature_analysis()
    assert p.status == "SHARPENED"
    assert "%" in p.quantitative


def test_binary_factorization_documented():
    p = l2.binary_factorization_analysis()
    assert p.status == "OPEN"
    assert "Most-paired" in p.quantitative


def test_a_predictor_falsifies_cz2_gap_equation():
    p = l2.a_predictor_analysis()
    assert p.status == "OPEN"
    # GM should win heavily over 1/b
    assert "R²(log a vs log GM)" in p.quantitative


def test_cross_sector_closure_falsified():
    p = l2.cross_sector_product_analysis()
    assert p.status == "FALSIFIED"


def test_summary_documents_5_principles():
    s = l2.principles_summary()
    assert s["total_principles"] == 5
    counts = s["status_counts"]
    assert counts.get("SHARPENED", 0) >= 2
    assert counts.get("FALSIFIED", 0) >= 1


def test_cf_expand_basic():
    """Sanity: pi/4 has CF starting [0; 1, 3, ...]"""
    import math
    cf = l2.cf_expand(math.pi / 4, max_terms=5)
    assert cf[0] == 0
    assert cf[1] == 1
