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
    s=read_sheet(input_path,"Scenarios")
    require_columns(s,[
        "scenario","fixed_fee","per_use_fee","eligible_volume","adoption_rate",
        "benefit_per_use","realization_probability","implementation_cost","performance_payment"
    ],"Scenarios")
    r=s.copy()
    r["active_uses"]=r["eligible_volume"]*r["adoption_rate"]
    r["total_cost"]=r["fixed_fee"]+r["active_uses"]*r["per_use_fee"]+r["implementation_cost"]+r["performance_payment"]
    r["realized_benefit"]=r["active_uses"]*r["benefit_per_use"]*r["realization_probability"]
    r["net_benefit"]=r["realized_benefit"]-r["total_cost"]
    r["roi"]=np.where(r["total_cost"]>0,r["net_benefit"]/r["total_cost"],np.nan)
    r["cost_per_active_use"]=np.where(r["active_uses"]>0,r["total_cost"]/r["active_uses"],np.nan)
    r=r.sort_values("net_benefit",ascending=False)
    r.to_csv(out/"pricing_scenario_results.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(r["scenario"],r["net_benefit"])
    ax.axhline(0,linewidth=1)
    ax.set_ylabel("Net benefit");ax.set_title("AI contract scenario comparison")
    ax.tick_params(axis="x",rotation=35)
    save_figure(fig,out/"pricing_scenarios.png")
    best=r.iloc[0]
    payload={"best_scenario":str(best["scenario"]),"best_net_benefit":float(best["net_benefit"]),
             "best_roi":None if pd.isna(best["roi"]) else float(best["roi"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"17_ai_pricing_contract_scenarios",input_path,payload)
    return payload
