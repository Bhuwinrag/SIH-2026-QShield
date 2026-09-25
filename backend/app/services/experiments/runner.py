import time
from typing import Dict, Any
from app.services.quantum.simulator import QuantumSimulation
from app.services.security.statistics import StatisticalSecurityEngine
from app.services.security.threat_attribution import ThreatAttributionEngine

def run_experiment_pipeline(
    seed: int,
    shots: int,
    attack_type: str,
    attack_strength: float,
    noise_enabled: bool,
    base_noise_level: float = 0.02
) -> Dict[str, Any]:
    """
    Executes the full QDS experiment pipeline.
    """
    start_time = time.time()
    
    # 1. Setup Attack Modifiers
    noise_level = base_noise_level if noise_enabled else 0.0
    is_fresh = True
    identity_match = True
    
    # The expected state Alice is teleporting
    legitimate_state = "+"
    
    # The actual state Alice teleports (might be altered by Forgery)
    actual_state_to_teleport = legitimate_state
    
    # Channel error models
    noise_type = "depolarizing"
    
    if attack_type == "REPLAY":
        is_fresh = False
    elif attack_type == "IMPERSONATION":
        identity_match = False
    elif attack_type == "CHANNEL_MANIPULATION":
        # Attacker introduces severe physical disturbance in the channel (intercept-resend or heavy depolarizing)
        noise_level = min(1.0, noise_level + attack_strength)
    elif attack_type == "FORGERY":
        # Attacker sends the wrong quantum state to forge the signature
        # Instead of |+> they send |0> or |1>
        actual_state_to_teleport = "1"
    elif attack_type == "NOISE_ONLY":
        # Elevated noise but not necessarily an attack.
        noise_level = min(0.15, noise_level + (attack_strength * 0.5))

    # 2. Quantum Simulation
    q_sim = QuantumSimulation(seed=seed, shots=shots)
    
    # Run the actual comprehensive simulation (evaluating X, Y, Z bases and calculating density matrix fidelity)
    sim_result = q_sim.simulate_comprehensive(
        state_to_teleport=actual_state_to_teleport,
        noise_level=noise_level,
        noise_type=noise_type
    )
    
    # 3. Construct the Legitimate Baseline
    # We must construct what the QMF *should* look like under the Legitimate State with Base Noise.
    # We run a quiet reference simulation to extract the baseline expected distributions.
    q_sim_baseline = QuantumSimulation(seed=seed, shots=shots)
    baseline_result = q_sim_baseline.simulate_comprehensive(
        state_to_teleport=legitimate_state,
        noise_level=base_noise_level,
        noise_type="depolarizing"
    )

    # 4. Construct QMF
    qmf_observed = {
        "bloch": {
            "rx": sim_result["bases"]["X"]["expectation"],
            "ry": sim_result["bases"]["Y"]["expectation"],
            "rz": sim_result["bases"]["Z"]["expectation"]
        },
        "fidelity": sim_result["fidelity"],
        "basis": {
            "X": {
                "observed_distribution": sim_result["bases"]["X"]["observed_distribution"],
            },
            "Y": {
                "observed_distribution": sim_result["bases"]["Y"]["observed_distribution"],
            },
            "Z": {
                "observed_distribution": sim_result["bases"]["Z"]["observed_distribution"],
            }
        },
        "bell": sim_result["bell_correlations"],
        "channel": {"loss": 0.0}, # Placeholder, not implemented in Qiskit directly here
        "freshness": {"fresh": is_fresh},
        "identity": {"consistent": identity_match}
    }
    
    qmf_baseline = {
        "bloch": {
            "rx": baseline_result["bases"]["X"]["expectation"],
            "ry": baseline_result["bases"]["Y"]["expectation"],
            "rz": baseline_result["bases"]["Z"]["expectation"]
        },
        "fidelity": baseline_result["fidelity"],
        "basis": {
            "X": {
                "baseline_distribution": baseline_result["bases"]["X"]["observed_distribution"]
            },
            "Y": {
                "baseline_distribution": baseline_result["bases"]["Y"]["observed_distribution"]
            },
            "Z": {
                "baseline_distribution": baseline_result["bases"]["Z"]["observed_distribution"]
            }
        },
        "bell": baseline_result["bell_correlations"]
    }

    # 5. Statistical Analysis
    stats_engine = StatisticalSecurityEngine(alpha_total=0.01)
    qmf_eval = stats_engine.evaluate_qmf(qmf_observed, qmf_baseline, shots)
    
    # Merge statistical evaluations into the QMF
    for basis, eval_res in qmf_eval["basis_evaluations"].items():
        qmf_observed["basis"][basis].update(eval_res)

    # 6. Threat Attribution
    threat_engine = ThreatAttributionEngine()
    attribution = threat_engine.attribute_threat(
        qmf=qmf_observed, 
        is_rejected=qmf_eval["is_rejected"], 
        anomalies=qmf_eval["anomalies"]
    )

    execution_time = (time.time() - start_time) * 1000 # ms
    
    return {
        "quantum_run": {
            "execution_time_ms": execution_time,
            "fidelity": qmf_observed["fidelity"],
            "bell_correlation": qmf_observed["bell"]["C_ZZ"],  # Legacy mapping for schema
            "channel_disturbance": noise_level,
            "x_error_rate": qmf_observed["basis"]["X"]["tv_distance"], # Mapped to TV for legacy schema compatibility
            "y_error_rate": qmf_observed["basis"]["Y"]["tv_distance"],
            "z_error_rate": qmf_observed["basis"]["Z"]["tv_distance"],
            "measurement_stats": sim_result["bases"]["Z"]["raw_counts"]
        },
        "attribution": attribution,
        "qmf_observed": qmf_observed,
        "qmf_baseline": qmf_baseline
    }
