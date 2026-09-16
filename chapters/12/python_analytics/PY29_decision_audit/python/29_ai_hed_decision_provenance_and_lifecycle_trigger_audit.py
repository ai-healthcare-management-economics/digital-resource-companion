"""AIHE-PY29 - AI-HED decision-provenance and lifecycle-trigger audit.

Digital Resource Companion V1.0. Synthetic demonstration only.
The module identifies matters requiring accountable review. It does not authorize,
renew, restrict, suspend, replace, or retire an intervention.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "decision_id", "intervention_version", "current_state", "effective_date",
    "evidence_cut_off", "decision_authority", "next_review", "open_triggers",
}
VALID_STATES = {'restricted use', 'authorized use', 'paused or suspended', 'conditional use', 'retired or superseded', 'under consideration', 'evaluation authorized'}

def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None

def provenance_audit(record: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    """Return traceable findings rather than an aggregate completeness score."""
    today = today or date.today()
    findings: list[dict[str, str]] = []
    missing = sorted(k for k in REQUIRED_FIELDS if k not in record or record[k] in (None, ""))
    for field in missing:
        findings.append({"category": "missing record", "finding": field, "response": "complete or justify absence"})

    intervention = str(record.get("intervention_version", ""))
    deployed = str(record.get("deployed_version", ""))
    if intervention and deployed and intervention != deployed:
        findings.append({"category": "version conflict", "finding": f"decision={intervention}; deployed={deployed}", "response": "reconcile identity and reassess affected evidence"})

    state = str(record.get("current_state", "")).strip().lower()
    if state and state not in VALID_STATES:
        findings.append({"category": "decision state", "finding": str(record.get("current_state")), "response": "record one of the seven institutional permission states; document implementation activity separately"})

    next_review = _parse_date(record.get("next_review"))
    if record.get("next_review") and next_review is None:
        findings.append({"category": "review date", "finding": str(record.get("next_review")), "response": "use an ISO date"})
    elif next_review and next_review < today:
        findings.append({"category": "overdue review", "finding": next_review.isoformat(), "response": "convene accountable review"})

    expiry = _parse_date(record.get("conditions_expiry"))
    if expiry and expiry < today:
        findings.append({"category": "expired condition", "finding": expiry.isoformat(), "response": "restrict use pending review unless a current authority determines otherwise"})

    triggers = record.get("open_triggers") or []
    if not isinstance(triggers, list):
        triggers = [str(triggers)]
    for trigger in triggers:
        findings.append({"category": "unresolved trigger", "finding": str(trigger), "response": "assign owner, evidence requirement, and decision date"})

    return {
        "decision_id": record.get("decision_id"),
        "current_state": record.get("current_state"),
        "audit_date": today.isoformat(),
        "findings": findings,
        "requires_accountable_review": bool(findings),
        "authorization_effect": "None - advisory audit only",
    }

def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "audit_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (output_dir / "audit_findings.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "finding", "response"])
        writer.writeheader(); writer.writerows(result["findings"])

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON AI-HED record; defaults to bundled synthetic data")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/generated"))
    parser.add_argument("--today", type=date.fromisoformat, help="Optional ISO audit date for reproducibility")
    args = parser.parse_args()
    default = Path(__file__).resolve().parents[1] / "data" / "29_synthetic_ai_hed_record.json"
    source = args.input or default
    record = json.loads(source.read_text(encoding="utf-8-sig"))
    result = provenance_audit(record, args.today)
    write_outputs(result, args.output_dir)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
