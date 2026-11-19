from pathlib import Path
import pandas as pd

REQUIRED = {"timestamp", "open", "high", "low", "close"}

def read_ohlc_csv(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Read CSV without fabricating data; convert aware times to UTC and retain source values."""
    path = Path(path)
    frame = pd.read_csv(path)
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"{path}: missing required columns: {sorted(missing)}")
    source = frame["timestamp"].astype(str).copy()
    parsed = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    frame["timestamp_source"] = source
    frame["_timestamp_kind"] = source.map(lambda v: "aware" if __import__("re").search(r"(?:Z|[+-]\d{2}:?\d{2})$",v.strip(),__import__("re").I) else "naive")
    frame["timestamp"] = parsed
    for col in ("open", "high", "low", "close", "volume"):
        if col in frame:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    kinds=source.map(lambda v: "aware" if __import__("re").search(r"(?:Z|[+-]\d{2}:?\d{2})$",v.strip(),__import__("re").I) else "naive")
    manifest = {"filename": str(path), "source_timezone": "embedded in timestamp when supplied; otherwise assumed UTC", "source_timestamp_kinds": sorted(kinds.unique().tolist()), "source_timezone_inconsistency": len(kinds.unique()) > 1, "source_timestamp_examples": source.head(3).tolist()}
    return frame, manifest
