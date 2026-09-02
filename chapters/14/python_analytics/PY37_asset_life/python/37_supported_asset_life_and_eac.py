"""AIHE-PY37 - Supported asset-life, eligibility, EAC, and residual-value analysis.

Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

def equivalent_annual_cost(present_value_cost: float, discount_rate: float, supported_years: int) -> float:
    if supported_years <= 0:
        raise ValueError("supported_years must be positive")
    if discount_rate == 0:
        return present_value_cost / supported_years
    factor = discount_rate * (1 + discount_rate) ** supported_years / ((1 + discount_rate) ** supported_years - 1)
    return present_value_cost * factor

def analyse_option(row: dict[str, str]) -> dict[str, object]:
    years = int(float(row["supported_years"]))
    minimum = int(float(row.get("minimum_supported_years", 0) or 0))
    mandatory = str(row.get("mandatory_eligible", "")).strip().lower() in {"true", "yes", "1"}
    eligible = mandatory and years >= minimum
    pv = float(row["present_value_cost"])
    residual = float(row.get("realizable_residual_value", 0) or 0)
    net_pv = pv - residual
    return {"option": row["option"], "eligible": eligible, "supported_years": years,
            "minimum_supported_years": minimum, "net_present_value_cost": net_pv,
            "expected_downtime_days": float(row.get("expected_downtime_days", 0) or 0),
            "equivalent_annual_cost": equivalent_annual_cost(net_pv, float(row["discount_rate"]), years) if eligible else None,
            "exclusion_reason": "" if eligible else "Mandatory eligibility or minimum supported-life requirement not met"}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/generated"))
    args = parser.parse_args()
    source = args.input or Path(__file__).resolve().parents[1] / "data" / "37_synthetic_asset_options.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle: results=[analyse_option(r) for r in csv.DictReader(handle)]
    eligible = sorted((r for r in results if r["eligible"]), key=lambda r: (r["equivalent_annual_cost"], r["expected_downtime_days"]))
    summary = {"preferred_on_eac_and_downtime": eligible[0]["option"] if eligible else None,
               "eligible_options": [r["option"] for r in eligible],
               "excluded_options": [r["option"] for r in results if not r["eligible"]],
               "decision_note": "Economic ranking follows mandatory eligibility; institutional judgement must also consider service quality, resilience, transition, and uncertainty."}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields=list(results[0]) if results else []
    with (args.output_dir / "asset_option_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(results)
    (args.output_dir / "asset_option_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
