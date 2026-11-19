# Data dictionary

Input CSV: `timestamp` (ISO datetime; aware values normalized to UTC; naive values assumed UTC), `open`, `high`, `low`, `close` (finite numeric), optional `volume`. Timestamp denotes candle opening. M5 spacing is five minutes and H1 spacing is one hour; larger gaps are counted and reported, not repaired.

Calculation output includes UTC decision timestamp, variant, instrument, M5 close, rolling mean/stddev/Z, current/previous H1 EMA, absolute EMA difference, ATR, regime, entry and exit flags, explicit position status, risk budget, reference distance, theoretical lots, estimated risk, account currency, and calculation status.
