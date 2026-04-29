"""Canonical atlas tests (HYPOTHESIS Step 29)."""

from dinos import foot_canonical_atlas as fca


def test_atlas_has_19_entries():
    """Final confirmed atlas: 19 metallic Foot resonances."""
    assert len(fca.CANONICAL_ATLAS) == 19


def test_sector_grouping():
    """Sectors: lepton (2), light_hadron, heavy_quark, gauge."""
    sectors = fca.by_sector()
    assert "lepton" in sectors
    assert "light_hadron" in sectors
    assert "heavy_quark" in sectors
    assert "gauge" in sectors
    assert len(sectors["lepton"]) == 2  # charged + neutrino


def test_metallic_factor_distribution_makes_sense():
    """Most expressions use 1-2 metallic factors, some use 3."""
    dist = fca.metallic_factor_distribution()
    assert dist.get(1, 0) >= 4   # singletons
    assert dist.get(2, 0) >= 8   # pairs (most common)
    assert dist.get(3, 0) >= 1   # at least one with 3


def test_each_entry_has_metallic_b_expression():
    """Every entry uses one of: silver, bronze, copper, plastic,
    supergolden, nickel, golden."""
    metallic_names = ["silver", "bronze", "copper", "plastic",
                       "supergolden", "nickel", "golden"]
    for e in fca.CANONICAL_ATLAS:
        # Check at least one metallic appears in the expression
        assert any(m in e.b_expression for m in metallic_names), e


def test_lepton_and_neutrino_share_b():
    """Charged leptons and neutrinos both at silver - 1."""
    leptons = [e for e in fca.CANONICAL_ATLAS if e.sector == "lepton"]
    assert len(leptons) == 2
    for e in leptons:
        assert "silver" in e.b_expression
