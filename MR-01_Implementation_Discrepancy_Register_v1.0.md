# M0-D02 | MR-01 Implementation Discrepancy Register v1.0

**Purpose:** Record ambiguities, implementation risks and omissions in the paper's Appendix A prototype.  
**Severity labels:** Critical = must resolve before demo use; High = must resolve before interpreting results; Medium = document and test.

| ID | Severity | Observation | Source evidence | Required resolution |
|---|---|---|---|---|
| D01 | High | M5 Z-score uses price array index 0, the current/forming bar in the prototype. | Appendix A, pp. 5–6 | Preserve in original replication; separately test completed-bar variant using index 1. |
| D02 | High | H1 EMA comparison uses shifts 0 and 5. Shift 0 can change while the H1 candle is forming. | Appendix A, p. 6 | Preserve in original replication; separately test completed H1 observations using shifts 1 and 6. |
| D03 | High | M5 ATR uses shift 0, so the volatility threshold and sizing input can change intrabar. | Appendix A, p. 6 | Preserve in original replication; completed-bar variant uses shift 1. |
| D04 | High | The momentum condition compares an H1 EMA price difference over five H1 bars with an M5 ATR. | Section 4 and Appendix A, p. 6 | Reproduce as written first; test predictive usefulness and sensitivity. Do not silently rescale. |
| D05 | Critical | The code uses 2 × ATR in lot sizing but does not place a stop-loss order. | Sections 5–6; Appendix A, p. 6 | Do not call 2 × ATR a stop. Define separate emergency controls before demo deployment. |
| D06 | Critical | Lot formula uses point and tick value but does not visibly account for tick size, volume step, minimum/maximum lot or broker-specific contract details. | Appendix A, p. 6 | Reconstruct broker-aware sizing and verify against HFM symbol specifications and calculator. |
| D07 | Critical | No visible guard against zero or invalid standard deviation. | Appendix A, p. 6 | Reject the signal when standard deviation is zero, non-finite or invalid. |
| D08 | High | Historical data-copy success and indicator validity are not visibly checked before calculations. | Appendix A, pp. 5–6 | Add data sufficiency, missing-value and indicator-readiness checks in independent calculator. |
| D09 | High | The paper does not define a maximum holding period or time-based exit. | Sections 6–8 | Keep unspecified in faithful replication; define an experimental safety procedure separately. |
| D10 | High | Strategy-level drawdown monitoring is described conceptually but no numerical threshold is provided. | Section 6 | Establish an MR-01 operational stop threshold; label it as an experiment control, not an author parameter. |
| D11 | High | No explicit spread, commission or slippage model is specified in the prototype. | Sections 7–8 | Use bid/ask-aware historical evaluation and record actual demo spread and fills. |
| D12 | Medium | The prototype's new-bar check is based on M5 bar time. | Appendix A, p. 7 | Preserve for replication; specify manual observation and decision timestamps consistently. |
| D13 | Medium | The code's one-position check is per symbol, but account-level interactions and manual duplicate orders are not addressed. | Appendix A, p. 5 | Maintain a one-position-per-instrument control in the manual procedure. |
| D14 | Medium | The paper does not fully specify how open positions should be handled if the momentum filter subsequently fails. | Appendix A, p. 5 | Preserve the code's observed behaviour: the momentum filter gates new entries; the open-position exit check occurs first and uses Z-score. Document this explicitly. |

## Variant decisions

### MR-01A-R — Original replication

Preserve the prototype's index-0 behaviour:
- M5 price index 0.
- H1 EMA shifts 0 and 5.
- M5 ATR shift 0.
- Original default parameters and formulas.

This variant is for source-faithful reconstruction, not preferred live or demo operation.

### MR-01A-C — Completed-candle variant

Use completed observations:
- M5 price index 1.
- H1 EMA shifts 1 and 6, preserving the five-bar separation.
- M5 ATR shift 1.

This is a deliberate timing modification. Results must be reported separately from MR-01A-R.

## Change-control rule

Every correction or added control must record:
1. The original behaviour.
2. The modified behaviour.
3. The reason for the change.
4. The expected effect.
5. The test used to evaluate it.

No undocumented changes are permitted after the strategy is frozen for forward-testing.
