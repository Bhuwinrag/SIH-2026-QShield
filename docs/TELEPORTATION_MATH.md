# Quantum Teleportation Mathematical Formalism

This document derives the exact teleportation protocol implemented in Q-SHIELD's Qiskit simulator, mapping the quantum operations to the specific qubit and classical bit ordering used in the codebase.

## 1. Input State Representation
The initial target state to be teleported is represented as a general single-qubit pure state on `q[0]`:
$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$
where $|\alpha|^2 + |\beta|^2 = 1$.

Supported initial states include:
- $|0\rangle$
- $|1\rangle$
- $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
- $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$

## 2. Qubit and Register Convention
The simulator initializes a 3-qubit quantum register `qr = q[0], q[1], q[2]`.
- **`q[0]`**: Alice's target state $|\psi\rangle$
- **`q[1]`**: Alice's half of the Bell pair
- **`q[2]`**: Bob's half of the Bell pair

Classical registers for measurement outcomes:
- **`crz`**: Holds Alice's Z-basis measurement of `q[0]`.
- **`crx`**: Holds Alice's X-basis measurement of `q[1]`.
- **`result_cr`**: Holds Bob's final measurement outcome of `q[2]`.

In Qiskit, bitstrings are read from right to left (Little-Endian). Thus, the classical outcome key `"c_result c_rx c_rz"` corresponds to the integer $2^2 \cdot \text{result} + 2^1 \cdot crx + 2^0 \cdot crz$.

## 3. Bell Pair Generation
A maximally entangled Bell state $|\Phi^+\rangle$ is created on `q[1]` and `q[2]`:
$$|\Phi^+\rangle = \frac{1}{\sqrt{2}} (|00\rangle + |11\rangle)_{12}$$

The full initial 3-qubit state is:
$$|\Psi_0\rangle = |\psi\rangle_0 \otimes |\Phi^+\rangle_{12} = \frac{1}{\sqrt{2}} (\alpha|0\rangle + \beta|1\rangle)_0 \otimes (|00\rangle + |11\rangle)_{12}$$
$$= \frac{1}{\sqrt{2}} [ \alpha|000\rangle + \alpha|011\rangle + \beta|100\rangle + \beta|111\rangle ]$$

## 4. Alice's Operations
Alice applies a CNOT gate with `q[0]` as control and `q[1]` as target (`cx(0,1)`):
$$|\Psi_1\rangle = \frac{1}{\sqrt{2}} [ \alpha|000\rangle + \alpha|011\rangle + \beta|110\rangle + \beta|101\rangle ]$$

Alice applies a Hadamard gate on `q[0]` (`h(0)`):
$$|\Psi_2\rangle = \frac{1}{2} [ \alpha(|0\rangle+|1\rangle)|00\rangle + \alpha(|0\rangle+|1\rangle)|11\rangle + \beta(|0\rangle-|1\rangle)|10\rangle + \beta(|0\rangle-|1\rangle)|01\rangle ]$$

Grouping by the states of Alice's qubits `q[0]` and `q[1]`:
$$|\Psi_2\rangle = \frac{1}{2} [ |00\rangle_A (\alpha|0\rangle + \beta|1\rangle)_B + |01\rangle_A (\alpha|1\rangle + \beta|0\rangle)_B + |10\rangle_A (\alpha|0\rangle - \beta|1\rangle)_B + |11\rangle_A (\alpha|1\rangle - \beta|0\rangle)_B ]$$

## 5. Measurement and Bob's Correction
Alice measures `q[0]` storing it in `crz` ($a$), and `q[1]` storing it in `crx` ($b$).
After measurement, the state collapses. Bob's state `q[2]` becomes:
- If $ab = 00 \implies |\psi\rangle_{Bob} = \alpha|0\rangle + \beta|1\rangle = I|\psi\rangle$
- If $ab = 01 \implies |\psi\rangle_{Bob} = \alpha|1\rangle + \beta|0\rangle = X|\psi\rangle$
- If $ab = 10 \implies |\psi\rangle_{Bob} = \alpha|0\rangle - \beta|1\rangle = Z|\psi\rangle$
- If $ab = 11 \implies |\psi\rangle_{Bob} = \alpha|1\rangle - \beta|0\rangle = ZX|\psi\rangle$

To recover the original state, Bob applies:
- `X` gate if `crx` ($b$) is 1.
- `Z` gate if `crz` ($a$) is 1.

The ordered operation is $Z^a X^b |\psi\rangle_{Bob}$. Since the system naturally produced $X^b Z^a |\psi\rangle$ (actually $Z^a X^b |\psi\rangle$ since $Z$ applies if $a=1$ and $X$ if $b=1$), Bob applies $Z^a X^b$ to invert it (noting $X$ is self-inverse, $Z$ is self-inverse, but they anti-commute. The code applies $X$ then $Z$.
If the state is $X|\psi\rangle$, applying $X$ then $Z^0$ yields $XX|\psi\rangle = |\psi\rangle$.
If the state is $Z|\psi\rangle$, applying $X^0$ then $Z$ yields $ZZ|\psi\rangle = |\psi\rangle$.
If the state is $ZX|\psi\rangle$, applying $X$ then $Z$ yields $ZXXZ|\psi\rangle = ZZ|\psi\rangle = |\psi\rangle$.

The state on `q[2]` is now exactly $|\psi\rangle$, up to a global phase.

## 6. Projective Measurements
Bob measures `q[2]` in a selected basis:
- **Z-basis**: Measure directly.
- **X-basis**: Apply Hadamard (`h(2)`), then measure.
- **Y-basis**: Apply $S^\dagger$ (`sdg(2)`), apply Hadamard (`h(2)`), then measure.

The probability of outcome $|+\rangle_B$ or $|-\rangle_B$ (where $B \in \{X, Y, Z\}$) is empirically estimated by the binary frequencies $\hat{p}(+)$ and $\hat{p}(-)$.
