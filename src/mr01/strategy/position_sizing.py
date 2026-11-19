from enum import Enum
from math import floor, isfinite
from pydantic import BaseModel, ConfigDict, Field, model_validator

class SizingStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    INVALID = "INVALID"

class BrokerSpec(BaseModel):
    model_config=ConfigDict(frozen=True)
    tick_size: float = Field(gt=0)
    tick_value: float = Field(gt=0, description="Monetary value of one tick per lot in account currency")
    contract_size: float = Field(gt=0)
    account_currency: str
    minimum_lot: float = Field(gt=0)
    maximum_lot: float = Field(gt=0)
    lot_increment: float = Field(gt=0)

    @model_validator(mode="after")
    def valid_volume_limits(self):
        if self.maximum_lot < self.minimum_lot:
            raise ValueError("maximum_lot must be greater than or equal to minimum_lot")
        if not self.account_currency.strip():
            raise ValueError("account_currency cannot be empty")
        return self

def theoretical_size(equity: float, atr_value: float, spec: BrokerSpec | None, risk_fraction: float=.005, atr_multiple: float=2.0) -> dict:
    """Floor to the allowed lot grid; never return a volume exceeding budget.

    Tick value must already be quoted in account currency. Contract size is retained
    as a required broker specification; broker tick value per lot already reflects contract economics and drives risk.
    """
    risk=equity*risk_fraction if isfinite(equity) else float("nan")
    distance=atr_value*atr_multiple if isfinite(atr_value) else float("nan")
    result={"status":SizingStatus.UNVERIFIED.value,"risk_budget":risk,"sizing_distance":distance,"lots":None,"estimated_risk":None,"account_currency":spec.account_currency if spec else None,"contract_size":spec.contract_size if spec else None}
    if spec is None: return result
    if not (isfinite(equity) and equity > 0 and isfinite(distance) and distance > 0):
        result["status"]=SizingStatus.INVALID.value; return result
    risk_per_lot=distance/spec.tick_size*spec.tick_value
    if not isfinite(risk_per_lot) or risk_per_lot <= 0:
        result["status"]=SizingStatus.INVALID.value; return result
    raw=risk/risk_per_lot
    # Grid anchored at zero. A minimum lot that exceeds budget is rejected.
    lots=floor(min(raw,spec.maximum_lot)/spec.lot_increment)*spec.lot_increment
    if lots < spec.minimum_lot or lots <= 0:
        result["status"]=SizingStatus.INVALID.value; return result
    estimated=lots*risk_per_lot
    if estimated > risk:
        lots=max(0.0,lots-spec.lot_increment); estimated=lots*risk_per_lot
    if lots < spec.minimum_lot:
        result["status"]=SizingStatus.INVALID.value; return result
    result.update(status=SizingStatus.VERIFIED.value,lots=lots,estimated_risk=estimated)
    return result
