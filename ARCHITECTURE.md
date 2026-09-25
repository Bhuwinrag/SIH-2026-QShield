# Q-SHIELD Architecture

## Core Pipeline
1. **Quantum State Generation**: `simulator.py` initializes $| \Psi \rangle$ and the bipartite Bell pair $(|00\rangle + |11\rangle)/\sqrt{2}$.
2. **Teleportation**: Entanglement operations and classical bit transmission (simulated).
3. **Pauli Correction**: Application of $X$ and $Z$ gates based on classical bits.
4. **Projective Measurement**: Histograms generated from X, Y, and Z measurement bases.
5. **QMF Generation**: The Quantum Measurement Fingerprint is serialized as a JSON vector containing fidelity, Bell correlations ($C_{XX}$, $C_{ZZ}$), and TV distances.
6. **Statistical Evidence**: `statistics.py` evaluates the QMF against the Hoeffding radius.
7. **Threat Attribution**: `threat_attribution.py` uses Stage 2 logic to categorize the threat (FORGERY, REPLAY, CHANNEL_MANIPULATION, IMPERSONATION).

## Native Windows Environment
- **PostgreSQL**: Stores Sessions, Experiments, and Threat Events.
- **Redis**: Task queue broker.
- **Celery**: Background processor for heavy Qiskit workloads (using `-P solo` for Windows compatibility).
- **FastAPI**: Synchronous gateway for the frontend.
