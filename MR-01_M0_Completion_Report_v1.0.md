# M0-D05 | MR-01 M0 Completion Report v1.0

**Milestone:** M0 — Methodology Extraction  
**Source reviewed:** Uploaded seven-page paper by Amaanullah Bhatti, January 2026  
**Research deadline target:** 26 November 2026  
**Status:** Documentation package issued; review and sign-off required before M1 is treated as formally authorised.

## 1. Deliverables issued

| ID | Deliverable | Status |
|---|---|---|
| M0-D01 | Technical Specification v1.0 | Issued |
| M0-D02 | Implementation Discrepancy Register v1.0 | Issued |
| M0-D03 | Risk Management Policy v1.0 | Issued |
| M0-D04 | Reproduction Protocol v1.0 | Issued |
| M0-D05 | M0 Completion Report v1.0 | Issued |

## 2. Decisions recorded

1. Primary research instrument is EUR/USD.
2. Broker/platform is HFM demo / MetaTrader 4.
3. Execution is manual.
4. Original prototype behaviour is preserved as MR-01A-R.
5. Completed-candle implementation is maintained separately as MR-01A-C.
6. The author's 0.5% sizing input is retained in the source-faithful specification.
7. The 2 × ATR distance is treated as a sizing reference, not an actual stop-loss.
8. Emergency risk controls are MR-01 experimental safeguards and not author-derived parameters.
9. No Métis dependency is permitted.

## 3. Source-derived methodology

The extracted default parameters are:
- Mean window: 50 M5 bars.
- Z-score entry: ±2.0.
- Z-score exit: absolute Z-score below 0.25.
- Momentum EMA: 50 on H1.
- EMA comparison: current value versus five bars earlier.
- Regime filter: absolute EMA difference below M5 ATR(14).
- Risk percentage: 0.5%.
- Sizing distance: 2 × M5 ATR(14).
- One position per instrument.

## 4. Material limitations

The paper's prototype is not a complete production implementation. It has no attached hard stop corresponding to its sizing distance, does not visibly handle all broker volume constraints, and leaves several operational matters unspecified. The paper itself identifies regime misclassification, news shocks, parameter calibration, slippage and spread widening as limitations.

No claim of profitability is made by this report.

## 5. M0 exit criteria

M0 is considered documentarily complete when:
- all five deliverables have been reviewed;
- source-derived facts are distinguished from MR-01 decisions;
- the two candle variants are recorded;
- risk controls are understood as separate from the published strategy;
- unresolved issues remain visible in the discrepancy register.

## 6. M1 entry conditions

M1 may proceed to build the independent signal calculator. It must use the M0 specification, retain both variants, implement calculation guards and produce reproducible outputs.

Historical and demo validation remain later gates. Demo trading is not authorised solely by M0 completion.

## 7. Final status

**M0: Deliverables issued.**  
**M0 sign-off: Pending user review.**  
**Next milestone: M1 — Independent Signal Calculator.**
