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
    tasks=read_sheet(input_path,"Tasks")
    require_columns(tasks,["task","baseline_minutes","ai_minutes","review_minutes","correction_minutes","annual_volume","redeployable_fraction","quality_factor","staff_cost_per_hour"],"Tasks")
    d=tasks.copy()
    d["gross_minutes_saved_per_task"]=d["baseline_minutes"]-d["ai_minutes"]
    d["net_minutes_saved_per_task"]=d["baseline_minutes"]-(d["ai_minutes"]+d["review_minutes"]+d["correction_minutes"])
    d["annual_net_hours_saved"]=d["net_minutes_saved_per_task"]*d["annual_volume"]/60
    d["released_capacity_hours"]=d["annual_net_hours_saved"]*d["redeployable_fraction"]
    d["quality_adjusted_capacity_hours"]=d["released_capacity_hours"]*d["quality_factor"]
    d["estimated_labor_value"]=d["quality_adjusted_capacity_hours"]*d["staff_cost_per_hour"]
    d["warning"]=np.where(d["net_minutes_saved_per_task"]<=0,"No net time saving",
                  np.where(d["redeployable_fraction"]<.25,"Savings may be too fragmented",""))
    d.to_csv(out/"workflow_productivity_results.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    x=np.arange(len(d));w=.35
    ax.bar(x-w/2,d["gross_minutes_saved_per_task"],width=w,label="Gross")
    ax.bar(x+w/2,d["net_minutes_saved_per_task"],width=w,label="Net")
    ax.set_xticks(x,d["task"],rotation=35,ha="right");ax.set_ylabel("Minutes per task")
    ax.set_title("Gross versus net AI-enabled time saving");ax.legend()
    save_figure(fig,out/"gross_vs_net_time_saving.png")
    payload={"annual_net_hours_saved":float(d["annual_net_hours_saved"].sum()),
             "quality_adjusted_capacity_hours":float(d["quality_adjusted_capacity_hours"].sum()),
             "estimated_labor_value":float(d["estimated_labor_value"].sum()),
             "tasks_with_no_net_saving":d.loc[d["net_minutes_saved_per_task"]<=0,"task"].astype(str).tolist()}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"28_workflow_productivity",input_path,payload)
    return payload
