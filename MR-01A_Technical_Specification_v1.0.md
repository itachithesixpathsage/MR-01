# M0-D01 | MR-01A Technical Specification v1.0

**Document status:** Baseline specification extracted from source  
**Primary source:** Amaanullah Bhatti, *A Regime-Conditioned Statistical Mean Reversion Framework for Intraday FX Markets*, January 2026  
**Research implementation:** EUR/USD, HFM demo, manual execution through MT4  
**Source locations:** Sections 3–8 and Appendix A, pages 2–7

## 1. Purpose

This document formalises the strategy described in Bhatti's paper so it can be independently reconstructed and evaluated. It records the published logic and default parameters without silently adding missing rules.

The paper describes a methodological framework, not a claim of guaranteed profitability.

## 2. Framework overview

The framework combines:

1. Volatility-normalised price deviations (Z-scores) for signal generation.
2. Higher-timeframe momentum filtering for regime classification.
3. Volatility-adjusted position sizing for risk normalisation.

The prototype uses M5 bars for signal construction and H1 bars for the momentum filter.

## 3. Instrument and experimental environment

| Item | MR-01 setting |
|---|---|
| Instrument | EUR/USD |
| Broker | HFM |
| Account | Demo |
| Platform | MetaTrader 4 |
| Execution | Manual |
| Signal timeframe | M5 |
| Regime timeframe | H1 |
| Research independence | No Métis dependency |

The instrument and execution environment are MR-01 research choices. They are not claims made by the paper.

## 4. Z-score signal construction

Let \(P_t\) denote the M5 closing price. The paper defines a standardised deviation:

\[
Z_t = \frac{P_t-\mu_t}{\sigma_t}
\]

where:
- \(P_t\) is the price observation;
- \(\mu_t\) is the mean of the selected rolling window;
- \(\sigma_t\) is the standard deviation of that window.

Appendix A sets `MeanWindow = 50` and calculates the mean and standard deviation over 50 M5 closing-price observations. The implementation divides the sum of squared deviations by 50 before taking the square root. This is population standard deviation (ddof=0).

\[
\mu_t = \frac{1}{50}\sum_{i=1}^{50}P_i
\]

\[
\sigma_t = \sqrt{\frac{1}{50}\sum_{i=1}^{50}(P_i-\mu_t)^2}
\]

\[
Z_t = \frac{P_t-\mu_t}{\sigma_t}
\]

**Published defaults:**
- Mean window: 50 M5 bars.
- Entry threshold: 2.0.
- Exit threshold: 0.25.

The paper's code reads the current M5 bar at index 0. The implications and alternative completed-bar convention are recorded in M0-D02 and M0-D04.

## 5. Multi-timeframe momentum filter

The paper proxies directional persistence using the slope of an exponential moving average on a higher timeframe.

Appendix A specifies:
- EMA period: 50.
- Momentum timeframe: H1.
- Comparison shift: 5 H1 bars.

The prototype computes:

\[
M_t = |EMA_{50,H1}(0)-EMA_{50,H1}(5)|
\]

The entry regime is considered eligible when:

\[
M_t < ATR_{14,M5}
\]

The filter therefore suppresses new mean-reversion entries when the absolute EMA change exceeds or equals the M5 ATR value.

**Important:** The comparison uses an H1 EMA difference and an M5 ATR. The paper specifies this comparison but does not provide a separate dimensional normalisation or empirical justification for the threshold. It must be tested as written before alternatives are considered.

## 6. Entry logic

Subject to the momentum filter passing and no existing position on the instrument:

| Condition | Action |
|---|---|
| \(Z_t \leq -2.0\) | Buy |
| \(Z_t \geq +2.0\) | Sell |
| Neither condition | No new entry |

The prototype permits only one position per instrument.

## 7. Exit logic

The prototype closes an existing position when:

\[
|Z_t| < 0.25
\]

The paper describes this as the dissipation of the original statistical dislocation.

The code checks the exit condition before evaluating new entries and returns after processing an existing position.

**Unspecified by the paper:** Maximum holding period, time-based exit, handling of a signal that moves further against an open position, and exact manual-execution handling when the Z-score crosses the exit threshold between observations.

## 8. Volatility and position sizing

Appendix A specifies:
- ATR period: 14.
- ATR timeframe: M5.
- Risk percentage: 0.5%.
- Sizing distance: 2 × ATR.

The intended risk budget is:

\[
R = Equity \times 0.005
\]

The sizing distance is:

\[
D = 2 \times ATR_{14,M5}
\]

The prototype then estimates lots using the risk amount, distance in points and symbol tick value.

**Critical distinction:** The 2 × ATR distance is used in the lot-sizing calculation. The prototype does not attach a corresponding stop-loss order. It must not be described as a hard stop.

The published lot-sizing expression does not explicitly account for all broker-specific constraints, including tick size, lot step, minimum volume, maximum volume and volume normalisation. See M0-D02.

## 9. Published default parameters

| Parameter | Default |
|---|---:|
| MeanWindow | 50 |
| Z_Entry | 2.0 |
| Z_Exit | 0.25 |
| MomentumEMA | 50 |
| MomentumTF | H1 |
| EMA comparison shift | 5 |
| RiskPercent | 0.5 |
| ATR_Period | 14 |
| ATR timeframe | M5 |
| Sizing distance | 2 × ATR |
| Concurrent positions | 1 per instrument |

## 10. Limitations identified by the paper

The paper identifies:
- Regime misclassification during abrupt structural breaks.
- Vulnerability to macroeconomic news shocks.
- Dependence on parameter calibration.
- Execution risks, including slippage and spread widening.

It recommends walk-forward testing, regime-segmented analysis and stress testing before live deployment.

## 11. Source boundaries and unspecified details

The paper does not fully specify:
- A complete broker-independent lot-sizing formula.
- A hard per-trade stop-loss.
- A numerical strategy-level drawdown threshold.
- A maximum holding period.
- A complete transaction-cost model.
- A detailed news filter.
- A full statistical backtest protocol or evidence of profitability.

These items must remain open or be labelled as MR-01 experimental controls. They must not be attributed to the author.

## 12. Reproduction requirement

The initial reconstruction must preserve the mathematical definitions and default parameters above. Any change in candle indexing, risk controls, execution assumptions or indicator implementation must be logged as a deviation and evaluated separately.

**Document version:** 1.0
