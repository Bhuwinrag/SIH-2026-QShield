import pytest
import math
from app.services.security.statistics import StatisticalSecurityEngine

def test_hoeffding_radius():
    engine = StatisticalSecurityEngine(alpha_total=0.01)
    r = engine.hoeffding_radius(10000)
    
    # alpha_basis = 0.01 / 3
    expected_r = math.sqrt(math.log(2.0 / (0.01 / 3)) / 20000)
    assert abs(r - expected_r) < 1e-6

def test_total_variation_distance():
    engine = StatisticalSecurityEngine()
    obs = {"0": 0.6, "1": 0.4}
    base = {"0": 0.5, "1": 0.5}
    tv = engine.total_variation_distance(obs, base)
    assert abs(tv - 0.1) < 1e-6

def test_kl_divergence():
    engine = StatisticalSecurityEngine()
    obs = {"0": 0.6, "1": 0.4}
    base = {"0": 0.5, "1": 0.5}
    kl = engine.empirical_kl_divergence(obs, base)
    # Expected: 0.6 * ln(0.6/0.5) + 0.4 * ln(0.4/0.5)
    expected_kl = 0.6 * math.log(1.2) + 0.4 * math.log(0.8)
    assert abs(kl - expected_kl) < 1e-6

def test_evaluate_basis_significant():
    engine = StatisticalSecurityEngine(alpha_total=0.01)
    obs = {"0": 0.8, "1": 0.2}
    base = {"0": 0.5, "1": 0.5}
    
    res = engine.evaluate_basis(obs, base, n=10000)
    
    assert abs(res["tv_distance"] - 0.3) < 1e-6
    # Hoeffding radius for n=10000 is ~0.017
    assert res["significant"] is True
    
def test_evaluate_basis_not_significant():
    engine = StatisticalSecurityEngine(alpha_total=0.01)
    obs = {"0": 0.505, "1": 0.495}
    base = {"0": 0.5, "1": 0.5}
    
    res = engine.evaluate_basis(obs, base, n=10000)
    
    assert res["significant"] is False
