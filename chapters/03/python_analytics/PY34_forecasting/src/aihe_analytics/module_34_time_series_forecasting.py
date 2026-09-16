from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    d=read_sheet(input_path,"TimeSeries");params=read_sheet(input_path,"Parameters")
    require_columns(d,["date","value"],"TimeSeries");require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    h=int(p.get("forecast_horizon",12));seasonal=int(p.get("seasonal_periods",12))
    d=d.copy();d["date"]=pd.to_datetime(d["date"]);d=d.sort_values("date").reset_index(drop=True)
    if len(d)<max(12,seasonal*2): raise ValueError("Provide at least two seasonal cycles or 12 observations.")
    holdout=min(h,max(3,len(d)//5));train=d.iloc[:-holdout];test=d.iloc[-holdout:]
    seasonal_component="add" if len(train)>=2*seasonal else None
    model=ExponentialSmoothing(train["value"],trend="add",seasonal=seasonal_component,seasonal_periods=seasonal if seasonal_component else None,initialization_method="estimated").fit()
    pred=model.forecast(holdout)
    mae=float(np.mean(np.abs(test["value"].to_numpy()-pred.to_numpy())))
    rmse=float(np.sqrt(np.mean((test["value"].to_numpy()-pred.to_numpy())**2)))
    final_model=ExponentialSmoothing(d["value"],trend="add",seasonal="add" if len(d)>=2*seasonal else None,
                                     seasonal_periods=seasonal if len(d)>=2*seasonal else None,initialization_method="estimated").fit()
    forecast=final_model.forecast(h)
    freq=pd.infer_freq(d["date"]) or "MS"
    future_dates=pd.date_range(d["date"].iloc[-1],periods=h+1,freq=freq)[1:]
    residual_sd=float(np.std(final_model.resid,ddof=1))
    f=pd.DataFrame({"date":future_dates,"forecast":forecast.to_numpy(),
                    "lower_95":forecast.to_numpy()-1.96*residual_sd,
                    "upper_95":forecast.to_numpy()+1.96*residual_sd})
    f.to_csv(out/"forecast.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,5));ax.plot(d["date"],d["value"],label="Observed")
    ax.plot(f["date"],f["forecast"],label="Forecast")
    ax.fill_between(f["date"],f["lower_95"],f["upper_95"],alpha=.2,label="Approximate 95% interval")
    ax.set_title("Operational or budget forecast");ax.legend()
    save_figure(fig,out/"forecast.png")
    payload={"holdout_mae":mae,"holdout_rmse":rmse,"forecast_horizon":h,"forecast_total":float(f["forecast"].sum())}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"34_time_series_forecasting",input_path,payload)
    return payload
