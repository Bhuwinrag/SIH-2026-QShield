import math
from typing import Dict, Any, List

class StatisticalSecurityEngine:
    def __init__(self, alpha_total: float = 0.01):
        """
        alpha_total: Total family-wise significance level.
        We apply Bonferroni correction for multi-basis evaluation (X, Y, Z).
        """
        self.alpha_total = alpha_total
        self.alpha_basis = alpha_total / 3.0  # Bonferroni correction
        
    def hoeffding_radius(self, n: int) -> float:
        """
        Computes the Hoeffding radius for a binary measurement given sample size n
        and the basis-specific significance alpha_basis.
        P(|p_hat - p| >= epsilon) <= 2 * exp(-2 * n * epsilon^2)
        epsilon = sqrt(ln(2 / alpha_basis) / (2 * n))
        """
        if n == 0:
            return 1.0
        return math.sqrt(math.log(2.0 / self.alpha_basis) / (2 * n))
        
    def total_variation_distance(self, p_obs: Dict[str, float], p_base: Dict[str, float]) -> float:
        """
        Calculates Total Variation Distance between two binary distributions.
        D_TV = 1/2 sum_i |p_obs[i] - p_base[i]| = |p_obs[0] - p_base[0]|
        """
        p_o_0 = p_obs.get("0", 0.0)
        p_b_0 = p_base.get("0", 0.0)
        return abs(p_o_0 - p_b_0)

    def empirical_kl_divergence(self, p_obs: Dict[str, float], p_base: Dict[str, float]) -> float:
        """
        Calculates D_KL(P_obs || P_base) for binary distributions.
        """
        p = p_obs.get("0", 0.0)
        q = p_base.get("0", 0.0)
        
        # Clip to prevent log(0) and division by zero
        p = max(1e-9, min(1.0 - 1e-9, p))
        q = max(1e-9, min(1.0 - 1e-9, q))
        
        d_kl = p * math.log(p / q) + (1.0 - p) * math.log((1.0 - p) / (1.0 - q))
        return max(0.0, d_kl)

    def evaluate_basis(self, obs_dist: Dict[str, float], base_dist: Dict[str, float], n: int) -> Dict[str, Any]:
        """
        Evaluates a single basis measurement distribution against its baseline.
        """
        tv_dist = self.total_variation_distance(obs_dist, base_dist)
        kl_div = self.empirical_kl_divergence(obs_dist, base_dist)
        radius = self.hoeffding_radius(n)
        
        # If the observed deviation exceeds the statistical envelope for the legitimate noise
        is_significant = tv_dist > radius
        
        return {
            "observed_distribution": obs_dist,
            "baseline_distribution": base_dist,
            "tv_distance": float(tv_dist),
            "kl_divergence": float(kl_div),
            "confidence_radius": float(radius),
            "significant": bool(is_significant)
        }

    def evaluate_qmf(self, observed_qmf_bases: Dict[str, Any], baseline_qmf_bases: Dict[str, Any], n: int) -> Dict[str, Any]:
        """
        Evaluates all bases and compiles the structural QMF evidence vector for the statistical tests.
        """
        results = {}
        anomalies = []
        
        obs_bases = observed_qmf_bases.get("basis", {})
        base_bases = baseline_qmf_bases.get("basis", {})
        
        for basis in ["X", "Y", "Z"]:
            obs_dist = obs_bases.get(basis, {}).get("observed_distribution", {"0": 0.5, "1": 0.5})
            base_dist = base_bases.get(basis, {}).get("baseline_distribution", {"0": 0.5, "1": 0.5})
            
            res = self.evaluate_basis(obs_dist, base_dist, n)
            results[basis] = res
            
            if res["significant"]:
                anomalies.append(basis)
                
        is_rejected = len(anomalies) > 0
        
        return {
            "is_rejected": is_rejected,
            "anomalies": anomalies,
            "basis_evaluations": results
        }
