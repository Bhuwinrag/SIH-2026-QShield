# Q-SHIELD Reproducibility Guide

To reproduce the scientific findings and statistical bounds of Q-SHIELD's threat detection mechanism:

## 1. Environment Setup
The simulation relies on exact numerical execution in Qiskit.
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

**Tested Versions**:
- Python: 3.13.x
- Qiskit: 1.x
- Qiskit-Aer: 0.14.x

## 2. Running the Benchmark Suite
The primary experimental validation is generated using the automated benchmark runner. This runner simulates 1800 independent quantum teleportation sessions across different noise levels and attack models.

```bash
cd backend
$env:PYTHONPATH="."
python -m app.services.research.benchmark
```

## 3. Seed Determinism
Every quantum execution in Q-SHIELD natively accepts a `seed` parameter passed directly to `AerSimulator.set_options(seed_simulator=seed)`.
When the same `seed` is provided alongside the same `attack_strength` and `base_noise_level`, the entire QMF and statistical output will be identically reproduced up to floating-point representation.

## 4. Evidence Replay
In the frontend UI, selecting an Experiment ID will query the backend. If you wish to manually replay a session outside the UI, use the `/experiments/{id}/run` API. If the `random_seed` was recorded in the database, the experiment execution is fully deterministic.
