from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class QDSSessionBase(BaseModel):
    signer_id: str
    verifier_id: str
    message_digest: str
    artifact_name: Optional[str] = None
    artifact_size: Optional[int] = None
    artifact_type: Optional[str] = None

class QDSSessionCreate(QDSSessionBase):
    pass

class QDSSessionResponse(QDSSessionBase):
    id: str
    session_nonce: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExperimentCreate(BaseModel):
    session_id: str
    shots: int = 1000
    noise_enabled: bool = True
    attack_type: str = "NORMAL"
    attack_strength: float = 0.0

class ExperimentResponse(BaseModel):
    id: str
    session_id: str
    status: str
    random_seed: Optional[int]
    shots: int
    attack_type: str
    attack_strength: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class QuantumRunResponse(BaseModel):
    id: str
    experiment_id: str
    execution_time_ms: float
    qmf_observed: Dict[str, Any]
    qmf_baseline: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class ThreatEventResponse(BaseModel):
    id: str
    threat_type: str
    severity: str
    decision: str
    reason: str
    evidence_summary: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SecurityEvidenceResponse(BaseModel):
    id: str
    basis_deviation: float
    fidelity_deviation: float
    correlation_deviation: float
    replay_indicator: bool
    identity_consistency: bool
    freshness_status: bool
    statistical_significance: float
    bound_threshold: float
    model_config = ConfigDict(from_attributes=True)

class FullExperimentResult(BaseModel):
    experiment: ExperimentResponse
    session: Optional[QDSSessionResponse] = None
    quantum_run: Optional[QuantumRunResponse] = None
    threat_event: Optional[ThreatEventResponse] = None
    security_evidence: Optional[SecurityEvidenceResponse] = None
