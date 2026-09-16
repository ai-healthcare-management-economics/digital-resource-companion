from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    years = read_sheet(input_path, "Years")
    require_columns(years, [
        "year","eligible_population","adoption_rate","implementation_cost",
        "recurring_cost_per_user","savings_per_user","low_multiplier","high_multiplier"
    ], "Years")
    result = years.copy()
    result["users"] = result["eligible_population"] * result["adoption_rate"]
    result["recurring_cost"] = result["users"] * result["recurring_cost_per_user"]
    result["estimated_savings"] = result["users"] * result["savings_per_user"]
    result["net_budget_impact"] = result["implementation_cost"] + result["recurring_cost"] - result["estimated_savings"]
    result["low_net_budget_impact"] = result["implementation_cost"] + result["recurring_cost"] - result["estimated_savings"]*result["high_multiplier"]
    result["high_net_budget_impact"] = result["implementation_cost"] + result["recurring_cost"] - result["estimated_savings"]*result["low_multiplier"]
    result["cumulative_net_budget_impact"] = result["net_budget_impact"].cumsum()
    result.to_csv(out/"budget_impact_by_year.csv", index=False)
    summary = {
        "total_base_budget_impact":float(result["net_budget_impact"].sum()),
        "total_low_budget_impact":float(result["low_net_budget_impact"].sum()),
        "total_high_budget_impact":float(result["high_net_budget_impact"].sum()),
        "first_year_with_net_savings": None
    }
    candidates = result.loc[result["net_budget_impact"] < 0, "year"]
    if len(candidates):
        summary["first_year_with_net_savings"] = int(candidates.iloc[0])
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(result["year"], result["net_budget_impact"], marker="o", label="Base")
    ax.fill_between(result["year"], result["low_net_budget_impact"], result["high_net_budget_impact"], alpha=.2, label="Scenario range")
    ax.axhline(0, linewidth=1)
    ax.set_xlabel("Year"); ax.set_ylabel("Net budget impact")
    ax.set_title("Multiyear budget-impact profile"); ax.legend()
    save_figure(fig, out/"budget_impact_profile.png")
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_metadata(out, "13_budget_impact_analysis", input_path, summary)
    return summary
