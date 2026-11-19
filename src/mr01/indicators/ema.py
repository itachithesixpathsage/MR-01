import numpy as np
import pandas as pd

def ema(close: pd.Series, period: int = 50) -> pd.Series:
    """Recursive EMA, alpha=2/(period+1), seeded with first close (pandas adjust=False).

    Warm-up is explicitly period-1 observations: values before that are masked. This
    convention is documented and may differ from terminal-specific EMA seeding.
    """
    x=pd.to_numeric(close, errors="coerce").astype(float)
    out=x.ewm(span=period, adjust=False, min_periods=period, ignore_na=False).mean()
    return out.where(np.isfinite(out))
