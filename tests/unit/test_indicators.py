import numpy as np
import pandas as pd
from mr01.indicators.zscore import rolling_zscore
from mr01.indicators.ema import ema
from mr01.indicators.atr import true_range, atr

def test_rolling_population_statistics():
    x=pd.Series(np.arange(1.,51.))
    mean,std,z=rolling_zscore(x,50)
    assert mean.iloc[-1] == 25.5
    assert np.isclose(std.iloc[-1],np.std(x,ddof=0))
    assert np.isclose(z.iloc[-1],(50-25.5)/np.std(x,ddof=0))

def test_zero_std_is_invalid():
    mean,std,z=rolling_zscore(pd.Series([2.]*50),50)
    assert std.iloc[-1] == 0 and np.isnan(z.iloc[-1])

def test_ema_warmup_and_recursive_convention():
    x=pd.Series([1.]*55)
    out=ema(x,50)
    assert out.iloc[:49].isna().all()
    assert out.iloc[49:].eq(1).all()

def test_true_range_and_wilder_atr():
    frame=pd.DataFrame({"high":[2.,3.,4.],"low":[1.,2.,3.],"close":[1.5,2.5,3.5]})
    assert np.allclose(true_range(frame).to_numpy(),[1,1.5,1.5])
    assert np.isclose(atr(frame,2).iloc[1],1.25)
