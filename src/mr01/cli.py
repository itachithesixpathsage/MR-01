from pathlib import Path
import json
import logging
import typer
import pandas as pd
from .data.ingestion import read_ohlc_csv
from .data.validation import validate_ohlc
from .variants import Variant
from .config import load_config
from .strategy.calculator import calculate
from .indicators.ema import ema
from .strategy.position_sizing import BrokerSpec
from .reporting.exports import write_quality, write_results, write_comparison
from .reporting.manifests import make_manifest, write_manifest

app=typer.Typer(no_args_is_help=True,help="Standalone MR-01 calculation and research CLI; no execution connectivity.")
logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")

def load_pair(m5_path,h1_path):
    m5,m5meta=read_ohlc_csv(m5_path); h1,h1meta=read_ohlc_csv(h1_path)
    q5=validate_ohlc(m5,5,50); q1=validate_ohlc(h1,60,50)
    return m5,h1,(q5,q1),(m5meta,h1meta)

def emit_quality(q5,q1,outdir):
    Path(outdir).mkdir(parents=True,exist_ok=True)
    write_quality(Path(outdir)/"data_quality_report.md","M5",q5); write_quality(Path(outdir)/"h1_data_quality_report.md","H1",q1)
    if not q5.valid or not q1.valid:
        raise typer.BadParameter("Input data failed validation; review data_quality_report.md")

@app.command("validate-data")
def validate_data(m5:Path=typer.Option(...,exists=True),h1:Path=typer.Option(...,exists=True),out:Path=typer.Option(Path("reports"))):
    a,b,qs,_=load_pair(m5,h1); emit_quality(*qs,out)
    typer.echo(json.dumps({"m5":qs[0].to_dict(),"h1":qs[1].to_dict()},indent=2))

@app.command("calculate")
def calculate_cmd(instrument:str=typer.Option("EURUSD"),variant:str=typer.Option(...,help="original or completed"),m5:Path=typer.Option(...,exists=True),h1:Path=typer.Option(...,exists=True),out:Path=typer.Option(Path("reports")),position:str=typer.Option("unknown",help="open, flat, or unknown"),equity:float | None=typer.Option(None),broker_spec:Path | None=typer.Option(None,exists=True),config_file:Path | None=typer.Option(None,exists=True,help="Optional YAML strategy configuration")):
    """Calculate indicators/signals for exactly one variant."""
    v=_variant(variant); a,b,qs,metas=load_pair(m5,h1); emit_quality(*qs,out)
    config=load_config(config_file)
    if instrument.upper().replace("/", "") != config.instrument:
        raise typer.BadParameter("--instrument must match the EURUSD instrument in config")
    spec=BrokerSpec.model_validate_json(broker_spec.read_text()) if broker_spec else None
    pos=_position(position)
    result=calculate(a,b,v,position_open=pos,equity=equity,broker_spec=spec,config=config)
    write_results(out,result)
    warnings=[]
    if v is Variant.ORIGINAL: warnings.append("OHLC history does not preserve forming-bar snapshots; original index-0 values cannot be independently reconstructed from finalized bars.")
    if spec is None: warnings.append("Broker contract specifications unavailable; theoretical sizing status is UNVERIFIED.")
    write_manifest(Path(out)/"run_manifest.json",make_manifest(m5,h1,a,b,v,config,warnings,metas))
    typer.echo(f"Wrote {len(result)} rows for {v.value} to {out}")

@app.command()
def compare(m5:Path=typer.Option(...,exists=True),h1:Path=typer.Option(...,exists=True),out:Path=typer.Option(Path("reports")),config_file:Path | None=typer.Option(None,exists=True,help="Optional YAML strategy configuration")):
    a,b,qs,metas=load_pair(m5,h1); emit_quality(*qs,out)
    config=load_config(config_file)
    r=calculate(a,b,Variant.ORIGINAL,position_open=None,config=config); c=calculate(a,b,Variant.COMPLETED,position_open=None,config=config)
    write_comparison(out,r,c)
    warnings=["OHLC history cannot reproduce forming-bar snapshots for MR-01A-R."]
    write_manifest(Path(out)/"run_manifest_R.json",make_manifest(m5,h1,a,b,Variant.ORIGINAL,config,warnings,metas))
    write_manifest(Path(out)/"run_manifest_C.json",make_manifest(m5,h1,a,b,Variant.COMPLETED,config,[],metas))
    typer.echo(f"Wrote separate-variant comparison to {out}/variant_comparison.csv")

@app.command()
def inspect(timestamp:str=typer.Argument(...,help="UTC timestamp; exact calculated decision timestamp"),variant:str=typer.Option(...),m5:Path=typer.Option(...,exists=True),h1:Path=typer.Option(...,exists=True),position:str=typer.Option("unknown"),equity:float | None=typer.Option(None),broker_spec:Path | None=typer.Option(None,exists=True),config_file:Path | None=typer.Option(None,exists=True,help="Optional YAML strategy configuration"),out:Path=typer.Option(Path("reports"))):
    v=_variant(variant); a,b,qs,_=load_pair(m5,h1); emit_quality(*qs,out)
    spec=BrokerSpec.model_validate_json(broker_spec.read_text()) if broker_spec else None
    config=load_config(config_file)
    result=calculate(a,b,v,position_open=_position(position),equity=equity,broker_spec=spec,config=config)
    t=pd.to_datetime(timestamp,utc=True); row=result[result.timestamp==t]
    if row.empty: raise typer.BadParameter("No exact decision timestamp found")
    record=row.iloc[0].to_dict()
    completed=v is Variant.COMPLETED
    # Convert decision time back to the selected M5 candle. CSV timestamps label opens.
    selected_time=t-pd.Timedelta(minutes=5) if completed else t
    mi=int(a.index[a.timestamp==selected_time][0]) if (a.timestamp==selected_time).any() else None
    if mi is None: raise typer.BadParameter("Selected M5 source candle was not found")
    start=max(0,mi-49)
    m5_window=a.iloc[start:mi+1][["timestamp","close"]].to_dict(orient="records")
    # Show enough H1 closes to cover EMA warm-up and the compared EMA shifts.
    eligible_h1=a.iloc[mi].timestamp
    if completed: eligible_h1=selected_time+pd.Timedelta(minutes=5)
    hi_candidates=b.index[b.timestamp<=eligible_h1]
    if completed: hi_candidates=b.index[(b.timestamp+pd.Timedelta(hours=1))<=eligible_h1]
    hi=int(hi_candidates[-1]) if len(hi_candidates) else -1
    h1_values=b.iloc[:hi+1][["timestamp","close"]].copy() if hi>=0 else b.iloc[:0][["timestamp","close"]].copy()
    h1_values["ema50"]=ema(b.close,50).iloc[:hi+1].to_numpy() if hi>=0 else []
    h1_window=h1_values.to_dict(orient="records")
    atr_window=a.iloc[:mi+1][["timestamp","high","low","close"]].to_dict(orient="records")
    record.update({"zscore_input_closes_m5":m5_window,"h1_ema_input_closes":h1_window,"atr_wilder_input_history_m5":atr_window,"sizing_assumptions":{"equity_supplied":equity is not None,"broker_spec_supplied":spec is not None,"sizing_reference_is_stop_loss":False}})
    typer.echo(json.dumps(record,indent=2,default=str))

@app.command()
def report(input:Path=typer.Option(...,exists=True),out:Path=typer.Option(Path("reports"))):
    """Build a concise Markdown summary from an indicator_calculations.csv output."""
    df=pd.read_csv(input)
    variants=sorted(df.variant.dropna().unique())
    if len(variants) != 1:
        raise typer.BadParameter("Report input must contain exactly one variant; run separate reports for MR-01A-R and MR-01A-C")
    counts=df.entry_signal.value_counts(dropna=False).to_dict()
    lines=["# MR-01 calculation report","",f"- Rows: {len(df)}",f"- Variant: {variants[0]}",f"- Calculation statuses: {json.dumps(df.calculation_status.value_counts().to_dict())}",f"- Entry signal counts: {json.dumps(counts)}",f"- Exits: {int(df.exit_signal.astype(str).str.lower().eq('true').sum())}","","This is a signal calculation report, not a performance evaluation. No historical backtest is performed in M1.",""]
    out.mkdir(parents=True,exist_ok=True); (out/"signal_report.md").write_text("\n".join(lines)); typer.echo(str(out/"signal_report.md"))

def _position(value):
    states={"open":True,"flat":False,"unknown":None}
    try: return states[value.lower()]
    except KeyError: raise typer.BadParameter("position must be open, flat, or unknown")

def _variant(value):
    v=value.lower()
    if v in ("original","r","mr-01a-r"): return Variant.ORIGINAL
    if v in ("completed","c","mr-01a-c"): return Variant.COMPLETED
    raise typer.BadParameter("variant must be original or completed")

if __name__=="__main__": app()
