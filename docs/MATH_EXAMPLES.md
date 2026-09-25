# Q-SHIELD: Mathematical Examples & Benchmarks

This document provides numerical examples of how Q-SHIELD processes quantum measurements into statistical bounds and threat decisions.

## Example 1: Normal Operation (Noiseless)
- **Prepared State**: $|+\rangle$
- **Measurement Basis (X)**: Expected = 100% $|0\rangle_X$ (due to teleportation mapping)
- **Observed Counts ($n=10000$)**: $0 \to 9990$, $1 \to 10$
- **Distributions**:
  - Expected: $P(0) = 1.0$, $P(1) = 0.0$
  - Observed: $P(0) = 0.999$, $P(1) = 0.001$
- **Total Variation Distance ($TV$)**:
  $$TV = \frac{1}{2} ( |1.0 - 0.999| + |0.0 - 0.001| ) = \frac{1}{2}(0.001 + 0.001) = 0.001$$
- **Hoeffding Envelope ($\alpha=0.01$, Bonferroni $m=3$)**:
  $$\epsilon = \sqrt{ \frac{\ln(2 / (\alpha/3))}{2n} } \approx 0.017$$
- **Decision**: $TV (0.001) \le \epsilon (0.017) \implies$ NORMAL (ACCEPT)

## Example 2: Normal Operation (Depolarizing Channel $p=0.02$)
- **Observed Counts ($n=10000$)**: $0 \to 9850$, $1 \to 150$
- **Distributions**:
  - Observed: $P(0) = 0.985$, $P(1) = 0.015$
- **Total Variation Distance ($TV$)**:
  $$TV = 0.015$$
- **Decision**: $TV (0.015) \le \epsilon (0.017) \implies$ NORMAL (ACCEPT). Natural channel noise does not trigger false positive.

## Example 3: Attack State (Intercept-Resend)
- **Eve** measures the teleported state in the Z-basis randomly, effectively destroying X-basis coherence.
- **Prepared State**: $|+\rangle$
- **Observed Counts ($n=10000$, X-basis)**: $0 \to 5020$, $1 \to 4980$
- **Distributions**:
  - Observed: $P(0) = 0.502$, $P(1) = 0.498$
- **Total Variation Distance ($TV$)**:
  $$TV = \frac{1}{2} ( |1.0 - 0.502| + |0.0 - 0.498| ) = 0.498$$
- **Decision**: $TV (0.498) > \epsilon (0.017) \implies$ STAGE 1 REJECTION. Stage 2 evaluates Fidelity ($~0.5$) and Bell Correlations ($\sim 0.0$) and correctly attributes as `CHANNEL_MANIPULATION` or `FORGERY` depending on structural traces.
