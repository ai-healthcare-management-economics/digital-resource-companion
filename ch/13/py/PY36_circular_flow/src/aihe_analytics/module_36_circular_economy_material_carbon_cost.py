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

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    assets=read_sheet(input_path,"Assets")
    params=_params(read_sheet(input_path,"Parameters"))
    cols=["asset","category","quantity","expected_life_years","remaining_life_years","annual_energy_kwh","carbon_factor_kg_per_kwh","embodied_carbon_kg","annual_water_l","annual_operating_cost","repair_cost","refurbish_cost","residual_value","repairable","refurbishable","takeback_available","recovery_rate","useful_outputs_per_year"]
    require_columns(assets,cols,"Assets")
    horizon=int(params.get("horizon_years",5)); discount=float(params.get("discount_rate",0.03))
    x=assets.copy()
    for col in [c for c in cols if c not in ["asset","category"]]: x[col]=pd.to_numeric(x[col],errors="coerce").fillna(0)
    annuity=sum(1/((1+discount)**y) for y in range(1,horizon+1))
    x["annual_operational_carbon_kg"]=x["quantity"]*x["annual_energy_kwh"]*x["carbon_factor_kg_per_kwh"]
    x["pv_operating_cost"]=x["quantity"]*x["annual_operating_cost"]*annuity
    x["pv_total_cost"]=x["pv_operating_cost"]+x["quantity"]*(x["repair_cost"]+x["refurbish_cost"])-x["quantity"]*x["residual_value"]/((1+discount)**horizon)
    x["lifecycle_energy_kwh"]=x["quantity"]*x["annual_energy_kwh"]*horizon
    x["lifecycle_water_l"]=x["quantity"]*x["annual_water_l"]*horizon
    x["lifecycle_carbon_kg"]=x["quantity"]*x["embodied_carbon_kg"]+x["annual_operational_carbon_kg"]*horizon
    x["circularity_score_0_1"]=(x["repairable"]+x["refurbishable"]+x["takeback_available"]+x["recovery_rate"])/4
    denom=(x["quantity"]*x["useful_outputs_per_year"]*horizon).replace(0,np.nan)
    x["cost_per_useful_output"]=x["pv_total_cost"]/denom
    x["carbon_per_useful_output_kg"]=x["lifecycle_carbon_kg"]/denom
    x.to_csv(out/"asset_results.csv",index=False)
    by=x.groupby("category",as_index=False)[["pv_total_cost","lifecycle_energy_kwh","lifecycle_water_l","lifecycle_carbon_kg"]].sum()
    by.to_csv(out/"category_summary.csv",index=False)
    summary={"pv_total_cost":float(x["pv_total_cost"].sum()),"lifecycle_energy_kwh":float(x["lifecycle_energy_kwh"].sum()),"lifecycle_water_l":float(x["lifecycle_water_l"].sum()),"lifecycle_carbon_kg":float(x["lifecycle_carbon_kg"].sum()),"weighted_circularity_score":float(np.average(x["circularity_score_0_1"],weights=np.maximum(x["quantity"],1)))}
    pd.DataFrame({"measure":summary.keys(),"value":summary.values()}).to_csv(out/"summary.csv",index=False)
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    fig,ax=plt.subplots(figsize=(10,5));ax.bar(by["category"],by["pv_total_cost"]);ax.set_title("Present-value lifecycle cost by category");ax.set_ylabel("Present-value cost");ax.tick_params(axis="x",rotation=40);save_figure(fig,out/"lifecycle_cost_by_category.png")
    fig,ax=plt.subplots(figsize=(8,5));ax.scatter(x["circularity_score_0_1"],x["lifecycle_carbon_kg"],s=np.maximum(x["pv_total_cost"],1)**.35);ax.set_xlabel("Circularity score (0-1)");ax.set_ylabel("Lifecycle carbon (kgCO2e)");ax.set_title("Circularity and lifecycle carbon");save_figure(fig,out/"circularity_carbon_comparison.png")
    write_metadata(out,"36_circular_economy_material_carbon_cost",input_path,summary)
    return summary
