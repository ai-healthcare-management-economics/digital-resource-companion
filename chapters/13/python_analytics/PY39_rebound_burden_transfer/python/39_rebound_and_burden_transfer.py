"""AIHE-PY39 - Rebound, induced-demand, and burden-transfer analysis.

Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

def analyse(row: dict[str, str]) -> dict[str, object]:
    base_volume=float(row["base_volume"]); new_volume=float(row["new_volume"])
    base_intensity=float(row["base_intensity"]); new_intensity=float(row["new_intensity"])
    before=base_volume*base_intensity; after=new_volume*new_intensity
    engineering_saving=base_volume*(base_intensity-new_intensity)
    realized_saving=before-after
    rebound_amount=engineering_saving-realized_saving
    rebound_fraction=rebound_amount/engineering_saving if engineering_saving else 0.0
    local=float(row.get("local_change",0) or 0); supplier=float(row.get("supplier_change",0) or 0); future=float(row.get("future_change",0) or 0)
    return {"scenario":row["scenario"],"before_total":before,"after_total":after,
            "engineering_saving":engineering_saving,"realized_saving":realized_saving,
            "rebound_amount":rebound_amount,"rebound_fraction":rebound_fraction,
            "local_change":local,"supplier_or_other_location_change":supplier,
            "future_period_change":future,"net_burden_change":local+supplier+future}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path)
    parser.add_argument("--output-dir",type=Path,default=Path("outputs/generated"))
    args=parser.parse_args()
    source=args.input or Path(__file__).resolve().parents[1]/"data"/"39_synthetic_rebound_scenarios.csv"
    with source.open(encoding="utf-8-sig",newline="") as handle: results=[analyse(r) for r in csv.DictReader(handle)]
    args.output_dir.mkdir(parents=True,exist_ok=True)
    fields=list(results[0]) if results else []
    with (args.output_dir/"rebound_burden_results.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(results)
    summary={"scenarios":len(results),"preference_warning":[r["scenario"] for r in results if r["realized_saving"]<0 or r["net_burden_change"]>0],
             "decision_note":"Report intensity and absolute demand together; report transferred burdens separately before drawing a conclusion."}
    (args.output_dir/"rebound_burden_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
