# Scientific Limitations of Q-SHIELD

Q-SHIELD successfully validates quantum digital signature (QDS) operations against noise using rigorous statistical bounds. However, as a research prototype, it possesses specific scientific limitations that must be acknowledged.

## 1. Simulation vs Hardware Reality
- **Limitation**: This is a simulation-based prototype running on `Qiskit AerSimulator` using ideal statevectors with parameterized Pauli/depolarizing noise.
- **Implication**: Real superconducting or photonic hardware exhibits complex error dynamics (e.g., crosstalk, amplitude damping, asymmetric read-out errors) that may not be perfectly bounded by a simplified Hoeffding envelope based solely on independent binary outcome assumptions.

## 2. Impersonation & Identity Cryptography
- **Limitation**: Q-SHIELD integrates an "identity consistency" check (simulating classical cryptographic mismatch).
- **Implication**: Quantum measurements alone *cannot* reveal the real-world identity of the signer. Identity/impersonation detection strictly requires protocol-level context matching, and the attribution engine relies on this external classical channel.

## 3. Replay & Freshness
- **Limitation**: Like impersonation, replay detection requires classical freshness nonces or timestamps.
- **Implication**: A perfectly valid quantum state can be a replay attack. The statistical bounds (Hoeffding/TV) will legitimately classify the state as "NORMAL", requiring the classical context engine to flag the reuse.

## 4. Finite Sample Detection
- **Limitation**: Statistical detection is governed by finite-sample probability bounds ($\delta$).
- **Implication**: There is always a non-zero probability of False Positives (rejecting legitimate noise) and False Negatives (accepting an attack). Q-SHIELD does not claim *information-theoretic security* in its finite-shot operation, but rather configurable statistical confidence ($1-\delta$).

## 5. Attack Indistinguishability
- **Limitation**: Depending on the available observables, two different attacks may produce overlapping Quantum Measurement Fingerprints (QMFs).
- **Implication**: A highly sophisticated intercept-resend attack carefully tuned to mimic expected depolarizing channel noise might require complex multi-qubit tomography to detect, which exceeds the simple 3-basis projective measurement implemented.
