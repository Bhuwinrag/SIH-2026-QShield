from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class QDSSession(Base):
    __tablename__ = "qds_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    signer_id = Column(String, nullable=False)
    verifier_id = Column(String, nullable=False)
    message_digest = Column(String, nullable=False)
    session_nonce = Column(String, nullable=False)
    
    # Artifact Metadata
    artifact_name = Column(String, nullable=True)
    artifact_size = Column(Integer, nullable=True)
    artifact_type = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    experiments = relationship("Experiment", back_populates="session", cascade="all, delete-orphan")

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("qds_sessions.id"))
    status = Column(String, default="CREATED")  # CREATED, RUNNING, COMPLETED, FAILED
    random_seed = Column(Integer, nullable=True)
    shots = Column(Integer, default=1000)
    noise_enabled = Column(Boolean, default=False)
    attack_type = Column(String, default="NORMAL") # NORMAL, FORGERY, IMPERSONATION, REPLAY, CHANNEL_MANIPULATION, NOISE_ONLY
    attack_strength = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)
    
    session = relationship("QDSSession", back_populates="experiments")
    quantum_run = relationship("QuantumRun", uselist=False, back_populates="experiment", cascade="all, delete-orphan")
    threat_event = relationship("ThreatEvent", uselist=False, back_populates="experiment", cascade="all, delete-orphan")
    security_evidence = relationship("SecurityEvidence", uselist=False, back_populates="experiment", cascade="all, delete-orphan")

class QuantumRun(Base):
    __tablename__ = "quantum_runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    execution_time_ms = Column(Float, nullable=True)
    
    # Store full JSON representation of QMF instead of flattening everything
    qmf_observed = Column(JSON, nullable=True)
    qmf_baseline = Column(JSON, nullable=True)
    
    experiment = relationship("Experiment", back_populates="quantum_run")

class ThreatEvent(Base):
    __tablename__ = "threat_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    threat_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    decision = Column(String, nullable=False) # ACCEPT / REJECT
    reason = Column(String, nullable=False)
    evidence_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    
    experiment = relationship("Experiment", back_populates="threat_event")

class SecurityEvidence(Base):
    __tablename__ = "security_evidence"
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    
    # Legacy fields mapping logic if necessary, but we can store SEV as JSON too
    basis_deviation = Column(Float, nullable=True)
    fidelity_deviation = Column(Float, nullable=True)
    correlation_deviation = Column(Float, nullable=True)
    replay_indicator = Column(Boolean, default=False)
    identity_consistency = Column(Boolean, default=True)
    freshness_status = Column(Boolean, default=True)
    
    statistical_significance = Column(Float, nullable=True) 
    bound_threshold = Column(Float, nullable=True)
    
    experiment = relationship("Experiment", back_populates="security_evidence")

