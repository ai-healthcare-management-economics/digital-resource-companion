from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

INCIDENT_CATEGORIES = [
    "Technical", "Clinical", "Workflow", "Privacy",
    "Cybersecurity", "Equity", "Communication",
]
RECONSTRUCTION_FIELDS = [
    "data_provenance", "model_version", "ai_output", "human_action",
    "context", "immediate_response", "corrective_action", "closure_status",
]

RECOMMENDED_CADENCE = pd.DataFrame([
    {"frequency":"Continuous / daily", "primary_purpose":"Technical surveillance and service protection", "minimum_review_content":"Availability, interfaces, data quality, latency, errors, cybersecurity alerts, logging, deployed version, and fallback status", "primary_owner":"Technical operations / MLOps"},
    {"frequency":"Weekly during pilots", "primary_purpose":"Operational and workflow review", "minimum_review_content":"Volume, action and override rates, delays, workarounds, support issues, capacity, and near misses", "primary_owner":"Clinical or operational service lead"},
    {"frequency":"Monthly", "primary_purpose":"Multidisciplinary performance and safety review", "minimum_review_content":"Technical and clinical performance, calibration, outcomes, incidents, changes, training, and corrective actions", "primary_owner":"AI governance / quality group"},
    {"frequency":"Quarterly / semi-annually", "primary_purpose":"Subgroup, workforce, and economic reassessment", "minimum_review_content":"Subgroup performance and access, workload, benefit realization, lifecycle cost, budget impact, trust, and comparator changes", "primary_owner":"Economics, equity, workforce, and quality leads"},
    {"frequency":"Annually", "primary_purpose":"Renew, restrict, replace, or retire", "minimum_review_content":"Intended use, accumulated evidence, realized value, residual risk, contract performance, alternatives, monitoring, and exit readiness", "primary_owner":"Executive sponsor and AI governance committee"},
    {"frequency":"Event triggered", "primary_purpose":"Extraordinary review", "minimum_review_content":"Material change, serious incident, repeated anomaly, unexplained disparity, or inability to monitor reliably", "primary_owner":"Named incident lead"},
])


def _status(row):
    value=float(row["value"]);warn=float(row["warning_threshold"]);stop=float(row["stop_threshold"])
    direction=str(row["direction"]).lower()
    if direction=="higher_is_worse":
        return "STOP" if value>=stop else ("WARNING" if value>=warn else "OK")
    if direction=="lower_is_worse":
        return "STOP" if value<=stop else ("WARNING" if value<=warn else "OK")
    raise ValueError("direction must be 'higher_is_worse' or 'lower_is_worse'.")


def _nonempty(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype(str).str.strip().ne("")


def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    mon=read_sheet(input_path,"Monitoring");thr=read_sheet(input_path,"Thresholds")
    require_columns(mon,["date","indicator","domain","value","subgroup","model_version"],"Monitoring")
    require_columns(thr,["indicator","direction","warning_threshold","stop_threshold","owner","response"],"Thresholds")
    d=mon.merge(thr,on="indicator",how="left",validate="many_to_one")
    if d["direction"].isna().any():
        raise ValueError("Every monitored indicator must have a row in Thresholds.")
    d["date"]=pd.to_datetime(d["date"]);d["status"]=d.apply(_status,axis=1)
    d=d.sort_values(["indicator","subgroup","date"])
    d.to_csv(out/"monitoring_status.csv",index=False)
    events=d[d["status"].isin(["WARNING","STOP"])].copy()
    events.to_csv(out/"governance_events.csv",index=False)
    latest=d.sort_values("date").groupby(["indicator","subgroup"],as_index=False).tail(1)
    latest.to_csv(out/"latest_indicator_status.csv",index=False)
    indicators=d["indicator"].drop_duplicates().tolist()
    for indicator in indicators[:6]:
        sub=d[d["indicator"]==indicator]
        fig,ax=plt.subplots(figsize=(9,5))
        for subgroup,g in sub.groupby("subgroup"):
            ax.plot(g["date"],g["value"],marker="o",label=str(subgroup))
        t=thr[thr["indicator"]==indicator].iloc[0]
        ax.axhline(t["warning_threshold"],linestyle="--",label="Warning")
        ax.axhline(t["stop_threshold"],linestyle=":",label="Stop")
        ax.set_title(f"Algorithmovigilance: {indicator}");ax.legend()
        save_figure(fig,out/f"indicator_{indicator.replace(' ','_').replace('/','_')}.png")

    # Operating cadence is always exported. A local Cadence sheet may supplement or replace it.
    xls=pd.ExcelFile(input_path)
    cadence=RECOMMENDED_CADENCE.copy()
    if "Cadence" in xls.sheet_names:
        local=pd.read_excel(input_path,sheet_name="Cadence")
        required=["frequency","primary_purpose","minimum_review_content","primary_owner"]
        require_columns(local,required,"Cadence")
        cadence=local[required].copy()
    cadence.to_csv(out/"algorithmovigilance_operating_cadence.csv",index=False)

    incident_count=0; open_incidents=0; reconstruction_gaps=0; category_issues=0
    if "Incidents" in xls.sheet_names:
        inc=pd.read_excel(input_path,sheet_name="Incidents")
        required=["incident_id","date","primary_category","secondary_category"]+RECONSTRUCTION_FIELDS
        require_columns(inc,required,"Incidents")
        inc["date"]=pd.to_datetime(inc["date"],errors="coerce")
        for c in ["primary_category","secondary_category"]:
            inc[c]=inc[c].fillna("").astype(str).str.strip().str.title()
        valid=set(INCIDENT_CATEGORIES)|{""}
        invalid=~inc["primary_category"].isin(INCIDENT_CATEGORIES) | ~inc["secondary_category"].isin(valid)
        inc["category_valid"]=~invalid
        completeness=[]
        missing=[]
        for _,row in inc.iterrows():
            miss=[f for f in RECONSTRUCTION_FIELDS if pd.isna(row[f]) or str(row[f]).strip()==""]
            missing.append("; ".join(miss)); completeness.append((len(RECONSTRUCTION_FIELDS)-len(miss))/len(RECONSTRUCTION_FIELDS))
        inc["reconstruction_completeness"]=completeness; inc["missing_reconstruction_fields"]=missing
        inc.to_csv(out/"incident_reconstruction_audit.csv",index=False)
        cats=pd.concat([inc["primary_category"],inc["secondary_category"]]).replace("",pd.NA).dropna().value_counts().rename_axis("category").reset_index(name="events")
        cats.to_csv(out/"incident_taxonomy_summary.csv",index=False)
        incident_count=int(len(inc)); open_incidents=int(~inc["closure_status"].astype(str).str.lower().isin(["closed","complete","approved"]).sum())
        reconstruction_gaps=int((inc["reconstruction_completeness"]<1).sum()); category_issues=int(invalid.sum())
    else:
        pd.DataFrame({"category":INCIDENT_CATEGORIES,"events":0}).to_csv(out/"incident_taxonomy_summary.csv",index=False)
        pd.DataFrame(columns=["incident_id","date","primary_category","secondary_category"]+RECONSTRUCTION_FIELDS+["category_valid","reconstruction_completeness","missing_reconstruction_fields"]).to_csv(out/"incident_reconstruction_audit.csv",index=False)

    payload={
        "warning_events":int((d["status"]=="WARNING").sum()),
        "stop_events":int((d["status"]=="STOP").sum()),
        "latest_stop_indicators":latest.loc[latest["status"]=="STOP","indicator"].astype(str).tolist(),
        "incident_count":incident_count,
        "open_incidents":open_incidents,
        "incidents_with_reconstruction_gaps":reconstruction_gaps,
        "incident_category_issues":category_issues,
        "cadence_rows":int(len(cadence)),
    }
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"27_algorithmovigilance_monitoring",input_path,payload)
    return payload
