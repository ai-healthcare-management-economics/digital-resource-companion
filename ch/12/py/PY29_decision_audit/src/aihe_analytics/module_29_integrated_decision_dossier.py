from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

SHEETS=["Use_Case","Evidence","Economics","Governance","Implementation","Monitoring"]
PASS_STATUSES={"complete","approved","n/a","na","pass"}
FAIL_STATUSES={"fail","failed","not acceptable","stop"}
CONDITIONAL_STATUSES={"conditional","pass with conditions","incomplete","pending","remediate"}


def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    rows=[]
    for sheet in SHEETS:
        d=read_sheet(input_path,sheet)
        require_columns(d,["item","response","status","owner","evidence_date","confidence"],sheet)
        x=d.copy();x["section"]=sheet
        norm=x["status"].fillna("").astype(str).str.strip().str.lower()
        x["complete"]=norm.isin(PASS_STATUSES)
        x["owner_missing"]=x["owner"].isna() | (x["owner"].astype(str).str.strip()=="")
        x["confidence_numeric"]=pd.to_numeric(x["confidence"],errors="coerce").clip(0,1)
        rows.append(x)
    all_items=pd.concat(rows,ignore_index=True)
    all_items.to_csv(out/"dossier_item_audit.csv",index=False)
    summary=all_items.groupby("section",as_index=False).agg(
        items=("item","count"),completed=("complete","sum"),mean_confidence=("confidence_numeric","mean"),owner_gaps=("owner_missing","sum"))
    summary["completion_rate"]=summary["completed"]/summary["items"]
    summary.to_csv(out/"dossier_domain_summary.csv",index=False)
    unresolved=all_items[~all_items["complete"]].copy()
    unresolved.to_csv(out/"unresolved_items.csv",index=False)

    xls=pd.ExcelFile(input_path)
    safeguards=pd.DataFrame(columns=["safeguard","status","evidence","residual_risk"])
    if "Safeguards" in xls.sheet_names:
        safeguards=pd.read_excel(input_path,sheet_name="Safeguards")
        require_columns(safeguards,["safeguard","status","evidence","residual_risk"],"Safeguards")
    safeguards.to_csv(out/"mandatory_safeguard_review.csv",index=False)
    safeguard_norm=safeguards["status"].fillna("").astype(str).str.strip().str.lower() if len(safeguards) else pd.Series(dtype=str)
    safeguard_fails=int(safeguard_norm.isin(FAIL_STATUSES).sum())
    safeguard_conditions=int(safeguard_norm.isin(CONDITIONAL_STATUSES).sum())
    safeguards_missing=bool(len(safeguards)==0)

    decision=pd.DataFrame(columns=["field","response"])
    if "Decision_Record" in xls.sheet_names:
        decision=pd.read_excel(input_path,sheet_name="Decision_Record")
        require_columns(decision,["field","response"],"Decision_Record")
    decision.to_csv(out/"decision_record.csv",index=False)

    unresolved_count=int(len(unresolved)); owner_gaps=int(all_items["owner_missing"].sum())
    if safeguard_fails>0:
        readiness="Not ready — mandatory safeguard failure"
    elif safeguards_missing or safeguard_conditions>0 or unresolved_count>0 or owner_gaps>0:
        readiness="Conditional — remediation or evidence required"
    else:
        readiness="Ready for accountable decision review"

    fig,ax=plt.subplots(figsize=(9,5));ax.bar(summary["section"],summary["completion_rate"])
    ax.set_ylim(0,1);ax.set_ylabel("Completion rate");ax.set_title("AI-HED completeness by decision domain")
    ax.tick_params(axis="x",rotation=35)
    save_figure(fig,out/"dossier_completeness.png")
    payload={
        "decision_readiness_category":readiness,
        "unresolved_item_count":unresolved_count,
        "owner_gap_count":owner_gaps,
        "least_complete_section":str(summary.sort_values("completion_rate").iloc[0]["section"]),
        "mandatory_safeguard_failures":safeguard_fails,
        "mandatory_safeguard_conditions":safeguard_conditions,
        "safeguard_sheet_missing":safeguards_missing,
        "decision_record_present":bool(len(decision)>0),
    }
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"29_integrated_decision_dossier",input_path,payload)
    return payload
