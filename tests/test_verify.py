"""Run the SymPy verification suite."""

from dinos import verify


def test_geodesic_to_dirac():
    assert verify.verify_geodesic_to_dirac()


def test_derrick_virial():
    assert verify.verify_derrick_virial()


def test_mass_closure():
    assert verify.verify_mass_closure()


def test_joint_closure():
    assert verify.verify_joint_closure()


def test_bulk_boundary_duality():
    assert verify.verify_bulk_boundary_duality()


def test_run_all_passes():
    results = verify.run_all()
    assert all(ok for _, ok in results), results
