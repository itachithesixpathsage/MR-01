import numpy as np
import pandas as pd
from mr01.data.validation import validate_ohlc
from mr01.strategy.calculator import calculate
from mr01.variants import Variant

def bars(n,freq,start):
    ts=pd.date_range(start,periods=n,freq=freq,tz="UTC")
    close=1.1+np.arange(n)*1e-5
    return pd.DataFrame({"timestamp":ts,"open":close,"high":close+.0002,"low":close-.0002,"close":close})

def test_validation_reports_missing_candle_and_duplicate():
    x=bars(5,"5min","2025-01-01")
    x=x.drop(index=2).reset_index(drop=True)
    q=validate_ohlc(x,5)
    assert q.missing_candles==1
    assert q.valid is False

def test_variants_are_separate_and_identified():
    m5=bars(80,"5min","2025-01-01")
    h1=bars(70,"h","2024-12-29")
    r=calculate(m5,h1,Variant.ORIGINAL,position_open=False)
    c=calculate(m5,h1,Variant.COMPLETED,position_open=False)
    assert set(r.variant)=={"MR-01A-R"}
    assert set(c.variant)=={"MR-01A-C"}
    assert c.timestamp.iloc[0] > r.timestamp.iloc[0]

def test_weekend_fx_closure_is_reported_without_being_a_missing_candle_failure():
    frame=pd.DataFrame({
        "timestamp":pd.to_datetime(["2025-01-03T20:00:00Z","2025-01-05T21:00:00Z"],utc=True),
        "open":[1.1,1.1],"high":[1.2,1.2],"low":[1.0,1.0],"close":[1.1,1.1],
    })
    q=validate_ohlc(frame,5)
    assert q.weekend_closure_gaps==1
    assert q.missing_candles==0
    assert q.valid
