import numpy as np
import pandas as pd

def rolling_zscore(close: pd.Series, window: int = 50) -> tuple[pd.Series,pd.Series,pd.Series]:
    """Windowed mean, population stddev (ddof=0), and Z; invalid/zero stddev -> NaN."""
    x=pd.to_numeric(close, errors="coerce")
    mean=x.rolling(window, min_periods=window).mean()
    std=x.rolling(window, min_periods=window).std(ddof=0)
    valid=np.isfinite(std) & (std > 0) & np.isfinite(x)
    z=((x-mean)/std).where(valid)
    return mean,std,z
