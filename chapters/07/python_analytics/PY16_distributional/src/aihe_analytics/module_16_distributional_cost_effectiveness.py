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
    groups=read_sheet(input_path,"Groups")
    params=read_sheet(input_path,"Parameters")
    require_columns(groups,["group","population","incremental_cost","incremental_effect","equity_weight","access_rate"],"Groups")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    wtp=float(p.get("willingness_to_pay",50000))
    result=groups.copy()
    result["access_adjusted_effect"]=result["incremental_effect"]*result["access_rate"]
    result["nmb_per_person"]=wtp*result["access_adjusted_effect"]-result["incremental_cost"]
    result["total_nmb"]=result["nmb_per_person"]*result["population"]
    result["equity_weighted_nmb"]=result["total_nmb"]*result["equity_weight"]
    result["effect_per_1000"]=result["access_adjusted_effect"]*1000
    result.to_csv(out/"distributional_results.csv",index=False)
    total_nmb=float(result["total_nmb"].sum())
    weighted=float(result["equity_weighted_nmb"].sum())
    max_gap=float(result["effect_per_1000"].max()-result["effect_per_1000"].min())
    fig,ax=plt.subplots(figsize=(9,5))
    x=np.arange(len(result))
    ax.bar(x-.18,result["total_nmb"],width=.36,label="Unweighted total NMB")
    ax.bar(x+.18,result["equity_weighted_nmb"],width=.36,label="Equity-weighted NMB")
    ax.set_xticks(x,result["group"],rotation=30,ha="right")
    ax.set_ylabel("Net monetary benefit");ax.set_title("Distribution of value by group");ax.legend()
    save_figure(fig,out/"distributional_nmb.png")
    payload={"total_nmb":total_nmb,"equity_weighted_nmb":weighted,
             "max_access_adjusted_effect_gap_per_1000":max_gap,
             "lowest_access_group":str(result.loc[result["access_rate"].idxmin(),"group"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"16_distributional_cost_effectiveness",input_path,payload)
    return payload
