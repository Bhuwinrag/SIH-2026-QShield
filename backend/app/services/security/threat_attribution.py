from typing import Dict, Any, List

class ThreatAttributionEngine:
    def __init__(self):
        pass

    def attribute_threat(self, qmf: Dict[str, Any], is_rejected: bool, anomalies: List[str]) -> Dict[str, Any]:
        """
        STAGE 1: Evaluate Legitimate Baseline H0.
        If is_rejected is False, return NORMAL.
        
        STAGE 2: If H0 is rejected, determine which attack hypothesis best explains the QMF evidence.
        """
        freshness = qmf.get("freshness", {}).get("fresh", True)
        identity = qmf.get("identity", {}).get("consistent", True)
        
        # Attack Evidence Extraction
        tv_x = qmf.get("basis", {}).get("X", {}).get("tv_distance", 0.0)
        tv_y = qmf.get("basis", {}).get("Y", {}).get("tv_distance", 0.0)
        tv_z = qmf.get("basis", {}).get("Z", {}).get("tv_distance", 0.0)
        
        fidelity = qmf.get("fidelity", 1.0)
        c_xx = qmf.get("bell", {}).get("C_XX", 1.0)
        c_zz = qmf.get("bell", {}).get("C_ZZ", 1.0)
        
        # Hypothesis Testing Logic (Deterministic Rules based on explicit bounds)
        
        if not freshness:
            # Replay attack context match. Quantum measurements may be perfectly valid.
            return self._build_sev("REPLAY", "CRITICAL", "Session nonce/timestamp reused. Freshness validation failed.", qmf)
            
        if not identity:
            # Impersonation context match.
            return self._build_sev("IMPERSONATION", "CRITICAL", "Signer identity context mismatch.", qmf)
            
        if is_rejected:
            # Enforce the Critical Invariant: If H0 is rejected, the system MUST NOT return NORMAL.
            # Differentiate Channel Manipulation vs Forgery.
            # Channel Manipulation physically degrades entanglement. Bell correlation < 0.85 is a strong indicator of channel disruption.
            if c_xx < 0.85 or c_zz < 0.85:
                return self._build_sev(
                    "CHANNEL_MANIPULATION", 
                    "HIGH", 
                    "Significant degradation in Bell correlation indicative of channel disturbance or intercept-resend.", 
                    qmf
                )
            # Forgery usually attacks a specific encoded state/basis resulting in high TV distance in one or more bases
            # without necessarily destroying underlying channel entanglement.
            elif len(anomalies) > 0 and (tv_x > 0.1 or tv_y > 0.1 or tv_z > 0.1):
                return self._build_sev(
                    "FORGERY", 
                    "CRITICAL", 
                    f"Measurement statistics deviate from expected baseline. Anomalies in bases: {', '.join(anomalies)}.", 
                    qmf
                )
            else:
                # Catch-all to preserve invariant
                return self._build_sev(
                    "ANOMALY_UNATTRIBUTED", 
                    "MEDIUM", 
                    "Statistically significant anomaly detected, but attribution uncertain.", 
                    qmf
                )
                
        # STAGE 1: H0 was not rejected.
        return self._build_sev("NORMAL", "NONE", "No threat detected. Protocol execution nominal within statistical bounds.", qmf)
        
    def _build_sev(self, threat_type: str, severity: str, reason: str, qmf: Dict[str, Any]) -> Dict[str, Any]:
        
        # Build the hypothesis evidence table essentially
        tv_max = max(
            qmf.get("basis", {}).get("X", {}).get("tv_distance", 0.0),
            qmf.get("basis", {}).get("Y", {}).get("tv_distance", 0.0),
            qmf.get("basis", {}).get("Z", {}).get("tv_distance", 0.0)
        )
        
        return {
            "threat_type": threat_type,
            "severity": severity,
            "decision": "REJECT" if threat_type != "NORMAL" else "ACCEPT",
            "reason": reason,
            "evidence_summary": {
                "max_tv_distance": tv_max,
                "fidelity": qmf.get("fidelity", 1.0),
                "c_xx": qmf.get("bell", {}).get("C_XX", 1.0),
                "c_zz": qmf.get("bell", {}).get("C_ZZ", 1.0),
                "freshness": qmf.get("freshness", {}).get("fresh", True),
                "identity": qmf.get("identity", {}).get("consistent", True)
            }
        }
