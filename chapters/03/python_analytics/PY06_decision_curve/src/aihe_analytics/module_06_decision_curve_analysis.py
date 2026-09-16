from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID="06"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out=ensure_output_dir(output_dir)
    data=read_sheet(input_path,"Predictions")
    require_columns(data,["actual","score"],"Predictions")
    actual=pd.to_numeric(data["actual"],errors="coerce")
    score=pd.to_numeric(data["score"],errors="coerce")
    valid=actual.notna()&score.notna()
    actual=actual.loc[valid].astype(int).to_numpy()
    score=score.loc[valid].clip(0,1).to_numpy()
    n=len(actual); prevalence=actual.mean()
    rows=[]
    for t in np.arange(0.02,0.81,0.02):
        pred=score>=t
        tp=((pred==1)&(actual==1)).sum()
        fp=((pred==1)&(actual==0)).sum()
        w=t/(1-t)
        model_nb=tp/n-fp/n*w
        all_nb=prevalence-(1-prevalence)*w
        rows.append({"threshold":t,"model_net_benefit":model_nb,"treat_all":all_nb,"treat_none":0.0})
    result=pd.DataFrame(rows)
    result["model_best"]=(result["model_net_benefit"]>result["treat_all"])&(result["model_net_benefit"]>0)
    result.to_csv(out/"decision_curve.csv",index=False)
    fig,ax=plt.subplots(figsize=(7.5,5))
    ax.plot(result["threshold"],result["model_net_benefit"],label="Model")
    ax.plot(result["threshold"],result["treat_all"],label="Treat all")
    ax.plot(result["threshold"],result["treat_none"],label="Treat none")
    ax.set_xlabel("Threshold probability"); ax.set_ylabel("Net benefit")
    ax.set_title("Decision-curve analysis"); ax.legend()
    save_figure(fig,out/"decision_curve.png")
    useful=result.loc[result["model_best"],"threshold"]
    summary={"rows_used":n,"prevalence":float(prevalence),"useful_threshold_min":float(useful.min()) if len(useful) else None,"useful_threshold_max":float(useful.max()) if len(useful) else None}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(pd.Series(summary).to_string())
