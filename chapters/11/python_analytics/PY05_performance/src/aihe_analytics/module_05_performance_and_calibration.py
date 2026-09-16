from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .metrics import confusion_metrics
from .plotting import save_figure

MODULE_ID = "05"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out = ensure_output_dir(output_dir)
    data = read_sheet(input_path,"Predictions")
    require_columns(data,["actual","score"],"Predictions")
    data["actual"] = pd.to_numeric(data["actual"],errors="coerce")
    data["score"] = pd.to_numeric(data["score"],errors="coerce").clip(1e-6,1-1e-6)
    data = data.dropna(subset=["actual","score"])
    actual = data["actual"].astype(int).to_numpy()
    score = data["score"].to_numpy()
    if len(np.unique(actual)) < 2:
        raise ValueError("Actual outcomes must include 0 and 1.")

    rows=[]
    for t in np.arange(0.05,0.96,0.05):
        m=confusion_metrics(actual,(score>=t).astype(int))
        rows.append({"threshold":float(t),**m})
    threshold_df=pd.DataFrame(rows)
    threshold_df["youden_index"]=threshold_df["sensitivity"]+threshold_df["specificity"]-1
    threshold_df.to_csv(out/"threshold_performance.csv",index=False)

    auc=roc_auc_score(actual,score)
    brier=brier_score_loss(actual,score)
    fpr,tpr,_=roc_curve(actual,score)
    fig,ax=plt.subplots(figsize=(7.2,5))
    ax.plot(fpr,tpr,label=f"Model (AUC={auc:.3f})")
    ax.plot([0,1],[0,1],linestyle="--",label="Chance")
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate")
    ax.set_title("ROC curve"); ax.legend()
    save_figure(fig,out/"roc_curve.png")

    fig,ax=plt.subplots(figsize=(7.2,5))
    ax.plot(threshold_df["threshold"],threshold_df["sensitivity"],label="Sensitivity")
    ax.plot(threshold_df["threshold"],threshold_df["specificity"],label="Specificity")
    ax.plot(threshold_df["threshold"],threshold_df["ppv"],label="PPV")
    ax.set_ylim(0,1); ax.set_xlabel("Threshold"); ax.set_ylabel("Metric")
    ax.set_title("Threshold trade-offs"); ax.legend()
    save_figure(fig,out/"threshold_tradeoffs.png")

    logit_score=np.log(score/(1-score))
    calib=sm.GLM(actual,sm.add_constant(logit_score),family=sm.families.Binomial()).fit()
    data["bin"]=pd.qcut(data["score"],q=min(10,data["score"].nunique()),duplicates="drop")
    bins=data.groupby("bin",observed=True).agg(mean_predicted=("score","mean"),observed_rate=("actual","mean"),n=("actual","size")).reset_index(drop=True)
    bins.to_csv(out/"calibration_bins.csv",index=False)
    fig,ax=plt.subplots(figsize=(6.2,5.2))
    ax.plot(bins["mean_predicted"],bins["observed_rate"],marker="o",label="Observed")
    ax.plot([0,1],[0,1],linestyle="--",label="Perfect")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_xlabel("Mean predicted probability"); ax.set_ylabel("Observed rate")
    ax.set_title("Calibration plot"); ax.legend()
    save_figure(fig,out/"calibration_plot.png")

    best=threshold_df.loc[threshold_df["youden_index"].idxmax()]
    summary={"rows_used":int(len(data)),"auc":float(auc),"brier_score":float(brier),"calibration_intercept":float(calib.params[0]),"calibration_slope":float(calib.params[1]),"illustrative_threshold":float(best["threshold"])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(pd.Series(summary).to_string())
