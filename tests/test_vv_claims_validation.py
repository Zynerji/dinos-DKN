"""vv.txt 20-algorithm audit tests (HYPOTHESIS Step 55)."""

from dinos import vv_claims_validation as vv


def test_vv_audit_has_20_entries():
    assert len(vv.VV_AUDIT) == 20


def test_vv_audit_zero_confirmed():
    s = vv.vv_status_summary()
    assert s["n_confirmed"] == 0


def test_vv_audit_has_overload_entries():
    """Some entries explicitly depend on already-falsified cz2 #2 / #8 / #9."""
    overloads = [a for a in vv.VV_AUDIT if a.verdict == "OVERLOAD"]
    assert len(overloads) >= 2


def test_vv_audit_has_complexity_false_entries():
    """Some claimed speedups don't hold (matrix powers, CF iteration, RS bounds)."""
    cf = [a for a in vv.VV_AUDIT if a.verdict == "COMPLEXITY_FALSE"]
    assert len(cf) >= 2


def test_each_audit_has_rationale():
    for a in vv.VV_AUDIT:
        assert len(a.rationale) > 30


def test_summary_total_matches_audit():
    s = vv.vv_status_summary()
    assert sum(s["verdict_counts"].values()) == s["total_algorithms"] == 20
