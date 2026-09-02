"""AIHE-PY38 - Circularity-adjusted evaluation of a remote diagnostic pathway.

Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

def adjusted_value(row: dict[str, str]) -> dict[str, object]:
    eligible = str(row.get("mandatory_eligible", "")).strip().lower() in {"true", "yes", "1"}
    health = float(row["health_net_monetary_benefit"])
    lifecycle = float(row["lifecycle_cost"])
    environment = float(row.get("monetized_environmental_effect", 0) or 0)
    residual = float(row.get("realizable_residual_value", 0) or 0)
    resilience = float(row.get("resilience_value", 0) or 0)
    value = health - lifecycle + environment + residual + resilience
    return {"pathway": row["pathway"], "eligible": eligible,
            "circularity_adjusted_net_value": value,
            "non_monetized_evidence": row.get("non_monetized_evidence", ""),
            "accounting_components": "health NMB - lifecycle cost + environmental value + residual value + resilience value"}

def double_count_check(effects: list[dict[str, str]]) -> list[str]:
    seen: dict[str, str] = {}; issues=[]
    for item in effects:
        effect_id=str(item.get("effect_id", "")).strip()
        category=str(item.get("category", "")).strip()
        if effect_id and effect_id in seen:
            issues.append(f"Potential double count: {effect_id} appears in {seen[effect_id]} and {category}")
        elif effect_id:
            seen[effect_id]=category
    return issues

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/generated"))
    args=parser.parse_args()
    source=args.input or Path(__file__).resolve().parents[1] / "data" / "38_synthetic_remote_diagnostic_pathways.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle: results=[adjusted_value(r) for r in csv.DictReader(handle)]
    eligible=sorted((r for r in results if r["eligible"]), key=lambda r:r["circularity_adjusted_net_value"], reverse=True)
    summary={"preferred_eligible_pathway": eligible[0]["pathway"] if eligible else None,
             "ranking": [r["pathway"] for r in eligible],
             "non_monetized_evidence_retained": {r["pathway"]:r["non_monetized_evidence"] for r in results},
             "decision_note":"A higher monetized result cannot override an eligibility or mandatory safeguard failure."}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields=list(results[0]) if results else []
    with (args.output_dir / "remote_pathway_results.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(results)
    (args.output_dir / "remote_pathway_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
