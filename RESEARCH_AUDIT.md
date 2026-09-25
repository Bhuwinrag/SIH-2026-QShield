# RESEARCH AUDIT: Q-SHIELD

## 1. Existing Implementation Overview
The current Q-SHIELD prototype is functionally connected end-to-end but uses a heuristic-driven simulation model rather than rigorous quantum measurement statistics. It features a FastAPI backend orchestrating Qiskit's `AerSimulator` via Celery, and a React Three Fiber frontend.

## 2. Scientific & Mathematical Assumptions
- **Teleportation Convention**: The code uses `qc.cx(0,1)` then `qc.h(0)`, measuring `q[0]` to `crz` and `q[1]` to `crx`. Bob applies `X` based on `crx` and `Z` based on `crz`. This is structurally standard, but the measurement bit ordering requires explicit documentation.
- **Statistics**: Hoeffding's inequality is correctly defined mathematically as `sqrt(-ln(alpha/2) / (2n))`, but it is applied to heuristic values rather than actual binary distributions from the simulator.
- **Current QMF Definition**: Currently defined loosely as a dictionary of `x_error_rate`, `fidelity`, `bell_correlation`, etc.

## 3. Potential Bugs
- **Qiskit Bit Ordering**: Qiskit returns bitstrings in Little Endian order relative to the classical registers (e.g., `cr2 cr1 cr0`). The current parsing logic (`key.split()`) depends strictly on how registers were appended.
- **Single Basis Execution**: The simulator runs in one basis at a time (`Z`, `X`, or `Y`), but the pipeline derives error rates for all three simultaneously using heuristics (`error_rate if basis == "X" else 0.01`).

## 4. Arbitrary Thresholds Found
- `runner.py` defines `bell_correlation: 1.0 - (noise_level * 1.5)` (Heuristic).
- `runner.py` defines `base_noise_level = 0.02`.
- `threat_attribution.py` makes deterministic choices based on boolean combinations of these heuristic thresholds, rather than formal statistical evidence vectors.

## 5. Missing Validations & Tests
- **No Unit Tests**: There are zero `pytest` suites implemented for the quantum correctness, statistical formulas, or attack engines.
- **Missing QMF Vectors**: Total Variation Distance, empirical KL-divergence, and explicit Pauli expectations (Bloch vectors) are not currently calculated.
- **No Legitimate Baseline Calibration**: The system compares observations to an idealized zero-noise state plus a hardcoded `base_noise_level = 0.02`, instead of learning a noise envelope from benchmark runs.

## 6. Security-Model Limitations
- **Fake Attack Transformations**: The current "Channel Manipulation" attack just artificially inflates the `noise_level` parameter rather than introducing a true quantum channel disturbance (e.g., intercept-resend or depolarizing channel insertion on the Bell pair).
- **Identity/Context constraints**: Impersonation sets a boolean flag rather than demonstrating the cryptography binding gap.

## 7. Recommended Corrections
1. **Remove Heuristics**: Rip out all hardcoded noise multiplication. All error rates and correlations must be derived strictly from `counts` returned by Qiskit.
2. **Formalize QMF**: Define the QMF as a strict vector `[r_x, r_y, r_z, F, D_TV_X, D_TV_Y, D_TV_Z, E_X, E_Y, E_Z, L, R]`.
3. **Formal Baseline Calibration**: Implement a setup phase that runs legitimate noise configurations to derive the expected distribution vectors before any attack is tested.
4. **Implement Real Threat Vectors**: 
   - *Forgery*: Alter the encoded state prior to signature verification.
   - *Impersonation*: Mismatch the identity metadata while maintaining a valid state.
   - *Replay*: Violate the freshness nonce.
   - *Channel Manipulation*: Introduce physical Pauli errors into the Bell pair distribution channel.
5. **Implement Statistical Engine**: Strictly apply Hoeffding bounds, Total Variation Distance, and empirical KL-divergence to the binary measurement outcomes.
6. **Automated Benchmarking**: Build the CLI runner to execute the required experiment matrix (Phases 11-18) and output `research_results.csv`.
