# M0-D04 | MR-01 Reproduction Protocol v1.0

## 1. Objective

Reconstruct Bhatti's published framework and distinguish source-faithful behaviour from a completed-candle operational variant.

## 2. Research variants

### Variant A — MR-01A-R: Original replication

Preserve the visible Appendix A behaviour:
- 50 M5 closing-price observations.
- Population standard deviation.
- Z-score entry at ±2.0.
- Z-score exit at absolute value below 0.25.
- H1 EMA(50).
- EMA comparison shifts 0 and 5.
- Regime condition: absolute EMA difference below M5 ATR(14).
- ATR sizing distance: 2 × ATR.
- Risk percentage input: 0.5%.
- One position per instrument.
- Prototype checks for a new M5 bar before calculations.
- The code checks an existing position's Z-score exit before applying the entry regime filter.

### Variant B — MR-01A-C: Completed-candle variant

Preserve the same formulas and parameter values, but use:
- M5 price index 1.
- H1 EMA shifts 1 and 6.
- M5 ATR index 1.

This variant changes observation timing and must not be represented as an exact copy of the prototype.

## 3. Calculation conventions

- Standard deviation: population, denominator N=50.
- EMA: document the exact library/platform implementation and initialisation convention.
- ATR: document the exact platform/library implementation, including true-range and smoothing convention.
- Timestamps: store in UTC; retain original broker timestamps separately if applicable.
- Bar alignment: H1 observations must be aligned to the M5 decision time without using future information.
- Invalid data: no signal when observations are missing, non-finite, insufficient or invalid.
- Zero standard deviation: no Z-score signal; mark observation invalid.

## 4. Required validation tests

### Unit tests
1. Mean on a known 50-value input.
2. Population standard deviation on a known input.
3. Z-score for known input.
4. EMA value and five-bar difference.
5. ATR on a known OHLC sequence.
6. Regime eligibility at values below, equal to and above the threshold.
7. Buy and sell threshold boundaries.
8. Exit threshold boundary.
9. Zero standard deviation.
10. Missing or insufficient observations.

### Reference observation checks
Select at least 20 historical decision timestamps. For each timestamp, record:
- M5 input observations.
- H1 input observations.
- Mean.
- Standard deviation.
- Z-score.
- EMA values and difference.
- ATR.
- Regime eligibility.
- Signal.
- Variant and candle indexing.

Manually or independently calculate the values and compare with the calculator. Record tolerances and discrepancies.

## 5. Historical evaluation protocol

- Use chronological data splits.
- Preserve a final untouched holdout.
- Avoid random shuffling of time-series observations.
- Include bid/ask spread and commission where data is available.
- Model slippage explicitly or report its omission as a limitation.
- Compare regime-conditioned signals with an otherwise identical Z-score-only baseline.
- Report trade count, net expectancy, profit factor, drawdown, holding time and confidence intervals.
- Segment performance by volatility and trading session.
- Perform parameter sensitivity only after the default specification has been reproduced.
- Account for multiple testing and parameter-selection bias.

## 6. Demo forward-test protocol

Demo deployment is permitted only after:
- signal calculations pass verification;
- broker lot sizing is checked;
- emergency risk controls are approved;
- execution and journaling procedures are ready;
- the selected strategy variant is frozen.

Record every executed trade and every rejected signal. Capture decision timestamp, signal values, regime, spread, intended entry, actual fill, size, exit, costs, result and rule compliance.

## 7. Acceptance logic

- **Pass for further investigation:** positive out-of-sample net expectancy, evidence that regime conditioning adds value, reasonable robustness and acceptable operational behaviour.
- **Inconclusive:** insufficient observations, wide uncertainty, unstable results or inadequate forward-test sample.
- **Fail:** negative net expectancy, no meaningful benefit from regime filtering, or results that collapse under realistic costs or robustness checks.

A demo result alone cannot establish a durable statistical edge.
