from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _params(df):
    require_columns(df,["parameter","value"],"Parameters")
    return dict(zip(df["parameter"].astype(str),df["value"]))

def _simulate(cohort,p,ai,rng):
    cycles=int(p.get("cycles",5));base=float(p.get("baseline_event_probability",.12))
    rr=float(p.get("ai_relative_risk",.8)); event_cost=float(p.get("event_cost",5000))
    annual_ai=float(p.get("annual_ai_cost",150));util_loss=float(p.get("event_utility_loss",.08))
    records=[]
    for _,person in cohort.iterrows():
        events=0;cost=0.0;qaly=0.0
        adherence=float(person["adherence_probability"]) if ai else 0.0
        for cycle in range(1,cycles+1):
            p_event=min(max(base*(0.5+float(person["risk_score"])),0),.95)
            if ai:
                effective=rng.random()<adherence
                p_event*=rr if effective else 1.0
                cost+=annual_ai
            event=rng.random()<p_event
            events+=int(event);cost+=event_cost*int(event);qaly+=1-util_loss*int(event)
        records.append({"patient_id":person["patient_id"],"subgroup":person["subgroup"],
                        "events":events,"cost":cost,"qaly":qaly})
    return pd.DataFrame(records)

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    cohort=read_sheet(input_path,"Cohort");p=_params(read_sheet(input_path,"Parameters"))
    require_columns(cohort,["patient_id","age","risk_score","subgroup","adherence_probability"],"Cohort")
    usual=_simulate(cohort,p,False,np.random.default_rng(seed))
    ai=_simulate(cohort,p,True,np.random.default_rng(seed+1))
    usual["strategy"]="Usual care";ai["strategy"]="AI"
    combined=pd.concat([usual,ai],ignore_index=True)
    combined.to_csv(out/"patient_level_results.csv",index=False)
    summary=combined.groupby(["strategy","subgroup"],as_index=False).agg(
        patients=("patient_id","count"),mean_events=("events","mean"),mean_cost=("cost","mean"),mean_qaly=("qaly","mean"))
    summary.to_csv(out/"subgroup_summary.csv",index=False)
    overall=combined.groupby("strategy").agg(mean_cost=("cost","mean"),mean_qaly=("qaly","mean"),mean_events=("events","mean"))
    dc=float(overall.loc["AI","mean_cost"]-overall.loc["Usual care","mean_cost"])
    de=float(overall.loc["AI","mean_qaly"]-overall.loc["Usual care","mean_qaly"])
    wtp=float(p.get("willingness_to_pay",50000));inmb=wtp*de-dc
    pivot=summary.pivot(index="subgroup",columns="strategy",values="mean_events")
    fig,ax=plt.subplots(figsize=(8,5));pivot.plot(kind="bar",ax=ax)
    ax.set_ylabel("Mean events per patient");ax.set_title("Microsimulation outcomes by subgroup")
    save_figure(fig,out/"subgroup_events.png")
    payload={"incremental_cost_per_patient":dc,"incremental_qaly_per_patient":de,
             "incremental_nmb_per_patient":float(inmb)}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"20_patient_microsimulation",input_path,payload)
    return payload
