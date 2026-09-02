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
    p=read_sheet(input_path,"Portfolio")
    required=["year","asset_or_service","category","purchases_avoided","repairs","refurbishments","life_extension_years","energy_kwh","water_l","carbon_kgco2e","virgin_material_kg","recovered_material_kg","verified_takeback","unverified_disposition","residual_value","rebound_indicator","safety_or_continuity_incidents","service_outputs"]
    require_columns(p,required,"Portfolio")
    p["year"]=pd.to_numeric(p["year"],errors="coerce").astype("Int64")
    for c in required[3:]:p[c]=pd.to_numeric(p[c],errors="coerce").fillna(0.0)
    annual=p.groupby("year",as_index=False)[required[3:]].sum()
    denom=annual["service_outputs"].replace(0,np.nan)
    for src,dst in [("energy_kwh","energy_kwh_per_output"),("water_l","water_l_per_output"),("carbon_kgco2e","carbon_kgco2e_per_output"),("virgin_material_kg","virgin_material_kg_per_output")]:annual[dst]=annual[src]/denom
    annual["recovery_share"]=annual["recovered_material_kg"]/(annual["recovered_material_kg"]+annual["virgin_material_kg"]).replace(0,np.nan)
    annual["verified_disposition_share"]=annual["verified_takeback"]/(annual["verified_takeback"]+annual["unverified_disposition"]).replace(0,np.nan)
    annual.to_csv(out/"annual_portfolio_summary.csv",index=False)
    latest=annual.sort_values("year").iloc[-1]
    prev=annual.sort_values("year").iloc[-2] if len(annual)>1 else None
    summary={"latest_year":int(latest["year"]),"purchases_avoided":float(latest["purchases_avoided"]),"life_extension_years":float(latest["life_extension_years"]),"recovery_share":None if pd.isna(latest["recovery_share"]) else float(latest["recovery_share"]),"verified_disposition_share":None if pd.isna(latest["verified_disposition_share"]) else float(latest["verified_disposition_share"]),"carbon_change_from_previous":None if prev is None else float(latest["carbon_kgco2e"]-prev["carbon_kgco2e"]),"incident_change_from_previous":None if prev is None else float(latest["safety_or_continuity_incidents"]-prev["safety_or_continuity_incidents"])}
    flags=[]
    if summary["verified_disposition_share"] is not None and summary["verified_disposition_share"]<0.95:flags.append("Verified disposition share below 95%")
    if prev is not None and latest["rebound_indicator"]>prev["rebound_indicator"]:flags.append("Rebound indicator increased")
    if prev is not None and latest["safety_or_continuity_incidents"]>prev["safety_or_continuity_incidents"]:flags.append("Safety or continuity incidents increased")
    summary["review_flags"]=flags
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    pd.DataFrame({"measure":summary.keys(),"value":[json.dumps(v) if isinstance(v,list) else v for v in summary.values()]}).to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5));ax.plot(annual["year"],annual["carbon_kgco2e_per_output"],marker="o",label="Carbon/output");ax.plot(annual["year"],annual["energy_kwh_per_output"],marker="o",label="Energy/output");ax.set_title("Portfolio environmental intensity trends");ax.set_xlabel("Year");ax.legend();save_figure(fig,out/"environmental_intensity_trends.png")
    fig,ax=plt.subplots(figsize=(9,5));ax.plot(annual["year"],annual["repairs"],marker="o",label="Repairs");ax.plot(annual["year"],annual["refurbishments"],marker="o",label="Refurbishments");ax.plot(annual["year"],annual["purchases_avoided"],marker="o",label="Purchases avoided");ax.set_title("Asset-life and circular activity trends");ax.set_xlabel("Year");ax.legend();save_figure(fig,out/"circular_activity_trends.png")
    write_metadata(out,"39_annual_circularity_portfolio_review",input_path,summary)
    return summary
