from mr01.strategy.regime_classifier import classify_regime, RegimeStatus
from mr01.strategy.signal_engine import evaluate
from mr01.strategy.position_sizing import BrokerSpec, theoretical_size

def test_regime_strict_boundary():
    assert classify_regime(0.999,1)==RegimeStatus.ELIGIBLE
    assert classify_regime(1,1)==RegimeStatus.INELIGIBLE
    assert classify_regime(1.001,1)==RegimeStatus.INELIGIBLE

def test_entry_boundaries_and_open_position():
    assert evaluate(-2,RegimeStatus.ELIGIBLE,False)["entry_signal"]=="BUY"
    assert evaluate(2,RegimeStatus.ELIGIBLE,False)["entry_signal"]=="SELL"
    assert evaluate(-2,RegimeStatus.INELIGIBLE,False)["entry_signal"]=="REGIME_BLOCKED"
    assert evaluate(2,RegimeStatus.ELIGIBLE,True)["entry_signal"]=="POSITION_ALREADY_OPEN"

def test_exit_strict_and_independent_of_regime():
    assert evaluate(.249,RegimeStatus.INELIGIBLE,True)["exit_signal"]
    assert evaluate(-.249,RegimeStatus.INVALID,True)["exit_signal"]
    assert not evaluate(.25,RegimeStatus.ELIGIBLE,True)["exit_signal"]
    assert not evaluate(-.25,RegimeStatus.ELIGIBLE,True)["exit_signal"]

def test_sizing_never_rounds_up_and_missing_specs_unverified():
    assert theoretical_size(10000,0.001,None)["status"]=="UNVERIFIED"
    spec=BrokerSpec(tick_size=.0001,tick_value=10,contract_size=100000,account_currency="USD",minimum_lot=.01,maximum_lot=100,lot_increment=.01)
    r=theoretical_size(10000,.001,spec)
    assert r["status"]=="VERIFIED"
    assert r["estimated_risk"] <= r["risk_budget"]
    assert r["lots"] == 0.25
    assert abs(r["estimated_risk"]-r["risk_budget"]) < 1e-9
