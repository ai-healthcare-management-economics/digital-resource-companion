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
    branches=read_sheet(input_path,"Branches")
    params=read_sheet(input_path,"Parameters")
    require_columns(branches,["strategy","role","branch","probability","cost","effect","events"],"Branches")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    wtp=float(p.get("willingness_to_pay",50000))
    cohort=float(p.get("cohort_size",1000))
    probs=branches.groupby("strategy")["probability"].sum()
    if ((probs-1).abs()>1e-6).any():
        bad=probs[(probs-1).abs()>1e-6]
        raise ValueError(f"Branch probabilities must sum to 1 within each strategy. Found: {bad.to_dict()}")
    b=branches.copy()
    b["weighted_cost"]=b["probability"]*b["cost"]
    b["weighted_effect"]=b["probability"]*b["effect"]
    b["weighted_events"]=b["probability"]*b["events"]
    summary=b.groupby(["strategy","role"],as_index=False)[["weighted_cost","weighted_effect","weighted_events"]].sum()
    summary=summary.rename(columns={"weighted_cost":"expected_cost","weighted_effect":"expected_effect","weighted_events":"expected_events"})
    summary["nmb"]=wtp*summary["expected_effect"]-summary["expected_cost"]
    summary["cohort_cost"]=summary["expected_cost"]*cohort
    summary["cohort_effect"]=summary["expected_effect"]*cohort
    summary.to_csv(out/"strategy_expected_values.csv",index=False)
    b.to_csv(out/"branch_contributions.csv",index=False)
    comp_rows=summary[summary["role"].astype(str).str.lower()=="comparator"]
    ai_rows=summary[summary["role"].astype(str).str.lower()=="ai"]
    if len(comp_rows)!=1 or len(ai_rows)!=1:
        raise ValueError("Branches must define exactly one comparator strategy and one AI strategy using the role column.")
    comp=comp_rows.iloc[0]; ai=ai_rows.iloc[0]
    dc=float(ai["expected_cost"]-comp["expected_cost"])
    de=float(ai["expected_effect"]-comp["expected_effect"])
    incremental={"comparator":str(comp["strategy"]),"ai_strategy":str(ai["strategy"]),
                 "incremental_cost":dc,"incremental_effect":de,
                 "icer":None if de==0 else float(dc/de),
                 "incremental_nmb":float(ai["nmb"]-comp["nmb"])}
    fig,ax=plt.subplots(figsize=(9,5))
    pivot=b.pivot_table(index="strategy",columns="branch",values="weighted_cost",aggfunc="sum",fill_value=0)
    pivot.plot(kind="bar",stacked=True,ax=ax)
    ax.set_ylabel("Expected cost contribution");ax.set_title("Decision-tree branch cost contributions")
    save_figure(fig,out/"branch_cost_contributions.png")
    (out/"summary.json").write_text(json.dumps(incremental,indent=2),encoding="utf-8")
    write_metadata(out,"18_decision_tree_pathway",input_path,incremental)
    return incremental
