from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from .ingestion import REQUIRED

@dataclass
class QualityReport:
    rows: int
    missing_columns: list[str]
    invalid_timestamps: int
    duplicate_timestamps: int
    non_monotonic_timestamps: int
    missing_candles: int
    weekend_closure_gaps: int
    missing_candle_examples: list[str]
    invalid_ohlc_rows: int
    non_finite_rows: int
    insufficient_observations: bool
    timeframe_minutes: int
    timezone_inconsistencies: int
    irregular_intervals: int
    valid: bool
    def to_dict(self): return asdict(self)

def validate_ohlc(frame: pd.DataFrame, timeframe_minutes: int, minimum_observations: int = 1) -> QualityReport:
    missing = sorted(REQUIRED - set(frame.columns))
    if missing:
        return QualityReport(len(frame), missing, 0, 0, 0, 0, 0, [], 0, 0, len(frame)<minimum_observations, timeframe_minutes, 0, 0, False)
    ts = pd.to_datetime(frame.timestamp, errors="coerce", utc=True)
    invalid_ts = int(ts.isna().sum())
    good_ts = ts.dropna()
    duplicate = int(good_ts.duplicated().sum())
    nonmono = int(not good_ts.is_monotonic_increasing)
    ordered=good_ts.sort_values()
    diffs=ordered.diff().dropna()
    expected = pd.Timedelta(minutes=timeframe_minutes)
    gaps = diffs[diffs > expected]
    missing_count=0
    weekend_gaps=0
    examples=[]
    # A gap crossing the standard FX weekend closure is recorded separately. Other
    # missing intervals are counted and prevent calculations until reviewed.
    for idx, delta in gaps.items():
        current=ordered.loc[idx]
        previous=ordered.loc[ordered.index.get_loc(idx)-1]
        if previous.weekday()==4 and current.weekday() in (6,0):
            weekend_gaps += 1
            continue
        missing_count += max(1, round(delta / expected)-1)
        if len(examples)<10: examples.append(str(current))
    irregular = int((diffs % expected != pd.Timedelta(0)).sum())
    aligned = int((good_ts.dt.floor(f"{timeframe_minutes}min") != good_ts).sum())
    numeric = frame[["open","high","low","close"]].apply(pd.to_numeric, errors="coerce")
    vals = numeric.to_numpy(dtype=float)
    nonfinite = int((~np.isfinite(vals)).any(axis=1).sum())
    bad = (numeric.high < numeric[["open","close","low"]].max(axis=1)) | (numeric.low > numeric[["open","close","high"]].min(axis=1))
    invalid_ohlc = int(bad.fillna(True).sum())
    enough = len(frame) < minimum_observations
    timezone_inconsistencies = int(frame["_timestamp_kind"].nunique() > 1) if "_timestamp_kind" in frame else 0
    invalid_intervals = irregular + aligned
    valid = not (missing or invalid_ts or duplicate or nonmono or missing_count or invalid_intervals or timezone_inconsistencies or invalid_ohlc or nonfinite or enough)
    return QualityReport(len(frame), missing, invalid_ts, duplicate, nonmono, missing_count, weekend_gaps, examples, invalid_ohlc, nonfinite, enough, timeframe_minutes, timezone_inconsistencies, invalid_intervals, valid)
