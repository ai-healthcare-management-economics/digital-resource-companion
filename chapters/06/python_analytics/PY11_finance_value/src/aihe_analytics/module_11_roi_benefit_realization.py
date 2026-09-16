from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _params(df):
    require_columns(df, ["parameter","value"], "Parameters")
    return dict(zip(df["parameter"].astype(str), df["value"]))

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    benefits = read_sheet(input_path, "Benefits")
    costs = read_sheet(input_path, "Costs")
    params = _params(read_sheet(input_path, "Parameters"))
    require_columns(benefits, [
        "benefit_item","gross_annual_amount","realization_probability",
        "attributable_fraction","start_year","end_year"
    ], "Benefits")
    require_columns(costs, [
        "cost_item","one_time_cost","annual_recurring_cost","start_year","end_year"
    ], "Costs")
    horizon = int(params.get("time_horizon_years", 5))
    discount = float(params.get("annual_discount_rate", 0.03))
    annual = []
    for year in range(0, horizon + 1):
        gross = 0.0; realized = 0.0; cost = 0.0
        for _, r in benefits.iterrows():
            if int(r["start_year"]) <= year <= int(r["end_year"]) and year > 0:
                g = float(r["gross_annual_amount"])
                gross += g
                realized += g * float(r["realization_probability"]) * float(r["attributable_fraction"])
        for _, r in costs.iterrows():
            if year == int(r["start_year"]):
                cost += float(r["one_time_cost"])
            if int(r["start_year"]) <= year <= int(r["end_year"]) and year > 0:
                cost += float(r["annual_recurring_cost"])
        df = 1 / ((1 + discount) ** year)
        annual.append({
            "year": year, "gross_benefit": gross, "risk_adjusted_benefit": realized,
            "cost": cost, "pv_gross_benefit": gross*df,
            "pv_risk_adjusted_benefit": realized*df, "pv_cost": cost*df,
            "pv_net_benefit": (realized-cost)*df
        })
    annual_df = pd.DataFrame(annual)
    pv_benefit = annual_df["pv_risk_adjusted_benefit"].sum()
    pv_cost = annual_df["pv_cost"].sum()
    net = pv_benefit - pv_cost
    roi = net / pv_cost if pv_cost else np.nan
    annual_df["cumulative_pv_net_benefit"] = annual_df["pv_net_benefit"].cumsum()
    payback_candidates = annual_df.loc[annual_df["cumulative_pv_net_benefit"] >= 0, "year"]
    payback = int(payback_candidates.iloc[0]) if len(payback_candidates) else None
    summary = pd.DataFrame({
        "measure":["PV risk-adjusted benefit","PV total cost","PV net benefit","ROI","Payback year"],
        "value":[pv_benefit,pv_cost,net,roi,payback if payback is not None else "Not reached"]
    })
    annual_df.to_csv(out/"annual_roi_cashflow.csv", index=False)
    summary.to_csv(out/"summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(annual_df["year"], annual_df["cumulative_pv_net_benefit"], marker="o")
    ax.axhline(0, linewidth=1)
    ax.set_xlabel("Year"); ax.set_ylabel("Cumulative PV net benefit")
    ax.set_title("Benefit-realization and payback profile")
    save_figure(fig, out/"cumulative_net_benefit.png")
    payload = {"pv_benefit":float(pv_benefit),"pv_cost":float(pv_cost),"net_benefit":float(net),
               "roi":None if np.isnan(roi) else float(roi),"payback_year":payback}
    (out/"summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_metadata(out, "11_roi_benefit_realization", input_path, payload)
    return payload
