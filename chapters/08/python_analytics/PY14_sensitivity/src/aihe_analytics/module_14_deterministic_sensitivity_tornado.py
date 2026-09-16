from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    params = read_sheet(input_path, "Parameters")
    model = read_sheet(input_path, "Model")
    require_columns(params, ["parameter","base","low","high"], "Parameters")
    require_columns(model, ["parameter","coefficient"], "Model")
    merged = params.merge(model, on="parameter", how="left")
    if merged["coefficient"].isna().any():
        raise ValueError("Every parameter must have a coefficient in the Model sheet.")
    intercept_rows = model[model["parameter"].astype(str).str.lower()=="intercept"]
    intercept = float(intercept_rows["coefficient"].iloc[0]) if len(intercept_rows) else 0.0
    merged = merged[merged["parameter"].astype(str).str.lower()!="intercept"].copy()
    base_outcome = intercept + (merged["base"]*merged["coefficient"]).sum()
    rows = []
    for _, r in merged.iterrows():
        low_outcome = base_outcome + (r["low"]-r["base"])*r["coefficient"]
        high_outcome = base_outcome + (r["high"]-r["base"])*r["coefficient"]
        rows.append({
            "parameter":r["parameter"],"base_outcome":base_outcome,
            "low_outcome":low_outcome,"high_outcome":high_outcome,
            "minimum_outcome":min(low_outcome,high_outcome),
            "maximum_outcome":max(low_outcome,high_outcome),
            "range":abs(high_outcome-low_outcome)
        })
    result = pd.DataFrame(rows).sort_values("range", ascending=True)
    result.to_csv(out/"one_way_sensitivity.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, max(5, len(result)*.45)))
    left = result["minimum_outcome"] - base_outcome
    width = result["maximum_outcome"] - result["minimum_outcome"]
    ax.barh(result["parameter"], width, left=left)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("Change from base-case outcome")
    ax.set_title("Tornado analysis")
    save_figure(fig, out/"tornado_chart.png")
    most = result.sort_values("range", ascending=False).iloc[0]
    payload = {"base_outcome":float(base_outcome),"most_influential_parameter":str(most["parameter"]),
               "largest_range":float(most["range"])}
    (out/"summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_metadata(out, "14_deterministic_sensitivity_tornado", input_path, payload)
    return payload
