from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID = "03"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out = ensure_output_dir(output_dir)
    data = read_sheet(input_path, "Data")
    require_columns(data, ["outcome","age","risk_score","cost"], "Data")
    for c in ["outcome","age","risk_score","cost"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    missing = pd.DataFrame({
        "variable": data.columns,
        "missing_count": [int(data[c].isna().sum()) for c in data.columns],
        "missing_percent": [float(data[c].isna().mean()*100) for c in data.columns]
    })
    complete = data.dropna()
    mean_imp = data.copy()
    median_imp = data.copy()
    for c in ["age","risk_score","cost"]:
        mean_imp[c] = mean_imp[c].fillna(mean_imp[c].mean())
        median_imp[c] = median_imp[c].fillna(median_imp[c].median())

    total = len(data)
    missing_outcomes = int(data["outcome"].isna().sum())
    positive_known = float(data["outcome"].sum(skipna=True))
    worst = positive_known / max(total,1)
    best = (positive_known + missing_outcomes) / max(total,1)
    scenarios = pd.DataFrame([
        {"scenario":"Observed outcomes only","outcome_rate":data["outcome"].mean(),"mean_cost":data["cost"].mean(),"rows":data["outcome"].notna().sum()},
        {"scenario":"Complete case","outcome_rate":complete["outcome"].mean(),"mean_cost":complete["cost"].mean(),"rows":len(complete)},
        {"scenario":"Mean imputation for predictors","outcome_rate":mean_imp["outcome"].mean(),"mean_cost":mean_imp["cost"].mean(),"rows":mean_imp["outcome"].notna().sum()},
        {"scenario":"Median imputation for predictors","outcome_rate":median_imp["outcome"].mean(),"mean_cost":median_imp["cost"].mean(),"rows":median_imp["outcome"].notna().sum()},
        {"scenario":"All missing outcomes are 0","outcome_rate":worst,"mean_cost":data["cost"].mean(),"rows":total},
        {"scenario":"All missing outcomes are 1","outcome_rate":best,"mean_cost":data["cost"].mean(),"rows":total},
    ])
    missing.to_csv(out/"missingness_profile.csv", index=False)
    scenarios.to_csv(out/"missing_data_scenarios.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.5,5))
    ax.barh(scenarios["scenario"][::-1], scenarios["outcome_rate"][::-1])
    ax.set_xlabel("Estimated outcome rate")
    ax.set_title("Sensitivity to missing-data assumptions")
    save_figure(fig, out/"missing_data_sensitivity.png")

    summary = {
        "rows": total, "complete_case_rows": int(len(complete)),
        "missing_outcomes": missing_outcomes,
        "worst_case_rate": float(worst), "best_case_rate": float(best)
    }
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_metadata(out, MODULE_ID, input_path, summary)
    print(scenarios.to_string(index=False))
