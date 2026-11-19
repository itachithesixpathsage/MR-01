from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
import pandas as pd
from .. import __version__
from ..config import StrategyConfig
from ..variants import Variant

def sha256(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def make_manifest(m5_path,h1_path,m5,h1,variant: Variant,config: StrategyConfig,warnings:list[str],source_meta=None) -> dict:
    def meta(path,frame):
        ts=pd.to_datetime(frame.timestamp,utc=True).dropna()
        return {"filename":str(path),"sha256":sha256(path),"rows":len(frame),"date_start_utc":str(ts.min()) if len(ts) else None,"date_end_utc":str(ts.max()) if len(ts) else None}
    return {"software":"mr01-independent-calculator","software_version":__version__,"execution_timestamp_utc":datetime.now(timezone.utc).isoformat(),"datasets":{"m5":{**meta(m5_path,m5),"source_metadata":(source_meta or ({},{}))[0]},"h1":{**meta(h1_path,h1),"source_metadata":(source_meta or ({},{}))[1]}},"instrument":config.instrument,"timeframes":{"m5":"M5","h1":"H1"},"variant":variant.value,"parameters":config.model_dump(),"data_quality_warnings":warnings}

def write_manifest(path,manifest): Path(path).write_text(json.dumps(manifest,indent=2,default=str)+"\n")
