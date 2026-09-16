from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _parameters(frame: pd.DataFrame) -> dict:
    require_columns(frame, ["parameter", "value"], "Parameters")
    return dict(zip(frame["parameter"].astype(str), frame["value"]))

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    costs = read_sheet(input_path, "Costs")
    params = _parameters(read_sheet(input_path, "Parameters"))
    require_columns(costs, [
        "category","cost_item","one_time_cost","annual_recurring_cost",
        "start_year","end_year","low_multiplier","high_multiplier","budget_owner"
    ], "Costs")
    horizon = int(params.get("time_horizon_years", 5))
    discount = float(params.get("annual_discount_rate", 0.03))
    eligible_volume = float(params.get("annual_eligible_volume", 1000))
    uptake = float(params.get("uptake_rate", 1.0))
    rows = []
    for _, r in costs.iterrows():
        for year in range(0, horizon + 1):
            active = int(r["start_year"]) <= year <= int(r["end_year"])
            base = (float(r["one_time_cost"]) if year == int(r["start_year"]) else 0.0)
            if active and year > 0:
                base += float(r["annual_recurring_cost"])
            pv_factor = 1 / ((1 + discount) ** year)
            rows.append({
                "category": r["category"], "cost_item": r["cost_item"],
                "budget_owner": r["budget_owner"], "year": year,
                "undiscounted_base_cost": base,
                "pv_base_cost": base * pv_factor,
                "pv_low_cost": base * float(r["low_multiplier"]) * pv_factor,
                "pv_high_cost": base * float(r["high_multiplier"]) * pv_factor,
            })
    detail = pd.DataFrame(rows)
    by_category = detail.groupby("category", as_index=False)[
        ["pv_low_cost","pv_base_cost","pv_high_cost"]
    ].sum()
    by_year = detail.groupby("year", as_index=False)[
        ["pv_low_cost","pv_base_cost","pv_high_cost"]
    ].sum()
    total_low = by_category["pv_low_cost"].sum()
    total_base = by_category["pv_base_cost"].sum()
    total_high = by_category["pv_high_cost"].sum()
    total_uses = max(eligible_volume * uptake * horizon, 1)
    summary = pd.DataFrame({
        "measure": [
            "Present value total cost - low",
            "Present value total cost - base",
            "Present value total cost - high",
            "Base cost per expected use",
            "Time horizon (years)",
            "Discount rate",
        ],
        "value": [total_low,total_base,total_high,total_base/total_uses,horizon,discount],
    })
    detail.to_csv(out/"annual_cost_detail.csv", index=False)
    by_category.to_csv(out/"cost_by_category.csv", index=False)
    by_year.to_csv(out/"cost_by_year.csv", index=False)
    summary.to_csv(out/"summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(by_category["category"], by_category["pv_base_cost"])
    ax.set_ylabel("Present value cost")
    ax.set_title("Base-case lifecycle cost by category")
    ax.tick_params(axis="x", rotation=45)
    save_figure(fig, out/"cost_by_category.png")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(by_year["year"], by_year["pv_base_cost"], marker="o", label="Base")
    ax.fill_between(by_year["year"], by_year["pv_low_cost"], by_year["pv_high_cost"], alpha=0.2, label="Low-high range")
    ax.set_xlabel("Year"); ax.set_ylabel("Present value cost")
    ax.set_title("Lifecycle cost profile"); ax.legend()
    save_figure(fig, out/"cost_by_year.png")
    payload = {
        "pv_total_low": float(total_low), "pv_total_base": float(total_base),
        "pv_total_high": float(total_high), "base_cost_per_expected_use": float(total_base/total_uses)
    }
    (out/"summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_metadata(out, "10_tcaio_lifecycle_costing", input_path, payload)
    return payload
