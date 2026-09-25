import traceback
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.domain import Experiment, QuantumRun, ThreatEvent, SecurityEvidence
from app.services.experiments.runner import run_experiment_pipeline
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def run_experiment_task(self, experiment_id: str):
    db = SessionLocal()
    try:
        exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not exp:
            logger.error(f"Experiment {experiment_id} not found.")
            return

        exp.status = "RUNNING"
        db.commit()

        # Run pipeline
        results = run_experiment_pipeline(
            seed=exp.random_seed,
            shots=exp.shots,
            attack_type=exp.attack_type,
            attack_strength=exp.attack_strength,
            noise_enabled=exp.noise_enabled
        )

        q_run_data = results["quantum_run"]
        attr_data = results["attribution"]
        qmf_observed = results["qmf_observed"]
        qmf_baseline = results["qmf_baseline"]

        # Persist QuantumRun
        qr = QuantumRun(
            experiment_id=exp.id,
            execution_time_ms=q_run_data["execution_time_ms"],
            qmf_observed=qmf_observed,
            qmf_baseline=qmf_baseline
        )
        db.add(qr)

        # Persist ThreatEvent
        te = ThreatEvent(
            experiment_id=exp.id,
            threat_type=attr_data["threat_type"],
            severity=attr_data["severity"],
            decision=attr_data["decision"],
            reason=attr_data["reason"],
            evidence_summary=attr_data.get("evidence_summary", {})
        )
        db.add(te)

        # Persist SecurityEvidence
        # This table maps the mathematical evidence vector
        se = SecurityEvidence(
            experiment_id=exp.id,
            basis_deviation=attr_data.get("evidence_summary", {}).get("max_tv_distance", 0.0),
            fidelity_deviation=attr_data.get("evidence_summary", {}).get("fidelity", 1.0), 
            correlation_deviation=attr_data.get("evidence_summary", {}).get("c_xx", 1.0), 
            replay_indicator=True if exp.attack_type == "REPLAY" else False,
            identity_consistency=False if exp.attack_type == "IMPERSONATION" else True,
            freshness_status=False if exp.attack_type == "REPLAY" else True,
            statistical_significance=attr_data.get("evidence_summary", {}).get("max_tv_distance", 0.0),
            bound_threshold=0.0 # Bounding is handled internally inside QMF evaluations now
        )
        db.add(se)

        exp.status = "COMPLETED"
        db.commit()

    except Exception as e:
        logger.error(f"Task failed: {traceback.format_exc()}")
        exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if exp:
            exp.status = "FAILED"
            db.commit()
    finally:
        db.close()
