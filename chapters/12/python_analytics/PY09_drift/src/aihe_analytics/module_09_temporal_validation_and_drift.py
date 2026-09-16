from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from sklearn.metrics import brier_score_loss, roc_auc_score
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .metrics import psi
from .plotting import save_figure

MODULE_ID="09"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out=ensure_output_dir(output_dir)
    data=read_sheet(input_path,"Monitoring")
    require_columns(data,["period","actual","score","feature_1","feature_2"],"Monitoring")
    for c in ["actual","score","feature_1","feature_2"]:
        data[c]=pd.to_numeric(data[c],errors="coerce")
    data=data.dropna(subset=["period","actual","score"])
    periods=list(pd.unique(data["period"]))
    if len(periods)<2: raise ValueError("At least two periods are required.")
    baseline=data[data["period"]==periods[0]]
    rows=[]
    for period in periods:
        g=data[data["period"]==period]
        actual=g["actual"].astype(int); score=g["score"].clip(0,1)
        row={"period":period,"n":len(g),"auc":roc_auc_score(actual,score) if actual.nunique()>1 else np.nan,"brier_score":brier_score_loss(actual,score),"mean_score":score.mean(),"observed_rate":actual.mean(),"score_psi":psi(baseline["score"],score),"feature_1_psi":psi(baseline["feature_1"],g["feature_1"]),"feature_2_psi":psi(baseline["feature_2"],g["feature_2"]),"score_ks_pvalue":ks_2samp(baseline["score"].dropna(),score.dropna()).pvalue if period!=periods[0] else 1.0}
        row["review_flag"]=bool((pd.notna(row["auc"]) and row["auc"]<0.65) or row["score_psi"]>0.20 or row["brier_score"]>0.25)
        rows.append(row)
    metrics=pd.DataFrame(rows)
    metrics.to_csv(out/"temporal_validation_metrics.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.plot(metrics["period"].astype(str),metrics["auc"],marker="o",label="AUC")
    ax.plot(metrics["period"].astype(str),metrics["brier_score"],marker="o",label="Brier score")
    ax.set_xlabel("Period"); ax.set_ylabel("Metric"); ax.set_title("Temporal performance")
    ax.tick_params(axis="x",rotation=30); ax.legend()
    save_figure(fig,out/"temporal_performance.png")
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.plot(metrics["period"].astype(str),metrics["score_psi"],marker="o",label="Score PSI")
    ax.plot(metrics["period"].astype(str),metrics["feature_1_psi"],marker="o",label="Feature 1 PSI")
    ax.plot(metrics["period"].astype(str),metrics["feature_2_psi"],marker="o",label="Feature 2 PSI")
    ax.axhline(.20,linestyle="--",label="Illustrative review threshold")
    ax.set_xlabel("Period"); ax.set_ylabel("PSI"); ax.set_title("Distribution shift")
    ax.tick_params(axis="x",rotation=30); ax.legend()
    save_figure(fig,out/"drift_monitoring.png")
    summary={"periods":len(periods),"baseline_period":str(periods[0]),"periods_flagged":int(metrics["review_flag"].sum()),"latest_period":str(periods[-1])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(metrics.to_string(index=False))
