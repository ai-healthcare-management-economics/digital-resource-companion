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
    o=read_sheet(input_path,"Options")
    required=["option","incremental_effect","willingness_to_pay","incremental_lifecycle_cost","residual_value","recovered_value","recovery_realization_cost","monetized_environmental_externality","resilience_value","equity_adjustment_value","energy_kwh","water_l","carbon_kgco2e","virgin_material_kg","recovered_material_kg","useful_outputs","mandatory_failure"]
    require_columns(o,required,"Options")
    numeric=[c for c in required if c not in {"option","mandatory_failure"}]
    for c in numeric:o[c]=pd.to_numeric(o[c],errors="coerce").fillna(0.0)
    o["conventional_nmb"]=o["willingness_to_pay"]*o["incremental_effect"]-o["incremental_lifecycle_cost"]
    o["net_residual_and_recovered_value"]=o["residual_value"]+o["recovered_value"]-o["recovery_realization_cost"]
    o["circularity_adjusted_nmb"]=o["conventional_nmb"]+o["net_residual_and_recovered_value"]-o["monetized_environmental_externality"]+o["resilience_value"]+o["equity_adjustment_value"]
    denom=o["useful_outputs"].replace(0,np.nan)
    for src,dst in [("energy_kwh","energy_kwh_per_output"),("water_l","water_l_per_output"),("carbon_kgco2e","carbon_kgco2e_per_output"),("virgin_material_kg","virgin_material_kg_per_output"),("recovered_material_kg","recovered_material_kg_per_output")]:o[dst]=o[src]/denom
    fail=o["mandatory_failure"].astype(str).str.lower().isin(["yes","true","1","fail"])
    o["eligible_for_ranking"]=~fail
    ranked=o.loc[~fail].sort_values("circularity_adjusted_nmb",ascending=False).copy()
    ranked["rank"]=range(1,len(ranked)+1)
    result=o.merge(ranked[["option","rank"]],on="option",how="left")
    result.to_csv(out/"option_results.csv",index=False)
    best=ranked.iloc[0] if len(ranked) else None
    summary={"preferred_option":None if best is None else str(best["option"]),"preferred_circularity_adjusted_nmb":None if best is None else float(best["circularity_adjusted_nmb"]),"eligible_options":int((~fail).sum()),"mandatory_failures":int(fail.sum()),"interpretation_note":"Environmental and circularity indicators remain separate unless their monetization is justified. Do not double count residual value, avoided procurement, carbon, resilience, or equity effects."}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    pd.DataFrame({"measure":summary.keys(),"value":summary.values()}).to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5));plot=result.sort_values("circularity_adjusted_nmb");ax.barh(plot["option"],plot["circularity_adjusted_nmb"]);ax.axvline(0,linewidth=1);ax.set_xlabel("Circularity-adjusted net benefit");ax.set_title("Circularity-adjusted net benefit by option");save_figure(fig,out/"circularity_adjusted_nmb.png")
    fig,ax=plt.subplots(figsize=(8,5));ax.scatter(result["carbon_kgco2e_per_output"],result["incremental_lifecycle_cost"],s=80);[ax.annotate(r["option"],(r["carbon_kgco2e_per_output"],r["incremental_lifecycle_cost"])) for _,r in result.iterrows()];ax.set_xlabel("Carbon per useful output (kgCO2e)");ax.set_ylabel("Incremental lifecycle cost");ax.set_title("Cost and carbon remain visible as separate dimensions");save_figure(fig,out/"cost_carbon_tradeoff.png")
    write_metadata(out,"38_circularity_adjusted_economic_evaluation",input_path,summary)
    return summary
