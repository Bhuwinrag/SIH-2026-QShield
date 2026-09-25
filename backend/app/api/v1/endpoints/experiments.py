from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Experiment, QDSSession, QuantumRun, ThreatEvent, SecurityEvidence
from app.schemas.domain import ExperimentCreate, ExperimentResponse, FullExperimentResult, QuantumRunResponse, ThreatEventResponse, SecurityEvidenceResponse
from app.workers.tasks import run_experiment_task
import random
from redis import Redis
import os

router = APIRouter()

@router.post("/", response_model=ExperimentResponse)
def create_experiment(exp_in: ExperimentCreate, db: Session = Depends(get_db)):
    session = db.query(QDSSession).filter(QDSSession.id == exp_in.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    db_exp = Experiment(
        session_id=exp_in.session_id,
        random_seed=random.randint(1, 1000000),
        shots=exp_in.shots,
        noise_enabled=exp_in.noise_enabled,
        attack_type=exp_in.attack_type,
        attack_strength=exp_in.attack_strength
    )
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.post("/{experiment_id}/run", response_model=dict)
def run_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if exp.status in ["RUNNING", "COMPLETED"]:
        raise HTTPException(status_code=400, detail="Experiment already running or completed")
        
    exp.status = "QUEUED"
    db.commit()
    
    # Check if redis is actually online to prevent delay() from hanging
    redis_online = False
    try:
        r = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=0.5)
        if r.ping():
            redis_online = True
    except Exception:
        pass

    if redis_online:
        try:
            run_experiment_task.delay(experiment_id)
            return {"status": "QUEUED", "message": "Experiment sent to background worker"}
        except Exception as e:
            redis_online = False
            
    if not redis_online:
        print("Redis unavailable -> synchronous execution fallback")
        try:
            # Execute synchronously without celery wrapper
            run_experiment_task(experiment_id)
            return {"status": "COMPLETED", "message": "Experiment executed synchronously (Redis unavailable)"}
        except Exception as sync_e:
            exp.status = "FAILED"
            db.commit()
            raise HTTPException(status_code=500, detail=str(sync_e))

@router.get("/latest", response_model=FullExperimentResult)
def get_latest_experiment(db: Session = Depends(get_db)):
    exp = db.query(Experiment).order_by(Experiment.created_at.desc()).first()
    if not exp:
        raise HTTPException(status_code=404, detail="No experiments found")
        
    return FullExperimentResult(
        experiment=exp,
        session=exp.session,
        quantum_run=exp.quantum_run,
        threat_event=exp.threat_event,
        security_evidence=exp.security_evidence
    )

@router.get("/{experiment_id}", response_model=FullExperimentResult)
def get_experiment_result(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    return FullExperimentResult(
        experiment=exp,
        session=exp.session,
        quantum_run=exp.quantum_run,
        threat_event=exp.threat_event,
        security_evidence=exp.security_evidence
    )
