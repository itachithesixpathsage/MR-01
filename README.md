# MR-01 Independent Signal Calculator

Standalone local research software for reconstructing the EUR/USD M5/H1 rules in the MR-01 M0 specification. It has no Métis dependency, broker connection, order execution, optimizer, or historical performance backtest.

## Install

Python 3.12+ is the supported runtime.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
```

## CSV format

M5 and H1 inputs each require `timestamp,open,high,low,close`; `volume` is optional. Naive timestamps are assumed UTC; timezone-aware timestamps are converted to UTC. Candle timestamps are interpreted as candle opening times. Files must be chronological and contain no duplicate timestamps. Gaps are reported, never filled. Quality reports are written before calculations; invalid datasets stop calculation.

```bash
mr01 validate-data --m5 data/raw/eurusd_m5.csv --h1 data/raw/eurusd_h1.csv --out reports
mr01 calculate --instrument EURUSD --variant completed --m5 data/raw/eurusd_m5.csv --h1 data/raw/eurusd_h1.csv --out reports --position flat
mr01 compare --m5 data/raw/eurusd_m5.csv --h1 data/raw/eurusd_h1.csv --out reports
mr01 inspect 2025-01-01T12:05:00Z --variant completed --m5 data/raw/eurusd_m5.csv --h1 data/raw/eurusd_h1.csv --position flat
mr01 report --input reports/indicator_calculations.csv --out reports
```

`inspect` writes data-quality reports to `reports` by default and shows the full recursive EMA/ATR source history plus the exact 50-close Z-score window. `--position` accepts `open`, `flat`, or `unknown` and defaults to unknown. Entry signals are suppressed unless the caller explicitly says the instrument is flat. The exit check is independent of regime eligibility. Each calculation invocation selects exactly one variant. `compare` produces explicitly suffixed columns.

Broker specs may be supplied as JSON with `tick_size`, `tick_value` (account currency per tick per lot), `contract_size`, `account_currency`, `minimum_lot`, `maximum_lot`, and `lot_increment`. No HFM values are presumed. Without specifications the sizing status is `UNVERIFIED`; 2×ATR is only a sizing reference and is not an attached stop-loss.

## Calculation conventions and limitations

- Z score uses the 50-close rolling window, population standard deviation (`ddof=0`), and rejects zero/non-finite standard deviation.
- EMA uses recursive `alpha=2/(period+1)`, seeded by the first close, masked until 50 observations. Terminal EMA initialization can differ and requires external reference validation.
- ATR uses true range including previous close, SMA seed over 14 valid true ranges, then Wilder smoothing. The first true range is high-low because previous close is unavailable.
- Completed variant uses the prior M5 row and the latest H1 bar fully closed by the M5 close time; its EMA comparison is five observations apart (terminal shifts 1 and 6).
- Original variant labels results with `MR-01A-R`, but finalized OHLC files cannot reconstruct the prototype's forming-bar snapshot at new-bar evaluation. Its historical output is therefore an OHLC-based approximation, not exact tick-level replication. Exact original replication needs timestamped intrabar snapshots.
- The calculator does not maintain simulated positions across rows. Supply position state explicitly; `unknown` prevents false claims about an open position or exit.
- Gaps may be scheduled market closures; inspect the report and source calendar before deciding they invalidate a dataset.
- No historical data was supplied, so the 20-observation independent reference verification is outstanding. Passing unit tests is not platform verification.

Run tests with `pytest`. M1 verification is incomplete until approved reference observations, regression fixtures, and MT4/MT5-compatible comparisons are recorded.
