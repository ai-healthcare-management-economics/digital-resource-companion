from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    options=read_sheet(input_path,"Options");params=read_sheet(input_path,"Parameters")
    require_columns(options,["option","unit_cost","value_per_unit","maximum_units","workforce_hours_per_unit","capacity_units_per_unit","minimum_units"],"Options")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    c=-options["value_per_unit"].astype(float).to_numpy()
    A=np.vstack([options["unit_cost"],options["workforce_hours_per_unit"],options["capacity_units_per_unit"]]).astype(float)
    b=np.array([float(p.get("budget_available",1000000)),float(p.get("workforce_hours_available",10000)),float(p.get("capacity_units_available",10000))])
    bounds=list(zip(options["minimum_units"].astype(float),options["maximum_units"].astype(float)))
    res=linprog(c,A_ub=A,b_ub=b,bounds=bounds,method="highs")
    if not res.success: raise ValueError(f"Optimization failed: {res.message}")
    result=options.copy();result["optimal_units"]=res.x
    result["total_cost"]=result["optimal_units"]*result["unit_cost"]
    result["total_value"]=result["optimal_units"]*result["value_per_unit"]
    result["workforce_used"]=result["optimal_units"]*result["workforce_hours_per_unit"]
    result["capacity_used"]=result["optimal_units"]*result["capacity_units_per_unit"]
    result.to_csv(out/"optimal_allocation.csv",index=False)
    resource=pd.DataFrame({
        "resource":["Budget","Workforce hours","Capacity units"],
        "available":b,
        "used":[result["total_cost"].sum(),result["workforce_used"].sum(),result["capacity_used"].sum()]
    })
    resource["utilization"]=resource["used"]/resource["available"]
    resource.to_csv(out/"resource_utilization.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5));ax.bar(result["option"],result["optimal_units"])
    ax.set_ylabel("Optimal units");ax.set_title("Constrained resource allocation");ax.tick_params(axis="x",rotation=35)
    save_figure(fig,out/"optimal_allocation.png")
    payload={"maximum_expected_value":float(result["total_value"].sum()),
             "total_cost":float(result["total_cost"].sum()),
             "binding_resources":resource.loc[resource["utilization"]>.999,"resource"].astype(str).tolist()}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"35_resource_allocation_optimization",input_path,payload)
    return payload
