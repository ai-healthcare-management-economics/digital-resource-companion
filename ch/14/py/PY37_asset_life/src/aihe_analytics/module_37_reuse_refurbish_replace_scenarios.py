from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _params(frame: pd.DataFrame) -> dict:
    require_columns(frame,["parameter","value"],"Parameters")
    return dict(zip(frame["parameter"].astype(str),frame["value"]))

def _minmax(series: pd.Series, higher_is_better: bool=False) -> pd.Series:
    lo,hi=float(series.min()),float(series.max())
    if hi==lo:return pd.Series(np.ones(len(series)),index=series.index)
    z=(series-lo)/(hi-lo)
    return z if higher_is_better else 1-z

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    o=read_sheet(input_path,"Options")
    p=_params(read_sheet(input_path,"Parameters")); w=_params(read_sheet(input_path,"Weights"))
    cols=["option","upfront_cost","annual_operating_cost","annual_energy_kwh","annual_carbon_kg","expected_life_years","annual_downtime_hours","annual_risk_cost","transition_cost","residual_value","circularity_score","safety_score","mandatory_failure"]
    require_columns(o,cols,"Options")
    for col in cols[1:-1]:o[col]=pd.to_numeric(o[col],errors="coerce").fillna(0)
    horizon=int(p.get("horizon_years",5));discount=float(p.get("discount_rate",0.03));annuity=sum(1/((1+discount)**y) for y in range(1,horizon+1))
    o["pv_lifecycle_cost"]=o["upfront_cost"]+o["transition_cost"]+(o["annual_operating_cost"]+o["annual_risk_cost"])*annuity-o["residual_value"]/((1+discount)**horizon)
    o["lifecycle_carbon_kg"]=o["annual_carbon_kg"]*horizon
    o["lifecycle_energy_kwh"]=o["annual_energy_kwh"]*horizon
    o["lifecycle_downtime_hours"]=o["annual_downtime_hours"]*horizon
    scores=pd.DataFrame(index=o.index)
    scores["cost"]=_minmax(o["pv_lifecycle_cost"]);scores["carbon"]=_minmax(o["lifecycle_carbon_kg"]);scores["downtime"]=_minmax(o["lifecycle_downtime_hours"]);scores["circularity"]=_minmax(o["circularity_score"],True);scores["safety"]=_minmax(o["safety_score"],True)
    totalw=sum(float(w.get(k,0)) for k in scores.columns) or 1
    o["weighted_score"]=sum(scores[k]*float(w.get(k,0)) for k in scores.columns)/totalw
    fail=o["mandatory_failure"].astype(str).str.lower().isin(["yes","true","1"]);o.loc[fail,"weighted_score"]=-1
    o["rank"]=o["weighted_score"].rank(ascending=False,method="min").astype(int)
    o.sort_values("rank").to_csv(out/"option_ranking.csv",index=False)
    best=o.sort_values("rank").iloc[0]
    summary={"preferred_option":str(best["option"]),"preferred_score":float(best["weighted_score"]),"preferred_pv_lifecycle_cost":float(best["pv_lifecycle_cost"]),"preferred_lifecycle_carbon_kg":float(best["lifecycle_carbon_kg"])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    pd.DataFrame({"measure":summary.keys(),"value":summary.values()}).to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5));colors=["tab:red" if f else "tab:blue" for f in fail];ax.scatter(o["lifecycle_carbon_kg"],o["pv_lifecycle_cost"],s=90,c=colors);[ax.annotate(r["option"],(r["lifecycle_carbon_kg"],r["pv_lifecycle_cost"])) for _,r in o.iterrows()];ax.set_xlabel("Lifecycle carbon (kgCO2e)");ax.set_ylabel("PV lifecycle cost");ax.set_title("Reuse-refurbish-replace option comparison");save_figure(fig,out/"cost_carbon_options.png")
    fig,ax=plt.subplots(figsize=(8,5));order=o.sort_values("weighted_score");ax.barh(order["option"],order["weighted_score"]);ax.set_xlabel("Weighted decision score");ax.set_title("Option ranking after mandatory safeguards");save_figure(fig,out/"weighted_option_scores.png")
    write_metadata(out,"37_reuse_refurbish_replace_scenarios",input_path,summary)
    return summary
