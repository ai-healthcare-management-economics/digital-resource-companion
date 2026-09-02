"""AIHE-PY29 - AI-HED decision-provenance and lifecycle-trigger audit
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

from datetime import date
REQUIRED={"decision_id","intervention_version","current_state","effective_date","evidence_cut_off","decision_authority","next_review","open_triggers"}

def provenance_audit(record: dict[str,object], today: date|None=None) -> dict[str,object]:
    today=today or date.today(); missing=sorted(k for k in REQUIRED if k not in record or record[k] in (None,"",[]))
    conflicts=[]
    if record.get("deployed_version") and record.get("intervention_version")!=record.get("deployed_version"): conflicts.append("Decision and deployed versions differ")
    overdue=False
    try: overdue=date.fromisoformat(str(record.get("next_review"))) < today
    except ValueError: pass
    return {"missing_authoritative_records":missing,"conflicting_versions":conflicts,"overdue_review":overdue,"unresolved_triggers":record.get("open_triggers",[]),"requires_accountable_review":bool(missing or conflicts or overdue or record.get("open_triggers"))}

if __name__ == "__main__":
    demo={"decision_id":"D-001","intervention_version":"2.0","deployed_version":"2.1","current_state":"restricted","effective_date":"2026-08-01","evidence_cut_off":"2026-07-15","decision_authority":"AI Governance Committee","next_review":"2026-09-30","open_triggers":["Upstream model changed"]}; print(provenance_audit(demo,date(2026,9,2)))
