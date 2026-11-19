from enum import Enum
import math

class RegimeStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    INVALID = "INVALID"

def classify_regime(momentum_difference: float, atr_value: float) -> RegimeStatus:
    if not (math.isfinite(momentum_difference) and math.isfinite(atr_value)) or atr_value <= 0:
        return RegimeStatus.INVALID
    return RegimeStatus.ELIGIBLE if momentum_difference < atr_value else RegimeStatus.INELIGIBLE
