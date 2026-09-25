import pytest
from app.services.security.statistics import StatisticalSecurityEngine
from app.services.security.threat_attribution import ThreatAttributionEngine

def test_statistics_engine_reads_nested_qmf():
    engine = StatisticalSecurityEngine(alpha_total=0.01)
    # Simulate a Forgery that flips distribution from 0->1
    obs = {
        "basis": {
            "X": {"observed_distribution": {"0": 0.0, "1": 1.0}}
        }
    }
    base = {
        "basis": {
            "X": {"baseline_distribution": {"0": 1.0, "1": 0.0}}
        }
    }
    res = engine.evaluate_qmf(obs, base, n=1000)
    assert res["is_rejected"] is True
    assert "X" in res["anomalies"]
    assert res["basis_evaluations"]["X"]["tv_distance"] == 1.0

def test_attribution_invariant_anomaly_unattributed():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {
            "X": {"tv_distance": 0.05} # low tv_distance, not catching Forgery explicitly but anomaly exists
        },
        "bell": {"C_XX": 0.95, "C_ZZ": 0.95},
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    # Forcing is_rejected = True to test the invariant
    res = engine.attribute_threat(qmf, is_rejected=True, anomalies=["X"])
    assert res["threat_type"] == "ANOMALY_UNATTRIBUTED"
    assert res["decision"] == "REJECT"

def test_attribution_forgery():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {
            "X": {"tv_distance": 0.5}
        },
        "bell": {"C_XX": 0.95, "C_ZZ": 0.95},
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    res = engine.attribute_threat(qmf, is_rejected=True, anomalies=["X"])
    assert res["threat_type"] == "FORGERY"
    assert res["decision"] == "REJECT"

def test_attribution_channel_manipulation():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {
            "Z": {"tv_distance": 0.15}
        },
        "bell": {"C_XX": 0.70, "C_ZZ": 0.70},
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    res = engine.attribute_threat(qmf, is_rejected=True, anomalies=["Z"])
    assert res["threat_type"] == "CHANNEL_MANIPULATION"
    assert res["decision"] == "REJECT"

def test_attribution_normal_noise():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {
            "Z": {"tv_distance": 0.02}
        },
        "bell": {"C_XX": 0.95, "C_ZZ": 0.95},
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    res = engine.attribute_threat(qmf, is_rejected=False, anomalies=[])
    assert res["threat_type"] == "NORMAL"
    assert res["decision"] == "ACCEPT"

def test_attribution_impersonation():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {},
        "freshness": {"fresh": True},
        "identity": {"consistent": False}
    }
    res = engine.attribute_threat(qmf, is_rejected=False, anomalies=[])
    assert res["threat_type"] == "IMPERSONATION"
    assert res["decision"] == "REJECT"
