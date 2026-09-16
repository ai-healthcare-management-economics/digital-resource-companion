from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID = "02"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out = ensure_output_dir(output_dir)
    data = read_sheet(input_path, "Data")
    numeric = ["outcome","cost","wait_time","age","risk_score"]
    require_columns(data, ["group",*numeric], "Data")
    for c in numeric:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    overall = data[numeric].describe().T.reset_index().rename(columns={"index":"variable"})
    grouped = data.groupby("group", dropna=False)[numeric].agg(["count","mean","median","std"]).reset_index()
    grouped.columns = ["_".join([str(x) for x in col if str(x)]) for col in grouped.columns.to_flat_index()]
    corr = data[numeric].corr(numeric_only=True)
    overall.to_csv(out/"overall_descriptive_statistics.csv", index=False)
    grouped.to_csv(out/"group_descriptive_statistics.csv", index=False)
    corr.to_csv(out/"correlation_matrix.csv")

    fig, ax = plt.subplots(figsize=(7.5,4.8))
    ax.hist(data["wait_time"].dropna(), bins=20)
    ax.set_xlabel("Wait time")
    ax.set_ylabel("Encounters")
    ax.set_title("Wait-time distribution")
    save_figure(fig, out/"wait_time_histogram.png")

    means = data.groupby("group")["cost"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(7.5,4.8))
    ax.bar(means.index.astype(str), means.values)
    ax.set_xlabel("Group")
    ax.set_ylabel("Mean cost")
    ax.set_title("Mean cost by group")
    ax.tick_params(axis="x", rotation=30)
    save_figure(fig, out/"mean_cost_by_group.png")

    fig, ax = plt.subplots(figsize=(6.5,5.2))
    image = ax.imshow(corr.to_numpy(), aspect="auto")
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr.index)), corr.index)
    ax.set_title("Correlation matrix")
    fig.colorbar(image, ax=ax)
    save_figure(fig, out/"correlation_heatmap.png")

    summary = {
        "rows": int(len(data)),
        "groups": int(data["group"].nunique(dropna=True)),
        "mean_cost": float(data["cost"].mean()),
        "mean_wait_time": float(data["wait_time"].mean()),
        "outcome_rate": float(data["outcome"].mean())
    }
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_metadata(out, MODULE_ID, input_path, summary)
    print(pd.Series(summary).to_string())
