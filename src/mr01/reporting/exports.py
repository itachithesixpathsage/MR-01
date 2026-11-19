from pathlib import Path
import json
import pandas as pd

def write_quality(path, label, report):
    d=report.to_dict()
    lines=[f"# Data quality report: {label}","",f"- Valid: **{d['valid']}**",f"- Rows: {d['rows']}",f"- Timeframe: {d['timeframe_minutes']} minutes",f"- Invalid timestamps: {d['invalid_timestamps']}",f"- Duplicate timestamps: {d['duplicate_timestamps']}",f"- Non-monotonic timestamps: {d['non_monotonic_timestamps']}",f"- Missing candles inferred from weekday gaps: {d['missing_candles']}",f"- Weekend closure gaps: {d['weekend_closure_gaps']}",f"- Invalid timeframe intervals/alignment: {d['irregular_intervals']}",f"- Source timezone inconsistencies: {d['timezone_inconsistencies']}",f"- Invalid OHLC rows: {d['invalid_ohlc_rows']}",f"- Rows with non-finite OHLC: {d['non_finite_rows']}",f"- Insufficient observations: {d['insufficient_observations']}",f"- Missing columns: {', '.join(d['missing_columns']) or 'none'}","", "Missing candles are reported, never filled. Timestamp gaps may also represent market closures; review examples against the source calendar.",""]
    Path(path).write_text("\n".join(lines))

def write_results(outdir, results:pd.DataFrame):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    results.to_csv(out/"indicator_calculations.csv",index=False)
    results.to_csv(out/"signal_history.csv",index=False)
    (out/"calculation_verification.md").write_text("# Calculation verification\n\nNo approved independent historical reference observations were supplied. Unit tests are present, but were not executable in the current environment because pytest and pandas are unavailable. The 20-observation reference verification and regression fixture remain pending. No historical performance evaluation was performed.\n")

def write_comparison(outdir, original, completed):
    left=original.add_suffix("_R").rename(columns={"timestamp_R":"timestamp"})
    right=completed.add_suffix("_C").rename(columns={"timestamp_C":"timestamp"})
    pd.merge(left,right,on="timestamp",how="outer").sort_values("timestamp").to_csv(Path(outdir)/"variant_comparison.csv",index=False)
