import pytest
from app.services.security.threat_attribution import ThreatAttributionEngine

def test_normal():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {},
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    
    res = engine.attribute_threat(qmf, is_rejected=False, anomalies=[])
    assert res["threat_type"] == "NORMAL"
    assert res["decision"] == "ACCEPT"

def test_replay_attack():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {},
        "freshness": {"fresh": False},
        "identity": {"consistent": True}
    }
    
    res = engine.attribute_threat(qmf, is_rejected=False, anomalies=[])
    assert res["threat_type"] == "REPLAY"
    assert res["decision"] == "REJECT"

def test_impersonation_attack():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {},
        "freshness": {"fresh": True},
        "identity": {"consistent": False}
    }
    
    res = engine.attribute_threat(qmf, is_rejected=False, anomalies=[])
    assert res["threat_type"] == "IMPERSONATION"
    assert res["decision"] == "REJECT"

def test_forgery_attack():
    engine = ThreatAttributionEngine()
    qmf = {
        "basis": {
            "X": {"tv_distance": 0.5}
        },
        "bell": {"C_XX": 0.95, "C_ZZ": 0.96}, # Bell correlation is good
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    
    res = engine.attribute_threat(qmf, is_rejected=True, anomalies=["X"])
    assert res["threat_type"] == "FORGERY"

def test_channel_manipulation():
    engine = ThreatAttributionEngine()
    qmf = {
        "bell": {"C_XX": 0.60, "C_ZZ": 0.55}, # Heavy channel degradation
        "fidelity": 0.65,
        "freshness": {"fresh": True},
        "identity": {"consistent": True}
    }
    
    res = engine.attribute_threat(qmf, is_rejected=True, anomalies=["X", "Y", "Z"])
    assert res["threat_type"] == "CHANNEL_MANIPULATION"
