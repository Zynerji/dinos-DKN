"""b-phi duality tests (HYPOTHESIS Step 25)."""

from dinos import foot_duality as fd


def test_ten_invariant_pairs_documented():
    """10 (b, phi) pairs (vector mesons phi unmatched)."""
    assert len(fd.ALL_INVARIANT_PAIRS) == 10


def test_all_b_alphabet_is_metallic():
    """Every confirmed b is metallic-derived (no exceptions)."""
    for p in fd.ALL_INVARIANT_PAIRS:
        assert p.b_alphabet == "metallic"


def test_phi_alphabets_are_rational_pi_rational_or_arccos():
    """Every phi belongs to one of three rational alphabets."""
    valid = {"rational", "pi-rational", "arccos(rational)"}
    for p in fd.ALL_INVARIANT_PAIRS:
        assert p.phi_alphabet in valid


def test_duality_report_counts_correctly():
    report = fd.generate_duality_report()
    assert report.n_pairs == 10
    assert report.n_b_metallic == 10  # all b are metallic
    # Distribution of phi alphabets
    assert (report.n_phi_rational + report.n_phi_pi_rational
            + report.n_phi_arccos == 10)
