"""Systematic Foot scan tests (HYPOTHESIS Step 14)."""

from math import isclose, sqrt

from dinos import foot_systematic_scan as fss


# -----------------------------------------------------------------------------
# Q-range theorem at b = sqrt(2)
# -----------------------------------------------------------------------------

def test_q_max_at_b_sqrt_2_is_about_2p44():
    """Maximum Q in any sign-flip branch at b = sqrt(2) is (1+2*sqrt(2))²/6."""
    q_max = fss.max_achievable_q_at_b_sqrt_2()
    expected = (1 + 2 * sqrt(2)) ** 2 / 6
    assert isclose(q_max, expected, rel_tol=1e-12)
    assert isclose(q_max, 2.443, abs_tol=0.01)


def test_lepton_q_three_halves_is_achievable():
    """Q = 3/2 is the all-positive branch at b = sqrt(2) — achievable."""
    assert fss.is_q_achievable_at_b_sqrt_2(1.5)


def test_neutrino_q_one_pt_9_is_achievable():
    """Q ~ 1.9 (neutrinos) is in the one-flip branch range."""
    assert fss.is_q_achievable_at_b_sqrt_2(1.9048)


def test_meson_q_around_2p7_is_NOT_achievable():
    """Q ~ 2.7 (typical mesons) is OUTSIDE the b = sqrt(2) range."""
    assert not fss.is_q_achievable_at_b_sqrt_2(2.7)


def test_baryon_q_around_3_is_NOT_achievable():
    """Q ~ 3.0 (baryons) is far above the achievable range."""
    assert not fss.is_q_achievable_at_b_sqrt_2(2.99)


# -----------------------------------------------------------------------------
# Fragment scan
# -----------------------------------------------------------------------------

def test_lepton_triplet_fits():
    """The (e, mu, tau) triplet fits at b = sqrt(2) (Q = 3/2)."""
    results = fss.run_full_scan()
    lepton_results = [r for r in results if r.family == "leptons"]
    assert len(lepton_results) == 1
    assert lepton_results[0].fits_at_b_sqrt_2
    assert isclose(lepton_results[0].koide_q, 1.5, abs_tol=1e-3)


def test_all_pseudoscalar_meson_triplets_reject():
    """No pseudoscalar meson 3-state subset fits at b = sqrt(2)."""
    results = fss.run_full_scan()
    ps_results = [r for r in results if r.family == "pseudoscalar_mesons"]
    assert len(ps_results) > 0
    for r in ps_results:
        assert not r.fits_at_b_sqrt_2, f"{r.name} unexpectedly fits"


def test_all_vector_meson_triplets_reject():
    """No vector meson 3-state subset fits at b = sqrt(2)."""
    results = fss.run_full_scan()
    v_results = [r for r in results if r.family == "vector_mesons"]
    for r in v_results:
        assert not r.fits_at_b_sqrt_2


def test_all_baryon_triplets_reject():
    """No light baryon octet triplet fits."""
    results = fss.run_full_scan()
    b_results = [r for r in results if r.family == "light_baryons"]
    for r in b_results:
        assert not r.fits_at_b_sqrt_2


def test_all_decuplet_baryon_triplets_reject():
    """No decuplet baryon triplet fits."""
    results = fss.run_full_scan()
    d_results = [r for r in results if r.family == "decuplet_baryons"]
    for r in d_results:
        assert not r.fits_at_b_sqrt_2


def test_gauge_boson_triplet_rejects():
    """(W, Z, H) gauge boson triplet doesn't fit at b = sqrt(2)."""
    results = fss.run_full_scan()
    g_results = [r for r in results if r.family == "gauge_bosons"]
    for r in g_results:
        assert not r.fits_at_b_sqrt_2


# -----------------------------------------------------------------------------
# Aggregate scan report
# -----------------------------------------------------------------------------

def test_scan_report_only_leptons_fit():
    """Aggregate report: only the lepton triplet fits b = sqrt(2)
    (out of all tested fragments)."""
    report = fss.generate_scan_report()
    assert report.n_fits == 1   # only the (e, mu, tau) triplet
    assert report.n_rejects > 10  # many rejects across mesons/baryons/gauge


def test_scan_report_lepton_in_fits():
    """Confirm the one fit is (e, mu, tau)."""
    report = fss.generate_scan_report()
    fit_names = [r.name for r in report.fits]
    assert "(e, mu, tau)" in fit_names


def test_implied_b_for_mesons_is_much_smaller():
    """At all-positive branch, mesons would require b ~ 0.4-0.5
    (NOT sqrt(2) = 1.41)."""
    results = fss.run_full_scan()
    ps_results = [r for r in results if r.family == "pseudoscalar_mesons"
                  and r.implied_b_at_all_positive is not None]
    for r in ps_results:
        assert r.implied_b_at_all_positive < 1.0  # well below sqrt(2)


def test_implied_b_for_baryons_is_tiny():
    """At all-positive branch, baryons would require b ~ 0.1
    (much smaller than leptons)."""
    results = fss.run_full_scan()
    b_results = [r for r in results if r.family == "light_baryons"
                 and r.implied_b_at_all_positive is not None]
    for r in b_results:
        assert r.implied_b_at_all_positive < 0.3
