"""AIHE-PY36 - Circular stock-flow, value-retention, and leakage accounting.

Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

NUMERIC = ["opening_stock", "new_inflow", "recovered_inflow", "outflow", "inner_loop_retained", "outer_loop_retained", "recovered_material", "disposed"]

def analyse_row(row: dict[str, str]) -> dict[str, object]:
    values = {key: float(row.get(key, 0) or 0) for key in NUMERIC}
    closing = values["opening_stock"] + values["new_inflow"] + values["recovered_inflow"] - values["outflow"]
    retained = values["inner_loop_retained"] + values["outer_loop_retained"] + values["recovered_material"]
    leakage = max(0.0, values["outflow"] - retained)
    retention_rate = retained / values["outflow"] if values["outflow"] else 0.0
    return {"period": row.get("period"), "resource": row.get("resource"), **values,
            "closing_stock": closing, "retained_value_flow": retained,
            "circular_leakage": leakage, "retention_rate": retention_rate}

def analyse(rows: Iterable[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, float]]:
    results = [analyse_row(row) for row in rows]
    total_outflow = sum(float(r["outflow"]) for r in results)
    total_retained = sum(float(r["retained_value_flow"]) for r in results)
    total_leakage = sum(float(r["circular_leakage"]) for r in results)
    summary = {"total_outflow": total_outflow, "total_retained_value_flow": total_retained,
               "total_circular_leakage": total_leakage,
               "overall_retention_rate": total_retained / total_outflow if total_outflow else 0.0}
    return results, summary

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/generated"))
    args = parser.parse_args()
    source = args.input or Path(__file__).resolve().parents[1] / "data" / "36_synthetic_stock_flows.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle: rows = list(csv.DictReader(handle))
    results, summary = analyse(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(results[0]) if results else []
    with (args.output_dir / "stock_flow_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(results)
    (args.output_dir / "stock_flow_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
