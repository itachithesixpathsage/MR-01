from pydantic import BaseModel, ConfigDict, Field, field_validator

class StrategyConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    instrument: str = "EURUSD"

    @field_validator("instrument")
    @classmethod
    def only_eurusd(cls, value: str) -> str:
        normalized=value.upper().replace("/", "")
        if normalized != "EURUSD":
            raise ValueError("MR-01 initial implementation supports EUR/USD only")
        return "EURUSD"
    z_window: int = Field(50, gt=1)
    z_entry: float = 2.0
    z_exit: float = 0.25
    ema_period: int = Field(50, gt=1)
    ema_shift: int = 5
    atr_period: int = Field(14, gt=1)
    risk_fraction: float = 0.005
    sizing_atr_multiple: float = 2.0

DEFAULT_CONFIG = StrategyConfig()

def load_config(path=None) -> StrategyConfig:
    """Load an explicit YAML config, or return the immutable published defaults."""
    if path is None:
        return DEFAULT_CONFIG
    import yaml
    with open(path, encoding="utf-8") as stream:
        values=yaml.safe_load(stream) or {}
    return StrategyConfig.model_validate(values)
