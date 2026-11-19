# M0-D03 | MR-01 Risk Management Policy v1.0

**Scope:** Independent research and HFM demo testing only.  
**This policy does not authorise live trading.**

## 1. Separate the author's model from MR-01 safeguards

The paper specifies a 0.5% equity risk amount and uses 2 × ATR as the assumed distance in its lot-sizing calculation. It does not place a stop-loss at that distance. It also describes conservative sizing, regime-based trade suppression and conceptual strategy-level drawdown monitoring.

MR-01 must preserve these facts in the source-faithful replication while separately defining operational safeguards for demo testing.

## 2. Source-derived sizing assumptions

\[
RiskBudget = Equity \times 0.005
\]

\[
SizingDistance = 2 \times ATR_{14,M5}
\]

The lot calculation must be reconstructed using the broker's actual EUR/USD contract specifications. The published prototype's simplified calculation is not accepted as broker-verified.

## 3. Demo-only safeguards

The following are provisional MR-01 experimental controls, not parameters from Bhatti's paper:

- Demo account only.
- EUR/USD only.
- One open position maximum.
- No martingale, grid, averaging down or adding to losing positions.
- No unattended positions.
- No order unless size and potential loss have been independently checked.
- Maintain an emergency account-level loss limit before demo deployment.
- Stop and investigate after any calculation, order-entry or execution-control error.

A proposed initial research cap is 0.25% equity planned risk per demo trade, with a proposed daily stop of 0.75% of starting daily equity. These are conservative MR-01 test controls and are not a reproduction of the author's 0.5% setting. If the research needs a strict author-faithful 0.5% sizing comparison, it should be performed in historical simulation first. Any demo variant using 0.5% must have a separately approved protective procedure.

## 4. Unprotected-position problem

Because the paper's prototype has no actual stop-loss, the 2 × ATR sizing distance does not cap the realised loss. An adverse move can exceed that distance.

Before demo deployment, MR-01 must choose and document one of the following:
- A protective emergency stop, clearly labelled as a deviation from the paper.
- A strictly supervised manual emergency-exit procedure with a defined maximum adverse-loss threshold.

The research must never imply that the source-faithful strategy has a guaranteed maximum loss per trade.

## 5. Broker constraints

Before calculating executable lots, verify:
- Contract size.
- Tick size.
- Tick value and account-currency conversion.
- Minimum and maximum lot.
- Lot step.
- Margin requirements and stop-out rules.
- Commission and spread model.
- Order execution constraints.

Reject any calculated volume that cannot be represented safely within broker constraints. Do not round a position upward if that increases risk beyond the approved budget.

## 6. News and abnormal conditions

The paper identifies macroeconomic news shocks, structural breaks, slippage and spread widening as failure modes. It does not specify a quantitative news filter.

MR-01 must define whether it will:
- exclude specified high-impact EUR/USD events from the demo test; or
- trade through them while recording event exposure and spread conditions.

Whichever choice is made must be frozen before forward-testing and reported as an experimental condition.

## 7. Stop conditions

Pause the experiment and investigate if:
- a position is opened without a valid signal;
- calculated volume exceeds the approved risk budget;
- the platform or data feed is unreliable;
- an exit cannot be executed as planned;
- the daily or account-level loss cap is reached;
- a material change occurs in broker conditions.

## 8. Policy boundary

Passing these controls does not establish profitability or justify live capital. This policy exists to prevent an experimental process from taking uncontrolled financial risk.
