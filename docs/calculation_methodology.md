# Calculation methodology

## Z score
For each current included close and 50-value window, calculate mean and population standard deviation (`ddof=0`); calculate `(close-mean)/stddev`. Zero/nonfinite standard deviation produces NaN and INVALID calculation status.

## EMA
Recursive EMA with alpha `2/(50+1)`, first-close seed and 50-observation warm-up. This is an explicit deterministic convention, not a claim that every MetaTrader build has identical initialization. Reference comparison remains required.

## ATR
True range is max of high-low, absolute high minus prior close, and absolute low minus prior close. First true range is high-low. Seed with the arithmetic mean of the first 14 true ranges, then use Wilder's recursion `(previous_ATR*13 + TR)/14`.

## Regime and signal
Eligible iff absolute EMA difference is strictly less than ATR. Entry boundaries are inclusive at ±2; exit is strict at absolute Z below 0.25. Exit uses Z and open position only, independent of regime. An unknown position state does not assert an entry is executable or an exit exists.

## Sizing
Risk budget is equity × 0.005; reference distance is ATR × 2. Risk per lot is distance/tick_size × tick_value. Volume is floored to lot increments and checked against min/max and budget. Tick value must be expressed in account currency and is the monetary tick value per lot, incorporating contract economics; contract size is also required and recorded as a broker specification. Actual HFM contract specifications must be verified for the particular account and symbol before sizing is considered verified.
