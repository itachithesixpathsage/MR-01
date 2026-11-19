from enum import Enum
from math import isfinite
from ..config import StrategyConfig, DEFAULT_CONFIG
from .regime_classifier import classify_regime, RegimeStatus

class EntrySignal(str, Enum):
    BUY="BUY"; SELL="SELL"; NO_SIGNAL="NO_SIGNAL"; REGIME_BLOCKED="REGIME_BLOCKED"; POSITION_ALREADY_OPEN="POSITION_ALREADY_OPEN"

def evaluate(zscore: float, regime: RegimeStatus, position_open: bool | None, config: StrategyConfig=DEFAULT_CONFIG) -> dict:
    """Entry decision. Position must be explicitly supplied; None means unknown/invalid."""
    if position_open is True:
        entry=EntrySignal.POSITION_ALREADY_OPEN
    elif position_open is None:
        entry=EntrySignal.NO_SIGNAL
    elif not isfinite(zscore) or regime is RegimeStatus.INVALID:
        entry=EntrySignal.NO_SIGNAL
    elif zscore <= -config.z_entry or zscore >= config.z_entry:
        entry=EntrySignal.BUY if regime is RegimeStatus.ELIGIBLE and zscore <= -config.z_entry else EntrySignal.SELL if regime is RegimeStatus.ELIGIBLE else EntrySignal.REGIME_BLOCKED
    else:
        entry=EntrySignal.NO_SIGNAL
    # Exit is independent of regime. Unknown position does not claim an exit.
    exit_signal=bool(position_open is True and isfinite(zscore) and abs(zscore) < config.z_exit)
    return {"entry_signal":entry.value,"exit_signal":exit_signal,"position_status":"OPEN" if position_open is True else "FLAT" if position_open is False else "UNKNOWN"}
