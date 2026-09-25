import os
import json
import csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from app.services.experiments.runner import run_experiment_pipeline

def run_benchmark():
    output_dir = "research"
    os.makedirs(f"{output_dir}/results", exist_ok=True)
    os.makedirs(f"{output_dir}/figures", exist_ok=True)
    os.makedirs(f"{output_dir}/reports", exist_ok=True)

    noise_levels = [0.0, 0.01, 0.02, 0.03, 0.05, 0.10]
    attacks = ["NORMAL", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL_MANIPULATION"]
    shots_list = [1000, 5000, 10000]
    seeds = list(range(42, 42 + 5)) # 5 seeds per config for speed

    results = []
    
    print("Starting Q-SHIELD Scientific Benchmark...")
    
    for shots in shots_list:
        for noise in noise_levels:
            for attack in attacks:
                for seed in seeds:
                    res = run_experiment_pipeline(
                        seed=seed,
                        shots=shots,
                        attack_type=attack,
                        attack_strength=0.1, # Arbitrary strong attack
                        noise_enabled=True,
                        base_noise_level=noise
                    )
                    
                    attr = res["attribution"]
                    q_run = res["quantum_run"]
                    
                    row = {
                        "seed": seed,
                        "shots": shots,
                        "base_noise_level": noise,
                        "true_attack": attack,
                        "predicted_threat": attr["threat_type"],
                        "is_rejected": attr["decision"] == "REJECT",
                        "fidelity": q_run["fidelity"],
                        "bell_c_zz": q_run["bell_correlation"],
                        "tv_x": q_run["x_error_rate"],
                        "tv_y": q_run["y_error_rate"],
                        "tv_z": q_run["z_error_rate"]
                    }
                    results.append(row)
                    
    df = pd.DataFrame(results)
    
    # Save raw CSV
    csv_path = f"{output_dir}/results/research_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} results to {csv_path}")
    
    # Calculate Metrics
    # True Attack -> Not NORMAL
    df["actual_positive"] = df["true_attack"] != "NORMAL"
    df["predicted_positive"] = df["is_rejected"]
    
    TP = len(df[(df["actual_positive"] == True) & (df["predicted_positive"] == True)])
    FP = len(df[(df["actual_positive"] == False) & (df["predicted_positive"] == True)])
    TN = len(df[(df["actual_positive"] == False) & (df["predicted_positive"] == False)])
    FN = len(df[(df["actual_positive"] == True) & (df["predicted_positive"] == False)])
    
    tpr = TP / (TP + FN) if (TP + FN) > 0 else 0
    fpr = FP / (FP + TN) if (FP + TN) > 0 else 0
    fnr = FN / (TP + FN) if (TP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    accuracy = (TP + TN) / (TP + TN + FP + FN) if len(df) > 0 else 0
    
    metrics = {
        "Total Experiments": len(df),
        "TP": TP, "FP": FP, "TN": TN, "FN": FN,
        "Detection Rate (TPR)": tpr,
        "False Positive Rate (FPR)": fpr,
        "False Negative Rate (FNR)": fnr,
        "Precision": precision,
        "Specificity": specificity,
        "Accuracy": accuracy
    }
    
    with open(f"{output_dir}/reports/metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
    print("\n--- GLOBAL METRICS ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    # Generate Figures
    generate_figures(df, output_dir)
    print("Benchmark completed. Results and figures generated in research/")

def generate_figures(df: pd.DataFrame, output_dir: str):
    # 1. Noise Level vs False Positive Rate
    normal_df = df[df["true_attack"] == "NORMAL"]
    fpr_by_noise = normal_df.groupby("base_noise_level")["is_rejected"].mean()
    
    plt.figure()
    fpr_by_noise.plot(kind='line', marker='o')
    plt.title("Noise Level vs False Positive Rate")
    plt.xlabel("Base Noise Level")
    plt.ylabel("False Positive Rate (FPR)")
    plt.grid(True)
    plt.savefig(f"{output_dir}/figures/fpr_vs_noise.png")
    plt.close()

    # 2. Noise Level vs Detection Rate
    attack_df = df[df["true_attack"] != "NORMAL"]
    tpr_by_noise = attack_df.groupby("base_noise_level")["is_rejected"].mean()
    
    plt.figure()
    tpr_by_noise.plot(kind='line', marker='o', color='red')
    plt.title("Noise Level vs Detection Rate")
    plt.xlabel("Base Noise Level")
    plt.ylabel("Detection Rate (TPR)")
    plt.grid(True)
    plt.savefig(f"{output_dir}/figures/tpr_vs_noise.png")
    plt.close()

    # 3. Detection Rate by Attack Type
    tpr_by_attack = attack_df.groupby("true_attack")["is_rejected"].mean()
    
    plt.figure()
    tpr_by_attack.plot(kind='bar', color=['blue', 'green', 'orange', 'purple'])
    plt.title("Detection Rate by Attack Type")
    plt.ylabel("Detection Rate (TPR)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/figures/tpr_by_attack.png")
    plt.close()
    
    # 4. Fidelity under different channel attacks
    fidelity_by_attack = df.groupby("true_attack")["fidelity"].mean()
    
    plt.figure()
    fidelity_by_attack.plot(kind='bar', color='teal')
    plt.title("Average State Fidelity by Attack Type")
    plt.ylabel("Fidelity")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/figures/fidelity_by_attack.png")
    plt.close()

if __name__ == "__main__":
    run_benchmark()
