import numpy as np
import pandas as pd

def true_range(ohlc: pd.DataFrame) -> pd.Series:
    prev=ohlc.close.shift(1)
    return pd.concat([ohlc.high-ohlc.low,(ohlc.high-prev).abs(),(ohlc.low-prev).abs()],axis=1).max(axis=1, skipna=True)

def atr(ohlc: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder ATR: TR=max(H-L,|H-prevC|,|L-prevC|), seed SMA(period), recursive thereafter."""
    tr=true_range(ohlc)
    values=np.full(len(tr),np.nan,dtype=float)
    arr=tr.to_numpy(dtype=float)
    if len(arr) >= period and np.isfinite(arr[:period]).all():
        values[period-1]=arr[:period].mean()
        for i in range(period,len(arr)):
            if np.isfinite(arr[i]) and np.isfinite(values[i-1]):
                values[i]=(values[i-1]*(period-1)+arr[i])/period
    return pd.Series(values,index=ohlc.index,name="atr")
