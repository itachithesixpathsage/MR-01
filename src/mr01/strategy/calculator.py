import numpy as np
import pandas as pd
from ..config import StrategyConfig, DEFAULT_CONFIG
from ..indicators.zscore import rolling_zscore
from ..indicators.ema import ema
from ..indicators.atr import atr
from ..variants import Variant
from ..data.validation import validate_ohlc
from ..strategy.regime_classifier import classify_regime
from ..strategy.signal_engine import evaluate
from ..strategy.position_sizing import theoretical_size, BrokerSpec

def calculate(m5: pd.DataFrame, h1: pd.DataFrame, variant: Variant, *, position_open: bool | None=None, equity: float | None=None, broker_spec: BrokerSpec | None=None, config: StrategyConfig=DEFAULT_CONFIG) -> pd.DataFrame:
    """Produce a separate chronological result frame for one variant only.

    Inputs use UTC candle-open timestamps. R reports the current M5 bar; C reports
    the latest completed M5 bar and timestamps the decision at that bar's close.
    H1 rows are selected only when their opening time is no later than the decision;
    completed mode additionally requires the H1 candle to have closed.
    """
    q5=validate_ohlc(m5,5,1)
    q1=validate_ohlc(h1,60,1)
    if not q5.valid or not q1.valid:
        raise ValueError(f"Invalid input data: M5={q5.to_dict()}, H1={q1.to_dict()}")
    m5=m5.copy().reset_index(drop=True); h1=h1.copy().reset_index(drop=True)
    for column in ("open", "high", "low", "close"):
        m5[column]=pd.to_numeric(m5[column],errors="raise")
        h1[column]=pd.to_numeric(h1[column],errors="raise")
    m5["timestamp"]=pd.to_datetime(m5.timestamp,utc=True); h1["timestamp"]=pd.to_datetime(h1.timestamp,utc=True)
    m_mean,m_std,m_z=rolling_zscore(m5.close,config.z_window)
    m_atr=atr(m5,config.atr_period)
    h_ema=ema(h1.close,config.ema_period)
    rows=[]
    completed=variant is Variant.COMPLETED
    for i in range(len(m5)):
        mi=i-1 if completed else i
        if mi < 0: continue
        bar=m5.iloc[mi]
        decision_time=bar.timestamp+pd.Timedelta(minutes=5) if completed else m5.iloc[i].timestamp
        # H1 current EMA observation: closed candle only in C; currently open/available
        # candle in R. Shift five observations backward to preserve published separation.
        candidates=np.flatnonzero((h1.timestamp <= decision_time).to_numpy())
        if completed:
            candidates=np.array([j for j in candidates if h1.iloc[j].timestamp+pd.Timedelta(hours=1) <= decision_time],dtype=int)
        hj=int(candidates[-1]) if len(candidates) else -1
        hcur=float(h_ema.iloc[hj]) if hj >= 0 else np.nan
        hprev=float(h_ema.iloc[hj-config.ema_shift]) if hj >= config.ema_shift else np.nan
        momentum=abs(hcur-hprev) if np.isfinite(hcur) and np.isfinite(hprev) else np.nan
        zi=float(m_z.iloc[mi]) if np.isfinite(m_z.iloc[mi]) else np.nan
        atr_value=float(m_atr.iloc[mi]) if np.isfinite(m_atr.iloc[mi]) else np.nan
        regime=classify_regime(momentum,atr_value)
        sig=evaluate(zi,regime,position_open,config)
        sizing=theoretical_size(equity,atr_value,broker_spec,config.risk_fraction,config.sizing_atr_multiple) if equity is not None else {"status":"UNVERIFIED","risk_budget":None,"sizing_distance":2*atr_value if np.isfinite(atr_value) else None,"lots":None,"estimated_risk":None,"account_currency":broker_spec.account_currency if broker_spec else None,"contract_size":broker_spec.contract_size if broker_spec else None}
        indicator_valid=bool(np.isfinite(zi) and np.isfinite(atr_value) and np.isfinite(momentum))
        rows.append({"timestamp":decision_time,"variant":variant.value,"instrument":config.instrument,"close":float(bar.close),"mean":float(m_mean.iloc[mi]) if np.isfinite(m_mean.iloc[mi]) else np.nan,"stddev":float(m_std.iloc[mi]) if np.isfinite(m_std.iloc[mi]) else np.nan,"zscore":zi,"ema_current":hcur,"ema_previous":hprev,"momentum_difference":momentum,"atr":atr_value,"regime_status":regime.value,"entry_signal":sig["entry_signal"],"exit_signal":sig["exit_signal"],"position_status":sig["position_status"],"theoretical_risk":sizing["risk_budget"],"sizing_distance":sizing["sizing_distance"],"theoretical_lots":sizing["lots"],"estimated_risk":sizing["estimated_risk"],"account_currency":sizing["account_currency"],"contract_size":sizing.get("contract_size"),"sizing_tick_size":broker_spec.tick_size if broker_spec else None,"sizing_tick_value":broker_spec.tick_value if broker_spec else None,"minimum_lot":broker_spec.minimum_lot if broker_spec else None,"maximum_lot":broker_spec.maximum_lot if broker_spec else None,"lot_increment":broker_spec.lot_increment if broker_spec else None,"sizing_status":sizing["status"],"calculation_status":"VALID" if indicator_valid else "INVALID"})
    return pd.DataFrame(rows)
