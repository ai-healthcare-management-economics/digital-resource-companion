from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    r=read_sheet(input_path,"Risks")
    require_columns(r,["risk_id","domain","description","likelihood","impact","control_effectiveness","owner","review_date","status","decision_trigger"],"Risks")
    d=r.copy();d["review_date"]=pd.to_datetime(d["review_date"],errors="coerce")
    d["inherent_risk"]=d["likelihood"].astype(float)*d["impact"].astype(float)
    ce=d["control_effectiveness"].astype(float).clip(0,1)
    d["residual_risk"]=d["inherent_risk"]*(1-ce)
    d["overdue"]=d["review_date"].notna() & (d["review_date"]<pd.Timestamp.today().normalize()) & ~d["status"].astype(str).str.lower().isin(["closed","accepted"])
    d["priority"]=pd.cut(d["residual_risk"],[-np.inf,4,9,15,np.inf],labels=["Low","Moderate","High","Critical"])
    d=d.sort_values(["residual_risk","overdue"],ascending=[False,False])
    d.to_csv(out/"prioritized_risk_register.csv",index=False)
    domain=d.groupby("domain",as_index=False).agg(risks=("risk_id","count"),mean_residual=("residual_risk","mean"),max_residual=("residual_risk","max"),overdue=("overdue","sum"))
    domain.to_csv(out/"risk_domain_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5));ax.bar(domain["domain"],domain["max_residual"])
    ax.set_ylabel("Maximum residual risk");ax.set_title("Risk exposure by domain");ax.tick_params(axis="x",rotation=35)
    save_figure(fig,out/"risk_by_domain.png")
    critical=d[d["priority"].astype(str)=="Critical"]
    payload={"risk_count":int(len(d)),"critical_risk_count":int(len(critical)),
             "overdue_action_count":int(d["overdue"].sum()),
             "highest_residual_risk":float(d["residual_risk"].max()) if len(d) else 0.0}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"26_integrated_risk_register",input_path,payload)
    return payload
