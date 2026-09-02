"""AIHE-PY40 - Lifecycle decision-state and trigger review.

Digital Resource Companion V1.0. Synthetic demonstration only.
The output is advisory and has no authorization effect.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Trigger:
    category: str
    severity: str
    resolved: bool = False
    description: str = ""

def propose_transition(current_state: str, triggers: list[Trigger]) -> dict[str, object]:
    open_triggers=[t for t in triggers if not t.resolved]
    severities={t.severity.strip().lower() for t in open_triggers}
    if "critical" in severities:
        proposed="suspend and convene accountable review"
    elif "major" in severities:
        proposed="restrict use and reassess"
    elif open_triggers:
        proposed="continue only with investigation, named ownership, and a defined review date"
    else:
        proposed="continue the current state subject to scheduled review"
    return {"current_state":current_state,"proposed_transition_for_review":proposed,
            "open_triggers":[asdict(t) for t in open_triggers],
            "authorization_effect":"None - accountable institutional decision required"}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path)
    parser.add_argument("--current-state",default="conditional use")
    parser.add_argument("--output-dir",type=Path,default=Path("outputs/generated"))
    args=parser.parse_args()
    source=args.input or Path(__file__).resolve().parents[1]/"data"/"40_synthetic_triggers.csv"
    with source.open(encoding="utf-8-sig",newline="") as handle:
        triggers=[Trigger(r["category"],r["severity"],r.get("resolved","").strip().lower() in {"true","yes","1"},r.get("description","")) for r in csv.DictReader(handle)]
    result=propose_transition(args.current_state,triggers)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"decision_state_review.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (args.output_dir/"open_triggers.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=["category","severity","resolved","description"]); writer.writeheader(); writer.writerows(result["open_triggers"])
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
