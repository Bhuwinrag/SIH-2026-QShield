import json
from app.services.experiments.runner import run_experiment_pipeline

def test_attack(attack_type: str, noise: float = 0.0):
    print(f"\n--- TARGETED EXPERIMENT: {attack_type} (Noise {noise}) ---")
    res = run_experiment_pipeline(
        seed=42,
        shots=1000,
        attack_type=attack_type,
        attack_strength=0.1,
        noise_enabled=True if noise > 0 else False,
        base_noise_level=noise
    )
    
    q_run = res["quantum_run"]
    attr = res["attribution"]
    qmf_obs = res["qmf_observed"]
    
    print(f"TV-X: {q_run['x_error_rate']:.4f}")
    print(f"TV-Y: {q_run['y_error_rate']:.4f}")
    print(f"TV-Z: {q_run['z_error_rate']:.4f}")
    print(f"Fidelity: {q_run['fidelity']:.4f}")
    print(f"CXX: {qmf_obs['bell']['C_XX']:.4f}")
    print(f"CZZ: {qmf_obs['bell']['C_ZZ']:.4f}")
    # Extract hoeffding radius from one of the basis evals
    try:
        rad = qmf_obs["basis"]["X"]["confidence_radius"]
        print(f"Hoeffding radius: {rad:.4f}")
    except:
        pass
        
    is_rejected = qmf_obs["basis"].get("X", {}).get("significant", False) or \
                  qmf_obs["basis"].get("Y", {}).get("significant", False) or \
                  qmf_obs["basis"].get("Z", {}).get("significant", False)
                  
    print(f"H0 decision (is_rejected): {is_rejected}")
    print(f"Final attribution: {attr['threat_type']} ({attr['decision']})")

if __name__ == "__main__":
    test_attack("NORMAL", 0.0)
    test_attack("FORGERY", 0.0)
    test_attack("IMPERSONATION", 0.0)
    test_attack("REPLAY", 0.0)
    test_attack("CHANNEL_MANIPULATION", 0.0)
    # Test normal with noise
    for n in [0.01, 0.02, 0.03, 0.05, 0.10]:
        test_attack("NORMAL", n)
