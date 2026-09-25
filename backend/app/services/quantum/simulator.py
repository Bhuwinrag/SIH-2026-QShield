import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, depolarizing_error
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
from typing import Dict, Any

class QuantumSimulation:
    def __init__(self, seed: int = None, shots: int = 1000):
        self.seed = seed
        self.shots = shots
        self.simulator = AerSimulator(method='statevector')
        if seed is not None:
            self.simulator.set_options(seed_simulator=seed)
        
    def generate_noise_model(self, error_rate: float = 0.0, noise_type: str = "depolarizing") -> NoiseModel:
        noise_model = NoiseModel()
        if error_rate <= 0.0:
            return noise_model
            
        if noise_type == "depolarizing":
            error = depolarizing_error(error_rate, 1)
            noise_model.add_all_qubit_quantum_error(error, ['id', 'rz', 'sx', 'x'])
        elif noise_type == "bit_flip":
            error = pauli_error([('X', error_rate), ('I', 1 - error_rate)])
            noise_model.add_all_qubit_quantum_error(error, ['id', 'rz', 'sx', 'x'])
        elif noise_type == "phase_flip":
            error = pauli_error([('Z', error_rate), ('I', 1 - error_rate)])
            noise_model.add_all_qubit_quantum_error(error, ['id', 'rz', 'sx', 'x'])
            
        return noise_model

    def get_target_statevector(self, state_str: str) -> Statevector:
        qc = QuantumCircuit(1)
        if state_str == "1":
            qc.x(0)
        elif state_str == "+":
            qc.h(0)
        elif state_str == "-":
            qc.x(0)
            qc.h(0)
        return Statevector.from_instruction(qc)

    def build_teleportation_circuit(self, state_to_teleport: str = "0", basis: str = "Z") -> QuantumCircuit:
        """
        Builds a quantum teleportation circuit.
        """
        qr = QuantumRegister(3, name="q")
        crz = ClassicalRegister(1, name="crz")
        crx = ClassicalRegister(1, name="crx")
        result_cr = ClassicalRegister(1, name="result")
        
        qc = QuantumCircuit(qr, crz, crx, result_cr)
        
        # Step 0: Prepare state to teleport on q[0]
        if state_to_teleport == "1":
            qc.x(0)
        elif state_to_teleport == "+":
            qc.h(0)
        elif state_to_teleport == "-":
            qc.x(0)
            qc.h(0)
            
        qc.barrier()
        
        # Step 1: Create Bell Pair on q[1] and q[2]
        qc.h(1)
        qc.cx(1, 2)
        
        qc.barrier()
        
        # Step 2: Alice measures q[0] and q[1] in Bell basis
        qc.cx(0, 1)
        qc.h(0)
        
        qc.barrier()
        
        qc.measure(0, crz)
        qc.measure(1, crx)
        
        qc.barrier()
        
        # Step 3: Bob applies Pauli corrections to q[2]
        qc.x(2).c_if(crx, 1)
        qc.z(2).c_if(crz, 1)
        
        qc.barrier()
        
        # Save density matrix before final measurement for fidelity analysis
        qc.save_density_matrix([2], label='final_dm')
        
        # Step 4: Bob measures q[2] in the chosen basis
        if basis == "X":
            qc.h(2)
        elif basis == "Y":
            qc.sdg(2)
            qc.h(2)
            
        qc.measure(2, result_cr)
        
        return qc

    def _parse_counts(self, counts: Dict[str, int]) -> Dict[str, int]:
        # Qiskit registers: crz, crx, result_cr
        # Key format: "result_cr crx crz"
        parsed_counts = {'0': 0, '1': 0}
        for key, count in counts.items():
            bits = key.split()
            if len(bits) == 3:
                res_bit = bits[0]
                parsed_counts[res_bit] += count
        return parsed_counts
        
    def _calculate_empirical_expectation(self, counts: Dict[str, int]) -> float:
        total = sum(counts.values())
        if total == 0: return 0.0
        p_plus = counts.get('0', 0) / total
        p_minus = counts.get('1', 0) / total
        return p_plus - p_minus

    def _get_theoretical_probabilities(self, state_str: str, basis: str) -> Dict[str, float]:
        target_sv = self.get_target_statevector(state_str)
        
        if basis == "Z":
            probs = target_sv.probabilities()
        elif basis == "X":
            qc = QuantumCircuit(1)
            qc.h(0)
            probs = target_sv.evolve(qc).probabilities()
        elif basis == "Y":
            qc = QuantumCircuit(1)
            qc.sdg(0)
            qc.h(0)
            probs = target_sv.evolve(qc).probabilities()
            
        return {"0": float(probs[0]), "1": float(probs[1])}

    def simulate_comprehensive(self, state_to_teleport: str, noise_level: float = 0.0, noise_type: str = "depolarizing") -> Dict[str, Any]:
        """
        Runs the teleportation circuit across all 3 bases to construct the full Bloch vector
        and extract precise density matrix fidelity.
        """
        noise_model = self.generate_noise_model(noise_level, noise_type)
        target_sv = self.get_target_statevector(state_to_teleport)
        
        results = {}
        for basis in ["X", "Y", "Z"]:
            qc = self.build_teleportation_circuit(state_to_teleport, basis)
            transpiled_qc = transpile(qc, self.simulator)
            
            job_result = self.simulator.run(transpiled_qc, shots=self.shots, noise_model=noise_model).result()
            raw_counts = job_result.get_counts()
            parsed_counts = self._parse_counts(raw_counts)
            
            # Theoretical baseline for this basis
            expected_probs = self._get_theoretical_probabilities(state_to_teleport, basis)
            
            # Fidelity from density matrix
            try:
                final_dm = job_result.data()['final_dm']
                fidelity = state_fidelity(target_sv, final_dm)
            except Exception:
                fidelity = 0.0
                
            expectation = self._calculate_empirical_expectation(parsed_counts)
            
            total = sum(parsed_counts.values())
            obs_probs = {
                "0": parsed_counts.get("0", 0) / max(total, 1),
                "1": parsed_counts.get("1", 0) / max(total, 1)
            }
            
            results[basis] = {
                "raw_counts": raw_counts,
                "parsed_counts": parsed_counts,
                "observed_distribution": obs_probs,
                "baseline_distribution": expected_probs,
                "expectation": expectation,
                "fidelity": fidelity
            }
            
        # The fidelity is theoretically independent of measurement basis prior to collapse
        # We take the fidelity from the Z basis run as representative
        avg_fidelity = results["Z"]["fidelity"]
        
        # Calculate C_XX and C_ZZ Bell correlations using separate simulation
        bell_correlations = self._simulate_bell_correlations(noise_model)
            
        return {
            "bases": results,
            "fidelity": avg_fidelity,
            "bell_correlations": bell_correlations
        }

    def _simulate_bell_correlations(self, noise_model: NoiseModel) -> Dict[str, float]:
        """
        Simulate Bell pair generation directly to assess channel correlation C_XX and C_ZZ.
        """
        # C_ZZ
        qc_z = QuantumCircuit(2, 2)
        qc_z.h(0)
        qc_z.cx(0, 1)
        qc_z.measure([0,1], [0,1])
        
        # C_XX
        qc_x = QuantumCircuit(2, 2)
        qc_x.h(0)
        qc_x.cx(0, 1)
        qc_x.h(0)
        qc_x.h(1)
        qc_x.measure([0,1], [0,1])
        
        czz = self._run_and_calculate_correlation(qc_z, noise_model)
        cxx = self._run_and_calculate_correlation(qc_x, noise_model)
        
        return {"C_XX": cxx, "C_ZZ": czz}
        
    def _run_and_calculate_correlation(self, qc: QuantumCircuit, noise_model: NoiseModel) -> float:
        transpiled = transpile(qc, self.simulator)
        res = self.simulator.run(transpiled, shots=self.shots, noise_model=noise_model).result()
        counts = res.get_counts()
        
        n_same = counts.get("00", 0) + counts.get("11", 0)
        n_diff = counts.get("01", 0) + counts.get("10", 0)
        total = n_same + n_diff
        
        if total == 0: return 0.0
        return (n_same - n_diff) / total
