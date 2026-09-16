from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    strategies = read_sheet(input_path, "Strategies")
    params = read_sheet(input_path, "Parameters")
    require_columns(strategies, ["strategy","cost_per_patient","effect_per_patient","role"], "Strategies")
    require_columns(params, ["parameter","value"], "Parameters")
    p = dict(zip(params["parameter"].astype(str), params["value"]))
    threshold = float(p.get("willingness_to_pay", 50000))
    comparator_rows = strategies[strategies["role"].astype(str).str.lower()=="comparator"]
    ai_rows = strategies[strategies["role"].astype(str).str.lower()=="ai"]
    if len(comparator_rows) != 1 or len(ai_rows) != 1:
        raise ValueError("Strategies must include exactly one row with role='comparator' and one with role='ai'.")
    comp = comparator_rows.iloc[0]; ai = ai_rows.iloc[0]
    dc = float(ai["cost_per_patient"] - comp["cost_per_patient"])
    de = float(ai["effect_per_patient"] - comp["effect_per_patient"])
    icer = dc/de if de != 0 else np.nan
    nmb_comp = threshold*float(comp["effect_per_patient"]) - float(comp["cost_per_patient"])
    nmb_ai = threshold*float(ai["effect_per_patient"]) - float(ai["cost_per_patient"])
    incremental_nmb = nmb_ai-nmb_comp
    if dc < 0 and de > 0:
        interpretation = "AI dominates: lower cost and greater effect."
    elif dc > 0 and de < 0:
        interpretation = "AI is dominated: higher cost and lower effect."
    elif incremental_nmb > 0:
        interpretation = "AI has positive incremental net monetary benefit at the selected threshold."
    else:
        interpretation = "Comparator has higher net monetary benefit at the selected threshold."
    result = pd.DataFrame({
        "measure":["Incremental cost","Incremental effect","ICER","Comparator NMB","AI NMB","Incremental NMB","Interpretation"],
        "value":[dc,de,icer,nmb_comp,nmb_ai,incremental_nmb,interpretation]
    })
    strategy_out = strategies.copy()
    strategy_out["nmb"] = threshold*strategy_out["effect_per_patient"]-strategy_out["cost_per_patient"]
    result.to_csv(out/"incremental_analysis.csv", index=False)
    strategy_out.to_csv(out/"strategy_results.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter([de],[dc],s=80)
    ax.axhline(0, linewidth=1); ax.axvline(0, linewidth=1)
    xs = np.linspace(min(-0.01,de*1.5), max(0.01,de*1.5), 100)
    ax.plot(xs, threshold*xs, linestyle="--", label=f"Threshold={threshold:,.0f}")
    ax.set_xlabel("Incremental effect"); ax.set_ylabel("Incremental cost")
    ax.set_title("Cost-effectiveness plane"); ax.legend()
    save_figure(fig, out/"cost_effectiveness_plane.png")
    payload = {"incremental_cost":dc,"incremental_effect":de,
               "icer":None if np.isnan(icer) else float(icer),
               "incremental_nmb":float(incremental_nmb),"interpretation":interpretation}
    (out/"summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_metadata(out, "12_cost_effectiveness_icer_nmb", input_path, payload)
    return payload
