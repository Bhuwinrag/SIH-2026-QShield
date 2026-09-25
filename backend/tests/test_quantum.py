import pytest
from app.services.quantum.simulator import QuantumSimulation
from qiskit.quantum_info import Statevector

def test_teleport_zero():
    sim = QuantumSimulation(shots=1000)
    res = sim.simulate_comprehensive("0")
    
    assert res["fidelity"] > 0.99
    
    z_basis_counts = res["bases"]["Z"]["parsed_counts"]
    # Should be almost 100% "0"
    assert z_basis_counts.get("0", 0) > 950
    assert z_basis_counts.get("1", 0) < 50
    
def test_teleport_plus():
    sim = QuantumSimulation(shots=1000)
    res = sim.simulate_comprehensive("+")
    
    assert res["fidelity"] > 0.99
    
    # In X basis, it should measure 0 almost 100%
    x_basis_counts = res["bases"]["X"]["parsed_counts"]
    assert x_basis_counts.get("0", 0) > 950
    
    # In Z basis, it should be 50/50
    z_basis_counts = res["bases"]["Z"]["parsed_counts"]
    assert 400 < z_basis_counts.get("0", 0) < 600

def test_pauli_error_degradation():
    sim_clean = QuantumSimulation(shots=1000)
    sim_noisy = QuantumSimulation(shots=1000)
    
    res_clean = sim_clean.simulate_comprehensive("0")
    res_noisy = sim_noisy.simulate_comprehensive("0", noise_level=0.1, noise_type="bit_flip")
    
    assert res_clean["fidelity"] > res_noisy["fidelity"]
    assert res_noisy["fidelity"] < 0.98

def test_bell_correlation():
    sim = QuantumSimulation(shots=1000)
    res = sim.simulate_comprehensive("+")
    
    # Clean channel should have near perfect correlation
    assert res["bell_correlations"]["C_ZZ"] > 0.95
    assert res["bell_correlations"]["C_XX"] > 0.95
