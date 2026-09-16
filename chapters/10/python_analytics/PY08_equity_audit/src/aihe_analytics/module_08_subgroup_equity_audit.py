from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import brier_score_loss, roc_auc_score
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .metrics import confusion_metrics
from .plotting import save_figure

MODULE_ID="08"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out=ensure_output_dir(output_dir)
    data=read_sheet(input_path,"Predictions")
    require_columns(data,["actual","score","subgroup"],"Predictions")
    data["actual"]=pd.to_numeric(data["actual"],errors="coerce")
    data["score"]=pd.to_numeric(data["score"],errors="coerce")
    data=data.dropna(subset=["actual","score","subgroup"])
    threshold=0.5
    if "threshold" in data and pd.to_numeric(data["threshold"],errors="coerce").notna().any():
        threshold=float(pd.to_numeric(data["threshold"],errors="coerce").dropna().iloc[0])
    rows=[]
    for subgroup,group in data.groupby("subgroup"):
        actual=group["actual"].astype(int).to_numpy()
        score=group["score"].clip(0,1).to_numpy()
        m=confusion_metrics(actual,(score>=threshold).astype(int))
        rows.append({"subgroup":subgroup,"n":len(group),"auc":roc_auc_score(actual,score) if len(np.unique(actual))>1 else np.nan,"brier_score":brier_score_loss(actual,score),"mean_predicted":score.mean(),"observed_rate":actual.mean(),**m})
    audit=pd.DataFrame(rows)
    audit.to_csv(out/"subgroup_equity_audit.csv",index=False)
    gap_rows=[]
    for metric in ["sensitivity","specificity","ppv","selection_rate","observed_rate"]:
        vals=audit[metric].dropna()
        gap_rows.append({"metric":metric,"minimum":vals.min(),"maximum":vals.max(),"absolute_gap":vals.max()-vals.min()})
    gaps=pd.DataFrame(gap_rows).sort_values("absolute_gap",ascending=False)
    gaps.to_csv(out/"disparity_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5))
    ax.bar(audit["subgroup"].astype(str),audit["sensitivity"])
    ax.set_ylim(0,1); ax.set_ylabel("Sensitivity"); ax.set_title(f"Sensitivity by subgroup at threshold {threshold:.2f}")
    ax.tick_params(axis="x",rotation=30)
    save_figure(fig,out/"subgroup_sensitivity.png")
    fig,ax=plt.subplots(figsize=(6.2,5.2))
    ax.scatter(audit["mean_predicted"],audit["observed_rate"],s=np.maximum(audit["n"],20))
    for _,r in audit.iterrows(): ax.annotate(str(r["subgroup"]),(r["mean_predicted"],r["observed_rate"]))
    ax.plot([0,1],[0,1],linestyle="--")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_xlabel("Mean predicted risk"); ax.set_ylabel("Observed rate")
    ax.set_title("Subgroup calibration overview")
    save_figure(fig,out/"subgroup_calibration.png")
    summary={"rows_used":int(len(data)),"groups":int(len(audit)),"largest_gap_metric":str(gaps.iloc[0]["metric"]),"largest_absolute_gap":float(gaps.iloc[0]["absolute_gap"])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(audit.to_string(index=False))
