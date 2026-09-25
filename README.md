# Q-SHIELD: Quantum Signature Security & Threat Intelligence Engine

## What Q-SHIELD is
Q-SHIELD is a deterministic, information-theoretic security observatory designed to verify teleportation-based Quantum Digital Signatures (QDS) and perform Threat Attribution without relying on AI or ML heuristics.

## Problem
Standard digital signatures fail when exposed to Shor's algorithm. Quantum Digital Signatures (QDS) solve this using physical entanglement, but ambient channel noise makes detecting intercept-resend attacks computationally ambiguous. Existing systems only answer "did it fail?", not "why did it fail?".

## Architecture
- **Frontend**: React + Vite + Three.js for simulated quantum state tracking and evidence playback.
- **Backend Core**: FastAPI orchestrating experimental sessions.
- **Quantum Model**: Qiskit AerSimulator (Statevector) performing actual Bell-state generation, Pauli corrections, and projective measurements.
- **Threat Model**: Two-stage attribution matrix (Stage 1: Hoeffding H0 Rejection | Stage 2: Distance-based Hypothesis Attribution).
- **Worker**: Celery + Redis for asynchronous intensive density-matrix computations.
- **Persistence**: PostgreSQL for structured evidence logging.

## Statistical Model
The engine leverages Hoeffding bounds ($\epsilon = \sqrt{\frac{\ln(2/\alpha)}{2n}}$) to construct a dynamic confidence envelope around the baseline Total Variation (TV) distances of X, Y, and Z basis measurements. Deviations outside this radius mathematically guarantee (with probability $1 - \alpha$) the presence of a non-environmental disturbance.

## How to Run
1. Start PostgreSQL and Redis natively.
2. Terminal 1: `.\run_backend.bat`
3. Terminal 2: `.\run_frontend.bat`
4. Open `http://localhost:5173`

## How to Reproduce
Run `python -m app.services.research.benchmark` to execute the exhaustive simulation matrix (shots x noise x attack). This will populate `backend/research` with raw CSV metrics and dynamic matplotlib charts mapping detection capabilities.

## Known Limitations
Simulation-based validation is limited by classical memory. Q-SHIELD currently caps statevector simulations at 3-qubits. Real-world implementations will require integrating directly with IBM Quantum or equivalent hardware via Qiskit Runtime.
