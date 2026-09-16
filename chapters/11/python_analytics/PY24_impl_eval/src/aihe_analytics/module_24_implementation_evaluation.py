from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    df=read_sheet(input_path,"TimeSeries")
    require_columns(df,["date","outcome","implementation_flag","uptake","balancing_measure"],"TimeSeries")
    d=df.copy();d["date"]=pd.to_datetime(d["date"]);d=d.sort_values("date").reset_index(drop=True)
    d["time"]=np.arange(len(d))
    first_post=d.index[d["implementation_flag"].astype(int)==1]
    if len(first_post)==0: raise ValueError("At least one row must have implementation_flag=1.")
    intervention_index=int(first_post[0])
    d["post"]=d["implementation_flag"].astype(int)
    d["time_after"]=np.where(d["post"]==1,d["time"]-intervention_index,0)
    X=sm.add_constant(d[["time","post","time_after"]])
    model=sm.OLS(d["outcome"].astype(float),X).fit()
    d["fitted"]=model.predict(X)
    pre=d.loc[d["post"]==0,"outcome"].astype(float)
    mean=float(pre.mean());sd=float(pre.std(ddof=1))
    d["center_line"]=mean;d["ucl"]=mean+3*sd;d["lcl"]=mean-3*sd
    coef=pd.DataFrame({"term":model.params.index,"coefficient":model.params.values,
                       "std_error":model.bse.values,"p_value":model.pvalues.values})
    coef.to_csv(out/"segmented_regression.csv",index=False);d.to_csv(out/"implementation_timeseries.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(d["date"],d["outcome"],marker="o",label="Observed")
    ax.plot(d["date"],d["fitted"],label="Segmented trend")
    ax.axvline(d.loc[intervention_index,"date"],linestyle="--",label="Implementation")
    ax.set_ylabel("Outcome");ax.set_title("Interrupted time-series evaluation");ax.legend()
    save_figure(fig,out/"interrupted_time_series.png")
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(d["date"],d["outcome"],marker="o")
    ax.plot(d["date"],d["center_line"],label="Pre-implementation mean")
    ax.plot(d["date"],d["ucl"],linestyle="--",label="Upper control limit")
    ax.plot(d["date"],d["lcl"],linestyle="--",label="Lower control limit")
    ax.set_title("Quality-control chart");ax.legend()
    save_figure(fig,out/"control_chart.png")
    pre_mean=float(d.loc[d["post"]==0,"outcome"].mean());post_mean=float(d.loc[d["post"]==1,"outcome"].mean())
    payload={"pre_mean":pre_mean,"post_mean":post_mean,"level_change":float(model.params["post"]),
             "slope_change":float(model.params["time_after"]),"r_squared":float(model.rsquared)}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"24_implementation_evaluation",input_path,payload)
    return payload
