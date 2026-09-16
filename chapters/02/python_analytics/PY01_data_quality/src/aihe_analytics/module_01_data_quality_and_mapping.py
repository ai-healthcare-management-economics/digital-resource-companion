from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID = "01"

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    del seed
    out = ensure_output_dir(output_dir)
    data = read_sheet(input_path, "Data")
    mapping = read_sheet(input_path, "Mapping")
    require_columns(mapping, ["local_field","standard_name","standard_code","required"], "Mapping")

    profile = []
    for column in data.columns:
        s = data[column]
        numeric = pd.to_numeric(s, errors="coerce")
        profile.append({
            "column": column,
            "dtype": str(s.dtype),
            "rows": len(s),
            "missing": int(s.isna().sum()),
            "missing_percent": float(s.isna().mean()*100),
            "unique_values": int(s.nunique(dropna=True)),
            "numeric_min": float(numeric.min()) if numeric.notna().any() else np.nan,
            "numeric_max": float(numeric.max()) if numeric.notna().any() else np.nan,
        })
    profile_df = pd.DataFrame(profile)
    mapping["present_in_data"] = mapping["local_field"].isin(data.columns)
    mapping["mapping_complete"] = (
        mapping["present_in_data"]
        & mapping["standard_name"].fillna("").astype(str).str.strip().ne("")
        & mapping["standard_code"].fillna("").astype(str).str.strip().ne("")
    )
    mapping["required_flag"] = mapping["required"].astype(str).str.lower().isin(["yes","true","1","required"])

    checks = [
        {"check":"duplicate rows","count":int(data.duplicated().sum())},
        {"check":"duplicate patient identifiers","count":int(data["patient_id"].duplicated().sum()) if "patient_id" in data.columns else 0},
        {"check":"required mappings incomplete","count":int((mapping["required_flag"] & ~mapping["mapping_complete"]).sum())},
    ]
    if "age" in data:
        age = pd.to_numeric(data["age"], errors="coerce")
        checks.append({"check":"age outside 0-120","count":int(((age<0)|(age>120)).sum())})
    if "model_score" in data:
        score = pd.to_numeric(data["model_score"], errors="coerce")
        checks.append({"check":"model score outside 0-1","count":int(((score<0)|(score>1)).sum())})
    if "cost" in data:
        cost = pd.to_numeric(data["cost"], errors="coerce")
        checks.append({"check":"negative cost","count":int((cost<0).sum())})
    checks_df = pd.DataFrame(checks)

    subgroup_rows = []
    for c in ["sex","language_group","hospital_site"]:
        if c in data.columns:
            counts = data[c].fillna("Missing").value_counts(dropna=False)
            for value, count in counts.items():
                subgroup_rows.append({"group_column":c,"group_value":value,"count":int(count),"percent":float(count/max(len(data),1)*100)})
    subgroup_df = pd.DataFrame(subgroup_rows)

    profile_df.to_csv(out/"column_profile.csv", index=False)
    mapping.to_csv(out/"mapping_audit.csv", index=False)
    checks_df.to_csv(out/"quality_checks.csv", index=False)
    subgroup_df.to_csv(out/"subgroup_coverage.csv", index=False)

    plot_df = profile_df.sort_values("missing_percent", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(8,5))
    ax.barh(plot_df["column"][::-1], plot_df["missing_percent"][::-1])
    ax.set_xlabel("Missing values (%)")
    ax.set_title("Highest-missingness fields")
    save_figure(fig, out/"missingness_profile.png")

    summary = {
        "rows": int(len(data)),
        "columns": int(data.shape[1]),
        "duplicate_rows": int(data.duplicated().sum()),
        "required_mapping_completeness_percent": float(
            mapping.loc[mapping["required_flag"],"mapping_complete"].mean()*100
        ) if mapping["required_flag"].any() else 100.0
    }
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_metadata(out, MODULE_ID, input_path, summary)
    print(pd.Series(summary).to_string())
